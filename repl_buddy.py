import os
from time import localtime
from re import search
from sys import stdin

# Helper function for cat() to avoid eating RAM with big buffers
def _read_file_chunk(file):
    while True:
        chunk = file.read(64)  # small chunks to avoid out of memory errors
        if chunk:
            yield chunk
        else: # empty chunk means end of the file
            return

# Functions named after their *nix shell counterparts
def cat(*file_list):
    if (len(file_list) == 0):
        print("usage: cat('FILE1', [FILE2], ...)")
    else:
        for file in file_list:
            try:
                stat = os.stat(file)
            except:
                print('File not found:', file)
            else:
                with open(file) as f:
                    for chunk in _read_file_chunk(f):
                        print(chunk, end='')
                print()

def cd(dirname='/'):
    os.chdir(dirname)

def date(seconds=None, short=False):
    months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    datetime = localtime(seconds)
    month = months[datetime[1] - 1]
    day = datetime[2]
    day_space = ' ' if day < 10 else ''
    year = datetime[0]
    hour = datetime[3]
    hour_zero = '0' if hour < 10 else ''
    minute = datetime[4]
    minute_zero = '0' if minute < 10 else ''
    if (short == True):
        return '{} {}{} {}{}:{}{}'.format(month, day_space,day, hour_zero, hour, minute_zero, minute)        
    else:
        return '{} {}{}, {} {}{}:{}{}'.format(month, day_space, day, year, hour_zero, hour, minute_zero, minute)

def grep(pattern=None, filename=None):
    if (pattern == None or filename == None):
        print("usage: grep('PATTERN', 'FILENAME')")
    else:
        with open(filename) as file:
            while (True):
                line = file.readline()
                if (not line):
                    break
                search_result = search(pattern, line)
                if (search_result != None):
                    print(line, end='')

def ls(path='.'):
    try:
        is_dir = True if os.stat(path)[0] & 0x4000 else False
    except:
        print('No such file or directory.')
    else:
        if (is_dir):
            parent = path + '/'
            list = os.listdir(path)
        else:
            parent = ''
            list = [path]

        print('total', len(list))
        if (len(list) != 0):
            print('type  size  mtime         name')
            for entry in list:
                properties = os.stat(parent + entry)
                type = 'd' if (properties[0] & 0x4000) else '-'
                size = properties[6]
                mtime = date(properties[8], short=True)
                print('{} {:8d}  {:>11s}  {}'.format(type, size, mtime, entry))

def mkdir(dirname=None):
    if (dirname == None):
        print("usage: mkdir('DIRNAME')")
    else:
        os.mkdir(dirname)

def mv(src_path=None, dest_path=None):
    if (src_path == None or dest_path == None):
        print("usage: mv('SOURCE', 'DEST')")
    else:
        try:    # Does dest_path exist?
            stat = os.stat(dest_path)
        except: # dest_path does not exist. No danger in renaming.
            os.rename(src_path, dest_path)
        else:   # dest_path exists, but maybe it's a directory???
            is_dir = stat[0] & 0x4000
            if (is_dir):
                os.rename(src_path, dest_path + '/' + src_path)
            else:
                print('Cowardly refusing to overwrite existing file.')

def pwd():
    print(os.getcwd())

def recv(filename='recv.txt', eof_marker='EOF'):
    with open(filename, 'wb') as f:
        num_lines = 0
        eof = None
        while (not eof):
            for line in stdin:
                if (line == eof_marker + '\n'):
                    print(num_lines)
                    eof = True
                    break
                f.write(line)
                num_lines += 1

def rm(filename=None):
    if (filename == None):
        print("usage: rm('FILENAME')")
    elif (filename == '*'):
        dir_list = os.listdir()
        for file in dir_list:
            os.remove(file)
    else:
        os.remove(filename)

def rmdir(dirname=None):
    if (dirname == None):
        print("usage: rmdir('DIRNAME')")
    else:
        os.remove(dirname)

def touch(filename=None):
    if (filename == None):
        print("usage: touch('FILENAME')")
    else:
        file = open(filename, 'w')
        file.close()


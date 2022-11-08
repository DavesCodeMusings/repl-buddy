import os
from time import localtime
from re import search
from sys import stdin, stdout

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
        print("Usage: cat('FILE1', [FILE2], ...)")
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

def clear():
    stdout.write('\x1B[H') # Move cursor to col 1, row 1
    stdout.write('\x1B[J') # clear from cursor to end

def date(seconds=None, short=False):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    datetime = localtime(seconds)
    month = months[datetime[1] - 1]
    day = datetime[2]
    day_space = ' ' if day < 10 else ''
    year = datetime[0]
    hour = datetime[3]
    hour_padding = '0' if hour < 10 else ''
    minute = datetime[4]
    minute_padding = '0' if minute < 10 else ''
    if (short == True):
        return '{} {}{} {}{}:{}{}'.format(month, day_space, day, hour_padding, hour, minute_padding, minute)        
    else:
        return '{} {}{}, {} {}{}:{}{}'.format(month, day_space, day, year, hour_padding, hour, minute_padding, minute)

def df(path='.'):
    properties = os.statvfs(path)
    fragment_size = properties[1]
    blocks_total = properties[2]
    blocks_available = properties[4]
    size_kb = int(blocks_total * fragment_size / 1024)
    avail_kb = int(blocks_available * fragment_size / 1024)
    used_kb = size_kb - avail_kb
    percent_used = round(100 * used_kb / size_kb)
    print('Filesystem      Size      Used     Avail   Use%')
    print('flash      {:8d}K {:8d}K {:8d}K   {:3d}%'.format(size_kb, used_kb, avail_kb, percent_used))

def grep(pattern=None, filename=None):
    if (pattern == None or filename == None):
        print("Usage: grep('PATTERN', 'FILENAME')")
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
            print('Type    Size  MTime         Name')
            for entry in list:
                properties = os.stat(parent + entry)
                if (properties[0] & 0x4000):  # entry is a directory
                    type = 'd'
                    size = 0
                else:
                    type = '-'
                    size = properties[6]
                mtime = date(properties[8], short=True)
                print('{} {:10d}  {:>11s}  {}'.format(type, size, mtime, entry))

def mkdir(dirname=None):
    if (dirname == None):
        print("Usage: mkdir('DIRNAME')")
    else:
        os.mkdir(dirname)

def mv(src_path=None, dest_path=None):
    if (src_path == None or dest_path == None):
        print("Usage: mv('SOURCE', 'DEST')")
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
        print("Usage: rm('FILENAME')")
    elif (filename == '*'):
        dir_list = os.listdir()
        for file in dir_list:
            os.remove(file)
    else:
        os.remove(filename)

def rmdir(dirname=None):
    if (dirname == None):
        print("Usage: rmdir('DIRNAME')")
    else:
        os.rmdir(dirname)

def touch(filename=None):
    if (filename == None):
        print("Usage: touch('FILENAME')")
    else:
        file = open(filename, 'w')
        file.close()


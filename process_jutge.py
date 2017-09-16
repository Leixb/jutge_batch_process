#!/usr/bin/python3

from glob import glob
from os.path import basename,isdir,isfile
from os import mkdir
from shutil import copyfile,move
from tempfile import gettempdir

import argparse

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--zip', metavar='file.zip', type=argparse.FileType('r'))
group.add_argument('--folder', type=str,default='')

parser.add_argument('--save-to', type=str,default='Problems_parsed')
parser.add_argument('--delay', metavar='milliseconds', type=int, default=100)
parser.add_argument('--no-download', action='store_true', default=0)
parser.add_argument('--overwritte', action='store_true', default=0)
parser.add_argument('--cookie', type=str, default='')
args = parser.parse_args()

if args.delay > 0:
    from time import sleep

if not args.no_download:
    from urllib.request import urlretrieve
    import httplib2
    from bs4 import BeautifulSoup, SoupStrainer 

def getname(code):
    web = 'https://jutge.org/problems/{}'.format(code)

    http = httplib2.Http()
    if args.cookie != '':
        headers = {"Cookie": "PHPSESSID={}".format(args.cookie),
                "Accept": "text/plain"}
        status, response = http.request(web,headers=headers)
    else :
        status, response = http.request(web)
    soup = BeautifulSoup(response,'lxml')

    name = "-".join(soup.find('title').text.split('-')[1:])
    name = name[1:].replace(' ','_').split()[0]

    return name

if args.folder!='':
    if args.no_download: exit(1)

    prev = ['','']
    cont = 0

    for prog in glob(args.folder + '/*.*'):
        try:
            code, ext = basename(prog).split('.')
            if isfile(prog) and len(code) == 9 and len(ext)>=1 and len(ext)<=3:
                if prev[0] == code:
                    name = prev[1]
                else:
                    name = getname(code)

                if name != 'Error' :
                    prev = [code,name]
                    file_name = '{}/{}.{}'.format(args.folder,name,ext)

                    if not isfile(file_name):
                        print('Moving {} to {} ...'.format(prog,file_name))
                        move(prog,file_name)
                        cont += 1
        except:
            print("Skipping {}...".format(prog))

    print ("FINISHED, {} files processed".format(cont))
    exit(0)

from zipfile import ZipFile

extract_to = gettempdir() + '/process_jutge_TMP'

zip = ZipFile(args.zip.name, 'r')
mkdir(extract_to)
zip.extractall(extract_to)
zip.close()

if not isdir(args.save_to): mkdir(args.save_to)

extensions = ['cc','c','hs','php','bf','py']

count = 0

for folder in glob(extract_to + '/*') :
    try:
        code = basename(folder)

        sources = []

        for ext in extensions :
            match = glob('{}/*AC.{}'.format(folder,ext))
            if match:
                sources.append([match[-1],ext]) # take last AC

        for source in sources :
            ext = source[1]
            if ext == 'cc': ext = 'cpp' # Use cpp over cc for c++ files

            if not glob('{}/{}*.{}'.format(args.save_to,code,ext)) or args.overwritte:
                if args.no_download:
                    name = code
                else:
                    name = getname(code)

                    if name == 'Error': name = code # If name cannot be found default to code to avoid collisions

                file_name = '{}/{}.{}'.format(args.save_to,name,ext)

                print('Copying {} to {} ...'.format(source[0],file_name))
                copyfile(source[0],file_name)

                count += 1

                if args.delay > 0:
                    sleep(args.delay / 1000.0)

    except: print('Skipping {}'.format(folder))

print ('FINISHED; Added {} programs'.format(count))


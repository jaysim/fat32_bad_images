#!/usr/bin/python
#-*- coding: utf-8 -*-

import os
import subprocess as sp
import argparse as ap
import time
import datetime

# bad_cc : bad cluster chain
# bad_de : bad directory entry
# bad_dirty : dirty flag
# bad_ent : bad match of de and lfn entry
# bad_lfn : bad lfn entry

result_dir = "result_output"
cmd = "{} -nfvV {} 2>&1"
current = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

untar_cmd="tar xf {} -C {}"

args=''

class CustomArgumentParser(ap.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def error(self, message):
        required_args = [action.metavar for action in self._actions if action.required]
        print("{}: error: the following arguments are required: ".format(self.prog) + ', '.join(required_args))
        print(self.format_help())
        self.exit(2)

def parse_argument():
    global args

    desc = 'FAT32 bad image test script with two fsck tools'
    path1_help = 'full path for dosfsck of fatprogs'
    path2_help = 'full path for fsck.fat of dosfstools'
    dir_help = 'corrupted images path for testing'

#    parser = ap.ArgumentParser(description=desc)
    parser = CustomArgumentParser(description=desc)
    parser.add_argument("path1", metavar='<dosfsck path>', help=path1_help)
    parser.add_argument("path2", metavar='<fsck.fat path>', help=path2_help)
    parser.add_argument("dirname", metavar='<testdir>', help=dir_help)

    try:
        args = parser.parse_args()
    except ap.ArgumentError as e:
        print(e.message + '\n' + e.argument)
        parser.print_help()
        exit(-1)

    return args

if __name__ != "__main__":
    print('This script  should be run by itsetl, not imported from other module')
    exit(1)

parse_argument()
fatprogs_path = args.path1
dosfstools_path = args.path2
dirname = args.dirname
if (args.dirname[-1] != "/"):
    dirname = args.dirname + "/"

if not os.path.isdir(dirname + result_dir):
    if os.path.isfile(dirname + result_dir):
        os.remove(dirname + result_dir)
    os.mkdir(dirname + result_dir)

dosfstools_output = dirname + result_dir + "/fsckcmp__dosfstools__{}.result.out".format(current)
fatprogs_output = dirname + result_dir + "/fsckcmp__fatprogs__{}.result.out".format(current)

if not (fatprogs_path and dosfstools_path and dirname):
    print("<dosfsck path> for fatprogs fsck, <fsck.fat path> for dosfstools fsck, <testdir> for testing directory should be specified")
    exit(1)

if not os.path.isfile(fatprogs_path):
    print('<dosfsck path>:' + fatprogs_path + ' does not exist')
    exit(1)

if not os.path.isfile(dosfstools_path):
    print('<fsck.fat path>:' + dosfstools_path + ' does not exist')
    exit(1)

#test_images=sorted([file for file in os.listdir(dirname) if file.endswith('.tgz')])
test_images=['fat32_bad_de01.tgz', 'fat32_bad_cc01.tgz']

print("== Start : {} =====================".format(dosfstools_path))
with open(dosfstools_output, 'a') as op:
    for image in test_images:
        try:
            untar_step=untar_cmd.format(dirname + image, dirname)
            dump_file = image.replace('.tgz', '.dump')
            proc = sp.run(untar_step, shell=True, stdout=sp.DEVNULL, stderr=sp.STDOUT)

            print("dosfstools fsck: " + dump_file)
            print("\n\n" + dump_file + " =======================================", file=op, flush=True)
            dosfstools_cmd=cmd.format(dosfstools_path, dump_file)
            proc = sp.run(dosfstools_cmd, shell=True, stdout=op, stderr=sp.STDOUT)
            op.flush()
            time.sleep(1)

        except sp.CalledProcessError as e:
            print(e.output)

print("== Start : {} =====================".format(fatprogs_path))
with open(fatprogs_output, 'a') as op:
    for image in test_images:
        try:
            dump_file = image.replace('.tgz', '.dump')
            print("fatprogs fsck: " + dump_file)
            print("\n\n" + dump_file + " =======================================", file=op, flush=True)
            op.flush()

            fatprogs_cmd=cmd.format(fatprogs_path, dump_file)
            proc = sp.run(fatprogs_cmd, shell=True, stdout=op, stderr=sp.STDOUT)
            op.flush()
            time.sleep(1)

        except sp.CalledProcessError as e:
            print(e.output)

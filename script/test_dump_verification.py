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

# support fsck tools execution file name
support_tools = {
        "fatprogs" : "dosfsck",
        "tfsck" : "fatfsck",
        "wfsck" : "fat_fsck",
        "dosfstools" : "fsck.fat",
}

fatprogs = support_tools.get("fatprogs")
tfsck = support_tools.get("tfsck")
wfsck = support_tools.get("wfsck")
dosfstools = support_tools.get("dosfstools")

dump_target="dump.file"
dump_output = "dump__{}__{}.result.out"
result_dir = "result_output"
current = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

fsck_cmd="time -v {} {} {} 2>&1"
dump_cmd="{} -o {} -v {} 2>&1"
untar_cmd="tar zxvf {} -C {}"

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

    desc = 'FAT32 bad image dump test script'
    verify_help = 'add verification pass option of dosfsck'
    path1_help = 'fsck full path for verifying dumped image, usually fatprogs fsck(dosfsck)'
    path2_help = 'dump full path for dumping image, usually fatprogs domp(dosfsdump)'
    dir_help = '(optional) dump test directory: default "./testdir/"'

#    parser = ap.ArgumentParser(description=desc)
    parser = CustomArgumentParser(description=desc)
    parser.add_argument("-v", help=verify_help, action='store_false')
    parser.add_argument("path1", metavar='<fsck>', help=path1_help)
    parser.add_argument("path2", metavar='<dump>', help=path2_help)
    parser.add_argument("dirname", nargs='?', metavar='<target_dir>', help=dir_help, default=".")

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
path1 = args.path1
path2 = args.path2
dirname = args.dirname
if (args.dirname[-1] != "/"):
    dirname = args.dirname + "/"

testdir = dirname + "testdir/"

# do not use origin dump file,
# you'd better use copied image to <test image path> for test

"""
dump_img="fat32_dumptest.img"
copy = "bash -c 'cp -a {} {} 2>&1'"
# copy dump test image(fat32_dumptest.img) to test directory
print("copy fat32_dump.img")
cp_dump_img = copy.format(dump_img, dirname)
sp.run(cp_dump_img, shell=True)

# some embedded device takes long time to copy in script
# you'd better test after copy them in command line
for image in test_images:
    try:
        print("copy image: " + image)
        pre_cp_cmd = copy.format(image, dirname)
        sp.run(pre_cp_cmd, shell=True)
    except sp.CalledProcessError as e:
        print(e.output)
"""

if not (path1 and path2 and dirname):
    print("<path1> for testing fsck, <path2> of dump utility, <path3> for testing directory should be specified")
    exit(1)

if not os.path.isfile(path1):
    print('<path1>:' + path1 + 'does not exist')
    exit(1)

if not os.path.isfile(path2):
    print('<path2>:' + path2 + 'does not exist')
    exit(1)

if fatprogs in path1:
    path1_arg = "-nfv"
    dump_output = dump_output.format(fatprogs, current)
    if (args.v):
        path1_arg = path1_arg + "V"
elif wfsck in path1:
    path1_arg = "-y"
    dump_output = dump_output.format(wfsck, current)
elif dosfstools in path1:
    path1_arg = "-nfv"
    dump_output = dump_output.format(dosfstools, current)
    if (args.v):
        path1_arg = path1_arg + "V"
elif tfsck in path1:
    path1_arg = "-a"
    dump_output = dump_output.format(tfsck, current)
else:
    print("Not support <fsck> : " + path2)
    exit(1)

test_images=sorted([file for file in os.listdir(dirname) if file.endswith('.tgz')])
#test_images=["fat32_bad_cc01.tgz"]

if not os.path.isdir(dirname + result_dir):
    if os.path.isfile(dirname + result_dir):
        os.remove(dirname + result_dir)
    os.mkdir(dirname + result_dir)

dump_output = dirname + result_dir + '/' + dump_output

if os.path.isfile(dump_output):
    os.remove(dump_output)

if not os.path.isdir(testdir):
    if os.path.isfile(testdir):
        os.remove(testdir)
    os.mkdir(testdir)

total_cnt = len(test_images)
success_cnt = 0

with open(dump_output, 'a') as fd_dump:
    for image in test_images:
        try:
            untar_step=untar_cmd.format(image, testdir)
            file = image.replace('.tgz', '.dump')
            print("== Start : {} =====================".format(file))
            proc = sp.run(untar_step, shell=True, stdout=sp.DEVNULL, stderr=sp.STDOUT)
            fd_dump.flush()

            print("dump step: " + file)
            print("\n\nDump: " + file + " =======================================", file=fd_dump, flush=True)

            dump_step=dump_cmd.format(path2, testdir + dump_target, testdir + file)
            proc = sp.run(dump_step, shell=True, stdout=fd_dump, stderr=sp.STDOUT)
            fd_dump.flush()
            time.sleep(1)

            print("fsck step: " + file)
            print("\n\nfsck: " + file + " =======================================", file=fd_dump, flush=True)

            fsck_step=fsck_cmd.format(path1, path1_arg, testdir + dump_target)
            proc = sp.run(fsck_step, shell=True, stdout=fd_dump, stderr=sp.STDOUT)
            if not (proc.returncode == 0 or proc.returncode == 1):
                print("Failed to dump {}".format(file))
                print("===================================")
                break

            success_cnt += 1
            fd_dump.flush()
            os.remove(testdir + dump_target)
            time.sleep(1)

        except sp.CalledProcessError as e:
            print(e.output)

if total_cnt == success_cnt:
    rm_cmd = "bash -c 'rm -rf {}/{}'".format(testdir, '*.dump')
    sp.run(rm_cmd, shell=True)

    os.rmdir(testdir)

print("\nPassed {} of {} images".format(success_cnt, total_cnt))
print("===================================")

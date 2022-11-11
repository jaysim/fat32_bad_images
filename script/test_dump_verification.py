#!/usr/bin/python
#-*- coding: utf-8 -*-

import os
import subprocess as sp
import argparse as ap
import time

# bad_cc : bad cluster chain
# bad_de : bad directory entry
# bad_dirty : dirty flag
# bad_ent : bad match of de and lfn entry
# bad_lfn : bad lfn entry
bad_sample=[
        "fat32_bad_cc02.dump",
        "fat32_bad_cc03.dump",
        ]

bad_images=[
        "fat32_bad_boot01.dump", "fat32_bad_boot02.dump", "fat32_bad_boot03.dump", "fat32_bad_boot04.dump",
        "fat32_bad_boot05.dump", "fat32_bad_boot06.dump", "fat32_bad_boot07.dump", "fat32_bad_boot08.dump",
        "fat32_bad_boot09.dump",
        "fat32_bad_cc01.dump", "fat32_bad_cc02.dump", "fat32_bad_cc03.dump", "fat32_bad_cc04.dump",
        "fat32_bad_cc05.dump", "fat32_bad_cc06.dump", "fat32_bad_cc07.dump", "fat32_bad_cc08.dump",
        "fat32_bad_cc09.dump", "fat32_bad_cc10.dump", "fat32_bad_cc11.dump", "fat32_bad_cc12.dump",
        "fat32_bad_cc13.dump", "fat32_bad_cc14.dump", "fat32_bad_cc15.dump", "fat32_bad_cc16.dump",
        "fat32_bad_cc17.dump",
        "fat32_bad_de01.dump", "fat32_bad_de02.dump", "fat32_bad_de03.dump", "fat32_bad_de04.dump",
        "fat32_bad_de05.dump", "fat32_bad_de06.dump", "fat32_bad_de07.dump", "fat32_bad_de08.dump",
        "fat32_bad_de09.dump", "fat32_bad_de10.dump", "fat32_bad_de11.dump", "fat32_bad_de13.dump",
        "fat32_bad_de14.dump", "fat32_bad_de15.dump", "fat32_bad_de16.dump", "fat32_bad_de17.dump",
        "fat32_bad_de18.dump", "fat32_bad_de19.dump", "fat32_bad_de20.dump", "fat32_bad_de21.dump",
        "fat32_bad_de22.dump", "fat32_bad_de23.dump", "fat32_bad_de24.dump", "fat32_bad_de25.dump",
        "fat32_bad_de26.dump", "fat32_bad_de27.dump", "fat32_bad_de28.dump", "fat32_bad_de29.dump",
        "fat32_bad_ent01.dump", "fat32_bad_ent02.dump", "fat32_bad_ent03.dump", "fat32_bad_ent04.dump",
        "fat32_bad_ent05.dump", "fat32_bad_ent06.dump",
        "fat32_bad_dirty01.dump",  "fat32_bad_dirty02.dump", "fat32_bad_dirty03.dump",
        "fat32_bad_fsinfo01.dump", "fat32_bad_fsinfo02.dump",
        "fat32_bad_lfn01.dump", "fat32_bad_lfn02.dump", "fat32_bad_lfn03.dump", "fat32_bad_lfn04.dump",
        "fat32_bad_lfn05.dump", "fat32_bad_lfn06.dump",
        "fat32_bad_vol01.dump", "fat32_bad_vol02.dump", "fat32_bad_vol03.dump", "fat32_bad_vol04.dump",
        "fat32_bad_vol05.dump", "fat32_bad_vol06.dump", "fat32_bad_vol07.dump", "fat32_bad_vol08.dump",
        "fat32_bad_vol09.dump", "fat32_bad_vol10.dump", "fat32_bad_vol11.dump", "fat32_bad_vol12.dump",
        "fat32_bad_vol13.dump", "fat32_bad_vol14.dump", "fat32_bad_vol15.dump", "fat32_bad_vol16.dump",
        "fat32_bad_vol17.dump",
        ]

# support fsck tools execution file name
fatprogs="dosfsck"
tfsck="fatfsck"
wfsck="fat_fsck"
dosfstools="fsck.fat"

dump_log_output="dump.log"
dump_file="dump.file"
dump_output = "_fsck_after_dump.out"
fsck_cmd="time -v {} {} {} 2>&1"
dump_cmd="{} -o {} -v {} 2>&1"

copy_dump="cp fat32_bad.img {}/fat32_dumptest.img"

test_images=bad_images
#test_images=bad_sample

args=''

def parse_argument():
    global args

    desc = 'FAT32 bad image dump test script'
    verify_help = 'add verification pass option of dosfsck'
    path1_help = 'full path for verifying dump using fsck, generally fatprogs fsck(dosfsck)'
    path2_help = 'full path for testing dump, generally fatprogs domp(dosfsdump)'
    dir_help = 'corrupted image(dump target) path for testing'

    parser = ap.ArgumentParser(description=desc)
    parser.add_argument("-v", help=verify_help, action='store_false')
    parser.add_argument("path1", metavar='<path1>', help=path1_help)
    parser.add_argument("path2", metavar='<path2>', help=path2_help)
    parser.add_argument("dirname", metavar='<path3>', help=dir_help)

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
    fsck_output = "[" + fatprogs + "]" + dump_output
    if (args.v):
        path1_arg = path1_arg + "V"
elif wfsck in path1:
    path1_arg = "-y"
    fsck_output = "[" + wfsck + "]" + dump_output
elif dosfstools in path1:
    path1_arg = "-nfv"
    fsck_output = "[" + dosfstools + "]" + dump_output
    if (args.v):
        path1_arg = path1_arg + "V"
elif tfsck in path1:
    path1_arg = "-a"
    fsck_output = "[" + tfsck + "]" + dump_output
else:
    print("Not support <fsck> : " + path2)
    exit(1)

fsck_step=fsck_cmd.format(path1, path1_arg, dirname + dump_file)

copy_dump = copy_dump.format(dirname)

dump_log_output = dirname + dump_log_output
fsck_output = dirname + fsck_output

if os.path.isfile(dump_log_output):
    os.remove(dump_log_output)

if os.path.isfile(fsck_output):
    os.remove(fsck_output)

fd_fsck = open(fsck_output, 'a')

with open(dump_log_output, 'a') as fd_dump:
    for image in test_images:
        try:
            dump_step=dump_cmd.format(path2, dirname + dump_file, dirname + image)

            print("dump step: " + image)
            print("\n\n" + image + " =======================================", file=fd_dump, flush=True)
            fd_dump.flush()

            proc = sp.run(dump_step, shell=True, stdout=fd_dump, stderr=sp.STDOUT)
            fd_dump.flush()
            time.sleep(1)

            print("fsck step: " + image)
            print("\n\n" + image + " =======================================", file=fd_fsck, flush=True)
            fd_fsck.flush()

            proc = sp.run(fsck_step, shell=True, stdout=fd_fsck, stderr=sp.STDOUT)
            fd_fsck.flush()
            time.sleep(1)

        except sp.CalledProcessError as e:
            print(e.output)

"""
rm_cmd = "bash -c 'rm -rf {}/{}'".format(dirname, dump_img)
sp.run(rm_cmd, shell=True)
"""
rm_cmd = "bash -c 'rm -rf {}/fat32_bad_* 2>&1'".format(dirname)
sp.run(rm_cmd, shell=True)

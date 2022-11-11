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

fsck_output = "_fsck_result.out"
verified_output = "_fsck_verified_result.out"

fsck_cmd="time -v {} {} {} 2>&1"

test_images=bad_images
#test_images=bad_sample

args=''

def parse_argument():
    global args

    desc = 'FAT32 bad image test & verification script'
    path1_help = 'full path of testing fsck, generally fatprogs fsck(dosfsck)'
    path2_help = 'full path of verifying fsck, generally use dosfstools fsck(fsck.fat)'
    dir_help = 'corrupted images path for testing'

    parser = ap.ArgumentParser(description=desc)
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
copy_cmd = "bash -c 'cp -a {} {} 2>&1'"
for image in test_images:
    try:
        print("copy image: " + image)
        pre_cp_cmd = copy_cmd.format(image, dirname)
        sp.run(pre_cp_cmd, shell=True)
    except sp.CalledProcessError as e:
        print(e.output)
"""

if not (path1 and path2 and dirname):
    print("<path1> for testing fsck, <path2> for verifying fsck, <path3> for testing directory should be specified")
    exit(1)

if not os.path.isfile(path1):
    print('<path1>:' + path1 + ' does not exist')
    exit(1)

if not os.path.isfile(path2):
    print('<patch2>:' + path2 + ' does not exist')
    exit(1)

if fatprogs in path1:
    path1_arg = "-afwv"
    path1_output = "[" + fatprogs + "]" + fsck_output
    path1_msg = fatprogs
elif dosfstools in path1:
    path1_arg = "-afwv"
    path1_output = "[" + dosfstools + "]" + fsck_output
    path1_msg =  dosfstools
elif wfsck  in path1:
    path1_arg = "-y"
    path1_output = "[" + wfsck  + "]" + fsck_output
    path1_msg = wfsck
elif tfsck in path1:
    path1_arg = "-r"
    path1_output = "[" + tfsck + "]" + fsck_output
    path1_msg = tfsck
else:
    print("Not support <path1> : " + path1)
    exit(1)

if dosfstools in path2:
    path2_arg = "-nf"
    path2_output = "[" + dosfstools + "]" + verified_output
    path2_msg = dosfstools
elif tfsck in path2:
    path2_arg = "-s -r"
    path2_output = "[" + tfsck + "]" + verified_output
    path2_msg = tfsck
elif fatprogs in path2:
    path2_arg = "-nfvl"
    path2_output = "[" + fatprogs + "]" + verified_output
    path2_msg = fatprogs
elif wfsck  in path2:
    path2_arg = "-y"
    path2_output = "[" + wfsck  + "]" + verified_output
    path2_msg = wfsck
else:
    print("Not support <path2> : " + path2)
    exit(1)

path2_output = dirname + path2_output
path1_output = dirname + path1_output

if os.path.isfile(path2_output):
    os.remove(path2_output)

if os.path.isfile(path1_output):
    os.remove(path1_output)

fd_path2 = open(path2_output, 'a')

with open(path1_output, 'a') as fd_path1:
    for image in test_images:
        try:
            fsck_step=fsck_cmd.format(path1, path1_arg, dirname + image)
            verify_step=fsck_cmd.format(path2, path2_arg, dirname + image)

            print(path1_msg + ": " + image)
            print("\n\n" + image + " =======================================", file=fd_path1, flush=True)
            fd_path1.flush()


            proc = sp.run(fsck_step, shell=True, stdout=fd_path1, stderr=sp.STDOUT)
            fd_path1.flush()
            time.sleep(1)

            print(path2_msg + ": " + image)
            print("\n\n" + image + " =======================================", file=fd_path2, flush=True)
            fd_path2.flush()

            proc = sp.run(verify_step, shell=True, stdout=fd_path2, stderr=sp.STDOUT)
            fd_path2.flush()
            time.sleep(1)

        except sp.CalledProcessError as e:
            print(e.output)

rm_cmd="bash -c 'rm -rf {}/fat32_bad_* 2>&1'".format(dirname)
sp.run(rm_cmd, shell=True)

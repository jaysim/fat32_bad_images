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

fsck_output = "fsck__{}__{}.result.out"
verified_output = "fsck__{}__{}.verified_result.out"
result_dir = "result_output"
current = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

fsck_cmd="time -v {} {} {} 2>&1"
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

    desc = 'FAT32 bad image checking & verifying script'
    path1_help = 'full path fsck for checking image, usually fatprogs fsck(dosfsck)'
    path2_help = 'full path fsck for verifying image, usually use dosfstools fsck(fsck.fat)'
    dir_help = 'corrupted images path for testing'

#    parser = ap.ArgumentParser(description=desc)
    parser = CustomArgumentParser(description=desc)
    parser.add_argument("path1", metavar='<fsck:check>', help=path1_help)
    parser.add_argument("path2", metavar='<fsck2:verify>', help=path2_help)
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
path1 = args.path1
path2 = args.path2
dirname = args.dirname
if (args.dirname[-1] != "/"):
    dirname = args.dirname + "/"

if not (path1 and path2 and dirname):
    print("<fsck:check> for checking fsck, <fsck2:verify> for verifying fsck, <testdir> for testing directory should be specified")
    exit(1)

if not os.path.isfile(path1):
    print('<path1>:' + path1 + ' does not exist')
    exit(1)

if not os.path.isfile(path2):
    print('<path2>:' + path2 + ' does not exist')
    exit(1)

if fatprogs in path1:
    path1_arg = "-afwv"
    path1_output = fsck_output.format(fatprogs, current)
    path1_msg = fatprogs
elif dosfstools in path1:
    path1_arg = "-afwv"
    path1_output = fsck_output.format(dosfstools, current)
    path1_msg =  dosfstools
elif wfsck in path1:
    path1_arg = "-y"
    path1_output = fsck_output.format(wfsck, current)
    path1_msg = wfsck
elif tfsck in path1:
    path1_arg = "-r"
    path1_output = fsck_output.format(tfsck, current)
    path1_msg = tfsck
else:
    print("Not support <path1> : " + path1)
    exit(1)

if dosfstools in path2:
    path2_arg = "-nf"
    path2_output = verified_output.format(dosfstools, current)
    path2_msg = dosfstools
elif tfsck in path2:
    path2_arg = "-s -r"
    path2_output = verified_output.format(tfsck, current)
    path2_msg = tfsck
elif fatprogs in path2:
    path2_arg = "-nfvl"
    path2_output = verified_output.format(fatprogs, current)
    path2_msg = fatprogs
elif wfsck in path2:
    path2_arg = "-y"
    path2_output = verified_output.format(wfsck, current)
    path2_msg = wfsck
else:
    print("Not support <path2> : " + path2)
    exit(1)

test_images=sorted([file for file in os.listdir(dirname) if file.endswith('.tgz')])
#test_images=['fat32_bad_de01.tgz', 'fat32_bad_cc01.tgz']

if not os.path.isdir(dirname + result_dir):
    if os.path.isfile(dirname + result_dir):
        os.remove(dirname + result_dir)
    os.mkdir(dirname + result_dir)

path2_output = dirname + result_dir + '/' + path2_output
path1_output = dirname + result_dir + '/' + path1_output

if os.path.isfile(path2_output):
    os.remove(path2_output)

if os.path.isfile(path1_output):
    os.remove(path1_output)

fd_path2 = open(path2_output, 'a')

total_cnt = len(test_images)
success_cnt = 0

with open(path1_output, 'a') as fd_path1:
    for image in test_images:
        try:
            untar_step=untar_cmd.format(dirname + image, dirname)
            dump_file = image.replace('.tgz', '.dump')
            print("== Start : {} =====================".format(dump_file))
            proc = sp.run(untar_step, shell=True, stdout=sp.DEVNULL, stderr=sp.STDOUT)

            print("Checking:\t" + path1_msg + ": " + dump_file)
            print("\n\n" + dump_file + " =======================================", file=fd_path1, flush=True)
            fd_path1.flush()

            fsck_step=fsck_cmd.format(path1, path1_arg, dirname + dump_file)
            proc = sp.run(fsck_step, shell=True, stdout=fd_path1, stderr=sp.STDOUT)
            fd_path1.flush()
            time.sleep(1)

            print("Verification:\t" + path2_msg + ": " + dump_file)
            print("\n\n" + dump_file + " =======================================", file=fd_path2, flush=True)
            fd_path2.flush()

            verify_step=fsck_cmd.format(path2, path2_arg, dirname + dump_file)
            proc = sp.run(verify_step, shell=True, stdout=fd_path2, stderr=sp.STDOUT)
            if proc.returncode != 0:
                print("Failed to check {}".format(dump_file))
                print("===================================")
                break

            success_cnt += 1
            fd_path2.flush()
            time.sleep(1)
            print("== Passed : {} ".format(dump_file))

        except sp.CalledProcessError as e:
            print(e.output)

rm_cmd="bash -c 'rm -rf {}/fat32_bad_*.dump 2>&1'".format(dirname)
sp.run(rm_cmd, shell=True)

print("\nPassed {} of {} images".format(success_cnt, total_cnt))
print("===================================")

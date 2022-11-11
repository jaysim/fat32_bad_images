#!/usr/bin/python
#-*- coding: utf-8 -*-

import struct
import sys
import os
import argparse as ap
import subprocess as sp
import hexdump

DEFINE_TEST = False

def getBytes(fd, pos, numBytes):
  os.lseek(fd, pos, os.SEEK_SET)
  byte = os.read(fd, numBytes)
  if (numBytes == 2):
    formatString = "H"
  elif (numBytes == 1):
    formatString = "B"
  elif (numBytes == 4):
    formatString = "i"
  else:
    raise Exception("Not implemented")
  return struct.unpack("<"+formatString, byte)[0]

def getString(fd, pos, numBytes):
  os.lseek(fd, pos, os.SEEK_SET)
  raw = os.read(fd, numBytes)
  return struct.unpack(str(numBytes)+"s", raw)[0]

def bytesPerSector(fd):
  return getBytes(fd,11,2)

def sectorsPerCluster(fd):
  return getBytes(fd,13,1)

def reservedSectorCount(fd):
  return getBytes(fd,14,2)

def numberOfFATs(fd):
  return getBytes(fd,16,1)

def FATStart(fd, numFat):
  return reservedSectorCount(fd) * bytesPerSector(fd)

def FATSize(fd):
  return getBytes(fd, 36, 4)

def rootStart(fd):
  return FATStart(fd,1) + (FATSize(fd) * numberOfFATs(fd) * bytesPerSector(fd))

def fsIdentityString(fd):
  return getString(fd,82,8)

def getDirTableEntry(fd):
  offset = rootStart(fd)
  while True:
    os.lseek(fd, offset + 0x0B, os.SEEK_SET)
    isLFN = (struct.unpack("b", os.read(fd, 1)[0] == 0x0F))
    if isLFN:
      fileName = "SKIPPED"
    else:
      os.lseek(fd, offset, os.SEEK_SET)
      fileName = struct.unpack("8s", os.read(fd, 8)[0])
    offset += 32
    yield (isLFN, fileName)

def ppNum(num):
  return "%s (%s)" % (hex(num), num)

def parse_argument():
    global args
    global parser

    desc = 'FAT32 Binary read/write script'
    wclus_help = 'write \'input file\'(binary) to cluster'
    rclus_help = 'read cluster'
    rfat_help = 'read FAT area that include <cluster> and write it to \'out-file\''
    wfat_help = 'read \'input file\'(binary) and write it to FAT area that include <cluster>'
    rsec_help = 'read sector and write it to \'out-file\'. sector 0 represents boot sector'
    wsec_help = 'read \'in-file\' and write it to specific sector, sector 0 represents boot sector'
    output_metavar = ("cluster", "out-file")
    input_metavar = ("cluster", "in-file")
    outsec_metavar = ("sector", "out-file")
    insec_metavar = ("sector", "in-file")

    parser=ap.ArgumentParser(description=desc)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-rb", nargs='+', metavar=outsec_metavar, help=rsec_help, dest="rsec")
    group.add_argument("-rc", metavar="cluster", help=rclus_help, dest="rclus")
    group.add_argument("-rf", nargs='+', metavar=output_metavar, help=rfat_help, dest="rfat")

    group.add_argument("-wb", nargs=2, metavar=insec_metavar, help=wsec_help, dest="wsec")
    group.add_argument("-wc", nargs=2, metavar=input_metavar, help=wclus_help, dest="wclus")
    group.add_argument("-wf", nargs=2, metavar=input_metavar, help=wfat_help, dest="wfat")
    parser.add_argument("device", help='fat32 volume, or dump file')
    try:
        args = parser.parse_args()
    except ap.ArgumentError as e:
        print(e.message + '\n' + e.argument)
        parser.print_help()
        exit(-1)

    return args

if __name__ != "__main__":
    print('This script should be run by itself, not imported from other module')
    exit(1)

args=''
option=os.O_RDONLY
data_path = None

parse_argument()
if (args.wclus or args.wfat or args.wsec):
    option=os.O_RDWR

fd = os.open(args.device, option)

sector_size = bytesPerSector(fd)
sec_per_clus = sectorsPerCluster(fd)
clus_size = sector_size * sec_per_clus
num_reserved_sector = reservedSectorCount(fd)
num_FATs = numberOfFATs(fd)
FAT1_start_addr = FATStart(fd, 1)
FAT_size = FATSize(fd)
data_start_addr = rootStart(fd)

# num. of fat entry in a cluster
fe_per_clus = int(clus_size / 4)

if (len(sys.argv) <= 2):
    parser.print_usage()
    print()
    print("You should specify one command option")
    exit(-1)

print("Bytes per sector:",        ppNum(sector_size))
print("Sectors per cluster:",     ppNum(sec_per_clus))
print("Reserved sector count:",   ppNum(num_reserved_sector))
print("Number of FATs:",          ppNum(num_FATs))
print("Start of FAT1:",           ppNum(FAT1_start_addr))
print("Size of FAT:",             ppNum(FAT_size))
print("Start of root directory:", ppNum(data_start_addr))
print("Identity string:",         fsIdentityString(fd))
print("Files & directories:")
print("arguement count",  type(args))
print("=============================================================")
print()

if (args.wclus):
    # handle for -w option
    wclus = int(args.wclus[0])
    data_path = args.wclus[1]

    if (wclus < 2):
        wclus = 2

    if not os.path.exists(data_path):
        print("{} does not exist".format(data_path))
        exit(-1)

    write_addr = (wclus - 2) * clus_size + data_start_addr

    print("Source Binary File:{}".format(data_path))
    print("Cluster #({}) address: {} ({})".format(wclus, hex(write_addr), write_addr))

    src_fd = os.open(data_path, os.O_RDONLY)
    src_buffer = os.read(src_fd, clus_size)

    os.lseek(fd, write_addr, os.SEEK_SET)
    if (DEFINE_TEST != True):
        os.write(fd, src_buffer)
        print("WRITE!!!!!!")
        pass
    else:
        # for test
        test_fd = os.open("./test_file.bin", os.O_RDWR|os.O_CREAT|os.O_TRUNC)
        os.write(test_fd, src_buffer)
        os.close(test_fd)
        ###

    print(hexdump.hexdump(src_buffer))

    os.close(src_fd)

elif (args.rclus):
    # handle for -r option
    rclus = int(args.rclus)
    if (rclus < 2):
        rclus = 2

    print("read {} cluster".format(rclus))
    read_addr = (rclus - 2) * clus_size + data_start_addr
    os.lseek(fd, read_addr, os.SEEK_SET)
    print("data start address: {} ({})".format(hex(data_start_addr), data_start_addr))
    print("cluster {} address: {} ({})".format(rclus, hex(read_addr), read_addr))
    src_buffer = os.read(fd, clus_size)
    print(hexdump.hexdump(src_buffer))

elif (args.rfat):
    # handle for -rf option
    if (len(args.rfat) > 2):
        print("-rf option has maximum 2 parameter only. separate positional paramter with '--' ")
        exit(-1)
    clus = int(args.rfat[0])
    if (len(args.rfat) > 1):
        data_path = args.rfat[1]

    if (clus < 2):
        clus = 2

    fe_block, fe_offset = divmod(clus, fe_per_clus)

    print("read fat sector include {} cluster".format(clus))
    print("  fat entry block(fe_block) : {}".format(fe_block))
    print("  fat entry offset(fe_offset) : {} ({})".format(hex(fe_offset * 4), fe_offset))

#    read_addr = fe_block * sector_size + FAT1_start_addr
    read_addr = fe_block * clus_size + FAT1_start_addr
    os.lseek(fd, read_addr, os.SEEK_SET)
#    src_buffer = os.read(fd, sector_size)
    src_buffer = os.read(fd, clus_size)

    print(hexdump.hexdump(src_buffer))

    if (data_path != None):
        dest_fd = os.open(data_path, os.O_RDWR|os.O_CREAT|os.O_TRUNC)
        os.write(dest_fd, src_buffer)
        os.close(dest_fd)

elif (args.wfat):
    # handle for -wf option
    clus = int(args.wfat[0])
    src_path = args.wfat[1]

    if (clus < 2):
        clus = 2

    fe_block, fe_offset = divmod(clus, fe_per_clus)

    if not os.path.exists(src_path):
        print("{} does not exist".format(src_path))
        exit(-1)

#    write_addr = fe_block * sector_size + FAT1_start_addr
    write_addr = fe_block * clus_size + FAT1_start_addr

    print("Source Binary File:{}".format(src_path))
    print("  fat entry block(fe_block) : {}".format(fe_block))
    print("  fat entry offset(fe_offset) : {} ({})".format(hex(fe_offset * 4), fe_offset))

    src_fd = os.open(src_path, os.O_RDONLY)
#    src_buffer = os.read(src_fd, sector_size)
    src_buffer = os.read(src_fd, clus_size)

    os.lseek(fd, write_addr, os.SEEK_SET)

    if (DEFINE_TEST != True):
        os.write(fd, src_buffer)
        print("WRITE!!!!!!")
        pass
    else:
        desc_path = './write_test.bin'
        print("Destination Binary File:{}".format(desc_path))
        # for test
        test_fd = os.open(desc_path, os.O_RDWR|os.O_CREAT|os.O_TRUNC)
        os.write(test_fd, src_buffer)
        os.close(test_fd)
        ###

    print(hexdump.hexdump(src_buffer))

    os.close(src_fd)
elif (args.rsec):

    if (len(args.rsec) > 2):
        print("-rb option has maximum 2 parameter only. use '--' to seprate position paramter")
        exit(-1)

    sector = int(args.rsec[0])
    if (len(args.rsec) > 1):
        data_path = args.rsec[1]

    if (sector == 0):
        # read boot sector
        print("read Boot Sector")
        os.lseek(fd, 0, os.SEEK_SET)
        src_buffer = os.read(fd, sector_size)
        pass
    elif (sector == 1):
        # fsinfo sector
        print("read FSinfo Sector")
        fsinfo_sector = getBytes(fd, 48, 2)
        fsinfo_addr = fsinfo_sector * sector_size
        os.lseek(fd, fsinfo_addr, os.SEEK_SET)
        src_buffer = os.read(fd, sector_size)
    else:
        os.lseek(fd, sector * sector_size, os.SEEK_SET)
        src_buffer = os.read(fd, sector_size)

    print(hexdump.hexdump(src_buffer))
    if (data_path != None):
        dest_fd = os.open(data_path, os.O_RDWR|os.O_CREAT|os.O_TRUNC)
        os.write(dest_fd, src_buffer)
        os.close(dest_fd)

elif (args.wsec):
    sector = int(args.wsec[0])
    src_path = args.wsec[1]

    if not os.path.exists(src_path):
        print("{} does not exist".format(src_path))
        exit(-1)

    src_fd = os.open(src_path, os.O_RDONLY)
    src_buffer = os.read(src_fd, sector_size)

    if (sector == 0):
        # boot sector
        os.lseek(fd, 0, os.SEEK_SET)
    elif (sector == 1):
        # fsinfo sector
        fsinfo_sector = getBytes(fd, 48, 2)
        fsinfo_addr = fsinfo_sector * sector_size
        os.lseek(fd, fsinfo_addr, os.SEEK_SET)
    else:
        os.lseek(fd, sector * sector_size, os.SEEK_SET)

    if (DEFINE_TEST != True):
        os.write(fd, src_buffer)
        print("WRITE!!!!!!")
        pass
    else:
        desc_path = './write_test.bin'
        print("Destination Binary File:{}".format(desc_path))
        # for test
        test_fd = os.open(desc_path, os.O_RDWR|os.O_CREAT|os.O_TRUNC)
        os.write(test_fd, src_buffer)
        os.close(test_fd)
        ###

    print(hexdump.hexdump(src_buffer))

    os.close(src_fd)


os.close(fd)

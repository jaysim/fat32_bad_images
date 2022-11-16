# Ovierview
fat32\_bad\_images repository contains test script for various corrupted
FAT32 images. You can test/verify repairing tools for FAT32 like fatprogs.

But, because of size limitation of github, can't share corrupted images.
Just share corrupted raw hexa data only. And will be looking for method
to share corrupted images.

Since the test scripts were written for fixed corrupted images, if you are
going to test your corrupted images, then you should modify images' name
in script. (list variable bad\_images)


## details for corrupted images
category of corrupted images are like below.

<code>
- bad_bootXX : boot sector corrupted images
- bad_ccXX : cluster chain corrupted images
- bad_deXX : directory entry(DE) corrupted images
- bad_dirtyXX : test image for filesystem dirty flag (boot sector and FAT #1)
- bad_entXX/bad_lfnXX : ".", ".." entry and lfn(long filename) corrupted images
- bad_volXX : volume label corrupted or missing images
</code>

## test script
Scripts are consist of creating and testing corrupted image and testing.
In this documents, will almost describe about testing scripts.

Scripts for testing is like below.
- test\_fsck\_verficiation.py
- test\_dump\_verification.py

### Script: test\_fsck\_verification.py
#### Description
Performs fsck test on corrupted images.(Images should be located in \<path3\>)
First, the script use fsck tools specified in \<path1\> arguement to repair
each corrupted image. After recovery, script also try to check again
for recoverd images using fsck tools specified in \<path2\> arguement.
That is verification step for \<path1\> fsck tools.

After verification step done, result file is created in *\<path3\>/result_output*.
You may check file, "\[\<tool\_name\>\]\_fsck\_verified\_result.out" in \<path3\>.
Verification is OK, if there are no problem detected in above file.

- fsck__\<path1 tool name\>__\<time\>.result.out : result file of performing \<path1\> fsck.
- fsck__\<path2 tool name\>__\<time\>.verified\_result.out : result file of performing \<path2\> fsck.

#### Script Help
<pre><code>
usage: test_fsck_verification.py [-h] "fsck:check" "fsck2:verify" "testdir"

FAT32 bad image checking & verifying script

positional arguments:
  "fsck:check"    full path fsck for checking image, usually fatprogs fsck(dosfsck)
  "fsck2:verify"  full path fsck for verifying image, usually use dosfstools fsck(fsck.fat)
  "testdir"       corrupted images path for testing

options:
  -h, --help      show this help message and exit
</code></pre>

#### Example
<pre><code>
python ./script/test_fsck_verification.py "path-to"/fatprogs/src/dosfsck /sbin/fsck.fat testdata
</code></pre>

### Script; test\_dump\_verficiation.py
#### Description
Performs dump test on corrupted images. First, dump from corrupted images using
dosfsdump of \<path2\>. Dumped image is written to 'dump.file' by default.

After dump, the script performs fsck tools on \<path1\> to check dumped file.
After script runs, "dump__\<path1 tool name\>__\<time\>.result.out" is created
in *\<path3\>/result_output* as a result file.

By comparing generated file(above) with fsck__\<path1 tool name\>__\<time\>.result.out which is result file of test\_fsck\_verification.py, it can be verified dump
tool works.

#### Script Help
<pre><code>
usage: test_dump_verification.py [-h] [-v] "fsck" "dump" ["target_dir"]

FAT32 bad image dump test script

positional arguments:
  "fsck"        fsck full path for verifying dumped image, usually fatprogs fsck(dosfsck)
  "dump"        dump full path for dumping image, usually fatprogs domp(dosfsdump)
  "target_dir"  (optional) dump test directory: default "./testdir/"

options:
  -h, --help    show this help message and exit
  -v            add verification pass option of dosfsck
</code></pre>

#### Example
<pre><code>
python ./script/test_dump_verficiation.py "path-to"/fatprogs/src/dosfsck "path-to"/fatprogs/src/dosfsdump testdata
</code></pre>
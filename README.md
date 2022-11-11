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

- bad\_bootXX : boot sector corrupted images
- bad\_ccXX : cluster chain corrupted images
- bad\_deXX : directory entry(DE) corrupted images
- bad\_dirtyXX : test image for filesystem dirty flag (boot sector and FAT #1)
- bad\_entXX/bad\_lfnXX : ".", ".." entry and lfn(long filename) corrupted images
- bad\_volXX : volume label corrupted or missing images

## test script
Scripts are consist of creating and testing corrupted image and testing.
In this documents, will almost describe about testing scripts.

Scripts for testing is like below.
- test\_fsck\_verficiation.py
- test\_dump\_verification.py

### Script: test\_fsck\_verification.py
#### Description
Performs fsck test on corrupted images.(Images should be located in <path3>)
First, the script use fsck tools specified in <path1> arguement to repair
each corrupted image. After recovery, script also try to check again
for recoverd images using fsck tools specified in <path2> arguement.
That is verification step for <path1> fsck tools.

After verification step done, result file is created in <path3>.
You may check file, "\[\<tool\_name\>\]\_fsck\_verified\_result.out" in <path3>.
Verification is OK, if there are no problem detected in above file.

- '\[\<tool\_name\>\]\_fsck\_result.out : result file of performing <path1> fsck.
- '\[\<tool\_name\>\]\_fsck\_verified\_result.out : result file of performing <path2> fsck.

#### Script Help
<pre><code>
usage: test_fsck_verification.py [-h] path1 path2 path3

FAT32 bad image test & verification script

positional arguments:
  path1     full path of testing fsck, generally fatprogs fsck(dosfsck)
  path2     full path of verifying fsck, generally use dosfstools fsck(fsck.fat)
  path3     corrupted images path for testing

optional arguments:
  -h, --help  show this help message and exit
</code></pre>

#### Example
<pre><code>
python ./script/test_fsck_verification.py <path-to>/fatprogs/src/dosfsck /sbin/fsck.fat testdata
</code></pre>

### Script; test\_dump\_verficiation.py
#### Description
Performs dump test on corrupted images. First, dump from corrupted images using
dosfsdump of \<path2\>. Dumped image is written to 'dump.file' by default.
If you use '-o \<output file\>', then 'output file' is written instead of
'dump.file'

After dump, the script performs fsck tools on \<path1\> to check dumped file.
After script runs, "\[\<tool\_name\>\]\_fsck\_after\_dump.out" is created
in \<path3\> as a result file.

By comparing generated file(above) with \<path1\>\_fsck\_result.out
which is result file of test\_fsck\_verification.py, it can be verified dump
tool works.

#### Script Help
<pre><code>
usage: test_dump_verification.py [-h] [-v] path1 path2 path3

FAT32 bad image dump test script

positional arguments:
  path1               full path for verifying dump using fsck, generally fatprogs fsck(dosfsck)
  path2               full path for testing dump, generally fatprogs domp(dosfsdump)
  path3               corrupted image(dump target) path for testing

optional arguments:
  -h, --help  show this help message and exit
  -v          add verification pass option of dosfsck
</code></pre>

#### Example
<pre><code>
python ./script/test_dump_verficiation.py <path-to>/fatprogs/src/dosfsck <path-to>/fatprogs/src/dosfsdump testdata
</code></pre>

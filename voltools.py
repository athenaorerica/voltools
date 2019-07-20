# voltools.py
# version 0.25 (because it's a quarter finished lmao)
#
# this file is part of voltools
#
# packer/extractor for vol files
#
# pre-production software
# may be licensed differently after completion
#
# written by and copyright © 2019 Erica Garcia [athenaorerica] <me@athenas.space>
# all rights reserved, distribution is prohibited.
#
# this code says: trans rights
#
# don't like that? suck it up, or write your own code ^-^

import os, sys

def unpack(filename):
    # open the file
    f = open(filename, "rb")

    # load the header into memory
    hdr = f.read(4)

    # check header
    if hdr.decode() == "PVOL":
        dumpVOL(f) # VOL dumping method
    elif hdr.decode() == " VOL":
        dumpVOL2(f) # VOL2 dumping method
    else: # what did you give me?!
        print("Invalid input file!")
        sys.exit(1)

def __parseDetailDirectory(detailDirEntries, fileDirContents, f):
    files = {}
    # parse detail directory entries
    for entry in detailDirEntries:
        # make sure it's a valid entry (4-null header)
        nulls = entry[:4]
        assert nulls == b'\x00\x00\x00\x00'

        # get filename offset from the entry
        fnOffset = int.from_bytes(entry[4:8], "little")

        # use a list to build filename
        fn = []

        # add characters to fn list until we find a null
        for i in fileDirContents[fnOffset::]:
            if i == 0: # if the character is null
                fn = "".join(fn) # turn list into string
                break
            fn.append(chr(i)) # add current character to fn list

        # get the offset at which file data is stored
        dataOffset = int.from_bytes(entry[8:12], "little")

        # get file length
        fLen = int.from_bytes(entry[12:15], "little")

        # check for the last null
        assert entry[16] == 0

        # seek to the file data entry
        f.seek(dataOffset)

        # check file header
        fHdr = f.read(4)
        assert fHdr.decode() == "VBLK"

        # we're already here, the file length's also in the header so might as well sanity check it
        assert fLen == int.from_bytes(f.read(3), "little")

        # seek past the unknown data
        f.seek(1, 1)

        # get file data, build entry and add to dict
        files.update({fn: f.read(fLen)})
    return files

def __dumpFiles(fileDict, fileName):
    # make directory for extracted files
    os.makedirs(fileName+"-ext", exist_ok=True)

    # dump files
    for fn, d in fileDict.items():
        nf = open(os.path.join(fileName+"-ext", fn), "wb") # open file for binary writing
        nf.write(d) # dump the entire value of the entry


def dumpVOL(f):
    # get 4-byte file directory offset
    fDirOffset = f.read(4)

    # seek to the file directory
    fDir = f.seek(int.from_bytes(fDirOffset, "little"))

    # read 4 bytes to get file directory header and check it
    fDirHdr = f.read(4)
    assert fDirHdr.decode() == "vols"

    # read 4 bytes to get the length of the file directory, and make it an int
    fDirLen = int.from_bytes(f.read(4), "little")

    # load the file directory's contents into memory
    fDirContent = f.read(fDirLen)

    # read 4 bytes to get detail directory header and check it
    dDirHdr = f.read(4)
    assert dDirHdr.decode() == "voli"

    # read 4 bytes to get detail directory length, and make it an int
    dDirLen = int.from_bytes(f.read(4), "little")

    # load the info directory's content into memory
    dDirContent = f.read(dDirLen)

    # make a list of info entries (17 bytes long) by dividing the content of the directory
    dDirEntries = [dDirContent[x:x+17] for x in range(0,len(dDirContent), 17)]

    # parse detail directory entries
    files = __parseDetailDirectory(dDirEntries,fDirContent,f)

    # dump files
    __dumpFiles(files, f.name)

def dumpVOL2(f):
    # get 4-byte empty directory offset
    eDirOffset = f.read(4)

    # seek to the empty directory
    eDir = f.seek(int.from_bytes(eDirOffset, "little"))

    # seek past the 16 bytes of empty directory
    f.seek(16, 1)

    # read file directory header and check
    assert f.read(4).decode() == "vols"

    # read file directory length and make it into an int
    fDirLen = int.from_bytes(f.read(4), "little")

    # read the contents of the file directory
    fDirContent = f.read(fDirLen)

    # read details directory header and check
    assert f.read(4).decode() == "voli"

    # read details directory length and make it into an int
    dDirLen = int.from_bytes(f.read(4), "little")

    # read details directory contents
    dDirContent = f.read(dDirLen)

    # split the details directory into 17 byte long entries
    dDirEntries = [dDirContent[x:x+17] for x in range(0,len(dDirContent), 17)]

    # parse detail directory entries
    files = __parseDetailDirectory(dDirEntries,fDirContent,f)

    # dump files
    __dumpFiles(files, f.name)


unpack(sys.argv[1])

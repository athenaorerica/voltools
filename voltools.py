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

    # read 4 bytes to get info directory header and check it
    iDirHdr = f.read(4)
    assert iDirHdr.decode() == "voli"

    # read 4 bytes to get info directory length, and make it an int
    iDirLen = int.from_bytes(f.read(4), "little")

    # load the info directory's content into memory
    iDirContent = f.read(iDirLen)

    # make a list of info entries (17 bytes long) by dividing the content of the directory
    iDirEntries = [iDirContent[x:x+17] for x in range(0,len(iDirContent), 17)]

    # declare dict for files
    files = {}

    # parse info directory entries
    for entry in iDirEntries:
        # make sure it's a valid entry (4-null header)
        nulls = entry[:4]
        assert nulls == b'\x00\x00\x00\x00'

        # get filename index from the entry
        fnIndex = int.from_bytes(entry[4:8], "little")

        # use a list to build filename
        fn = []

        # add characters to fn list until we find a null
        for i in fDirContent[fnIndex::]:
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

    # make directory for extracted files
    os.makedirs(f.name+"-ext", exist_ok=True)

    # dump files
    for fn, d in files.items():
        nf = open(os.path.join(f.name+"-ext", fn), "wb") # open file for binary writing
        nf.write(d) # dump the entire value of the entry

def dumpVOL2(f):
    return NotImplemented

unpack(sys.argv[1])

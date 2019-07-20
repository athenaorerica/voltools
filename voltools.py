# voltools.py
# this file is part of vol-expacker
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
    fdiroffset = f.read(4)

    # seek to the file directory
    fdir = f.seek(int.from_bytes(fdiroffset, "little"))

    # read 4 bytes to get file directory header and check it
    fdirhdr = f.read(4)
    assert fdirhdr.decode() == "vols"

    # read 4 bytes to get the length of the file directory, and make it an int
    fdirlen = int.from_bytes(f.read(4), "little")

    # load the file directory's contents into memory
    fdircontent = f.read(fdirlen)

    # read 4 bytes to get info directory header and check it
    idirhdr = f.read(4)
    assert idirhdr.decode() == "voli"

    # read 4 bytes to get info directory length, and make it an int
    idirlen = int.from_bytes(f.read(4), "little")

    # load the info directory's content into memory (to EOF)
    idircontent = f.read()

    # make a list of info entries (17 bytes long) by dividing the content of the directory
    idirentries = [idircontent[x:x+17] for x in range(0,len(idircontent), 17)]

    # declare dict for files
    files = {}

    # parse info directory entries
    for entry in idirentries:
        # make sure it's a valid entry (4-null header)
        nulls = entry[:4]
        assert nulls == b'\x00\x00\x00\x00'

        # get filename index from the entry
        fnindex = int.from_bytes(entry[4:8], "little")

        # use a list to build filename
        fn = []

        # add characters to fn list until we find a null
        for i in fdircontent[fnindex::]:
            if i == 0: # if the character is null
                fn = "".join(fn) # turn list into string
                break
            fn.append(chr(i)) # add current character to fn list

        # get the offset at which file data is stored
        dataoffset = int.from_bytes(entry[8:12], "little")

        # get file length
        flen = int.from_bytes(entry[12:15], "little")

        # check for the last null
        assert entry[16] == 0

        # seek to the file data entry
        f.seek(dataoffset)

        # check file header
        fhdr = f.read(4)
        assert fhdr.decode() == "VBLK"

        # we're already here, the file length's also in the header so might as well sanity check it
        assert flen == int.from_bytes(f.read(3), "little")

        # seek past the unknown data
        f.seek(1, 1)

        # get file data, build entry and add to dict
        files.update({fn: f.read(flen)})

    # make directory for extracted files
    os.makedirs(f.name+"-ext", exist_ok=True)

    # dump files
    for fn, d in files.items():
        nf = open(os.path.join(f.name+"-ext", fn), "wb") # open file for binary writing
        nf.write(d) # dump the entire value of the entry

def dumpVOL2(f):
    return NotImplemented

unpack(sys.argv[1])

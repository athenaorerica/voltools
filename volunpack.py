# volunpack.py
# version 0.75 (more than half finished now!)
#
# this file is part of voltools
#
# unpacker for vol files
#
# pre-production software
# may be licensed differently after completion
#
# written by and copyright © 2019 Erica Garcia [athenaorerica] <me@athenas.space>
# licensed under the MIT license [https://license.athenas.space/mit] | SPDX-License-Identifier: MIT
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
        dumpPVOL(f) # PVOL dumping method
    elif hdr.decode() == " VOL":
        dumpVOL2(f) # VOL2 dumping method
    elif hdr.decode() == "VOLN":
        dumpVOLN(f) # VOLN dumping method
    else: # what did you give me?!
        print("Invalid input file!")
        sys.exit(1)

def __parseDetailDirectory(detailDirEntries, fileDirContents, f):
    # just declaring some constants for readability
    COMPRESSION_NONE = 0
    COMPRESSION_LZH = 3

    # declare a dict to keep the files
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

        # get file length from details directory
        fLenFromDir = int.from_bytes(entry[12:15], "little")

        # check whether file is compressed or not
        compressionFlag = entry[16]

        # seek to the file data entry
        f.seek(dataOffset)

        # check file header
        fHdr = f.read(4)
        assert fHdr.decode() == "VBLK"

        # some vols are weird and have mismatched filesize in the directory and header, so storing both
        fLenFromHdr = int.from_bytes(f.read(3), "little")

        # seek past the unknown data
        f.seek(1, 1)

        # provisionally set length to what the file directory claims
        fLen = fLenFromDir

        # make a decision if filesizes are discrepant
        if fLenFromDir != fLenFromHdr:
            if compressionFlag == COMPRESSION_LZH: # if the file is LZH compressed
                fLen = fLenFromHdr if fLenFromHdr < fLenFromDir else fLenFromDir # go with the filesize specified in header if it's smaller, otherwise use directory's
        # (if the file is not LZH compressed, filesize still defaults to the directory's)

        # get file data and decompress if necessary
        fileData = __decompressFile(f.read(fLen), compressionFlag)

        # build file entry and add to dict
        files.update({fn: fileData})
    return files

def __decompressFile(fileData, compressionFlag):
    if compressionFlag == 0:
        return fileData
    elif compressionFlag == 3:
        return fileData # placeholder while I figure out what the hell this butchered form of LZH is

def __dumpFiles(fileDict, fileName):
    # dump files
    for fn, d in fileDict.items():
        path = os.path.join(fileName+"-ext", fn) # construct the target path
        os.makedirs(os.path.dirname(path), exist_ok=True) # make sure we actually have somewhere to put the file
        nf = open(path, "wb") # open file for binary writing
        nf.write(d) # dump the entire value of the entry

def dumpPVOL(f):
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
    dDirHdr = f.read(4).decode()
    assert dDirHdr in ["voli", '\x00vol']

    # sometimes PVOL has some weird padding between file and details directories, so skip a byte if there's a null
    if dDirHdr == '\x00vol':
        f.seek(1,1)

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
    dDirHdr = f.read(4).decode()
    assert dDirHdr in ["voli", '\x00vol']

    # sometimes VOL2 has some weird padding between file and details directories, so skip a byte if there's a null
    if dDirHdr == '\x00vol':
        f.seek(1,1)

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

def dumpVOLN(f):
    raise NotImplementedError

unpack(sys.argv[1])

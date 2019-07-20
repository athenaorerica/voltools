# volpack.py
# version 0.75 (more than half finished now!)
#
# this file is part of voltools
#
# packer for vol files
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

def pack(dirname):
    open(dirname+".vol", "wb") # create file
    f = open(dirname+".vol", 'r+b') # open file for writing in bin mode
    packVOL(dirname, f)

def packVOL(src, volFile):
    # declare a list to hold filenames
    filesToPack = []
    for (dp, dn, fn) in os.walk(src): # walk the current directory
        filesToPack.extend(fn) # add filenames to the list
        src = dp # for good measure, make the source the dirpath
        break # stop after the first layer
    volFile.write(b'PVOL\xde\xad\xbe\xef') # write pvol header and file directory pointer placeholder
    fDirPointer = None # declare pointer
    fileInfo = {} # create a dict to hold some info on files we'll need later
    for i in filesToPack: # for every file that's going in the vol
        filePath = os.path.join(src, i) # get its canonical path
        fileSize = os.path.getsize(filePath) # get its size
        compressionFlag = b'\x03' if os.path.splitext(filePath)[1] == ".lzh" else b'\x00' # if it ends with .lzh set the proper compression flag
        fileInfo.update({i:[volFile.tell(), fileSize, compressionFlag]}) # add file pointer, file size, and compression flag to the file info dict
        volFile.write(b'VBLK') # write file header
        volFile.write(fileSize.to_bytes(3, "little")) # write file size
        volFile.write(b'\x80') # write the weird character
        volFile.write(open(filePath, "rb").read()) # write file data
    fDirPointer = volFile.tell() # save the file directory pointer for later
    volFile.seek(4) # go back to the vol header
    volFile.write(fDirPointer.to_bytes(4, "little")) # write the file directory pointer
    volFile.seek(fDirPointer) # return to the file directory pointer
    volFile.write(b'vols') # write file directory header
    fDirContentOffsets = {} # make a dict to keep track of the filename offsets
    fileDirContents = b'' # declare what we're gonna be writing
    for x in filesToPack: # for every file that's going in the vol
        if fileInfo.get(i)[2] != b'\x00':
            i = i[:-4] # truncate the .lzh if it's a compressed file
        fDirContentOffsets.update({x:len(fileDirContents)}) # keep track of the current filename's offset
        fileDirContents += x.encode() # add the filename to the write buffer
        fileDirContents += b'\x00' # null terminate
    volFile.write(len(fileDirContents).to_bytes(4, "little")) # write the length of the file directory's contents
    volFile.write(fileDirContents) # write the file directory's contents
    volFile.write(b'voli') # write the detail directory header
    detailDirContents = [] # using a list this time to buffer the content
    for k, v in fileInfo.items(): # for every file that has information
        detailDirEntry = (b'\x00' * 4) + fDirContentOffsets.get(k).to_bytes(4, "little") + v[0].to_bytes(4, "little") + v[1].to_bytes(4, "little") + v[2] # construct an entry: 4 nulls, filename offset, file offset, file size, and compression flag
        detailDirContents.append(detailDirEntry) # add the entry to the buffer
    detailDirContents = b''.join(detailDirContents) # make the buffer a bytes object
    volFile.write(len(detailDirContents).to_bytes(4, "little")) # write the length of the detail directory's contents
    volFile.write(detailDirContents) # write the content
    volFile.close() # we're done!

pack(sys.argv[1])

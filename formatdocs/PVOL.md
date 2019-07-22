# PVOL Format Spec

Endianness: Little

Used in:
 - Star Siege (Beta)

```
<File>
    char   {4} = "PVOL" // Header
    uint32 {4}          // Absolute pointer to FileNameDirectory

    <DataBlock>
    	<DataBlock_entry> // one per file
            char   {4} = "VBLK" // Header
            uint24 {3}          // size of File Data
            byte   {1} = 0x80   // Unknown
            byte   {x}          // File Data
        </DataBlock_entry>
    </DataBlock>

    <FileNameDirectory>
        char   {4} = "vols" // Header
        uint32 {4}          // size of FileNameDirectory_contents
        <FileNameDirectory_contents>
        	<FileNameDirectory_entry> // one per file
        		char   {x}        // Filename
        		byte   {1} = null // Filename Terminator
        	</FileNameDirectory_entry>
        </FileNameDirectory_contents>
    </FileNameDirectory>

    byte   {0|1} = null // Padding, may or may not be there, can't find a reason for its absence/inclusion

    <DetailsDirectory>
     	char   {4} = "voli" // Header
        uint32 {4}          // size of DetailsDirectory_contents
        <DetailsDirectory_contents>
            <DetailsDirectory_entry> // one per file
            uint32 {4} = null // Padding/Header
            uint32 {4}        // Relative pointer to filename (FileNameDirectory_contents + x)
            uint32 {4}        // Absolute pointer to file's DataBlock_entry
            uint32 {4}        // Size of file
            byte   {1} = [0x00 | 0x03] // Compression Flag - 0x00 if uncompressed, 0x03 if LZH compressed
            </DetailsDirectory_entry>
        </DetailsDirectory_contents>
    </DetailsDirectory>
</File>
```

## Lempel-Ziv/Huffman Compression

Tables to en/decode the upper 6 bits of the slider dictionary's pointer

Encoding tables
```
// Length table (64-byte)
    03 04 04 04 05 05 05 05
    05 05 05 05 06 06 06 06
    06 06 06 06 06 06 06 06
    07 07 07 07 07 07 07 07
    07 07 07 07 07 07 07 07
    07 07 07 07 07 07 07 07
    08 08 08 08 08 08 08 08
    08 08 08 08 08 08 08 08

// Code table (64-byte)
    00 20 30 40 50 58 60 68
    70 78 80 88 90 94 98 9C
    A0 A4 A8 AC B0 B4 B8 BC
    C0 C2 C4 C6 C8 CA CC CE
    D0 D2 D4 D6 D8 DA DC DE
    E0 E2 E4 E6 E8 EA EC EE
    F0 F1 F2 F3 F4 F5 F6 F7
    F8 F9 FA FB FC FD FE FF

```

Decoding tables
```
// Length table (256-byte)
    03 03 03 03 03 03 03 03
    03 03 03 03 03 03 03 03
    03 03 03 03 03 03 03 03
    03 03 03 03 03 03 03 03
    04 04 04 04 04 04 04 04
    04 04 04 04 04 04 04 04
    04 04 04 04 04 04 04 04
    04 04 04 04 04 04 04 04
    04 04 04 04 04 04 04 04
    04 04 04 04 04 04 04 04
    05 05 05 05 05 05 05 05
    05 05 05 05 05 05 05 05
    05 05 05 05 05 05 05 05
    05 05 05 05 05 05 05 05
    05 05 05 05 05 05 05 05
    05 05 05 05 05 05 05 05
    05 05 05 05 05 05 05 05
    05 05 05 05 05 05 05 05
    06 06 06 06 06 06 06 06
    06 06 06 06 06 06 06 06
    06 06 06 06 06 06 06 06
    06 06 06 06 06 06 06 06
    06 06 06 06 06 06 06 06
    06 06 06 06 06 06 06 06
    07 07 07 07 07 07 07 07
    07 07 07 07 07 07 07 07
    07 07 07 07 07 07 07 07
    07 07 07 07 07 07 07 07
    07 07 07 07 07 07 07 07
    07 07 07 07 07 07 07 07
    08 08 08 08 08 08 08 08
    08 08 08 08 08 08 08 08

// Code table (256-byte)
    00 00 00 00 00 00 00 00
    00 00 00 00 00 00 00 00
    00 00 00 00 00 00 00 00
    00 00 00 00 00 00 00 00
    01 01 01 01 01 01 01 01
    01 01 01 01 01 01 01 01
    02 02 02 02 02 02 02 02
    02 02 02 02 02 02 02 02
    03 03 03 03 03 03 03 03
    03 03 03 03 03 03 03 03
    04 04 04 04 04 04 04 04
    05 05 05 05 05 05 05 05
    06 06 06 06 06 06 06 06
    07 07 07 07 07 07 07 07
    08 08 08 08 08 08 08 08
    09 09 09 09 09 09 09 09
    0A 0A 0A 0A 0A 0A 0A 0A
    0B 0B 0B 0B 0B 0B 0B 0B
    0C 0C 0C 0C 0D 0D 0D 0D
    0E 0E 0E 0E 0F 0F 0F 0F
    10 10 10 10 11 11 11 11
    12 12 12 12 13 13 13 13
    14 14 14 14 15 15 15 15
    16 16 16 16 17 17 17 17
    18 18 19 19 1A 1A 1B 1B
    1C 1C 1D 1D 1E 1E 1F 1F
    20 20 21 21 22 22 23 23
    24 24 25 25 26 26 27 27
    28 28 29 29 2A 2A 2B 2B
    2C 2C 2D 2D 2E 2E 2F 2F
    30 31 32 33 34 35 36 37
    38 39 3A 3B 3C 3D 3E 3F
```

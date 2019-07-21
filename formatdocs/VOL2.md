# VOL2 Format Spec

Endianness: Little

```
<File>
    char   {4} = " VOL" // Header
    uint32 {4}			// Absolute pointer to EmptyDirectory

    <DataBlock>
    	<DataBlock_entry> // one per file
            char   {4} = "VBLK" // Header
            uint24 {3}          // size of File Data
            byte   {1} = 0x80   // Unknown
            byte   {x}          // File Data
        </DataBlock_entry>
    </DataBlock>

    <EmptyDirectory>
        char   {4} = "vols" // File Name Directory header
        char   {4} = null   // Empty Data
        char   {4} = "voli" // Details Directory header
        char   {4} = null   // Empty Data
    </EmptyDirectory>

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

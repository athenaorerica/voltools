# PVOL Format Spec

Endianness: Little

```
<File>
    char   {4} = "PVOL" // Header
    uint32 {4}			// Absolute pointer to FileNameDirectory

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

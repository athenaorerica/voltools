# VOLN Format Spec

Endianness: Little

Used in:
 - Earth Siege 1
 - Earth Siege 2

```
<File>
    char   {4} = "VOLN" // Header
    byte   {4} // Unknown, looks like a flag? Looks like every byte here is either 0x00 or 0x01, which seems wasteful.
    // undocumented past this point
</File>

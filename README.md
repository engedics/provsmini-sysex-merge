# SysEx preset combiner tool for the Behringer Pro VS Mini synthesizer
A tool for combining/merging SysEx **preset** files for bulk upload to the Behringer Pro VS Mini synthesizer.

## Why
The synthesizer only holds 32 presets. The new firmware comes with a new set of presets, the official website still contains the old one, and you can download many more.

Both changing the whole preset memory back-and-forth and uploading them one-by-one is time consuming, collect your favorite presets into a folder instead and upload the combined result easily.

## How
The first 8 bytes and last 2 bytes of each SysEx preset file are stripped away. The combined file is given a specific 8 byte preamble and 2 byte terminator at the ends of the concatenated preset contents.

To get an overview of the supported arguments:
```shell
python3 provsmini_preset_combiner.py --help
```

To run in its simplest form:
```shell
python3 provsmini_preset_combiner.py /path/to/your/collection
```

Then, upload the output file (by default: combined.syx in the source folder) with SynthTribe (Send -> All Presets).

## Disclaimer
I'm not responsible for any damage inflicted upon the synthesizer! I've tried a few combinations, and they all uploaded fine, although I couldn't figure out the role of the first byte of the terminator.

**UPDATE:** It's a checksum, added a [calculation](https://github.com/RomanKubiak/ctrlr/discussions/634#discussioncomment-9183868) for it.

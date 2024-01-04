# The Motion Analysis HTR to SMD Converter

<div align="center">
    <img src="https://github.com/hampta/htr2smd/blob/main/assets/screenshot.png?raw=true" alt="Screenshot" width="75%">
</div>

## Introduction
[HTR](https://research.cs.wisc.edu/graphics/Courses/cs-838-1999/Jeff/HTR.html) is a hierarchical representation of a motion sequence. 

It is a sequence of hierarchical transformations, each of which is a 3D translation followed by a 3D rotation. 

The HTR format is used by [Cryengine](https://www.cryengine.com/).

This tool converts HTR files to the [SMD](https://developer.valvesoftware.com/wiki/Studiomdl_Data) format used by the [Source Engine](https://developer.valvesoftware.com/wiki/Source_Engine).

## Installation
### From Source
```bash
git clone https://github.com/hampta/htr2smd
cd htr2smd
python htr2smd.py <input_htr_file>
python htr2smd.py <input_htr_folder>
python htr2smd.py <input_htr_file> <input_htr_file> <input_htr_file>
python htr2smd.py <input_htr_folder> <input_htr_folder> <input_htr_folder>
```
### From compiled binary
Download the executable from releases - [htr2smd](https://github.com/hampta/htr2smd/releases/latest)
```bash
./htr2smd.exe <input_htr_file>
./htr2smd.exe <input_htr_folder>
./htr2smd.exe <input_htr_file> <input_htr_file> <input_htr_file>
./htr2smd.exe <input_htr_folder> <input_htr_folder> <input_htr_folder>
```
Or just drag and drop the HTR file(s) or folder(s) onto the executable.

After conversion, the SMD files will be created in the *SMD* folder in the same directory as the HTR file(s) or folder(s).

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements
* [Valve Corporation](https://www.valvesoftware.com/) for the [Source Engine](https://developer.valvesoftware.com/wiki/Source_Engine)
* [Crytek](https://www.crytek.com/) for [Cryengine](https://www.cryengine.com/)
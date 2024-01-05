import os
import sys
import math
import glob
from pathlib import Path

from typing import List

OUTPUT_DIR = "./SMD"
EXECUTABLE_NAME = os.path.basename(sys.argv[0])
ASCII_ART = """\033[1;32m
██╗░░██╗████████╗██████╗░  ████████╗░█████╗░  ░██████╗███╗░░░███╗██████╗░
██║░░██║╚══██╔══╝██╔══██╗  ╚══██╔══╝██╔══██╗  ██╔════╝████╗░████║██╔══██╗
███████║░░░██║░░░██████╔╝  ░░░██║░░░██║░░██║  ╚█████╗░██╔████╔██║██║░░██║
██╔══██║░░░██║░░░██╔══██╗  ░░░██║░░░██║░░██║  ░╚═══██╗██║╚██╔╝██║██║░░██║
██║░░██║░░░██║░░░██║░░██║  ░░░██║░░░╚█████╔╝  ██████╔╝██║░╚═╝░██║██████╔╝
╚═╝░░╚═╝░░░╚═╝░░░╚═╝░░╚═╝  ░░░╚═╝░░░░╚════╝░  ╚═════╝░╚═╝░░░░░╚═╝╚═════╝░

░█████╗░░█████╗░███╗░░██╗██╗░░░██╗███████╗██████╗░████████╗███████╗██████╗░
██╔══██╗██╔══██╗████╗░██║██║░░░██║██╔════╝██╔══██╗╚══██╔══╝██╔════╝██╔══██╗
██║░░╚═╝██║░░██║██╔██╗██║╚██╗░██╔╝█████╗░░██████╔╝░░░██║░░░█████╗░░██████╔╝
██║░░██╗██║░░██║██║╚████║░╚████╔╝░██╔══╝░░██╔══██╗░░░██║░░░██╔══╝░░██╔══██╗
╚█████╔╝╚█████╔╝██║░╚███║░░╚██╔╝░░███████╗██║░░██║░░░██║░░░███████╗██║░░██║
░╚════╝░░╚════╝░╚═╝░░╚══╝░░░╚═╝░░░╚══════╝╚═╝░░╚═╝░░░╚═╝░░░╚══════╝╚═╝░░╚═╝
"""

if getattr(sys, 'frozen', False):
    # frozen
    __location__ = sys._MEIPASS
else:
    # unfrozen
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    EXECUTABLE_NAME = f"python {EXECUTABLE_NAME}"

# [SegmentNames&Hierarchy]
# #CHILD	PARENT
class HTRSegment:
    def __init__(self, name: str, parent: str, id: int = 0, parent_id: int = -1):
        self.name: str = name
        self.parent: str = parent
        self.id: int = id
        self.parent_id: int = parent_id


# [BasePosition]
# SegmentName Tx, Ty, Tz, Rx, Ry, Rz, BoneLength
class HTRBasePosition:
    def __init__(self, name: str, Tx: float, Ty: float, Tz: float, Rx: float, Ry: float, Rz: float, BoneLength: float):
        self.name: str = name
        self.Tx: float = Tx
        self.Ty: float = Ty
        self.Tz: float = Tz
        self.Rx: float = Rx
        self.Ry: float = Ry
        self.Rz: float = Rz
        self.bone_length: float = BoneLength


# Beginning of Data. Separated by tabs
# Fr	Tx	Ty	Tz	Rx	Ry	Rz	SF
class HTRFrame:
    def __init__(self, id: int, Tx: float, Ty: float, Tz: float, Rx: float, Ry: float, Rz: float, SF: float):
        self.id: int = id
        self.Tx: float = Tx
        self.Ty: float = Ty
        self.Tz: float = Tz
        self.Rx: float = Rx
        self.Ry: float = Ry
        self.Rz: float = Rz
        self.SF: float = SF


class HTRBoneFrames:
    def __init__(self, bone_name: str, bone_id: int, frames: List[HTRFrame]):
        self.bone_name: str = bone_name
        self.bone_id: int = bone_id
        self.list: List[HTRFrame] = frames


class HTRFile:
    # [Header]
    file_type: str
    data_type: str
    file_version: int
    num_segments: int
    num_frames: int
    data_frame_rate: int
    euler_rotation_order: str
    calibration_units: str
    rotation_units: str
    global_axis_of_gravity: str
    bone_length_axis: str
    scale_factor: float
    # [SegmentNames&Hierarchy]
    segments: List[HTRSegment]
    # [BasePosition]
    base_positions: List[HTRBasePosition]
    frames: List[HTRBoneFrames]
    
    def __init__(self, htr_file):
        self._htr_file = htr_file
        self.load_header()
        self.load_segments()
        self.load_base_positions()
        self.indexate_bones()
        self.load_frames()

    def load_header(self):
        header = self._htr_file.split("[Header]")[1].split("[SegmentNames&Hierarchy]")[0].split("\n")
        # remove lines that start with #
        header = [line for line in header if not line.startswith("#")]
        # remove trailing whitespace
        header = [line.rstrip() for line in header]
        # remove empty lines
        header: List[str] = [line for line in header if line]
        self.file_type: str = header[0].split()[1]
        self.data_type: str = header[1].split()[1]
        self.file_version: int = int(header[2].split()[1])
        self.num_segments: int = int(header[3].split()[1])
        self.num_frames: int = int(header[4].split()[1])
        self.data_frame_rate: int = int(header[5].split()[1])
        self.euler_rotation_order: str = header[6].split()[1]
        self.calibration_units: str = header[7].split()[1]
        self.rotation_units: str = header[8].split()[1]
        self.global_axis_of_gravity: str = header[9].split()[1]
        self.bone_length_axis: str = header[10].split()[1]
        self.scale_factor: str = float(header[11].split()[1])

    def load_segments(self):
        _segments: List[str] = self._htr_file.split("[SegmentNames&Hierarchy]")[-1].split("[BasePosition]")[0].split("\n")
        # remove lines that start with #
        _segments = [line for line in _segments if not line.startswith("#")]
        # remove trailing whitespace
        _segments = [line.rstrip() for line in _segments]
        # remove empty lines
        _segments = [line for line in _segments if line]
        self.segments: List[HTRSegment] = []
        for segment in _segments:
            segment_name, segment_parent = segment.split()
            # calculate bone id
            bone_id = self.segments.index(segment_name) if segment_name in self.segments else len(self.segments)
            # calculate bone parent id
            for i, bone in enumerate(self.segments):
                if bone.name == segment_parent:
                    bone_parent_id = i
                    break
            else:
                bone_parent_id = -1
            self.segments.append(HTRSegment(segment_name, segment_parent, bone_id, bone_parent_id))

    def load_base_positions(self):
        _base_positions: List[str] = self._htr_file.split("[BasePosition]")[-1].split("\n")
        # remove lines that start with #
        _base_positions = [line for line in _base_positions if not line.startswith("#")]
        # remove trailing whitespace
        _base_positions = [line.rstrip() for line in _base_positions]
        # remove empty lines
        _base_positions = [line for line in _base_positions if line]
        self.base_positions: List[HTRBasePosition] = []
        for base_position in _base_positions:
            if base_position.startswith("["):
                break
            name, Tx, Ty, Tz, Rx, Ry, Rz, bone_length = base_position.split()
            self.base_positions.append(HTRBasePosition(name, float(Tx), float(Ty),
                                                  float(Tz), float(Rx), float(Ry),
                                                  float(Rz), float(bone_length)))

    def load_frames(self):
        _frames: List[str] = self._htr_file.split("[BasePosition]")[-1].split(f"[{self.segments[0].name}]")[-1].split("\n")
        _frames[0] = f"[{self.segments[0].name}]"
        # remove lines that start with #
        _frames = [line for line in _frames if not line.startswith("#")]
        # remove trailing whitespace
        _frames = [line.rstrip() for line in _frames]
        # remove empty lines
        _frames = [line for line in _frames if line]
        self.frames: List[HTRBoneFrames] = []
        for frame in _frames:
            if frame.startswith("["):
                bone_name = frame.replace("[", "").replace("]", "")
                bone_id = self.bone_index[bone_name].id
                self.frames.append(HTRBoneFrames(bone_name, bone_id, []))
                continue
            frame_number, Tx, Ty, Tz, Rx, Ry, Rz, SF = frame.split()
            self.frames[-1].list.append(HTRFrame(int(frame_number), float(Tx), float(Ty),
                                            float(Tz), float(Rx), float(Ry), float(Rz), float(SF)))
    
    def indexate_bones(self):
        self.bone_index = {bone.name: bone for bone in self.segments}

    def to_radians(self, Rx: float, Ry: float, Rz: float):
        if self.rotation_units == "Degrees":
            Rx = math.radians(Rx)
            Ry = math.radians(Ry)
            Rz = math.radians(Rz)
        return Rx,Ry,Rz
    
    def apply_scale(self, bone_id: int, Tx: float, Ty: float, Tz: float):
        scale_factor = self.base_positions[bone_id].bone_length * self.scale_factor
        Tx /= scale_factor
        Ty /= scale_factor
        Tz /= scale_factor
        return Tx,Ty,Tz

    # IDK if this is correct
    def apply_base_position(self, bone_id: int, Tx: float, Ty: float, Tz: float, 
                            Rx: float, Ry: float, Rz: float):
        base_position = self.base_positions[bone_id]
        Tx -= base_position.Tx
        Ty -= base_position.Ty
        Tz -= base_position.Tz
        Rx -= base_position.Rx
        Ry -= base_position.Ry
        Rz -= base_position.Rz
        return Tx,Ty,Tz,Rx,Ry,Rz

def smd_bone_hierarchy(htr_file: HTRFile):
    # calculate bone hierarchy
    bone_hierarchy = []
    for i, segment in enumerate(htr_file.segments):
        if segment.parent == "GLOBAL":
            bone_hierarchy.append(f"{i} \"{segment.name}\" -1")
            continue
        # find parent index
        for j, bone in enumerate(htr_file.segments):
            if bone.name == segment.parent:
                bone_hierarchy.append(f"{i} \"{segment.name}\" {j}")
                break
    return bone_hierarchy

def fix_rotation(Tx: float, Ty: float, Rz: float):
    Rz += math.radians(180)
    return -Tx,-Ty,Rz

def convert(file_name="animation.htr"):
    with open(file_name, "r") as f:
        htr_file = f.read()

    # parse htr file
    htr = HTRFile(htr_file)

    # write smd header
    smd = "version 1\nnodes\n"

    # write bone hierarchy
    bone_hierarchy = smd_bone_hierarchy(htr)
    for bone in bone_hierarchy:
        smd += f"{bone}\n"
    smd += "end\n"

    # write skeleton animation
    smd += "skeleton\n"

    for i in range(htr.num_frames):
        smd += f"time {i}\n"
        for bone_frames in htr.frames:
            frame = bone_frames.list[i]
            Tx, Ty, Tz = htr.apply_scale(bone_frames.bone_id, frame.Tx, frame.Ty, frame.Tz)
            Rx, Ry, Rz = htr.to_radians(frame.Rx, frame.Ry, frame.Rz)
            # Tx, Ty, Tz, Rx, Ry, Rz = htr.apply_base_position(bone_frames.bone_id, Tx, Ty, Tz, Rx, Ry, Rz)
            
            # fix rotation for smd format
            if bone_frames.bone_id == 0:
                Tx, Ty, Rz = fix_rotation(Tx, Ty, Rz)
                
            # write bone position
            smd += f"{bone_frames.bone_id} {Tx:.6f} {Ty:.6f} {Tz:.6f} {Rx:.6f} {Ry:.6f} {Rz:.6f}\n"

    smd += "end\n"

    # write smd file
    file_dir = os.path.dirname(os.path.realpath(file_name))
    output_dir = Path(file_dir) / OUTPUT_DIR
    output_file = Path(output_dir) / Path(file_name).with_suffix(".smd").name
    
    os.makedirs(output_dir, exist_ok=True)
    with open(output_file, "w") as f:
        f.write(smd)
        
    print(f"Converted {file_name} to {output_file}")

def main():
    print(ASCII_ART)
    print("\033[0;32mAuthor: hampta, Idea: H3ADROOM")
    print("\033[0;32mhttps://t.me/antioldspicesquad\033[0m\n")
    args = sys.argv[1:]
    if not args:
        print(f"usage: {EXECUTABLE_NAME} <htr_file>")
        print(f"       {EXECUTABLE_NAME} <htr_file> <htr_file> ...")
        print(f"       {EXECUTABLE_NAME} <htr_dir>")
        print(f"       {EXECUTABLE_NAME} <htr_dir> <htr_dir> ...\n\n")
        input("Press enter to exit...")
        sys.exit(0)
    for arg in args:
        if os.path.isdir(arg):
            for file in glob.glob(f"{arg}/*.htr"):
                convert(file)
        elif os.path.isfile(arg):
            convert(arg)
        else:
            print(f"File or directory {arg} does not exist!")
            input("Press enter to exit...")
            sys.exit(1)
    print("Done!")


if __name__ == "__main__":
    main()
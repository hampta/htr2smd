import os
import sys
import math

from typing import List

OUTPUT_DIR = "./SMD"
EXECUTABLE_NAME = os.path.basename(sys.argv[0])

if getattr(sys, 'frozen', False):
    # frozen
    __location__ = sys._MEIPASS
else:
    # unfrozen
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    EXECUTABLE_NAME = f"python {EXECUTABLE_NAME}"

class HTRHeader:
    def __init__(self, htr_file: str):
        header = htr_file.split("[Header]")[1].split("[SegmentNames&Hierarchy]")[0].split("\n")
        # remove lines that start with #
        header = [line for line in header if not line.startswith("#")]
        # remove trailing whitespace
        header = [line.rstrip() for line in header]
        # remove empty lines
        header: List = [line for line in header if line]
        self.FileType: str = header[0].split()[1]
        self.DataType: str = header[1].split()[1]
        self.FileVersion: int = int(header[2].split()[1])
        self.NumSegments: int = int(header[3].split()[1])
        self.NumFrames: int = int(header[4].split()[1])
        self.DataFrameRate: int = int(header[5].split()[1])
        self.EulerRotationOrder: str = header[6].split()[1]
        self.CalibrationUnits: str = header[7].split()[1]
        self.RotationUnits: str = header[8].split()[1]
        self.GlobalAxisofGravity: str = header[9].split()[1]
        self.BoneLengthAxis: str = header[10].split()[1]
        self.ScaleFactor: str = float(header[11].split()[1])

# [SegmentNames&Hierarchy]
# #CHILD	PARENT
class HTRSegment:
    def __init__(self, name: str, parent: str, id: int = 0, parent_id: int = -1):
        self.name: str = name
        self.parent: str = parent
        self.id: int = id
        self.parent_id: int = parent_id


class HTRSegmentNamesHierarchy:
    def __init__(self, htr_file: str):
        self._segments = htr_file.split("[SegmentNames&Hierarchy]")[-1].split("[BasePosition]")[0].split("\n")
        # remove lines that start with #
        self._segments = [line for line in self._segments if not line.startswith("#")]
        # remove trailing whitespace
        self._segments = [line.rstrip() for line in self._segments]
        # remove empty lines
        self._segments = [line for line in self._segments if line]
        self.segments: List[HTRSegment] = []
        for segment in self._segments:
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
        self.BoneLength: float = BoneLength

class HTRBasePositions:
    # SegmentName Tx, Ty, Tz, Rx, Ry, Rz, BoneLength
    def __init__(self, htr_file):
        self._base_positions: List = htr_file.split("[BasePosition]")[-1].split("\n")
        # remove lines that start with #
        self._base_positions = [line for line in self._base_positions if not line.startswith("#")]
        # remove trailing whitespace
        self._base_positions = [line.rstrip() for line in self._base_positions]
        # remove empty lines
        self._base_positions = [line for line in self._base_positions if line]
        self.base_positions: List[HTRBasePosition] = []
        for base_position in self._base_positions:
            if base_position.startswith("["):
                break
            name, Tx, Ty, Tz, Rx, Ry, Rz, BoneLength = base_position.split()
            self.base_positions.append(HTRBasePosition(name, float(Tx), float(Ty),
                                                       float(Tz), float(Rx), float(Ry),
                                                       float(Rz), float(BoneLength)))

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
    def __init__(self, htr_file):
        self.header = HTRHeader(htr_file)
        self.segment_names_hierarchy = HTRSegmentNamesHierarchy(htr_file)
        self.base_positions = HTRBasePositions(htr_file)
        self.animation: List[HTRBoneFrames] = self.load_frames(htr_file)

    def load_frames(self, htr_file):
        _frames = htr_file.split("[BasePosition]")[-1].split(f"[{self.segment_names_hierarchy.segments[0].name}]")[-1].split("\n")
        _frames[0] = f"[{self.segment_names_hierarchy.segments[0].name}]"
        # remove lines that start with #
        _frames = [line for line in _frames if not line.startswith("#")]
        # remove trailing whitespace
        _frames = [line.rstrip() for line in _frames]
        # remove empty lines
        _frames = [line for line in _frames if line]
        frames: List[HTRBoneFrames] = []
        for frame in _frames:
            if frame.startswith("["):
                bone_name = frame.replace("[", "").replace("]", "")
                bone_id = self.get_bone_id(bone_name)
                frames.append(HTRBoneFrames(bone_name, bone_id, []))
                continue
            frame_number, Tx, Ty, Tz, Rx, Ry, Rz, SF = frame.split()
            frames[-1].list.append(HTRFrame(int(frame_number), float(Tx), float(Ty),
                                            float(Tz), float(Rx), float(Ry), float(Rz), float(SF)))
        return frames

    def get_bone_id(self, bone_name: str):
        for i, bone in enumerate(self.segment_names_hierarchy.segments):
            if bone.name == bone_name:
                return i
        return -1


def smd_bone_hierarchy(htr_file: HTRFile):
    # calculate bone hierarchy
    bone_hierarchy = []
    for i, segment in enumerate(htr_file.segment_names_hierarchy.segments):
        if segment.parent == "GLOBAL":
            bone_hierarchy.append(f"{i} \"{segment.name}\" -1")
            continue
        # find parent index
        for j, bone in enumerate(htr_file.segment_names_hierarchy.segments):
            if bone.name == segment.parent:
                bone_hierarchy.append(f"{i} \"{segment.name}\" {j}")
                break
    # write bone hierarchy
    for bone in bone_hierarchy:
        yield bone


def convert(file_name="animation.htr"):
    with open(file_name, "r") as f:
        htr_file = f.read()

    # parse htr file
    htr = HTRFile(htr_file)

    # write smd header
    smd = "version 1\n nodes\n  "

    # write bone hierarchy
    smd += "\n  ".join(smd_bone_hierarchy(htr))
    smd += "\nend\n"

    # write skeleton animation
    smd += "skeleton\n"

    for i in range(htr.header.NumFrames):
        smd += f"  time {i}\n"
        for bone_frames in htr.animation:
            for frame in bone_frames.list:
                if frame.id < i:
                    continue
                # convert to meters and radians
                Tx = frame.Tx * 0.1 * htr.header.ScaleFactor
                Ty = frame.Ty * 0.1 * htr.header.ScaleFactor
                Tz = frame.Tz * 0.1 * htr.header.ScaleFactor
                # convert to radians
                if htr.header.RotationUnits == "Degrees":
                    Rx = math.radians(frame.Rx)
                    Ry = math.radians(frame.Ry)
                    Rz = math.radians(frame.Rz)
                else:
                    Rx = frame.Rx
                    Ry = frame.Ry
                    Rz = frame.Rz

                # fix rotation for root bone
                if bone_frames.bone_id == 0:
                    Rz += math.radians(180)

                # write bone position
                smd += f"   {bone_frames.bone_id} {Tx:.6f} {Ty:.6f} {Tz:.6f} {Rx:.6f} {Ry:.6f} {Rz:.6f}\n"
                break

    smd += "end\n"

    file_dir = os.path.dirname(os.path.realpath(file_name))
    output_dir = os.path.join(file_dir, OUTPUT_DIR)

    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, 
                               os.path.basename(file_name)
                               .replace(".htr", ".smd"))

    with open(output_file, "w") as f:
        f.write(smd)

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
            for file in os.listdir(arg):
                if not file.endswith(".htr"):
                    continue
                print(f"Converting {file}...")
                convert(os.path.join(arg, file))
        if arg.endswith(".htr"):
            print(f"Converting {arg}...")
            convert(arg)
        else:
            print(f"Error: {arg} is not a htr file")
    print("Done!")


if __name__ == "__main__":
    main()
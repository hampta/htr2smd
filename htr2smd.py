import os
import sys
import math
import glob

OUTPUT_DIR = "./SMD"
EXECUTABLE_NAME = os.path.basename(sys.argv[0])
ASCII_ART = """\033[1;32m
 __    __  ________  _______          ______          ______   __       __  _______  
/  |  /  |/        |/       \        /      \        /      \ /  \     /  |/       \ 
$$ |  $$ |$$$$$$$$/ $$$$$$$  |      /$$$$$$  |      /$$$$$$  |$$  \   /$$ |$$$$$$$  |
$$ |__$$ |   $$ |   $$ |__$$ |      $$____$$ |      $$ \__$$/ $$$  \ /$$$ |$$ |  $$ |
$$    $$ |   $$ |   $$    $$<        /    $$/       $$      \ $$$$  /$$$$ |$$ |  $$ |
$$$$$$$$ |   $$ |   $$$$$$$  |      /$$$$$$/         $$$$$$  |$$ $$ $$/$$ |$$ |  $$ |
$$ |  $$ |   $$ |   $$ |  $$ |      $$ |_____       /  \__$$ |$$ |$$$/ $$ |$$ |__$$ |
$$ |  $$ |   $$ |   $$ |  $$ |      $$       |      $$    $$/ $$ | $/  $$ |$$    $$/ 
$$/   $$/    $$/    $$/   $$/       $$$$$$$$/        $$$$$$/  $$/      $$/ $$$$$$$/  
"""


# [SegmentNames&Hierarchy]
# #CHILD	PARENT
class HTRSegment:
    def __init__(self, name, parent, id = 0, parent_id = -1):
        self.name = name
        self.parent = parent
        self.id = id
        self.parent_id = parent_id


# [BasePosition]
# SegmentName Tx, Ty, Tz, Rx, Ry, Rz, BoneLength
class HTRBasePosition:
    def __init__(self, name, Tx, Ty, Tz, Rx, Ry, Rz, BoneLength):
        self.name = name
        self.Tx = Tx
        self.Ty = Ty
        self.Tz = Tz
        self.Rx = Rx
        self.Ry = Ry
        self.Rz = Rz
        self.bone_length = BoneLength


# Beginning of Data. Separated by tabs
# Fr	Tx	Ty	Tz	Rx	Ry	Rz	SF
class HTRFrame:
    def __init__(self, id, Tx, Ty, Tz, Rx, Ry, Rz, SF):
        self.id = id
        self.Tx = Tx
        self.Ty = Ty
        self.Tz = Tz
        self.Rx = Rx
        self.Ry = Ry
        self.Rz = Rz
        self.SF = SF


class HTRBoneFrames:
    def __init__(self, bone_name, bone_id, frames):
        self.bone_name = bone_name
        self.bone_id = bone_id
        self.list = frames

# [Header]
class HTRFile:
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
        header = [line for line in header if line]
        self.file_type = header[0].split()[1]
        self.data_type = header[1].split()[1]
        self.file_version = int(header[2].split()[1])
        self.num_segments = int(header[3].split()[1])
        self.num_frames = int(header[4].split()[1])
        self.data_frame_rate = int(header[5].split()[1])
        self.euler_rotation_order = header[6].split()[1]
        self.calibration_units = header[7].split()[1]
        self.rotation_units = header[8].split()[1]
        self.global_axis_of_gravity = header[9].split()[1]
        self.bone_length_axis = header[10].split()[1]
        self.scale_factor = float(header[11].split()[1])

    def load_segments(self):
        _segments = self._htr_file.split("[SegmentNames&Hierarchy]")[-1].split("[BasePosition]")[0].split("\n")
        # remove lines that start with #
        _segments = [line for line in _segments if not line.startswith("#")]
        # remove trailing whitespace
        _segments = [line.rstrip() for line in _segments]
        # remove empty lines
        _segments = [line for line in _segments if line]
        self.segments = []
        for bone_id, segment in enumerate(_segments):
            segment_name, segment_parent = segment.split()
            # calculate bone id
            # calculate bone parent id
            for i, bone in enumerate(self.segments):
                if bone.name == segment_parent:
                    bone_parent_id = i
                    break
            else:
                bone_parent_id = -1
            self.segments.append(HTRSegment(segment_name, segment_parent, bone_id, bone_parent_id))

    def load_base_positions(self):
        _base_positions = self._htr_file.split("[BasePosition]")[-1].split("\n")
        # remove lines that start with #
        _base_positions = [line for line in _base_positions if not line.startswith("#")]
        # remove trailing whitespace
        _base_positions = [line.rstrip() for line in _base_positions]
        # remove empty lines
        _base_positions = [line for line in _base_positions if line]
        self.base_positions = []
        for base_position in _base_positions:
            if base_position.startswith("["):
                break
            name, Tx, Ty, Tz, Rx, Ry, Rz, bone_length = base_position.split()
            self.base_positions.append(HTRBasePosition(name, float(Tx), float(Ty),
                                                  float(Tz), float(Rx), float(Ry),
                                                  float(Rz), float(bone_length)))

    def load_frames(self):
        _frames = self._htr_file.split("[BasePosition]")[-1].split(f"[{self.segments[0].name}]")[-1].split("\n")
        _frames[0] = f"[{self.segments[0].name}]"
        # remove lines that start with #
        _frames = [line for line in _frames if not line.startswith("#")]
        # remove trailing whitespace
        _frames = [line.rstrip() for line in _frames]
        # remove empty lines
        _frames = [line for line in _frames if line]
        self.frames = []
        for frame in _frames:
            if frame.startswith("["):
                bone_name = frame.replace("[", "").replace("]", "")
                bone_id = self.bone_index.index(bone_name)
                self.frames.append(HTRBoneFrames(bone_name, bone_id, []))
                continue
            frame_number, Tx, Ty, Tz, Rx, Ry, Rz, SF = frame.split()
            self.frames[-1].list.append(HTRFrame(int(frame_number), float(Tx), float(Ty),
                                            float(Tz), float(Rx), float(Ry), float(Rz), float(SF)))
    
    def indexate_bones(self):
        self.bone_index = []
        for bone in self.segments:
            self.bone_index.append(bone.name)
            

    def to_radians(self, Rx, Ry, Rz):
        if self.rotation_units == "Degrees":
            Rx = math.radians(Rx)
            Ry = math.radians(Ry)
            Rz = math.radians(Rz)
        return Rx,Ry,Rz
    
    def apply_scale(self, bone_id, Tx, Ty, Tz):
        scale_factor = self.base_positions[bone_id].bone_length * self.scale_factor
        Tx /= scale_factor
        Ty /= scale_factor
        Tz /= scale_factor
        return Tx,Ty,Tz

    # IDK if this is correct
    def apply_base_position(self, bone_id, Tx, Ty, Tz, 
                            Rx, Ry, Rz):
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

def fix_rotation(Tx, Ty, Rz):
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
        # smd += f"{bone}\n"
        smd += bone + "\n"
    smd += "end\n"

    # write skeleton animation
    smd += "skeleton\n"

    for i in range(htr.num_frames):
        # smd += f"time {i}\n"
        smd += "time " + str(i) + "\n"
        for bone_frames in htr.frames:
            frame = bone_frames.list[i]
            Tx, Ty, Tz = htr.apply_scale(bone_frames.bone_id, frame.Tx, frame.Ty, frame.Tz)
            Rx, Ry, Rz = htr.to_radians(frame.Rx, frame.Ry, frame.Rz)
            # Tx, Ty, Tz, Rx, Ry, Rz = htr.apply_base_position(bone_frames.bone_id, Tx, Ty, Tz, Rx, Ry, Rz)
            
            # fix rotation for smd format
            if bone_frames.bone_id == 0:
                Tx, Ty, Rz = fix_rotation(Tx, Ty, Rz)
                
            # write bone position
            smd += f"{bone_frames.bone_id} {Tx:.6g} {Ty:.6g} {Tz:.6g} {Rx:.6g} {Ry:.6g} {Rz:.6g}\n"
            # Tx = round(Tx, 6)
            # Ty = round(Ty, 6)
            # Tz = round(Tz, 6)
            # Rx = round(Rx, 6)
            # Ry = round(Ry, 6)
            # Rz = round(Rz, 6)
            
            # smd += str(bone_frames.bone_id) + " " + str(Tx) + " " + str(Ty) + " " + str(Tz) + " " + str(Rx) + " " + str(Ry) + " " + str(Rz) + "\n"

    smd += "end\n"

    # write smd file
    file_dir = os.path.dirname(os.path.realpath(file_name))
    
    output_dir = os.path.join(file_dir, OUTPUT_DIR)
    output_file = os.path.join(output_dir, os.path.basename(file_name).replace(".htr", ".smd"))
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
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
            for file in glob.glob(f"{arg}/*.htr", recursive=True):
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
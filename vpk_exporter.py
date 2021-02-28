import vpk
import os

import errno

# Request information important to exporting only the needed files
vpk_location = input("Please specify the location of the VPK (Most likely <game>_misc_dir.vpk): ")
hl2_vpk_location = input("Please specify the location of the VPK for hl2 (used for missing resources): ")
output_path = input("Please specify the location to write the exported files to: ")

required_materials = input("Please specify the location of a file containing the list of needed material files: ")
required_materials_file = open(required_materials, "r")
required_materials = required_materials_file.read().strip().split("\n")
required_materials_file.close()

required_models = input("Please specify the location of a file containing the list of needed model files: ")
required_models_file = open(required_models, "r")
required_models = required_models_file.read().strip().split("\n")
required_models_file.close()

vpk_game = vpk.open(vpk_location)
vpk_hl2 = vpk.open(hl2_vpk_location)

fetched_files = 0

def write_output_file(path, data):
    if not os.path.exists(path):
        try:
            os.makedirs(os.path.dirname(path))
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
            
    output_file = open(path, "wb")
    output_file.write(data)
    output_file.close()

def read_null_terminated(data):
    for index in range(len(data)):
        if data[index] == 0:
            return str(data[:index], 'UTF-8')

def get_texture_names(mdl):
    texture_count = int.from_bytes(mdl[204:208], byteorder='little', signed=False)
    texture_offset = int.from_bytes(mdl[208:212], byteorder='little', signed=False)
    
    textures = []
    
    for texture_index in range(texture_count):
        base_offset = texture_offset + (texture_index * 64)
        name_offset_from_base = int.from_bytes(mdl[base_offset:base_offset+4], byteorder='little', signed=False)

        name = read_null_terminated(mdl[base_offset + name_offset_from_base:])
        textures.append(name)
    return textures

def get_texture_dirs(mdl):
    dir_count = int.from_bytes(mdl[212:216], byteorder='little', signed=False)
    dir_list_offset = int.from_bytes(mdl[216:220], byteorder='little', signed=False)

    dirs = []
    for index in range(dir_count):
        base_offset = dir_list_offset + (index * 4)
        offset = int.from_bytes(mdl[base_offset:base_offset+4], byteorder='little', signed=False)

        path = read_null_terminated(mdl[offset:]).replace("\\", "/")
        if path.startswith("/"):
            path = path[1:]
        dirs.append(path)
    return dirs

# Predefine vpk_data
vpk_data = vpk_game

# Fetch material files
print("Fetching materials...")
for filename in required_materials:
    if filename in vpk_game:
        vpk_data = vpk_game
    else:
        vpk_data = vpk_hl2 # Test the other vpk as well
    if filename in vpk_data:
        write_output_file(os.path.join(output_path, filename), vpk_data.get_file(filename).read())
        fetched_files += 1
    else:
        print("Failed to fetch file `" + filename + "`")
        
print("Fetched " + str(fetched_files) + "/" + str(len(required_materials)) + " materials")


fetched_models = 0
fetched_materials = 0
# Fetch model/material combos
print("Fetching models and their materials...")
for filename in required_models:
    if filename in vpk_game:
        vpk_data = vpk_game
    else:
        vpk_data = vpk_hl2 # Test the other vpk as well
    if filename in vpk_data:
        mdl = vpk_data.get_file(filename).read()
        write_output_file(os.path.join(output_path, filename), mdl)
        fetched_models += 1

        textures = get_texture_names(mdl)
        texture_dirs = get_texture_dirs(mdl)
        for texture in textures:
            found = False
            for directory in texture_dirs:
                texture_filename = os.path.join("materials/", directory, texture + ".vmt")
                if texture_filename.lower() in vpk_game:
                    vpk_data = vpk_game
                else:
                    vpk_data = vpk_hl2 # Test the other vpk as well
                if texture_filename.lower() in vpk_data:
                    write_output_file(os.path.join(output_path, texture_filename), vpk_data.get_file(texture_filename.lower()).read())
                    fetched_materials += 1
                    found = True
                    break
            if found == False:
                print("Failed to fetch file `" + texture + "`")
            
    else:
        print("Failed to fetch file `" + filename + "`")

print("Fetched " + str(fetched_models) + "/" + str(len(required_models)) + " models and " + str(fetched_materials) + " materials")

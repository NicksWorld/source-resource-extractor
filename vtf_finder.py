import vpk
import os
import re

import errno

# Request information important to exporting only the needed files
vpk_location = input("Please specify the location of the VPK (Most likely <game>_textures_dir.vpk): ")
hl2_vpk_location = input("Please specify the location of the VPK for hl2 (used for missing resources): ")
output_path = input("Please specify the output location: ")

vpk_game = vpk.open(vpk_location)
vpk_hl2 = vpk.open(hl2_vpk_location)

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

fetched_files = 0
    
# Search for all vmt files that could require a vtf
for dirpath, dirnames, files in os.walk(output_path):
    for name in files:
        if name.lower().endswith(".vmt"):
            # Read the file
            vmt_file = open(os.path.join(dirpath, name))
            vmt = vmt_file.read()
            vmt_file.close()

            # Match with regex
            vtf_list = re.findall('"\$(?:basetexture2|basetexture|blendmodulatetexture)"\s"(.*)"', vmt)
            for vtf in vtf_list:
                vtf = "materials/" + vtf.lower().replace("\\", "/") + ".vtf"
                # Locate and write VTF file
                if vtf in vpk_game:
                    vpk_data = vpk_game
                else:
                    vpk_data = vpk_hl2 # Test the other vpk as well
                    
                if vtf in vpk_data:
                    write_output_file(os.path.join(output_path, vtf), vpk_data.get_file(vtf).read())
                    fetched_files += 1
                else:
                    print("Failed to fetch file `" + vtf + "`")

print("Fetched" + str(fetched_files) + " VTF files")

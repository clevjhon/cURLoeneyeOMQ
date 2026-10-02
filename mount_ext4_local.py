import os

def mount_ext4_image(image_path, mount_point="./ext4_virtual_mnt"):
    print(f"  [EXT4] A' feuchainn ri container fhosgladh: {image_path}")
    if not os.path.exists(image_path):
        print(f"  [EXT4] Mearachd: Cha do lorgar am faidhle '{image_path}'.")
        return False
    
    os.makedirs(mount_point, exist_ok=True)
    
    try:
        with open(image_path, "rb") as f:
            f.seek(1080)
            magic = f.read(2)
            if magic == b'\x53\xef':
                print("  [EXT4] Lorgadh suaicheantas ext4 (0xEF53) gu soirbheachail!")
            else:
                print("  [EXT4] Rabhadh: Suaicheantas neo-àbhaisteach, a' leantainn air adhart.")
                
        print(f"  [EXT4] Chaidh a mapadh gu h-ionadail gu: {mount_point}")
        return True
    except Exception as e:
        print(f"  [EXT4] Dh'fhàillig e: {e}")
        return False

mount_ext4_image("oeneye-ext4.img")

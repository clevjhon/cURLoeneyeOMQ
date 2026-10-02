import os
import shutil
import datetime

def run_backup():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"backup_{timestamp}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Backup workspace, shared storage, and emulator script if they exist
    items_to_backup = ["workspace", "shared_storage", "emu_dos.py"]
    backed_up = []
    
    for item in items_to_backup:
        if os.path.exists(item):
            dest = os.path.join(backup_dir, item)
            if os.path.isdir(item):
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)
            backed_up.append(item)
            
    print(f"Snapshot created successfully in folder: {backup_dir}")
    print(f"Backed up items: {', '.join(backed_up)}")

if __name__ == "__main__":
    run_backup()

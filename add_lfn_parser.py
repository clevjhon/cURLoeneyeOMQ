with open("emu.py", "r") as f:
    code = f.read()

lfn_command = """
        elif cmd.upper() == "LFNCHECK":
            print("--- OENEYE SDK VFAT/LFN Slot Verification ---")
            # Simulated directory slot (32 bytes) with ATTR_LONG_NAME (0x0F)
            sample_slot = bytearray(32)
            sample_slot[0x00] = 0x41  # LDIR_Ord (Last long entry flag)
            sample_slot[0x0B] = 0x0F  # LDIR_Attr (ATTR_LONG_NAME)
            
            attr = sample_slot[0x0B]
            if attr == 0x0F:
                print("Detected VFAT LFN metadata slot (Attribute: 0x0F)")
                print("Skipping execution handle as required by OENEYE VFAT spec.")
            else:
                print("Standard 8.3 short entry detected.")
"""

if 'elif cmd.upper() == "GO":' in code:
    code = code.replace('elif cmd.upper() == "GO":', lfn_command + '\n        elif cmd.upper() == "GO":')
    with open("emu.py", "w") as f:
        f.write(code)
    print("Added LFNCHECK command to MOSFETQ-DOS!")
else:
    print("Could not locate command hook.")

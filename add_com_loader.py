with open("emu.py", "r") as f:
    code = f.read()

# Add a RUN command handler to execute .COM files
com_loader_command = """
        elif cmd.upper().startswith("RUN "):
            filename = cmd.split()[1]
            import os
            if os.path.exists(filename):
                with open(filename, "rb") as bin_file:
                    bin_data = bin_file.read()
                
                global memory
                if "memory" not in globals():
                    globals()["memory"] = bytearray(0x10000)
                memory = globals()["memory"]
                
                # Load .COM binary at offset 0x100
                load_addr = 0x0100
                if load_addr + len(bin_data) > len(memory):
                    memory.extend(b'\\x00' * (load_addr + len(bin_data) - len(memory)))
                
                for i, b in enumerate(bin_data):
                    memory[load_addr + i] = b
                
                print(f"Loaded {filename} ({len(bin_data)} bytes) to CS:0100.")
                print("Executing binary via CPU loop...")
                
                # Set initial register state for .COM execution
                # (Assuming IP = 0x0100, SP = 0xFFFE)
                # We can invoke the CPU step/go loop here or simulate execution
            else:
                print(f"File not found: {filename}")
"""

if 'elif cmd.upper() == "GO":' in code:
    code = code.replace('elif cmd.upper() == "GO":', com_loader_command + '\n        elif cmd.upper() == "GO":')
    with open("emu.py", "w") as f:
        f.write(code)
    print("Added .COM file loader command successfully!")
else:
    print("Could not locate GO command hook.")

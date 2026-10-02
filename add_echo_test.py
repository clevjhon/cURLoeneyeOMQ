with open("emu.py", "r") as f:
    code = f.read()

# Add a TESTECH command to the shell loop
echo_command = """
        elif cmd.upper() == "TESTECH":
            print("--- Testing INT 21h AH=0Ah (Input) + AH=09h (Output) ---")
            global memory
            if "memory" not in globals():
                memory = bytearray(0x10000)
            
            # Setup buffer at DS:DX = 0x0700
            ds_dx = 0x0700
            memory[ds_dx] = 40  # Max length
            
            # 1. Call AH=0Ah for buffered input
            regs_in = {"AX": 0x0A00, "DS": 0x0000, "DX": 0x0700}
            handle_interrupt(0x21, regs_in, memory)
            
            # 2. Extract length and append '$' terminator for AH=09h
            length_read = memory[ds_dx + 1]
            str_end = ds_dx + 2 + length_read
            memory[str_end] = ord('$')  # DOS string terminator
            
            print("\\nEchoing back using INT 21h AH=09h:")
            regs_out = {"AX": 0x0900, "DS": 0x0000, "DX": ds_dx + 2}
            handle_interrupt(0x21, regs_out, memory)
            print()
"""

# Insert before the "else:" or "GO" command handler
if 'elif cmd.upper() == "GO":' in code:
    code = code.replace('elif cmd.upper() == "GO":', echo_command + '\n        elif cmd.upper() == "GO":')
    with open("emu.py", "w") as f:
        f.write(code)
    print("Added TESTECH command successfully!")
else:
    print("Could not locate GO command hook.")

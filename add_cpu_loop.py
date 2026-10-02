with open("emu.py", "r") as f:
    code = f.read()

# Replace the placeholder execution print in the RUN command with a working CPU loop
old_exec = """                print(f"Loaded {filename} ({len(bin_data)} bytes) to CS:0100.")
                print("Executing binary via CPU loop...")
                
                # Set initial register state for .COM execution
                # (Assuming IP = 0x0100, SP = 0xFFFE)
                # We can invoke the CPU step/go loop here or simulate execution"""

new_exec = """                print(f"Loaded {filename} ({len(bin_data)} bytes) to CS:0100.")
                print("Executing binary via CPU loop...")
                
                # Initialize registers for .COM execution
                regs = {"IP": 0x0100, "CS": 0x0000, "AX": 0, "BX": 0, "CX": 0, "DX": 0}
                running = True
                
                while running:
                    ip = regs["IP"]
                    if ip >= len(memory):
                        print("CPU Error: Instruction Pointer out of bounds.")
                        break
                    
                    opcode = memory[ip]
                    regs["IP"] += 1
                    
                    if opcode == 0x90:  # NOP
                        pass
                    elif opcode == 0xCD:  # INT imm8
                        if regs["IP"] < len(memory):
                            int_num = memory[regs["IP"]]
                            regs["IP"] += 1
                            if int_num == 0x20:  # Terminate program
                                print("Program terminated normally via INT 20h.")
                                running = False
                            elif int_num == 0x21:
                                # Hook into our existing handle_interrupt
                                handle_interrupt(0x21, regs, memory)
                    else:
                        print(f"Unknown opcode 0x{opcode:02X} at IP: 0x{ip-1:04X}")
                        running = False"""

code = code.replace(old_exec, new_exec)

with open("emu.py", "w") as f:
    f.write(code)

print("Added CPU execution loop for .COM binaries!")

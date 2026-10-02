with open("emu.py", "r") as f:
    code = f.read()

# Locate the broken AH=0Ah block and replace it cleanly
target_start = "elif ah == 0x0A:"
if target_start in code:
    parts = code.split(target_start)
    prefix = parts[0]
    # Find where this block ends (e.g. before next elif or return True)
    suffix_parts = parts[1].split("return True")
    # suffix_parts[0] contains the broken lines, suffix_parts[1] is the rest of the function/file
    
    clean_block = """elif ah == 0x0A:
            import sys
            line_input = sys.stdin.readline().rstrip('\\n') + '\\r'
            ds = regs.get('DS', 0)
            dx = regs.get('DX', 0)
            ds_dx = (ds << 4) + dx
            # Ensure memory is large enough
            if ds_dx + 256 > len(memory):
                memory.extend(b'\\x00' * (ds_dx + 256 - len(memory)))
            max_len = memory[ds_dx] if memory[ds_dx] > 0 else 30
            input_bytes = line_input.encode('ascii', errors='ignore')[:max_len]
            memory[ds_dx + 1] = len(input_bytes)
            for idx, b in enumerate(input_bytes):
                memory[ds_dx + 2 + idx] = b
            return True
"""
    code = prefix + clean_block + suffix_parts[1]
    with open("emu.py", "w") as f:
        f.write(code)
    print("Cleaned and patched AH=0Ah handler successfully!")
else:
    print("AH=0Ah handler not found.")

with open("emu.py", "r") as f:
    lines = [line.rstrip('\n') for line in f.readlines()]

# Retain stable code up to the main loop termination boundary
valid_lines = [l for i, l in enumerate(lines) if i < 478]

# Append the Tartan sett 2/2 twill matrix and Euler coupling within the correct scope
final_block = [
    "    # Tartan Sett 2/2 Twill Weave Pattern & Euler Phase Coupling",
    "    try:",
    "        tartan_sett_seq = [2, 2, 4, 4, 6, 6]",
    "        import math",
    "        euler_coupling = math.exp(0.5)",
    "        if 'env_state' in globals():",
    "            env_state['tartan_sett_matrix'] = [val * euler_coupling for val in tartan_sett_seq]",
    "    except Exception as tartan_err:",
    "        print(f'Tartan coupling warning: {tartan_err}')",
    "except (KeyboardInterrupt, EOFError):",
    "    print('\\n[MOSFETQ-DOS] Session terminated under Tartan-Euler equilibrium.')",
    "    break"
]

valid_lines.extend(final_block)

with open("emu.py", "w") as f:
    f.write('\n'.join(valid_lines) + '\n')

print("Successfully integrated Tartan sett weave matrix with Euler coupling!")

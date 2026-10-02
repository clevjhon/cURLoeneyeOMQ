with open("emu.py", "r") as f:
    lines = f.readlines()

# Keep lines up to 480, then append a clean, correctly indented main execution loop wrapper and exit handler
clean_lines = lines[:480]

trailing_clean = [
    "\n    except (KeyboardInterrupt, EOFError):\n",
    "        print('\\n[MOSFETQ-DOS] Session terminated by user interrupt.')\n",
    "        break\n"
]

clean_lines.extend(trailing_clean)

with open("emu.py", "w") as f:
    f.writelines(clean_lines)

print("Sanitized file tail and fixed indentation successfully!")

import os

def run(line):
    parts = line.strip().split()
    if not parts:
        return

    cmd = parts[0].lower()

    if cmd == "help":
        print("Available commands: dir, cls, exit")
    elif cmd == "dir":
        print("Directory of A:\\")
        for f in os.listdir('.'):
            print(f"  {f}")
    elif cmd == "cls":
        print("\033[H\033[J", end="")
    elif cmd == "exit":
        print("Exiting EMU-DOS...")
        exit(0)
    else:
        print(f"Bad command or file name: {parts[0]}")

if __name__ == "__main__":
    print("EMU-DOS initialized. Type commands below:")
    while True:
        try:
            line = input("A:\\> ")
            run(line)
        except (KeyboardInterrupt, EOFError):
            break


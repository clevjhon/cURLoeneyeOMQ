import sys
import os

QUIET_MODE = "-Q" in sys.argv

if not QUIET_MODE:
    print("Pascal Emulator v1.0 - Interactive Mode")

def run_hanoi(n=3, source='A', target='C', auxiliary='B'):
    if n == 1:
        print(f"Move disk 1 from {source} to {target}")
        return
    run_hanoi(n - 1, source, auxiliary, target)
    print(f"Move disk {n} from {source} to {target}")
    run_hanoi(n - 1, auxiliary, target, source)

def run(line):
    parts = line.strip().split()
    if not parts:
        return

    cmd = parts[0].lower()

    if cmd == "help":
        print("Available commands: dir, cls, hanoi, exit")
    elif cmd == "dir":
        print("Directory of A:\\")
        for f in os.listdir('.'):
            print(f"  {f}")
    elif cmd == "hanoi":
        print("Solving Towers of Hanoi (3 disks):")
        run_hanoi(3)
    elif cmd == "cls":
        print("\033[H\033[J", end="")
    elif cmd == "exit":
        print("Exiting Emulator...")
        exit(0)
    else:
        print(f"Bad command or file name: {parts[0]}")

if __name__ == "__main__":
    while True:
        try:
            line = input("A:\\> ")
            run(line)
        except (KeyboardInterrupt, EOFError):
            break


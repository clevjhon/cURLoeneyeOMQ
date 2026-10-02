import subprocess
import os

def run_step(script_name):
    print(f"\n[PIPELINE] Executing {script_name}...")
    if os.path.exists(script_name):
        result = subprocess.run(["python3", script_name], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[PIPELINE] Success: {script_name} completed.")
            if result.stdout.strip():
                print(result.stdout.strip())
        else:
            print(f"[PIPELINE] Error in {script_name}:\n{result.stderr.strip()}")
    else:
        print(f"[PIPELINE] Warning: {script_name} not found, skipping.")

if __name__ == '__main__':
    print("=== OENEYE UPDATE AUTOMATION PIPELINE ===")
    run_step("update.py")
    run_step("update_channels.py")
    run_step("update_emu.py")
    print("\n=== PIPELINE EXECUTION COMPLETE ===")

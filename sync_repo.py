import os
import subprocess
import sys

def run_git_command(args):
    try:
        result = subprocess.run(["git"] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Git error: {e.stderr}", file=sys.stderr)
        return False

def main():
    print("--- Starting oeneye repository sync ---")
    if not run_git_command(["status"]): return
    print("Staging changes...")
    if not run_git_command(["add", "."]): return
    commit_msg = input("Enter commit message (default: 'Auto-update workspace and backups'): ").strip()
    if not commit_msg: commit_msg = "Auto-update workspace and backups"
    if not run_git_command(["commit", "-m", commit_msg]):
        print("No changes to commit or commit failed.")
        return
    branch = input("Enter target branch [main/dev/monokernel]: ").strip()
    if not branch: branch = "main"
    print(f"Pushing to origin/{branch}...")
    if run_git_command(["push", "origin", branch]):
        print("Successfully synced with GitHub!")
    else:
        print("Push failed. Check your authentication/token settings.")

if __name__ == "__main__":
    main()

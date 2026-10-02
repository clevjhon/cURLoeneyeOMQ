import socket
import sys

def run_irc(server="irc.libera.chat", port=6697, nick="oeneyeUser"):
    print(f"[oeneyeIRC] Connecting to {server}:{port} as {nick}...")
    # Minimal client skeleton for the oeneyeOS ecosystem
    print("[oeneyeIRC] Ready. Type /JOIN <channel> or /QUIT to exit.")
    
    while True:
        try:
            cmd = input(f"[{nick}]> ").strip()
            if cmd.upper() == "/QUIT":
                print("[oeneyeIRC] Disconnecting...")
                break
            elif cmd.upper().startswith("/JOIN "):
                channel = cmd.split()[1]
                print(f"[oeneyeIRC] Joined {channel} (Simulated session)")
            else:
                print(f"[oeneyeIRC] Sent: {cmd}")
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    run_irc()

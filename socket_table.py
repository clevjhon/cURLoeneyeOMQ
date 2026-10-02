SOCKET_TABLE = {}
def register_socket(id, state="ACTIVE"):
    SOCKET_TABLE[id] = state
    return f"[{id}] -> {state} [o∞o]"
if __name__ == "__main__":
    print(register_socket("Device 0 [0:0]"))

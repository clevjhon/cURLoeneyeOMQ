import os

def align_binaries():
    print("START: Scanning for unaligned binary assets...")
    extensions = ('.img', '.bin', '.s')
    
    for filename in os.listdir('.'):
        if filename.endswith(extensions) and os.path.isfile(filename):
            size = os.path.getsize(filename)
            remainder = size % 512
            
            if remainder != 0:
                padding_needed = 512 - remainder
                print(f"Padding {filename}: current size {size} bytes. Adding {padding_needed} zero-bytes.")
                
                with open(filename, 'ab') as f:
                    f.write(b'\x00' * padding_needed)
                    
                new_size = os.path.getsize(filename)
                print(f"SUCCESS: {filename} is now aligned at {new_size} bytes (Remainder: {new_size % 512})")
            else:
                print(f"SKIPPED: {filename} is already 512-byte aligned ({size} bytes).")

    print("Alignment sequence complete!")

if __name__ == "__main__":
    align_binaries()

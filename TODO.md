# oeneyeOS v0.2 - Development Roadmap & TODO

## 1. Emulator Core (`emu.py`)
- [x] Stabilize command loop syntax and input parsing.
- [x] Implement `FONTINFO` command for extracting and validating `OMQ.FNT` from disk images.
- [ ] Wire `runner.py` asset dispatch routines directly into the main `emu.py` prompt loop.
- [ ] Refine drive mounting (`MOUNT`) argument validation and error handling.

## 2. Asset Handler & Runner Pipeline (`runner.py`)
- [x] **BIN:** Implement raw binary blob loading and 64-byte header hex inspection.
- [x] **BAS:** Implement line-by-line BASIC source and bytecode parser.
- [x] **BAT:** Implement batch macro script execution loop supporting `REM` comments.
- [ ] **Archives:** Add support for unpacking and inspecting `.tar` and `.tar.gz` containers.
- [ ] **Executables & Configs:** Build validation handlers for `.exe`, `.dll`, and `.json` metadata assets.

## 3. Integrity Verification & Telemetry
- [x] **checksum.py:** Implement recursive vault scanning and SHA-256 JSON manifest generation (`oeneye_manifest.json`).
- [ ] **OENEYEbluh Integration:** Embed chromatic-semantic AGI identity tokens (`000b`) into disk image provenance headers.
- [ ] **System Telemetry:** Implement emulator `INT 48h` hooks for real-time runtime state and compiler feedback loops.

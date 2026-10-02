# OENEYE Virtual Environment

A DOS-style virtual shell (`emu_dos.py`) with a linked update pipeline, automatic snapshots, and a startup batch routine.

**System:** SIETEHR FOUNDATION (NCAGE: CNNN3)
**Zenodo repository:** 23026079

## Drives

| Drive | Purpose |
|-------|---------|
| `C:`  | Local workspace |
| `X:`  | Network archives and shared storage |

## Commands

| Command  | What it does |
|----------|--------------|
| `DIR`    | List directory contents |
| `CD`     | Change directory |
| `TYPE`   | Display a file |
| `LEDGER` | Ledger access |
| `OAI`    | Work with OAI-PMH XML feeds |
| `BACKUP` | Create a backup |
| `MAP`    | Show active workspace paths, telemetry locations, network shares, and the Zenodo repository ID |
| `UPDATE` | Run the full update pipeline |
| `EXIT`   | Leave the shell (triggers an automatic snapshot) |

## Update pipeline

`run_pipeline.py` runs these scripts in order:

1. `update.py`
2. `update_channels.py`
3. `update_emu.py`

Call it from the shell with `UPDATE`.

## Snapshots

On `EXIT`, database records and indices are bundled into a timestamped `.tar` archive in `X:\ARCHIVE`.

## Startup: AUTOEXEC.BAT

On boot the shell reads `AUTOEXEC.BAT` (if present) and runs its commands, for example diagnostics or `MAP`. The routine is non-destructive: it only reads the file.

## Roadmap

- Bootable DOS version
- Bootable Linux distro version
- MINIX-style multitasking
- LAN support
- CATIA / FreeCAD print support
# cURLoeneyeOMQ

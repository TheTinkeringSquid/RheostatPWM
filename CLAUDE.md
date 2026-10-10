# B2500 Cluster LED PWM Dimmer — Agent Instructions (Claude + Codex)
<!-- CLAUDE.md and AGENTS.md are identical; edit both together. Router, not a diary: keep under ~100 lines. -->

## What this is
A small RP2040 (Seeed XIAO) board for a 1996 Dodge B2500 instrument-cluster LED conversion. It reads the factory headlight rheostat as an analog input and drives the cluster illumination with a protected high-side 12 V PWM output. Repo: `TheTinkeringSquid/RheostatPWM`.
Status: PCB fully routed and DRC-clean; gerbers in `hardware/gerbers/`.

## Hard constraints
- **Cluster illumination only.** Never adapt it for exterior lights, brake or turn signals, airbags, engine controls, or anything safety-critical.
- Never power the MCU from `DIM_IN` (it browns out when the rheostat is turned down).
- If the factory dimmer turns out to be low-side, already PWM, or multiplexed, **stop** and revise the input circuit rather than forcing this design.

## Where things live
| Need | Go to |
|---|---|
| How it works, J1 pinout, install, safety | `README.md` |
| **Netlist (single source of truth for schematic and board)** | `hardware/scripts/netlist.py` |
| Generators | `hardware/scripts/gen_sch.py`, `gen_pcb.py`, `gen_bom.py`, `export_fab.py` |
| KiCad project, schematic PDF, footprints | `hardware/kicad/` |
| Fab output, BOM, JLCPCB files | `hardware/gerbers/`, `hardware/*.csv`, `hardware/fabrication_notes.md` |
| Firmware and calibration constants | `firmware/src/main.cpp` (top of file), `firmware/platformio.ini` |

## Commands
- Schematic: `python hardware/scripts/gen_sch.py`
- Board: `& "C:/Program Files/KiCad/10.0/bin/python.exe" hardware/scripts/gen_pcb.py` (needs KiCad's Python)
- BOM: `python hardware/scripts/gen_bom.py`
- Fab output (runs DRC, gerbers, drill, BOM): `python hardware/scripts/export_fab.py`
- Firmware: `cd firmware && pio run` · `pio run -t upload` · `pio device monitor` (115200)

## Rules
- **Change the netlist, then regenerate.** Don't hand-edit generated KiCad files and then rerun `gen_pcb.py`: it rebuilds the board from scratch and **discards manual KiCad edits**. Ask before regenerating if manual edits may exist.
- After any hardware change: DRC must show 0 violations and 0 unconnected, and say so. Regenerate gerbers with `export_fab.py`.
- Calibration constants are tuned on the bench against the real dimmer. Don't change their defaults without bench data.
- Commit or push only when Nathan says so. The untracked `hardware/*.zip` files are build artifacts; ask before committing them.

## Applied learning
<!-- One-line bullets added when something fails repeatedly. Prune often. -->
-

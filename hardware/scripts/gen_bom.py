#!/usr/bin/env python3
"""Emit a grouped BOM CSV from the shared netlist.

    python hardware/scripts/gen_bom.py

Identical parts (same value + footprint + DNP state) are grouped onto one
line. F1 is included and flagged as an off-board inline harness fuse.
Run with any Python 3; no KiCad modules required.
"""

import csv
import sys
from collections import OrderedDict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from netlist import COMPONENTS  # noqa: E402

OUT = SCRIPT_DIR.parent / "b2500_cluster_pwm_dimmer_bom.csv"

# Per-ref-prefix purchasing/assembly notes (brief BOM guidance).
NOTES = {
    "U1": "Seeed XIAO RP2040 module on 2x7 socket headers",
    "U2": "Pololu D36V28F5 buck module, mounted OFF-BOARD; wire its VIN/GND/VOUT to the 3-pin header (match label to label)",
    "Q1": ">=40V Vds, >=2A, low Rds(on); TO-220",
    "Q2": "small logic-level N-MOSFET / 2N7000",
    "F1": "OFF-BOARD: inline blade fuse in the vehicle harness; size to LED current",
    "D1": "reverse-polarity series Schottky, >=3A >=40V",
    "D2": "TVS across protected VIN-GND",
    "D3": "optional 5V isolation diode (USB backfeed)",
    "D4": "ADC clamp to 3V3/GND",
    "D5": "12V zener, Q1 gate-source protection",
    "J1": "5-pos 5.08mm pluggable terminal (or locking automotive conn)",
    "JP1": "open to isolate vehicle 5V during USB programming",
    "R10": "DNP RC snubber across PWM_OUT (fit only if edge ringing)",
    "C5": "DNP RC snubber across PWM_OUT (fit only if edge ringing)",
    "R1": "DNP IGN-sense divider (future firmware)",
    "R2": "DNP IGN-sense divider (future firmware)",
}


def main():
    groups = OrderedDict()
    for ref, _sym, value, footprint, dnp, on_board, _nets, _xy in COMPONENTS:
        note = NOTES.get(ref, "")
        key = (value, footprint, dnp, on_board, note)
        groups.setdefault(key, []).append(ref)

    rows = []
    for (value, footprint, dnp, on_board, note), refs in groups.items():
        refs_sorted = sorted(refs, key=lambda r: (r[0], int("".join(c for c in r if c.isdigit()) or 0)))
        flags = []
        if dnp:
            flags.append("DNP")
        if not on_board:
            flags.append("OFF-BOARD")
        rows.append({
            "Refs": ",".join(refs_sorted),
            "Qty": len(refs),
            "Value": value,
            "Footprint": footprint,
            "Fit": " ".join(flags) if flags else "FIT",
            "Notes": note,
        })

    rows.sort(key=lambda r: r["Refs"])
    with OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["Refs", "Qty", "Value", "Footprint", "Fit", "Notes"])
        w.writeheader()
        w.writerows(rows)

    fitted = sum(r["Qty"] for r in rows if r["Fit"] == "FIT")
    print(f"wrote {OUT}")
    print(f"  {len(rows)} line items, {fitted} parts to fit on-board")


if __name__ == "__main__":
    main()

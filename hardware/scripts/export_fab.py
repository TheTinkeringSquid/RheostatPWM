#!/usr/bin/env python3
"""Export fabrication outputs: gerbers, drill files, and the BOM CSV.

    python hardware/scripts/export_fab.py

Run this AFTER the signal nets have been routed in the KiCad GUI. It shells
out to kicad-cli for the gerbers/drill and to gen_bom.py for the BOM. A DRC
gate runs first: if unrouted (ratsnest) or other errors remain, it warns but
still exports so you can inspect intermediate output.
"""

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
KICAD = Path(r"C:/Program Files/KiCad/10.0/bin/kicad-cli.exe")
PCB = SCRIPT_DIR.parent / "kicad" / "b2500_cluster_pwm_dimmer.kicad_pcb"
GERBER_DIR = SCRIPT_DIR.parent / "gerbers"
DRC_RPT = SCRIPT_DIR.parent / "kicad" / "drc.rpt"


def run(args):
    print("›", " ".join(str(a) for a in args))
    return subprocess.run(args, check=False).returncode


def main():
    GERBER_DIR.mkdir(parents=True, exist_ok=True)

    # DRC gate (advisory).
    rc = run([KICAD, "pcb", "drc", "--severity-error", "--exit-code-violations",
              "-o", DRC_RPT, PCB])
    if rc == 5:
        print("WARNING: DRC reports errors (likely unrouted signal nets). "
              "Finish routing in the KiCad GUI before treating gerbers as final.")

    run([KICAD, "pcb", "export", "gerbers", "--no-protel-ext",
         "-o", str(GERBER_DIR) + "/", PCB])
    run([KICAD, "pcb", "export", "drill", "--format", "excellon",
         "--excellon-separate-th", "-o", str(GERBER_DIR) + "/", PCB])

    run([sys.executable, str(SCRIPT_DIR / "gen_bom.py")])
    print("done; gerbers + drill in hardware/gerbers/, BOM in hardware/")


if __name__ == "__main__":
    main()

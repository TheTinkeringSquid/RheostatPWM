#!/usr/bin/env python3
"""Generate b2500_cluster_pwm_dimmer.kicad_sch (KiCad 8 format).

Connectivity is done with global labels at every pin, so the netlist is
explicit and easy to audit against the design brief. Run with any Python 3;
no KiCad modules required.
"""

import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from netlist import COMPONENTS, HARNESS_SINGLE_PIN_NETS  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "kicad" / "b2500_cluster_pwm_dimmer.kicad_sch"
PROJECT = "b2500_cluster_pwm_dimmer"
NS = uuid.UUID("9b1d6a2e-0000-4000-8000-b2500c105a01")
ROOT = str(uuid.uuid5(NS, "root-sheet"))

def uid(key: str) -> str:
    return str(uuid.uuid5(NS, key))

FONT = "(effects (font (size 1.27 1.27)))"

# ---------------------------------------------------------------- symbols
# Pin tuples: (number, name, x, y, angle)  -- lib coords, +y up.
# Angle: 0 pin points right (body right of connection point),
# 180 left, 270 down (conn above body), 90 up (conn below body).

def pins_lr(defs):
    return defs

SYMBOLS = {
    "R": {
        "graphics": "(rectangle (start -1.016 -2.54) (end 1.016 2.54) (stroke (width 0.254) (type default)) (fill (type none)))",
        "pins": [("1", "~", 0, 5.08, 270), ("2", "~", 0, -5.08, 90)],
    },
    "C": {
        "graphics": ("(polyline (pts (xy -2.032 0.762) (xy 2.032 0.762)) (stroke (width 0.508) (type default)) (fill (type none)))"
                      "(polyline (pts (xy -2.032 -0.762) (xy 2.032 -0.762)) (stroke (width 0.508) (type default)) (fill (type none)))"),
        "pins": [("1", "~", 0, 5.08, 270), ("2", "~", 0, -5.08, 90)],
    },
    "CP": {
        "graphics": ("(polyline (pts (xy -2.032 0.762) (xy 2.032 0.762)) (stroke (width 0.508) (type default)) (fill (type none)))"
                      "(polyline (pts (xy -2.032 -0.762) (xy 2.032 -0.762)) (stroke (width 0.508) (type default)) (fill (type none)))"
                      "(polyline (pts (xy -1.778 1.778) (xy -1.016 1.778)) (stroke (width 0.254) (type default)) (fill (type none)))"
                      "(polyline (pts (xy -1.397 2.159) (xy -1.397 1.397)) (stroke (width 0.254) (type default)) (fill (type none)))"),
        "pins": [("1", "+", 0, 5.08, 270), ("2", "-", 0, -5.08, 90)],
    },
    "FUSE": {
        "graphics": ("(rectangle (start -0.762 -2.54) (end 0.762 2.54) (stroke (width 0.254) (type default)) (fill (type none)))"
                      "(polyline (pts (xy 0 2.54) (xy 0 -2.54)) (stroke (width 0.254) (type default)) (fill (type none)))"),
        "pins": [("1", "~", 0, 5.08, 270), ("2", "~", 0, -5.08, 90)],
    },
    "D": {
        "graphics": ("(polyline (pts (xy -1.27 0) (xy 1.27 1.27) (xy 1.27 -1.27) (xy -1.27 0)) (stroke (width 0.254) (type default)) (fill (type none)))"
                      "(polyline (pts (xy -1.27 1.27) (xy -1.27 -1.27)) (stroke (width 0.254) (type default)) (fill (type none)))"),
        "pins": [("1", "K", -5.08, 0, 0), ("2", "A", 5.08, 0, 180)],
    },
    "D_ZENER": {
        "graphics": ("(polyline (pts (xy -1.27 0) (xy 1.27 1.27) (xy 1.27 -1.27) (xy -1.27 0)) (stroke (width 0.254) (type default)) (fill (type none)))"
                      "(polyline (pts (xy -1.905 1.905) (xy -1.27 1.27) (xy -1.27 -1.27) (xy -0.635 -1.905)) (stroke (width 0.254) (type default)) (fill (type none)))"),
        "pins": [("1", "K", -5.08, 0, 0), ("2", "A", 5.08, 0, 180)],
    },
    "D_TVS": {
        "graphics": ("(polyline (pts (xy 0 1.27) (xy 0 -1.27)) (stroke (width 0.254) (type default)) (fill (type none)))"
                      "(polyline (pts (xy -2.54 1.27) (xy 0 0) (xy -2.54 -1.27) (xy -2.54 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))"
                      "(polyline (pts (xy 2.54 1.27) (xy 0 0) (xy 2.54 -1.27) (xy 2.54 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))"),
        "pins": [("1", "~", -5.08, 0, 0), ("2", "~", 5.08, 0, 180)],
    },
    "BAT54S": {
        "graphics": "(rectangle (start -3.81 -3.81) (end 3.81 2.54) (stroke (width 0.254) (type default)) (fill (type none)))",
        "pins": [("1", "A_GND", -5.08, 0, 0), ("2", "K_3V3", 5.08, 0, 180), ("3", "COM", 0, -5.08, 90)],
    },
    "Q_NMOS": {  # 2N7000 TO-92: pad 1=S, 2=G, 3=D
        "graphics": "(circle (center 0.635 0) (radius 2.794) (stroke (width 0.254) (type default)) (fill (type none)))",
        "pins": [("2", "G", -5.08, 0, 0), ("3", "D", 2.54, 5.08, 270), ("1", "S", 2.54, -5.08, 90)],
    },
    "Q_PMOS": {  # FQP27P06 TO-220: pad 1=G, 2=D, 3=S
        "graphics": "(circle (center 0.635 0) (radius 2.794) (stroke (width 0.254) (type default)) (fill (type none)))",
        "pins": [("1", "G", -5.08, 0, 0), ("3", "S", 2.54, 5.08, 270), ("2", "D", 2.54, -5.08, 90)],
    },
    "CONN_01X05": {
        "graphics": "(rectangle (start -2.54 -7.62) (end 2.54 7.62) (stroke (width 0.254) (type default)) (fill (type none)))",
        "pins": [("1", "VIN_RAW", 5.08, 5.08, 180), ("2", "GND", 5.08, 2.54, 180),
                 ("3", "DIM_IN", 5.08, 0, 180), ("4", "PWM_OUT", 5.08, -2.54, 180),
                 ("5", "IGN_SENSE", 5.08, -5.08, 180)],
    },
    "HDR_1X02": {
        "graphics": "(rectangle (start -2.54 -5.08) (end 2.54 5.08) (stroke (width 0.254) (type default)) (fill (type none)))",
        "pins": [("1", "~", 5.08, 2.54, 180), ("2", "~", 5.08, -2.54, 180)],
    },
    "SW_PUSH": {
        "graphics": ("(polyline (pts (xy -2.54 1.27) (xy 2.54 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))"
                      "(circle (center -2.54 0) (radius 0.508) (stroke (width 0.254) (type default)) (fill (type none)))"
                      "(circle (center 2.54 0) (radius 0.508) (stroke (width 0.254) (type default)) (fill (type none)))"),
        "pins": [("1", "~", -5.08, 0, 0), ("2", "~", 5.08, 0, 180)],
    },
    "TP": {
        "graphics": "(circle (center 0 0) (radius 0.762) (stroke (width 0.254) (type default)) (fill (type none)))",
        "pins": [("1", "~", 0, -2.54, 90)],
    },
    "XIAO_RP2040": {
        "graphics": "(rectangle (start -12.7 -10.16) (end 12.7 10.16) (stroke (width 0.254) (type default)) (fill (type background)))",
        "pins": [
            ("1", "D0/A0", -15.24, 7.62, 0), ("2", "D1/A1", -15.24, 5.08, 0),
            ("3", "D2/A2", -15.24, 2.54, 0), ("4", "D3/A3", -15.24, 0, 0),
            ("5", "D4/SDA", -15.24, -2.54, 0), ("6", "D5/SCL", -15.24, -5.08, 0),
            ("7", "D6/TX", -15.24, -7.62, 0),
            ("8", "D7/RX", 15.24, -7.62, 180), ("9", "D8/SCK", 15.24, -5.08, 180),
            ("10", "D9/MISO", 15.24, -2.54, 180), ("11", "D10/MOSI", 15.24, 0, 180),
            ("12", "3V3", 15.24, 2.54, 180), ("13", "GND", 15.24, 5.08, 180),
            ("14", "5V", 15.24, 7.62, 180),
        ],
    },
    "BUCK_D36V28F5": {
        # Off-board Pololu module, wired to a 3-pin header (VIN/GND/VOUT).
        "graphics": "(rectangle (start -7.62 -5.08) (end 7.62 5.08) (stroke (width 0.254) (type default)) (fill (type background)))",
        "pins": [("1", "VIN", -10.16, 2.54, 0), ("2", "GND", -10.16, -2.54, 0),
                 ("3", "VOUT", 10.16, 2.54, 180)],
    },
}

# ------------------------------------------------------------- components
# COMPONENTS is imported from netlist.py (single source of truth).
# Each entry: (ref, symbol, value, footprint, dnp, on_board, {pad: net}, sch_xy)

NOTES = [
    (40, 30, "Power input: fused 12V lights feed -> reverse protection -> TVS -> bulk caps -> buck + high-side switch"),
    (40, 90, "DIM sense: factory rheostat output, high-impedance divider 100k/22k, RC filter, BAT54S clamp"),
    (40, 150, "MCU: Seeed XIAO RP2040.  JP1 open = vehicle 5V disconnected for safe USB programming"),
    (40, 210, "High-side PWM: D1(MCU) -> R8 -> Q2 2N7000 -> R7 -> Q1 FQP27P06 P-MOSFET. R6/D5 protect gate. R10/C5 = DNP snubber"),
    (40, 268, "F1 is an INLINE mini-blade fuse in the vehicle harness at the feed tap, not board-mounted: it must protect the wire run to the board."),
]


def stub_and_label(net, cx, cy, angle):
    """Wire stub 2.54mm outward from pin conn point + global label at the end."""
    if angle == 0:      # body right -> stub left
        ex, ey, la = cx - 2.54, cy, 180
    elif angle == 180:  # body left -> stub right
        ex, ey, la = cx + 2.54, cy, 0
    elif angle == 270:  # body below -> stub up
        ex, ey, la = cx, cy - 2.54, 90
    else:               # 90: body above -> stub down
        ex, ey, la = cx, cy + 2.54, 270
    w = (f'  (wire (pts (xy {cx:g} {cy:g}) (xy {ex:g} {ey:g})) (stroke (width 0) (type default)) '
         f'(uuid "{uid(f"w-{net}-{cx}-{cy}")}"))\n')
    g = (f'  (global_label "{net}" (shape passive) (at {ex:g} {ey:g} {la}) (fields_autoplaced yes) '
         f'(effects (font (size 1.27 1.27)) (justify {"right" if la == 180 else "left"})) '
         f'(uuid "{uid(f"gl-{net}-{ex}-{ey}")}") '
         f'(property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {ex:g} {ey:g} 0) '
         f'(effects (font (size 1.27 1.27)) hide)))\n')
    return w + g


def lib_symbol(name, spec):
    s = f'    (symbol "b2500:{name}" (exclude_from_sim no) (in_bom yes) (on_board yes)\n'
    s += f'      (property "Reference" "U" (at 0 7.62 0) {FONT})\n'
    s += f'      (property "Value" "{name}" (at 0 -7.62 0) {FONT})\n'
    s += f'      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))\n'
    s += f'      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))\n'
    s += f'      (property "Description" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))\n'
    s += f'      (symbol "{name}_0_1"\n        {spec["graphics"]}\n      )\n'
    s += f'      (symbol "{name}_1_1"\n'
    for num, pname, px, py, ang in spec["pins"]:
        s += (f'        (pin passive line (at {px:g} {py:g} {ang}) (length 2.54) '
              f'(name "{pname}" {FONT}) (number "{num}" {FONT}))\n')
    s += '      )\n    )\n'
    return s


def snap(v):
    """Snap to the 2.54mm schematic connection grid."""
    return round(v / 2.54) * 2.54


def instance(ref, sym, value, footprint, dnp, on_board, pinnets, pos):
    x, y = snap(pos[0]), snap(pos[1])
    spec = SYMBOLS[sym]
    s = f'  (symbol (lib_id "b2500:{sym}") (at {x:g} {y:g} 0) (unit 1)\n'
    s += f'    (exclude_from_sim no) (in_bom yes) (on_board {"yes" if on_board else "no"}) (dnp {"yes" if dnp else "no"})\n'
    s += f'    (uuid "{uid(f"sym-{ref}")}")\n'
    s += f'    (property "Reference" "{ref}" (at {x:g} {y - 14:g} 0) {FONT})\n'
    s += f'    (property "Value" "{value}" (at {x:g} {y + 14:g} 0) {FONT})\n'
    s += (f'    (property "Footprint" "{footprint}" (at {x:g} {y:g} 0) '
          f'(effects (font (size 1.27 1.27)) hide))\n')
    s += (f'    (property "Datasheet" "" (at {x:g} {y:g} 0) '
          f'(effects (font (size 1.27 1.27)) hide))\n')
    s += (f'    (property "Description" "" (at {x:g} {y:g} 0) '
          f'(effects (font (size 1.27 1.27)) hide))\n')
    for num, _, _, _, _ in spec["pins"]:
        s += f'    (pin "{num}" (uuid "{uid(f"pin-{ref}-{num}")}"))\n'
    s += (f'    (instances (project "{PROJECT}" (path "/{ROOT}" '
          f'(reference "{ref}") (unit 1))))\n  )\n')

    extra = ""
    for num, _, px, py, ang in spec["pins"]:
        cx, cy = x + px, y - py   # schematic sheet Y axis is inverted
        net = pinnets.get(num)
        if net is None:
            extra += f'  (no_connect (at {cx:g} {cy:g}) (uuid "{uid(f"nc-{ref}-{num}")}"))\n'
        else:
            extra += stub_and_label(net, cx, cy, ang)
    return s + extra


def check_nets():
    """Every net must land on at least two pins, except documented harness-side nets."""
    counts = {}
    for ref, sym, _, _, _, _, pinnets, _ in COMPONENTS:
        for net in pinnets.values():
            if net is not None:
                counts[net] = counts.get(net, 0) + 1
    bad = [n for n, c in counts.items() if c < 2 and n not in HARNESS_SINGLE_PIN_NETS]
    if bad:
        raise SystemExit(f"net(s) with a single pin (probable typo): {bad}")


def main():
    check_nets()
    out = []
    out.append('(kicad_sch\n  (version 20231120)\n  (generator "eeschema")\n  (generator_version "8.0")\n')
    out.append(f'  (uuid "{ROOT}")\n  (paper "A2")\n')
    out.append('  (title_block\n    (title "Dodge B2500 Instrument Cluster LED PWM Dimmer")\n'
               '    (date "2026-06-11")\n    (rev "A")\n'
               '    (comment 1 "Cluster illumination only - NOT for safety-critical circuits")\n'
               '    (comment 2 "Reads factory rheostat as analog sense, drives cluster LEDs with high-side 12V PWM")\n  )\n')
    out.append('  (lib_symbols\n')
    for name, spec in SYMBOLS.items():
        out.append(lib_symbol(name, spec))
    out.append('  )\n')

    for ref, sym, value, fp, dnp, ob, pinnets, pos in COMPONENTS:
        out.append(instance(ref, sym, value, fp, dnp, ob, pinnets, pos))

    for tx, ty, msg in NOTES:
        out.append(f'  (text "{msg}" (exclude_from_sim no) (at {tx:g} {ty:g} 0) '
                   f'{FONT} (uuid "{uid(f"txt-{tx}-{ty}")}"))\n')

    out.append(f'  (sheet_instances (path "/" (page "1")))\n')
    out.append(')\n')

    OUT.write_text("".join(out), encoding="utf-8", newline="\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate b2500_cluster_pwm_dimmer.kicad_sch (KiCad 8 format).

Connectivity is done with global labels at every pin, so the netlist is
explicit and easy to audit against the design brief. Run with any Python 3;
no KiCad modules required.
"""

import uuid
from pathlib import Path

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
        "graphics": "(rectangle (start -7.62 -5.08) (end 7.62 5.08) (stroke (width 0.254) (type default)) (fill (type background)))",
        "pins": [("1", "EN", -10.16, -2.54, 0), ("2", "VIN", -10.16, 2.54, 0),
                 ("3", "GND", 10.16, -2.54, 180), ("4", "VOUT", 10.16, 2.54, 180)],
    },
}

# ------------------------------------------------------------- components
FP_R = "Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder"
FP_C = "Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder"
FP_TP = "TestPoint:TestPoint_THTPad_D1.5mm_Drill0.7mm"

# ref: (symbol, value, footprint, dnp, on_board, {pin: net}), position (x, y)
COMPONENTS = [
    ("F1",  "FUSE", "2A mini blade, INLINE IN HARNESS", "", False, False,
     {"1": "12V_LIGHTS_FEED", "2": "VIN_RAW"}, (40, 50)),
    ("D1",  "D", "1N5822", "Diode_THT:D_DO-201AD_P15.24mm_Horizontal", False, True,
     {"1": "VIN_PROT", "2": "VIN_RAW"}, (75, 50)),
    ("D2",  "D_TVS", "P6KE24CA", "Diode_THT:D_DO-15_P10.16mm_Horizontal", False, True,
     {"1": "VIN_PROT", "2": "GND"}, (110, 50)),
    ("C1",  "CP", "47uF 50V", "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm", False, True,
     {"1": "VIN_PROT", "2": "GND"}, (140, 50)),
    ("C2",  "C", "100nF 50V", FP_C, False, True,
     {"1": "VIN_PROT", "2": "GND"}, (165, 50)),
    ("U2",  "BUCK_D36V28F5", "Pololu D36V28F5", "b2500:Pololu_D36V28F5", False, True,
     {"1": None, "2": "VIN_PROT", "3": "GND", "4": "5V_BUCK"}, (210, 50)),
    ("JP1", "HDR_1X02", "5V_LINK", "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical", False, True,
     {"1": "5V_BUCK", "2": "5V_JMP"}, (250, 50)),
    ("D3",  "D", "1N5819", "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal", False, True,
     {"1": "5V_XIAO", "2": "5V_JMP"}, (280, 50)),
    ("C4",  "C", "10uF", FP_C, False, True,
     {"1": "5V_XIAO", "2": "GND"}, (305, 50)),

    ("J1",  "CONN_01X05", "Phoenix MKDS-1,5-5-5.08", "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-5-5.08_1x05_P5.08mm_Horizontal", False, True,
     {"1": "VIN_RAW", "2": "GND", "3": "DIM_IN", "4": "PWM_OUT", "5": "IGN_SENSE_RAW"}, (40, 110)),
    ("R3",  "R", "100k 1%", FP_R, False, True, {"1": "DIM_IN", "2": "DIM_DIV"}, (75, 110)),
    ("R4",  "R", "22k 1%", FP_R, False, True, {"1": "DIM_DIV", "2": "GND"}, (100, 110)),
    ("C3",  "C", "100nF", FP_C, False, True, {"1": "DIM_DIV", "2": "GND"}, (125, 110)),
    ("R5",  "R", "1k", FP_R, False, True, {"1": "DIM_DIV", "2": "DIM_ADC"}, (150, 110)),
    ("D4",  "BAT54S", "BAT54S", "Package_TO_SOT_SMD:SOT-23", False, True,
     {"1": "GND", "2": "3V3", "3": "DIM_ADC"}, (180, 110)),
    ("R1",  "R", "100k (DNP)", FP_R, True, True, {"1": "IGN_SENSE_RAW", "2": "IGN_DIV"}, (210, 110)),
    ("R2",  "R", "22k (DNP)", FP_R, True, True, {"1": "IGN_DIV", "2": "GND"}, (235, 110)),
    ("TP4", "TP", "TP_DIM_ADC", FP_TP, False, True, {"1": "DIM_ADC"}, (260, 110)),

    ("U1",  "XIAO_RP2040", "XIAO RP2040", "b2500:XIAO_RP2040_THT", False, True,
     {"1": "DIM_ADC", "2": "PWM_GATE", "3": "CAL_BTN", "4": "IGN_DIV",
      "5": None, "6": None, "7": None, "8": None, "9": None, "10": None, "11": None,
      "12": "3V3", "13": "GND", "14": "5V_XIAO"}, (75, 170)),
    ("R8",  "R", "100R", FP_R, False, True, {"1": "PWM_GATE", "2": "Q2_G"}, (125, 170)),
    ("R9",  "R", "100k", FP_R, False, True, {"1": "Q2_G", "2": "GND"}, (150, 170)),
    ("SW1", "SW_PUSH", "CAL", "Button_Switch_THT:SW_PUSH_6mm", False, True,
     {"1": "CAL_BTN", "2": "GND"}, (180, 170)),
    ("TP5", "TP", "TP_PWM_GATE", FP_TP, False, True, {"1": "PWM_GATE"}, (210, 170)),
    ("TP3", "TP", "TP_3V3", FP_TP, False, True, {"1": "3V3"}, (235, 170)),
    ("TP2", "TP", "TP_5V", FP_TP, False, True, {"1": "5V_XIAO"}, (260, 170)),

    ("Q2",  "Q_NMOS", "2N7000", "Package_TO_SOT_THT:TO-92_Inline", False, True,
     {"2": "Q2_G", "3": "Q2_D", "1": "GND"}, (75, 230)),
    ("R7",  "R", "100R", FP_R, False, True, {"1": "Q2_D", "2": "Q1_G"}, (105, 230)),
    ("R6",  "R", "10k", FP_R, False, True, {"1": "VIN_PROT", "2": "Q1_G"}, (130, 230)),
    ("D5",  "D_ZENER", "1N5242B 12V", "Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal", False, True,
     {"1": "VIN_PROT", "2": "Q1_G"}, (160, 230)),
    ("Q1",  "Q_PMOS", "FQP27P06", "Package_TO_SOT_THT:TO-220-3_Vertical", False, True,
     {"1": "Q1_G", "3": "VIN_PROT", "2": "PWM_OUT"}, (190, 230)),
    ("R10", "R", "100R (DNP)", FP_R, True, True, {"1": "PWM_OUT", "2": "SNUB"}, (220, 230)),
    ("C5",  "C", "10nF 100V (DNP)", FP_C, True, True, {"1": "SNUB", "2": "GND"}, (245, 230)),
    ("TP6", "TP", "TP_PWM_OUT", FP_TP, False, True, {"1": "PWM_OUT"}, (275, 230)),
    ("TP1", "TP", "TP_VIN", FP_TP, False, True, {"1": "VIN_PROT"}, (300, 230)),
    ("TP7", "TP", "TP_GND", FP_TP, False, True, {"1": "GND"}, (325, 230)),
]

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
    allowed_single = {"12V_LIGHTS_FEED"}
    bad = [n for n, c in counts.items() if c < 2 and n not in allowed_single]
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

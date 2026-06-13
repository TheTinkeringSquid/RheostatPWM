#!/usr/bin/env python3
"""Generate b2500_cluster_pwm_dimmer.kicad_pcb with the KiCad pcbnew API.

Run with KiCad's bundled Python, e.g.

    & "C:/Program Files/KiCad/10.0/bin/python.exe" hardware/scripts/gen_pcb.py

Flow:
  1. Load + place every on-board footprint from the shared netlist.
  2. Create nets and bind them to pads.
  3. Draw the board edge, mounting holes, silkscreen and ground pours.
  4. Auto-route the non-ground nets (GND is handled by the pours), then fill.

The router is a deliberately simple Manhattan/MST router. The high-current
loop (VIN_PROT -> Q1 -> PWM_OUT) is placed compactly near the connector so it
routes as short, wide copper; the DIM sense network is kept on the far side of
the board from the MOSFET switching node, as the brief requires.
"""

import os
import sys
from pathlib import Path

import pcbnew

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from netlist import COMPONENTS, power_nets  # noqa: E402

KICAD_FP = Path(r"C:/Program Files/KiCad/10.0/share/kicad/footprints")
PROJ_FP_PREFIX = "b2500"
PROJ_FP_DIR = SCRIPT_DIR.parent / "kicad" / "symbols_and_footprints" / "b2500.pretty"
OUT = SCRIPT_DIR.parent / "kicad" / "b2500_cluster_pwm_dimmer.kicad_pcb"

BOARD_W = 94.0
BOARD_H = 62.0
POWER_NETS = power_nets()

W_SIGNAL = 0.4
W_POWER = 1.5

# Only the two high-current nets that terminate at the connector (VIN_RAW and
# PWM_OUT) are pre-routed, with hand-authored waypoints. Every other net is
# left as ratsnest for interactive routing in the KiCad GUI.

# ref -> (x_mm, y_mm, rotation_deg). Floorplan, origin top-left, y down.
# Coordinates were fitted against the real footprint courtyards (see
# _diag_overlaps.py) so the board is courtyard- and edge-clean.
PLACE = {
    # connector at the left edge, terminals facing off-board (left)
    "J1": (12, 30, 90),
    # input protection across the top, left -> right
    "D1": (38, 9, 180),
    "D2": (46, 13, 90),
    "C1": (54, 10, 90),
    "C2": (61, 9, 0),
    "U2": (75, 14, 0),
    # 5 V path on the right
    "JP1": (87, 27, 90),
    "D3": (87, 42, 90),
    "C4": (81, 33, 90),
    # DIM sense divider, mid-board corridor, away from the MOSFET node
    "R3": (26, 28, 0),
    "R4": (33, 24, 90),
    "C3": (38, 24, 90),
    "R5": (45, 28, 0),
    "D4": (51, 30, 0),
    "TP4": (51, 23, 0),
    # MCU
    "U1": (68, 42, 0),
    # optional cal button, open gap above the MCU
    "SW1": (57, 18, 0),
    # gate drive, clustered near the MCU PWM pin; Q1_G runs down-left to Q1
    "R8": (55, 46, 0),
    "R9": (55, 50, 90),
    "Q2": (46, 47, 0),
    "R7": (40, 47, 0),
    "R6": (33, 47, 90),
    "D5": (36, 51, 90),
    # IGN divider (DNP) near the connector IGN pin
    "R1": (24, 42, 0),
    "R2": (30, 42, 90),
    # high-side MOSFET, bottom-left, next to J1 PWM_OUT/VIN
    "Q1": (26, 53, 0),
    "R10": (34, 58, 0),
    "C5": (42, 58, 0),
    # test points: TP_PWM_OUT by the output, the rest along the bottom edge
    "TP6": (16, 53, 0),
    "TP1": (46, 58, 0),
    "TP7": (55, 58, 0),
    "TP5": (64, 58, 0),
    "TP3": (73, 58, 0),
    "TP2": (82, 58, 0),
}

# (x_mm, y_mm, text, rotation, size_mm). Per-pin labels sit just right of each
# J1 pad (J1 at y=30, 5.08 mm pitch: pin1=y30 ... pin5=y9.68).
SILK = [
    (20, 9.68, "IGN (opt)", 0, 0.8),
    (20, 14.76, "PWM OUT->CLUSTER", 0, 0.8),
    (20, 19.84, "DIM SENSE", 0, 0.8),
    (20, 24.92, "GND", 0, 0.8),
    (20, 30.0, "VIN 12V LIGHTS", 0, 0.8),
    (47, 3, "Dodge B2500 Cluster LED PWM Dimmer  Rev A", 0, 1.0),
    (56, 28, "USB: DISCONNECT VEHICLE POWER FIRST", 0, 0.8),
    (47, 61, "CLUSTER ILLUMINATION ONLY - NOT SAFETY CRITICAL", 0, 1.0),
]

# Ground-stitch vias in open areas (clear of all footprint courtyards).
STITCH_VIAS = [(45, 38), (33, 34), (66, 28), (12, 48)]


def fp_path(libid):
    lib, name = libid.split(":", 1)
    if lib == PROJ_FP_PREFIX:
        return str(PROJ_FP_DIR), name
    return str(KICAD_FP / f"{lib}.pretty"), name


def vec(x, y):
    return pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))


def main():
    if OUT.exists():
        os.remove(OUT)
    board = pcbnew.NewBoard(str(OUT))
    board.SetCopperLayerCount(2)

    # ---- nets ---------------------------------------------------------
    netmap = {}

    def get_net(name):
        if name not in netmap:
            n = pcbnew.NETINFO_ITEM(board, name)
            board.Add(n)
            netmap[name] = n
        return netmap[name]

    get_net("GND")

    # ---- footprints + pad nets ---------------------------------------
    placed = {}
    pad_nets = {}  # net name -> list[(x_nm, y_nm)]
    padpos = {}    # (ref, padnumber) -> (x_nm, y_nm)
    for ref, sym, value, footprint, dnp, on_board, pinnets, _ in COMPONENTS:
        if not on_board:
            continue
        if ref not in PLACE:
            raise SystemExit(f"no placement for {ref}")
        libdir, name = fp_path(footprint)
        fp = pcbnew.FootprintLoad(libdir, name)
        if fp is None:
            raise SystemExit(f"failed to load footprint {footprint}")
        x, y, rot = PLACE[ref]
        fp.SetPosition(vec(x, y))
        fp.SetReference(ref)
        fp.SetValue(value)
        fp.SetOrientationDegrees(rot)
        if dnp:
            try:
                fp.SetDNP(True)
            except Exception:
                pass
        board.Add(fp)
        placed[ref] = fp

        for pad in fp.Pads():
            num = pad.GetNumber()
            p = pad.GetPosition()
            padpos[(ref, num)] = (p.x, p.y)
            net = pinnets.get(num)
            if net is None:
                continue
            pad.SetNet(get_net(net))
            pad_nets.setdefault(net, []).append((p.x, p.y))

    # ---- board outline ------------------------------------------------
    for a, b in [((0, 0), (BOARD_W, 0)), ((BOARD_W, 0), (BOARD_W, BOARD_H)),
                 ((BOARD_W, BOARD_H), (0, BOARD_H)), ((0, BOARD_H), (0, 0))]:
        seg = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_SEGMENT)
        seg.SetStart(vec(*a))
        seg.SetEnd(vec(*b))
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetWidth(pcbnew.FromMM(0.15))
        board.Add(seg)

    # ---- mounting holes ----------------------------------------------
    # Two M3 holes per the BOM (M1-M2), placed diagonally. The terminal block
    # fills the left edge, so the second hole goes bottom-left, not top-left.
    mh_dir = str(KICAD_FP / "MountingHole.pretty")
    for mx, my in [(BOARD_W - 5, 8), (6, BOARD_H - 6)]:
        mh = pcbnew.FootprintLoad(mh_dir, "MountingHole_3.2mm_M3_Pad")
        mh.SetPosition(vec(mx, my))
        for pad in mh.Pads():
            pad.SetNet(netmap["GND"])
        board.Add(mh)

    # ---- silkscreen ---------------------------------------------------
    for sx, sy, text, rot, size in SILK:
        t = pcbnew.PCB_TEXT(board)
        t.SetText(text)
        t.SetLayer(pcbnew.F_SilkS)
        t.SetPosition(vec(sx, sy))
        t.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(size), pcbnew.FromMM(size)))
        t.SetTextThickness(pcbnew.FromMM(0.15))
        t.SetHorizJustify(pcbnew.GR_TEXT_H_ALIGN_LEFT)
        if rot:
            t.SetTextAngleDegrees(rot)
        board.Add(t)

    # ---- ground pours on both layers ---------------------------------
    gnd = netmap["GND"]
    inset = 0.6
    corners = [(inset, inset), (BOARD_W - inset, inset),
               (BOARD_W - inset, BOARD_H - inset), (inset, BOARD_H - inset)]
    for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
        zone = pcbnew.ZONE(board)
        zone.SetLayer(layer)
        zone.SetNetCode(gnd.GetNetCode())
        zone.SetAssignedPriority(0)
        zone.SetMinThickness(pcbnew.FromMM(0.25))
        zone.SetLocalClearance(pcbnew.FromMM(0.3))
        zone.SetIsFilled(False)
        outline = zone.Outline()
        outline.NewOutline()
        for cx, cy in corners:
            outline.Append(pcbnew.FromMM(cx), pcbnew.FromMM(cy))
        board.Add(zone)

    # ---- pre-route the two high-current connector nets ---------------
    # Hand-authored waypoint paths (mm) that approach the connector and Q1
    # perpendicular to their pad rows, so no foreign pad is crossed. The
    # VIN_PROT bus into the Q1 source is left as ratsnest for the GUI, where
    # it should be drawn as a short wide pour-fed trace.
    board.BuildConnectivity()
    w_pwr = pcbnew.FromMM(W_POWER)

    def P(ref, num):
        return tuple(pcbnew.ToMM(c) for c in padpos[(ref, num)])

    j1_1 = P("J1", "1")          # VIN_RAW
    d1_2 = P("D1", "2")          # VIN_RAW
    j1_4 = P("J1", "4")          # PWM_OUT
    q1_2 = P("Q1", "2")          # PWM_OUT (drain)
    tp6 = P("TP6", "1")          # PWM_OUT test point
    r10_1 = P("R10", "1")        # PWM_OUT (snubber tap)

    # VIN_RAW: both pads are through-hole, so route it on the back copper to
    # pass cleanly under the PWM_OUT spine without a crossing or vias.
    route_path(board, netmap["VIN_RAW"], w_pwr, [
        j1_1, (d1_2[0], j1_1[1]), d1_2,
    ], layer=pcbnew.B_Cu)

    # PWM_OUT: a spine that runs clear of the J1 pad column (x=19) and below
    # the Q1 pad row (y=spine_y), with short perpendicular taps to each pad.
    spine_x = 19.0
    spine_y = q1_2[1] + 4.0
    route_path(board, netmap["PWM_OUT"], w_pwr, [
        j1_4, (spine_x, j1_4[1]), (spine_x, spine_y), (r10_1[0], spine_y), r10_1,
    ])
    route_path(board, netmap["PWM_OUT"], w_pwr, [q1_2, (q1_2[0], spine_y)])   # drop to Q1 drain
    route_path(board, netmap["PWM_OUT"], w_pwr, [tp6, (spine_x, tp6[1])])     # tap test point

    # ---- ground stitching vias (open areas only) ---------------------
    for sx, sy in STITCH_VIAS:
        add_via(board, gnd, pcbnew.FromMM(sx), pcbnew.FromMM(sy))

    # ---- fill ---------------------------------------------------------
    board.BuildConnectivity()
    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())

    board.Save(str(OUT))
    print(f"wrote {OUT}")
    print(f"  footprints placed: {len(placed)}")
    print(f"  nets: {len(netmap)}")


def add_track(board, net, a, b, width, layer=pcbnew.F_Cu):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pcbnew.VECTOR2I(a[0], a[1]))
    t.SetEnd(pcbnew.VECTOR2I(b[0], b[1]))
    t.SetWidth(width)
    t.SetLayer(layer)
    t.SetNet(net)
    board.Add(t)


def add_via(board, net, x, y):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I(x, y))
    v.SetDrill(pcbnew.FromMM(0.4))
    v.SetWidth(pcbnew.FromMM(0.8))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetNet(net)
    board.Add(v)


def route_path(board, net, width, mm_pts, layer=pcbnew.F_Cu):
    """Lay a polyline of tracks through the given (x_mm, y_mm) waypoints."""
    for i in range(len(mm_pts) - 1):
        a = pcbnew.VECTOR2I(pcbnew.FromMM(mm_pts[i][0]), pcbnew.FromMM(mm_pts[i][1]))
        b = pcbnew.VECTOR2I(pcbnew.FromMM(mm_pts[i + 1][0]), pcbnew.FromMM(mm_pts[i + 1][1]))
        add_track(board, net, (a.x, a.y), (b.x, b.y), width, layer)


if __name__ == "__main__":
    main()

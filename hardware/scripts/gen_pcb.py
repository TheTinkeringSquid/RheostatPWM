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

import math
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

# Remaining nets, auto-routed by the collision-aware MST router. VIN_RAW,
# PWM_OUT and the VIN_PROT trunk are routed explicitly before these (their
# tracks become obstacles the autorouter avoids). GND is handled by the pours.
SIGNAL_ROUTES = [
    ("5V_BUCK", [("U2", "4"), ("JP1", "1")]),
    ("5V_JMP",  [("JP1", "2"), ("D3", "2")]),
    ("5V_XIAO", [("D3", "1"), ("C4", "1"), ("U1", "14"), ("TP2", "1")]),
    ("3V3",     [("U1", "12"), ("D4", "2"), ("TP3", "1")]),
    ("DIM_IN",  [("J1", "3"), ("R3", "1")]),
    ("DIM_DIV", [("R3", "2"), ("R4", "1"), ("C3", "1"), ("R5", "1")]),
    ("DIM_ADC", [("R5", "2"), ("D4", "3"), ("TP4", "1"), ("U1", "1")]),
    ("IGN_SENSE_RAW", [("J1", "5"), ("R1", "1")]),
    ("IGN_DIV", [("R1", "2"), ("R2", "1"), ("U1", "4")]),
    ("PWM_GATE", [("U1", "2"), ("R8", "1"), ("TP5", "1")]),
    ("Q2_G",    [("R8", "2"), ("R9", "1"), ("Q2", "2")]),
    ("Q2_D",    [("Q2", "3"), ("R7", "1")]),
    ("Q1_G",    [("Q1", "1"), ("R6", "2"), ("D5", "2"), ("R7", "2")]),
    ("SNUB",    [("R10", "2"), ("C5", "1")]),
    ("CAL_BTN", [("SW1", "1"), ("U1", "3")]),
]


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
    pad_smd = {}   # (ref, padnumber) -> bool
    pad_meta = []  # obstacle list: dict(x, y, r, smd, net) in nm
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
            sz = pad.GetSize()
            smd = pad.GetAttribute() == pcbnew.PAD_ATTRIB_SMD
            pad_smd[(ref, num)] = smd
            net = pinnets.get(num)
            netname = net if net is not None else f"__nc_{ref}_{num}"
            pad_meta.append({"ref": ref, "num": num, "x": p.x, "y": p.y,
                             "r": max(sz.x, sz.y) // 2, "smd": smd, "net": netname})
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

    # ---- routing ------------------------------------------------------
    board.BuildConnectivity()
    router = Router(board, pad_meta, netmap, padpos, pad_smd)

    # Ground stitching vias first, so the signal router treats them as
    # obstacles to clear.
    for sx, sy in STITCH_VIAS:
        router.add_via("GND", (pcbnew.FromMM(sx), pcbnew.FromMM(sy)))

    def P(ref, num):
        return padpos[(ref, num)]   # (x_nm, y_nm)

    NM = pcbnew.FromMM

    # -- high-current connector nets: hand-authored, approached perpendicular
    #    to each pad row so no neighbouring pad is crossed.
    j1_1, d1_2 = P("J1", "1"), P("D1", "2")
    router.path("VIN_RAW", W_POWER,
                [j1_1, (d1_2[0], j1_1[1]), d1_2], layer=pcbnew.B_Cu)

    q1_2, j1_4, r10_1, tp6 = P("Q1", "2"), P("J1", "4"), P("R10", "1"), P("TP6", "1")
    spine_x, spine_y = NM(19.0), q1_2[1] + NM(4.0)
    router.path("PWM_OUT", W_POWER,
                [j1_4, (spine_x, j1_4[1]), (spine_x, spine_y), (r10_1[0], spine_y), r10_1])
    router.path("PWM_OUT", W_POWER, [q1_2, (q1_2[0], spine_y)])
    router.path("PWM_OUT", W_POWER, [tp6, (spine_x, tp6[1])])

    # -- VIN_PROT: the high-current bus. Routed wide (W_POWER); the long edge
    #    from the top input cluster down to the Q1 source is maze-routed
    #    around the dense middle of the board.
    if not router.net("VIN_PROT", W_POWER,
                      [("D1", "1"), ("D2", "1"), ("C1", "1"), ("C2", "1"),
                       ("U2", "2"), ("Q1", "3"), ("D5", "1"), ("R6", "1"),
                       ("TP1", "1")]):
        print("  WARN: net VIN_PROT not fully routed")

    # -- bond duplicate same-net pads of a single footprint (e.g. the two
    #    legs of the tactile switch share pad number "1"): KiCad wants copper
    #    between them, and they sit close on a clear row.
    bonded = {}
    for p in pad_meta:
        bonded.setdefault((p["ref"], p["num"], p["net"]), []).append((p["x"], p["y"]))
    for (ref, _num, net), pts in bonded.items():
        if net in netmap and len(pts) > 1:
            pts.sort()
            for i in range(len(pts) - 1):
                router.path(net, W_SIGNAL, [pts[i], pts[i + 1]])

    # -- everything else: collision-aware MST autoroute.
    for net, refs in SIGNAL_ROUTES:
        w = W_POWER if net in POWER_NETS else W_SIGNAL
        if not router.net(net, w, refs):
            print(f"  WARN: net {net} not fully routed")

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


# ----------------------------------------------------------- geometry
def _pt_seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / float(dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def _ccw(a, b, c):
    return (c[1] - a[1]) * (b[0] - a[0]) - (b[1] - a[1]) * (c[0] - a[0])


def _seg_seg_dist(a1, a2, b1, b2):
    if (_ccw(a1, b1, b2) > 0) != (_ccw(a2, b1, b2) > 0) and \
       (_ccw(a1, a2, b1) > 0) != (_ccw(a1, a2, b2) > 0):
        return 0.0
    return min(
        _pt_seg_dist(a1[0], a1[1], b1[0], b1[1], b2[0], b2[1]),
        _pt_seg_dist(a2[0], a2[1], b1[0], b1[1], b2[0], b2[1]),
        _pt_seg_dist(b1[0], b1[1], a1[0], a1[1], a2[0], a2[1]),
        _pt_seg_dist(b2[0], b2[1], a1[0], a1[1], a2[0], a2[1]),
    )


# ----------------------------------------------------------- router
CLR_NM = pcbnew.FromMM(0.30)         # keep-out margin (>= board DRC clearances)
VIA_R_NM = pcbnew.FromMM(0.8) // 2   # via radius
GRID_NM = pcbnew.FromMM(0.5)         # maze-router grid pitch


class Router:
    """Collision-aware Manhattan/MST router for 2-layer boards with a GND
    pour on both copper layers. Each connection is an L-shape; the router
    tries both orientations and both layers and drops a via at the corner
    when the two legs differ, rejecting any candidate that comes within
    CLR_NM of a foreign pad, track, or via. SMD pads are F.Cu only."""

    def __init__(self, board, pad_meta, netmap, padpos, pad_smd):
        self.board = board
        self.pads = pad_meta
        self.netmap = netmap
        self.padpos = padpos
        self.pad_smd = pad_smd
        self.tracks = []
        self.vias = []

    # -- primitive emit + register --------------------------------------
    def _track(self, net, a, b, w, layer):
        add_track(self.board, self.netmap[net], a, b, w, layer)
        self.tracks.append({"a": a, "b": b, "layer": layer, "hw": w // 2, "net": net})

    def add_via(self, net, p):
        add_via(self.board, self.netmap[net], p[0], p[1])
        self.vias.append({"x": p[0], "y": p[1], "net": net})

    def path(self, net, w_mm, pts, layer=pcbnew.F_Cu):
        """Explicit polyline (waypoints already known to be clear)."""
        w = pcbnew.FromMM(w_mm)
        for i in range(len(pts) - 1):
            if pts[i] != pts[i + 1]:
                self._track(net, pts[i], pts[i + 1], w, layer)

    # -- clearance checks ----------------------------------------------
    def _seg_ok(self, a, b, layer, hw, net):
        for pad in self.pads:
            if pad["net"] == net:
                continue
            if pad["smd"] and layer != pcbnew.F_Cu:
                continue
            if _pt_seg_dist(pad["x"], pad["y"], a[0], a[1], b[0], b[1]) < pad["r"] + hw + CLR_NM:
                return False
        for t in self.tracks:
            if t["net"] == net or t["layer"] != layer:
                continue
            if _seg_seg_dist(a, b, t["a"], t["b"]) < hw + t["hw"] + CLR_NM:
                return False
        for v in self.vias:
            if v["net"] == net:
                continue
            if _pt_seg_dist(v["x"], v["y"], a[0], a[1], b[0], b[1]) < VIA_R_NM + hw + CLR_NM:
                return False
        return True

    def _via_ok(self, p, net):
        for pad in self.pads:
            d = math.hypot(pad["x"] - p[0], pad["y"] - p[1])
            if pad["net"] == net:
                continue
            if d < pad["r"] + VIA_R_NM + CLR_NM:
                return False
        # keep vias clear of every footprint courtyard (avoid pth-in-courtyard)
        for pad in self.pads:
            if math.hypot(pad["x"] - p[0], pad["y"] - p[1]) < pad["r"] + pcbnew.FromMM(0.7):
                return False
        for t in self.tracks:
            if t["net"] == net:
                continue
            if _pt_seg_dist(p[0], p[1], t["a"][0], t["a"][1], t["b"][0], t["b"][1]) \
                    < VIA_R_NM + t["hw"] + CLR_NM:
                return False
        for v in self.vias:
            if math.hypot(v["x"] - p[0], v["y"] - p[1]) < 2 * VIA_R_NM + CLR_NM:
                return False
        return True

    # -- connection -----------------------------------------------------
    @staticmethod
    def _layers(pt):
        return (pcbnew.F_Cu,) if pt[2] == "F" else (pcbnew.F_Cu, pcbnew.B_Cu)

    def connect(self, net, w_mm, A, B):
        a, b = (A[0], A[1]), (B[0], B[1])
        if a == b:
            return True
        w = pcbnew.FromMM(w_mm)
        hw = w // 2
        cands = []  # (score, segs[(p,q,layer)], via_or_None)
        aligned = a[0] == b[0] or a[1] == b[1]
        corners = [a] if aligned else [(b[0], a[1]), (a[0], b[1])]
        for corner in corners:
            for l1 in self._layers(A):
                if aligned:
                    if l1 not in self._layers(B):
                        continue
                    score = (1 if l1 == pcbnew.B_Cu else 0)
                    cands.append((score, [(a, b, l1)], None))
                    continue
                for l2 in self._layers(B):
                    via = corner if l1 != l2 else None
                    score = (10 if via else 0) + (l1 == pcbnew.B_Cu) + (l2 == pcbnew.B_Cu)
                    cands.append((score, [(a, corner, l1), (corner, b, l2)], via))
        cands.sort(key=lambda c: c[0])
        for _score, segs, via in cands:
            if not all(self._seg_ok(s[0], s[1], s[2], hw, net) for s in segs):
                continue
            if via is not None and not self._via_ok(via, net):
                continue
            for s in segs:
                self._track(net, s[0], s[1], w, s[2])
            if via is not None:
                self.add_via(net, via)
            return True

        # Fallback: 3-segment detour around obstacles, swept on a single layer
        # (no vias). Try F.Cu first, then B.Cu if both endpoints reach it.
        step = pcbnew.FromMM(1.0)
        lo, hi = pcbnew.FromMM(4.0), pcbnew.FromMM(BOARD_W - 4.0)
        loy, hiy = pcbnew.FromMM(4.0), pcbnew.FromMM(BOARD_H - 4.0)
        layers = [pcbnew.F_Cu]
        if pcbnew.B_Cu in self._layers(A) and pcbnew.B_Cu in self._layers(B):
            layers.append(pcbnew.B_Cu)
        best = None
        for layer in layers:
            for mx in range(lo, hi, step):
                pth = [a, (mx, a[1]), (mx, b[1]), b]
                if self._poly_ok(pth, layer, hw, net):
                    length = sum(abs(pth[i][0] - pth[i + 1][0]) + abs(pth[i][1] - pth[i + 1][1])
                                 for i in range(3))
                    if best is None or length < best[0]:
                        best = (length, pth, layer)
            for my in range(loy, hiy, step):
                pth = [a, (a[0], my), (b[0], my), b]
                if self._poly_ok(pth, layer, hw, net):
                    length = sum(abs(pth[i][0] - pth[i + 1][0]) + abs(pth[i][1] - pth[i + 1][1])
                                 for i in range(3))
                    if best is None or length < best[0]:
                        best = (length, pth, layer)
            if best is not None:
                break
        if best is not None:
            _, pth, layer = best
            for i in range(3):
                if pth[i] != pth[i + 1]:
                    self._track(net, pth[i], pth[i + 1], w, layer)
            return True

        # Last resort: grid maze (Lee) router.
        return self.maze_connect(net, w_mm, A, B)

    def _poly_ok(self, pts, layer, hw, net):
        for i in range(len(pts) - 1):
            if pts[i] == pts[i + 1]:
                continue
            if not self._seg_ok(pts[i], pts[i + 1], layer, hw, net):
                return False
        return True

    def _pt(self, ref):
        x, y = self.padpos[ref]
        return (x, y, "F" if self.pad_smd[ref] else "TH")

    def net(self, net, w_mm, refs, seeds=None):
        """Connect every pad of `refs` with an MST. `seeds` are pre-connected
        waypoint coordinates (e.g. an explicit trunk) on F.Cu."""
        pts = [self._pt(r) for r in refs]
        connected = [(s[0], s[1], "F") for s in seeds] if seeds else [pts.pop(0)]
        remaining = pts
        ok = True
        while remaining:
            best = None
            for c in connected:
                for r in remaining:
                    d = abs(c[0] - r[0]) + abs(c[1] - r[1])
                    if best is None or d < best[0]:
                        best = (d, c, r)
            _, c, r = best
            if not self.connect(net, w_mm, c, r):
                ok = False
                print(f"    {net}: FAILED {pcbnew.ToMM(c[0]):.1f},{pcbnew.ToMM(c[1]):.1f}"
                      f" -> {pcbnew.ToMM(r[0]):.1f},{pcbnew.ToMM(r[1]):.1f}")
            connected.append(r)
            remaining.remove(r)
        return ok

    # -- maze (Lee) router ---------------------------------------------
    def _stamp(self, blocked, cx, cy, rad, nx, ny):
        gi0 = max(0, int((cx - rad) // GRID_NM))
        gi1 = min(nx, int((cx + rad) // GRID_NM) + 1)
        gj0 = max(0, int((cy - rad) // GRID_NM))
        gj1 = min(ny, int((cy + rad) // GRID_NM) + 1)
        r2 = rad * rad
        for i in range(gi0, gi1 + 1):
            dx = i * GRID_NM - cx
            for j in range(gj0, gj1 + 1):
                dy = j * GRID_NM - cy
                if dx * dx + dy * dy <= r2:
                    blocked.add((i, j))

    def maze_connect(self, net, w_mm, A, B):
        w = pcbnew.FromMM(w_mm)
        hw = w // 2
        nx = int(pcbnew.FromMM(BOARD_W) // GRID_NM)
        ny = int(pcbnew.FromMM(BOARD_H) // GRID_NM)
        edge = pcbnew.FromMM(0.8)
        imin, imax = int(edge // GRID_NM) + 1, nx - int(edge // GRID_NM) - 1
        jmin, jmax = int(edge // GRID_NM) + 1, ny - int(edge // GRID_NM) - 1

        safe = GRID_NM  # discretisation margin: a track between two free cells
                        # must not graze an obstacle that sits between them.
        blocked = {pcbnew.F_Cu: set(), pcbnew.B_Cu: set()}
        via_block = set()
        for pad in self.pads:
            if pad["net"] == net:
                continue
            rad = pad["r"] + hw + CLR_NM + safe
            layers = (pcbnew.F_Cu,) if pad["smd"] else (pcbnew.F_Cu, pcbnew.B_Cu)
            for ly in layers:
                self._stamp(blocked[ly], pad["x"], pad["y"], rad, nx, ny)
            self._stamp(via_block, pad["x"], pad["y"],
                        pad["r"] + max(VIA_R_NM + CLR_NM, pcbnew.FromMM(0.7)) + safe, nx, ny)
        for t in self.tracks:
            if t["net"] == net:
                continue
            rad = t["hw"] + hw + CLR_NM + safe
            vrad = t["hw"] + VIA_R_NM + CLR_NM + safe
            n = max(2, int((abs(t["a"][0] - t["b"][0]) + abs(t["a"][1] - t["b"][1])) // (GRID_NM // 2)) + 1)
            for k in range(n + 1):
                f = k / float(n)
                px = int(t["a"][0] + f * (t["b"][0] - t["a"][0]))
                py = int(t["a"][1] + f * (t["b"][1] - t["a"][1]))
                self._stamp(blocked[t["layer"]], px, py, rad, nx, ny)
                self._stamp(via_block, px, py, vrad, nx, ny)
        for v in self.vias:
            if v["net"] == net:
                continue
            for ly in (pcbnew.F_Cu, pcbnew.B_Cu):
                self._stamp(blocked[ly], v["x"], v["y"], VIA_R_NM + hw + CLR_NM + safe, nx, ny)
            self._stamp(via_block, v["x"], v["y"], 2 * VIA_R_NM + CLR_NM + safe, nx, ny)

        def cell(p):
            return (int(round(p[0] / GRID_NM)), int(round(p[1] / GRID_NM)))

        a_layers = self._layers(A)
        b_layers = self._layers(B)
        si, sj = cell(A)
        ti, tj = cell(B)
        goal = {(ly, ti, tj) for ly in b_layers}

        from collections import deque
        start_states = [(ly, si, sj) for ly in a_layers]
        prev = {}
        dq = deque()
        for s in start_states:
            prev[s] = None
            dq.append(s)
        found = None
        while dq:
            cur = dq.popleft()
            if cur in goal:
                found = cur
                break
            ly, i, j = cur
            for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ni, nj = i + di, j + dj
                if not (imin <= ni <= imax and jmin <= nj <= jmax):
                    continue
                nxt = (ly, ni, nj)
                if nxt not in prev and (ni, nj) not in blocked[ly]:
                    prev[nxt] = cur
                    dq.append(nxt)
            oly = pcbnew.B_Cu if ly == pcbnew.F_Cu else pcbnew.F_Cu
            nxt = (oly, i, j)
            if nxt not in prev and (i, j) not in via_block \
                    and (i, j) not in blocked[oly] and (i, j) not in blocked[ly]:
                prev[nxt] = cur
                dq.append(nxt)
        if found is None:
            return False

        chain = []
        cur = found
        while cur is not None:
            chain.append(cur)
            cur = prev[cur]
        chain.reverse()

        # emit: stub from A to first cell, grid path with vias, stub to B
        def cc(i, j):
            return (i * GRID_NM, j * GRID_NM)
        prev_pt = (A[0], A[1])
        prev_layer = chain[0][0]
        for k in range(len(chain)):
            ly, i, j = chain[k]
            pt = cc(i, j)
            if ly != prev_layer:
                self.add_via(net, prev_pt)   # layer change at the shared cell
                prev_layer = ly
            if pt != prev_pt:
                self._track(net, prev_pt, pt, w, ly)
                prev_pt = pt
        if (B[0], B[1]) != prev_pt:
            self._track(net, prev_pt, (B[0], B[1]), w, prev_layer)
        return True


def add_via(board, net, x, y):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I(x, y))
    v.SetDrill(pcbnew.FromMM(0.4))
    v.SetWidth(pcbnew.FromMM(0.8))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    v.SetNet(net)
    board.Add(v)


if __name__ == "__main__":
    main()

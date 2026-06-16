"""Single source of truth for the B2500 cluster PWM dimmer netlist.

Both gen_sch.py (schematic) and gen_pcb.py (board) import COMPONENTS from
here so the two views cannot drift apart. Each entry is:

    (ref, symbol, value, footprint, dnp, on_board, {pad: net}, sch_xy)

`footprint` is the KiCad "lib:name" id. `on_board` False means the part is
documented in the schematic but not placed on the PCB (F1 is inline in the
vehicle harness). A net value of None marks an intentional no-connect.
"""

FP_R = "Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder"
FP_C = "Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder"
FP_TP = "TestPoint:TestPoint_THTPad_D1.5mm_Drill0.7mm"

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
    # Pololu D36V28F5 mounts OFF-BOARD, wired to this 3-pin header so the
    # connection is orientation-proof (match VIN/GND/VOUT label to label).
    ("U2",  "BUCK_D36V28F5", "Pololu D36V28F5 (off-board, wired)",
     "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical", False, True,
     {"1": "VIN_PROT", "2": "GND", "3": "5V_BUCK"}, (210, 50)),
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

    ("Q2",  "Q_NMOS", "2N7000", "Package_TO_SOT_THT:TO-92_Inline_Wide", False, True,
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

    # Green power-on indicator: lights whenever protected 12 V is present.
    ("R11", "R", "3.3k", FP_R, False, True, {"1": "VIN_PROT", "2": "LED_A"}, (300, 170)),
    ("D6",  "LED", "Green LED (PWR)", "LED_THT:LED_D3.0mm", False, True,
     {"1": "GND", "2": "LED_A"}, (325, 170)),
]

# Nets that legitimately land on a single board pad (the other end leaves the
# board through the harness) and must not trip the "single pin" sanity check.
HARNESS_SINGLE_PIN_NETS = {"12V_LIGHTS_FEED"}


def power_nets():
    """Nets that carry load current and want wide copper."""
    return {"VIN_RAW", "VIN_PROT", "PWM_OUT", "5V_BUCK", "5V_JMP", "5V_XIAO"}

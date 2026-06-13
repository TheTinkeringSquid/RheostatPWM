# Fabrication & Assembly Notes

> **This board is for instrument-cluster illumination only.** It is not for
> exterior lighting, brake lights, turn signals, airbags, engine controls, or
> any safety-critical circuit. Do not use it outside its intended purpose.

## Board specification

| Item            | Value                                                   |
|-----------------|---------------------------------------------------------|
| Layers          | 2 (signal/F.Cu + signal/B.Cu), ground pour on both      |
| Size            | ~94 × 62 mm                                             |
| Copper weight   | 1 oz (35 µm) minimum; 2 oz preferred for the power path |
| Min track / clr | 0.25 mm / 0.20 mm (power nets routed 1.5 mm)            |
| Min hole        | 0.3 mm; vias 0.8 mm / 0.4 mm                            |
| Finish          | HASL or ENIG, lead-free                                 |
| Mounting        | 2 × M3 (GND-connected pads)                            |

## ⚠️ Routing status — read before ordering

The committed `b2500_cluster_pwm_dimmer.kicad_pcb` is **placed and
ground-poured with only the two high-current connector nets (`VIN_RAW`,
`PWM_OUT`) routed.** All other signal nets are still ratsnest. **Do not send the
gerbers to a fab until the remaining nets are routed and DRC is clean.**

To finish and export:

1. Open the project in KiCad 10, route the ratsnest in the PCB editor.
2. Route the `VIN_PROT` bus from the bulk caps/D1 into the Q1 source as a short,
   wide trace — this is the high-current load path and is intentionally left for
   manual placement.
3. Keep the `DIM_IN`/ADC divider network (R3/R4/R5/C3/D4) away from the Q1
   switching node and the VIN input.
4. `Edit > Fill All Zones`, then run DRC to zero errors.
5. Run `python hardware/scripts/export_fab.py` to write gerbers + Excellon drill
   into `hardware/gerbers/` and regenerate the BOM.

## Assembly notes

- **F1 is OFF-BOARD.** Use an inline blade fuse in the vehicle harness at the
  feed tap, sized to the measured LED cluster current (1–2 A typical). It must
  protect the wire run to the board.
- **U1 (XIAO RP2040)** mounts on two 1×7 socket headers so it is removable; the
  USB-C connector is used for programming.
- **U2 (Pololu D36V28F5)** is a module on a 1×4 header. **Verify the module's
  pin order (EN / VIN / GND / VOUT) against its own silkscreen** before
  soldering — module pinouts vary by revision.
- **Q1 (FQP27P06, TO-220)** is the high-side P-MOSFET. Leave clearance around the
  tab; add a small heatsink only if bench testing shows it running warm (it
  should stay cool at <1 A LED load).
- **Do-not-populate (DNP):**
  - `R10` + `C5` — RC snubber across `PWM_OUT`. Fit only if a scope shows
    switching-edge ringing.
  - `R1` + `R2` — `IGN_SENSE` divider reserved for future firmware.
- **JP1** links the buck 5 V to the XIAO 5 V. Leave it **open** when programming
  over USB with vehicle power applied, to prevent 5 V backfeed (D3 also helps).
- Test points: `TP_VIN`, `TP_5V`, `TP_3V3`, `TP_DIM_ADC`, `TP_PWM_GATE`,
  `TP_PWM_OUT`, `TP_GND`.

---

## Bench test procedure (before installing in the van)

1. Build the PCB; do **not** connect it to the van.
2. Inspect for shorts.
3. Power from a current-limited bench supply at 12 V.
4. Confirm the 5 V rail (`TP_5V`) and 3.3 V rail (`TP_3V3`).
5. Drive `DIM_IN` with a potentiometer or adjustable supply (0–14.4 V).
6. Connect a 12 V LED test lamp (or resistor + LED) to `PWM_OUT`.
7. Sweep `DIM_IN` from 0 V to 14.4 V and verify:
   - LEDs off near zero input.
   - Smooth brightness increase.
   - Full brightness near full dimmer input.
   - Q1 does not get hot.
   - No XIAO brownouts.
8. Scope `TP_PWM_OUT` / `TP_PWM_GATE` to confirm PWM frequency (~976 Hz) and a
   clean edge. Fit the R10/C5 snubber if you see ringing.
9. Tune firmware constants `ADC_OFF_THRESHOLD`, `ADC_MIN_INPUT`, `ADC_MAX_INPUT`,
   `DUTY_MIN`, `GAMMA` using the serial monitor (115200 baud):
   - record `filtered=` at lights-off, barely-on, and full-bright;
   - set `ADC_MIN_INPUT` just below barely-on, `ADC_MAX_INPUT` to full-bright,
     `ADC_OFF_THRESHOLD` just above the true-off noise floor.

## In-vehicle test procedure

1. Disconnect the battery before wiring.
2. Verify the factory wire functions with a DMM.
3. Install an inline fuse if the feed is not already appropriately fused.
4. Connect board **ground first**.
5. Connect `VIN_RAW` to a full-bright park/headlight-switched 12 V feed.
6. Connect the rheostat output sense to `DIM_IN`.
7. Connect the cluster LED feed to `PWM_OUT`.
8. Reconnect the battery.
9. Test with parking lights / headlights on. Check:
   - the dimmer knob smoothly adjusts cluster brightness;
   - no flicker while the engine runs;
   - no radio noise;
   - board and MOSFET stay cool;
   - cluster lights turn off when park/headlights are off.

If the dimmer works backward, set `REVERSE_DIMMER_DIRECTION = true` in firmware
(invert in software, not by rewiring power).

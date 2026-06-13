# Gerbers

Fabrication output for the B2500 cluster PWM dimmer — RS-274X gerbers plus
Excellon drill files (`-PTH.drl`, `-NPTH.drl`). The board is fully routed and
DRC-clean, so these are **ready to manufacture**.

To order: zip the contents of this directory and upload to any PCB fab
(JLCPCB, PCBWay, OSH Park, Aisler, …). Settings: 2-layer, 1.6 mm, 1 oz copper
(2 oz optional for the power path), HASL or ENIG.

These files are generated, not hand-edited. Regenerate after any board change
with:

```powershell
python ../scripts/export_fab.py
```

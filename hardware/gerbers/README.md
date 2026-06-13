# Gerbers

This directory holds the fabrication output (gerbers + Excellon drill files).

It is **generated**, not hand-edited. The files are produced only after the
signal nets have been routed in the KiCad GUI (see
[../fabrication_notes.md](../fabrication_notes.md)). To generate them:

```powershell
python ../scripts/export_fab.py
```

Until routing is complete and DRC is clean, do not send these files to a
fabricator.

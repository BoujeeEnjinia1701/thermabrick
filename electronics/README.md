# Electronics

| Path | Contents |
| --- | --- |
| `src/schematic.py` | Generator for the test article controller schematic (TBK-DWG-003), the source of truth for that circuit |
| `src/board.py` | Generator for the optional controller board: schematic, PCB layout, gerbers and TBK-DWG-004 |
| `test-article/` | KiCad project for TBK-DWG-003: the whole controller, mains and low voltage, as hand-wired modules |
| `controller-board/` | KiCad project for the optional low-voltage controller board, with gerbers for fabrication |

Change a circuit in its script, not in KiCad, then regenerate from the repo root:

```bash
python electronics/src/schematic.py
```

```bash
python electronics/src/board.py
```

Both scripts need KiCad 9 or later. They look for it in `/Applications/KiCad`, in `~/Applications/KiCad`, or on the mounted KiCad disk image.

`schematic.py` runs KiCad's electrical rules check (ERC). It then exports the netlist and checks every net against the circuit the script declares. It fails on any ERC error or net mismatch.

`board.py` works in three stages:

1. It builds and checks the board schematic in the same way as `schematic.py`.
2. It re-runs itself inside KiCad's bundled Python. That stage places the footprints, routes the board with its own two-layer grid router (F.Cu preferred, clearance 0.25 mm against a 0.2 mm rule) and pours the GND plane on B.Cu.
3. It runs KiCad's DRC with schematic parity, then exports the gerber and drill package and the drawing sheet.

The P1 board passes with 0 errors, 0 warnings and 0 unconnected items. The routing is reproducible, but KiCad assigns fresh internal IDs, so the `.kicad_pcb` file changes on every run even when the layout does not.

Both projects carry every symbol and footprint they use, so they open without KiCad's global libraries installed. Terminal numbers on K1, U1 and U2 of TBK-DWG-003 are functional; wire to each part's own label.

**Board fit.** The board takes an ESP32-DevKitC V4 with 38 pins and header rows 25.4 mm apart. 30-pin and narrow clone boards do not fit. The pinout follows the Espressif DevKitC V4 user guide, header J2 on the left and J3 on the right, both numbered from the antenna end. Check your module against it before soldering the sockets.

**Licenses.** CERN-OHL-S-2.0 for the hardware; MIT for the generator scripts.

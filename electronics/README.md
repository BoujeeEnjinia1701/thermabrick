# Electronics

| Path | Contents |
| --- | --- |
| `src/schematic.py` | Generator for the test article controller schematic; the source of truth for the circuit |
| `test-article/` | KiCad 9/10 project: schematic, project symbol library (`thermabrick.kicad_sym`) and a PDF export |

The schematic is drawing TBK-DWG-003. The generator also places it on the portfolio sheet in `cad/drawings/TBK-DWG-003` (SVG, PDF, PNG). Change the circuit in `src/schematic.py`, not in KiCad, then regenerate from the repo root:

```bash
python electronics/src/schematic.py
```

The generator needs KiCad 9 or later. It looks for `kicad-cli` on the PATH, in `/Applications/KiCad`, in `~/Applications/KiCad`, or on the mounted KiCad disk image. It then:

1. runs KiCad's electrical rules check (ERC), and fails on any error;
2. exports the netlist and checks every net against the connections declared in the script, and fails on any mismatch;
3. exports the PDF and builds the ANSI B sheet.

The project library holds every symbol the schematic uses, so it opens without KiCad's global libraries installed. Terminal numbers on K1, U1 and U2 are functional; wire to each part's own label. Licensed CERN-OHL-S-2.0 (hardware) and MIT (the generator script).

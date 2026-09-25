# Build log

Dated entries, newest first. One entry per working session, whether building the test article (stages A to L of `docs/07-build/test-article-build.md`), running a test (TP0 to TP6 of TBK-TST-001), or sourcing parts.

## Writing an entry

Start each entry from the template with the helper, run from the repo root:

```bash
python build-log/new_entry.py "Drum preparation" --stage B
```

The helper names the file `YYYY-MM-DD-short-title.md` and fills in the date, author, stage and repo commit. It also adds the record table for that stage and lists the entry in the index below. Without `--stage`, it writes a blank record table. `TEMPLATE.md` holds the layout.

Conventions:

- **Record measurements when you take them,** with units, in the entry's record table. Test data goes to `docs/05-tests/data/` through the logger; the entry names the data file.
- **Log every deviation.** Each one names the document to change, whether drawing, cut list, BOM or procedure. The entry is not closed until those changes are committed.
- **Record actual prices** against the BOM estimate, so the next build's BOM can be corrected.
- **Save photos** to `media/build/` as `YYYY-MM-DD-stage-short-name.jpg`.
- **Leave raw notes unedited** after the session. Correct them with a dated note below the original.

## Entries

<!-- index start -->
- [2026-09-24: Kit 1.3.1](2026-09-24-kit-1-3-1.md)
- [2026-09-24: Kit 1.3.0](2026-09-24-kit-1-3-0.md)
- [2026-09-24: Kit 1.2.0 and TRL target capped at 3](2026-09-24-kit-1-2-0.md)
- [2026-09-24: TRL 3 recorded](2026-09-24-trl-3-recorded.md)
<!-- index end -->

# Adlib to AtoM Converter

![Museum object metadata becoming an archival import table](assets/adlib-to-atom.png)

If your archive has catalogue records in Axiell Adlib and wants to move them to AtoM (Access to Memory), the records need to be rearranged for the new system. This tool helps with that step.

It reads an **XML export** from Adlib, which is a copy of the catalogue data, and creates a **CSV file** for review before an AtoM import. A CSV is a table you can open in spreadsheet software. The tool works with exported files; it does not connect to either live catalogue.

For example, imagine an Adlib record for a *Parish minute book* with the reference `PAR/42`, creator *Parish Office*, and date `1901`. The converter puts those details into the corresponding columns of one AtoM-style CSV row. An archivist can then check the row before importing it.

## Who might use it?

An archivist, museum worker, or migration consultant preparing to move catalogue data from Adlib or Axiell Collections into AtoM. You need an Adlib XML export and the exact name of the destination repository in AtoM.

## What it does

- Moves common details such as identifiers, titles, descriptions, creators, and dates into AtoM CSV columns.
- Reads nested Adlib XML and selects the requested language when a field has several translations. For example, `--culture en` selects an English title when one is available.
- Keeps multiple creator and date entries aligned in the CSV. If one entry has no corresponding value, it uses a `NULL` placeholder so the positions stay clear.
- Processes records incrementally to reduce memory use with large exports.

The included `default_mapping.json` defines which Adlib fields go into which AtoM columns. You can supply a different mapping file if your export uses other fields.

## Before you import the CSV

Check a sample of the output against the Adlib export, especially titles, identifiers, creators, dates, and the repository name. Missing titles may appear as `[Untitled]`; an identifier that cannot be found may appear as `UNKNOWN`. These are prompts for review, not completed descriptions.

The converter creates a CSV; it does **not** import records into AtoM or check whether every field in your particular export has been mapped. Keep the original XML export. **Choose a new output filename:** the current command replaces an existing CSV at the output path.

## Set it up with your AI agent

Copy and paste this into an agent that can work on your computer:

```text
Set up the Adlib to AtoM Converter from https://github.com/matthewbrutonall/adlib-to-atom on my computer. Check that Python 3.8 or later is available, clone the repository into its own folder, and verify that `python3 cli.py --help` works from that folder. Show me the command I would use for an Adlib XML export, but do not process any collection data yet.
```

## Run it yourself

You need Python 3.8 or later. The normal conversion uses Python's standard library; no extra packages are needed when running the script from this repository.

```bash
git clone https://github.com/matthewbrutonall/adlib-to-atom.git
cd adlib-to-atom
python3 cli.py --help
```

To convert an export, replace the example filenames and repository name with your own:

```bash
python3 cli.py adlib-export.xml atom-import.csv --repository "Example Archive"
```

`--repository` is required. Use the exact repository name authorised in your AtoM system. The default language is English (`en`); use `--culture` for another language. Use `--mapping your-mapping.json` for a custom field mapping.

## For developers

The converter uses Python's streaming XML parser and a JSON field map. To install the optional test dependency and run the tests:

```bash
python3 -m pip install -e ".[dev]"
pytest tests/
```

Released under the [MIT License](LICENSE).

# Adlib to AtoM Converter

![Museum object metadata becoming an archival import table](assets/adlib-to-atom.png)

A standalone, memory-safe XML parser that converts Axiell Adlib (and Axiell Collections) XML exports into Artefactual's AtoM ISAD(G) CSV format.

## Features
*   **Memory-Safe XML Streaming:** Uses `xml.etree.ElementTree.iterparse()` and element-clearing to process gigabyte-sized museum exports without exhausting RAM.
*   **Grouped XML Support:** Recursively traverses Adlib's grouped XML wrappers (e.g., `<production>`, `<dimension>`) to locate nested data.
*   **Culture-Aware Extraction:** Intelligently extracts the correct multilingual `<value lang="...">` tags from WebAPI exports.
*   **Strict Parallel Arrays:** Perfectly pads missing actors or dates with `NULL` to satisfy AtoM's strict event array rules.
*   **JSON Mapping:** Easily customizable Adlib tag-to-AtoM header mapping via `default_mapping.json`.

## Installation

```bash
# Clone the repository
git clone https://github.com/matthewbrutonall/adlib-to-atom.git
cd adlib-to-atom

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install development dependencies (pytest)
pip install -e .[dev]
```

## Usage

```bash
python cli.py <input.xml> <output.csv> --repository <atom-repo-name>
```

**Options:**
*   `--repository` (Required): The authorized name of the repository in AtoM (prevents ghost records).
*   `--culture` (Optional): The target culture code for multilingual selection (default: `en`).
*   `--mapping` (Optional): Path to a custom JSON mapping profile.

## Testing
Run the test suite using pytest:
```bash
pytest tests/
```

## License
Released under the [MIT License](LICENSE).

# XML Editor

A desktop and CLI XML editor for social network data. It supports validation, auto-correction, formatting, minification, compression/decompression, JSON export, and basic graph-based analysis/visualization of relationships.

---

## Features

- **Rich GUI** (PySide6):
  - Load XML files via *Browse* or *Manual* modes
  - Validate XML structure with inline annotations
  - Auto-correct common structural issues (unbalanced/mismatched tags)
  - Pretty-print formatted XML with wrapping
  - Minify XML (remove unnecessary whitespace)
  - Compress / decompress XML with a custom token-based algorithm
  - Export parsed XML to JSON
  - Visualize user network as a graph (via `GraphController` and visualization window)

- **CLI interface**:
  - `verify`: validate an XML file (and optionally fix)
  - `format`: format/pretty-print an XML file
  - `json`: convert XML to JSON
  - `mini`: minify XML (placeholder for integration with `XMLController.minify`)
  - `compress`: compress XML (placeholder for integration with `compress_to_string`)
  - `decompress`: decompress XML (placeholder for integration with `decompress_from_string`)

- **Utilities**:
  - `file_io`: safe read/write helpers and pretty-formatting helpers
  - `token_utils`: XML tokenization and tag helpers
  - `binary_utils.ByteUtils`: low-level integer packing/unpacking for compression
  - `xml_tree`: higher-level XML tree abstractions (`XMLTree`, `XMLNode`, `XMLParseError`)

---

## Architecture

At a high level, the project is organized into four main layers:

- **UI Layer (`src/ui/`)**
  - Windows: `BaseXMLWindow`, `BrowseWindow`, `LandingWindow`, `CodeViewerWindow`, `GraphVisualizationWindow`, etc.
  - Responsible for all user interaction, dialogs, and presentation.
  - Delegates actual work to controllers.

- **Controllers Layer (`src/controllers/`)**
  - `XMLController`: core XML logic (tokenization, formatting, minification, validation, auto-correction, compression/decompression, JSON export).
  - `GraphController`: builds and manages the graph representation of the XML data for visualization and analysis.

- **Utilities Layer (`src/utils/`)**
  - Shared, stateless helpers for file I/O, XML tokenization, binary packing, and XML tree manipulation.

- **CLI Layer (`cli.py`)**
  - Command-line entry point that wires arguments to `XMLController` and utilities.

### Module Interaction Diagram

```mermaid
graph TD
  subgraph CLI
    CLI[cli.py]
  end

  subgraph UI[PySide6 UI (src/ui)]
    BaseXML[BaseXMLWindow]
    Browse[BrowseWindow]
    Landing[LandingWindow]
    CodeViewer[CodeViewerWindow]
    GraphVis[GraphVisualizationWindow]
  end

  subgraph Controllers[src/controllers]
    XMLCtrl[XMLController]
    GraphCtrl[GraphController]
  end

  subgraph Utils[src/utils]
    FIO[file_io]
    Tok[token_utils]
    BUtils[ByteUtils]
    XTree[xml_tree (XMLTree, XMLNode, XMLParseError)]
  end

  %% UI to controllers
  BaseXML --> XMLCtrl
  BaseXML --> GraphCtrl
  Browse --> BaseXML
  Landing --> BaseXML
  CodeViewer --> BaseXML
  GraphVis --> GraphCtrl

  %% CLI to controllers
  CLI --> XMLCtrl

  %% Controllers to utils
  XMLCtrl --> FIO
  XMLCtrl --> Tok
  XMLCtrl --> BUtils
  XMLCtrl --> XTree
  GraphCtrl --> XTree
  GraphCtrl --> FIO
```

---

## Project Structure

```text
xml-editor/
├─ cli.py                      # CLI entry point
├─ app_main.py                 # GUI entry point (Qt application)
├─ assets/
│  ├─ images/
│  └─ samples/                 # Sample XML data for testing/demo
├─ src/
│  ├─ __init__.py
│  ├─ controllers/
│  │  ├─ __init__.py           # Exports XMLController, GraphController, ByteUtils
│  │  └─ xml_controller.py     # Core XML logic
│  ├─ ui/
│  │  ├─ __init__.py
│  │  ├─ base_xml_window.py    # Shared base window logic
│  │  ├─ browse_window.py      # "Browse" mode (load from file)
│  │  ├─ code_viewer_window.py # Raw code viewer
│  │  ├─ landing_window.py     # Start/landing screen
│  │  └─ manual_window.py      # Manual text-entry mode
│  └─ utils/
│     ├─ __init__.py           # Re-exports helpers and ByteUtils, XMLTree, ...
│     ├─ file_io.py            # Safe file I/O & pretty-format helpers
│     ├─ token_utils.py        # Tag/token helpers
│     ├─ binary_utils.py       # ByteUtils for compression
│     └─ xml_tree.py           # XML tree abstractions
└─ tests/
   └─ xml_controller_test.py   # Unit tests for XMLController
```

---

## Installation

### Prerequisites

- **Python**: 3.10+ (recommended)
- **Dependencies** (minimum):
  - `PySide6`
  - Any other libraries required by your environment (e.g., `networkx`/`matplotlib` if GraphController uses them)

### Setup

```bash
# Clone the repository
git clone <your-repo-url> xml-editor
cd xml-editor

# (Optional) create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt  # if present
# OR manually:
pip install PySide6
```

> If you do not have a `requirements.txt` yet, you can generate one from your environment with `pip freeze > requirements.txt`.

---

## Running the GUI

From the project root:

```bash
python app_main.py
```

This will launch the PySide6 desktop UI. Use the *Browse* or *Manual* modes to load XML, then run operations from the right-hand panel (validate, correct, format, compress, decompress, export JSON, visualize network, etc.).

---

## Running the CLI

From the project root:

```bash
# Show help
python cli.py --help

# Verify XML structure
python cli.py verify -i assets/samples/sample.xml

# Verify and write fixed XML to a new file
python cli.py verify -i assets/samples/non_formatted.xml -o output_data/corrected.xml -f

# Format XML
python cli.py format -i assets/samples/sample.xml -o output_data/formatted.xml

# Convert to JSON
python cli.py json -i assets/samples/sample.xml -o output_data/xml_to_json.json
```

> Note: The `mini`, `compress`, and `decompress` CLI commands are wired but may still be evolving; they should be implemented to delegate to `XMLController.minify`, `compress_to_string`, and `decompress_from_string` respectively.

---

## Testing

To run the tests (from the project root):

```bash
pytest
```

or, if you prefer unittest or another runner, adapt accordingly.

---

## Contributing & Extensibility

- **New operations** (e.g., advanced validations, XPath queries, analytics) should be added to `XMLController` (and/or new controllers) and then exposed via:
  - UI: `BaseXMLWindow` and derived windows
  - CLI: `cli.py`
- **New visualizations** can be added by extending `GraphController` and `GraphVisualizationWindow`.
- **Utilities** should remain stateless and reusable across both UI and CLI.

Please follow existing coding style and keep controllers thin (business logic) and UI/views focused on presentation and user interaction.

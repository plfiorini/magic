# Moxfield to Forge Deck Converter

A Python tool to convert Magic: The Gathering deck lists from Moxfield format to Forge format, with special support for Commander/EDH decks.

## Features

- Converts Moxfield deck exports (text or JSON) to Forge-compatible `.dck` files
- Automatically detects Commander/EDH decks (100-card singleton format)
- Handles set codes and collector numbers
- Normalizes promo set codes (removes 'P' prefix for Forge compatibility)
- Preserves special markers and foil indicators
- Supports both regular and Commander deck formats

## Project Structure

```
moxfield_to_forge.py    # Main converter script
lists/                  # Directory containing Moxfield deck exports
  ├── convert          # Batch conversion script
  ├── zurgo.txt        # Example: Mardu Surge deck
  ├── valgavoth.txt    # Example: Rakdos pain deck
  ├── edgar.txt        # Example: Vampire tribal
  ├── elas.txt         # Example: Aristocrats deck
  ├── elfs.txt         # Example: Elf tribal
  ├── braids.txt       # Example: Aristocrats variant
  ├── vren2.txt        # Example: Dimir rats
  ├── hakbal.txt       # Example: Merfolk explorers
  ├── hearthhull.txt   # Example: Jund lands
  ├── toph.txt         # Example: Gruul lands combo
  ├── toph2.txt        # Example: Gruul lands variant
  ├── toph3.txt        # Example: Gruul lands casual
  ├── sephiroth.txt    # Example: Mono-black aristocrats
  ├── greengoblin.txt  # Example: Rakdos reanimator
  ├── hashaton.txt     # Example: Esper reanimator
  ├── axonil.txt       # Example: Mono-red burn
  └── axonil2.txt      # Example: Mono-red burn variant
```

## Usage

### Single Deck Conversion

```bash
# Basic usage
./moxfield_to_forge.py input.txt output.dck

# With flags
./moxfield_to_forge.py -i deck.txt -o converted.dck

# Override deck name
./moxfield_to_forge.py -i deck.txt -o output.dck --name "My Awesome Deck"
```

### Batch Conversion

Use the [`lists/convert`](lists/convert) script to convert multiple decks at once:

```bash
cd lists
./convert
```

This script converts all deck lists in the `lists/` directory using predefined deck names.

### Demo Mode

```bash
./moxfield_to_forge.py --demo
```

## Input Format

The converter accepts Moxfield deck exports in text format:

```
1 Card Name (SET) 123
2 Another Card (SET2) 456 *F*
1 Double-Faced Card / Other Side (SET3) 789
```

**Format details:**
- Quantity at the start of each line
- Card name
- Set code in parentheses (e.g., `(LCI)`, `(DSK)`)
- Optional collector number
- Optional special markers (e.g., `*F*` for foil)

## Output Format

The converter generates Forge `.dck` files:

```
[metadata]
Name=Deck Name
[Commander]
1 Commander Card|SET|[123]
[Main]
1 Card Name|SET|[456]
2 Another Card|SET2|[789]
```

**For Commander decks:**
- First card becomes the Commander
- Remaining 99 cards go in the Main section
- Automatically detected for 100-card singleton decks

**For regular decks:**
- All cards go in the Main section
- Optional Sideboard section

## Set Code Normalization

The converter automatically handles promo set codes:
- `PBLB` → `BLB`
- `PMKM` → `MKM`
- `PDMU` → `DMU`

## Command Line Options

```
usage: moxfield_to_forge.py [-h] [-i INPUT_FILE_ALT] [-o OUTPUT_FILE_ALT]
                            [-n NAME] [--demo] [--version]
                            [input_file] [output_file]

positional arguments:
  input_file            Input Moxfield deck file (.txt or .json)
  output_file           Output Forge deck file (.dck)

optional arguments:
  -h, --help            show this help message and exit
  -i, --input INPUT_FILE_ALT
                        Input Moxfield deck file (.txt or .json)
  -o, --output OUTPUT_FILE_ALT
                        Output Forge deck file (.dck)
  -n, --name NAME       Override deck name in the output file
  --demo                Run with sample deck data and display output
  --version             show program's version number and exit
```

## Examples

Convert the Zurgo Mardu Surge deck:
```bash
./moxfield_to_forge.py lists/zurgo.txt ~/.forge/decks/commander/zurgo.dck
```

Convert with custom name:
```bash
./moxfield_to_forge.py -i lists/valgavoth.txt -o valgavoth.dck --name "Endless Pain"
```

## Requirements

- Python 3.6 or higher
- No external dependencies required

## License

This is a utility script for personal use with Magic: The Gathering deck management tools.

## Related Tools

- [Moxfield](https://www.moxfield.com/) - Deck building platform
- [Forge](https://github.com/Card-Forge/forge) - Magic: The Gathering game engine
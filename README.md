# Clash Royale Tilemap Converter

Convert Clash Royale tilemap CSV files into PDF format for easy visualization.

## Features

- Convert CSV tilemap files to high-quality PDF documents
- Support for the latest Clash Royale tilemap format
- Automatic parsing of tile types and layout
- Generate clear, readable map visualizations

## System Requirements

- Python 3.7 or higher

## Installation

1. Clone or download the project:
```bash
git clone https://github.com/Darklighture/cr-new-tilemap.git
cd cr-new-tilemap
```

2. Install dependencies:
```bash
pip install pyyaml reportlab python-box
```
Or install using requirements.txt:
```bash
pip install -r requirements.txt
```

## Usage

1. Prepare your tilemap CSV file:
   - Place your `tilemap.csv` file in the `data` directory

2. Run the conversion program:
```bash
python main.py
```

3. The generated PDF file will be saved in the `output` directory

## Project Structure

```
cr-tilemap/
├── run.py              # Main program
├── requirements.txt     # Dependencies list
├── data/               # Input data directory (place tilemap.csv here)
├── output/             # Output directory (generated PDF files)
├── config/             # Configuration files
└── README.md           # Documentation
```

## Notes

- Ensure `tilemap.csv` exists in the `data` directory
- Output directory will be created automatically
- If you encounter dependency issues, ensure you're using the latest versions

## Troubleshooting

1. **"ModuleNotFoundError" when running**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`

2. **Invalid CSV file format**
   - Ensure your CSV file follows the standard Clash Royale tilemap format

3. **Generated PDF shows no content**
   - Check if the CSV file contains valid tile data
   - Verify file paths and names are correct

## Support

For issues, refer to the original repository: [smlbiobot/cr-tilemap](https://github.com/smlbiobot/cr-tilemap)

## License

This project is licensed under the MIT License. See LICENSE file for details.
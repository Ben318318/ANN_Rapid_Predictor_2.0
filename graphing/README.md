# Neural Tract Visualization Setup Guide

This guide will help you set up and run the 3D neural tract visualization tool.

## Prerequisites

- Python 3.10 or higher
- pip (Python package installer)

## Step 1: Create and Activate Virtual Environment

```powershell
# Create a new virtual environment
python -m venv venvs/viz

# Activate the virtual environment
# On Windows:
.\venvs\viz\Scripts\Activate.ps1
# On Linux/Mac:
# source venvs/viz/bin/activate
```

## Step 2: Install Required Packages

```powershell
# Install required packages
python -m pip install numpy plotly kaleido
```

## Step 3: Prepare Your Data Files

You need two input files:
1. Tract file (`.xyz` or `.xyz.ini` format) containing fiber coordinates
2. Results JSON file containing threshold data

Example file structure:
```
your_project_folder/
├── processed_tract.xyz.ini    # Fiber tract data
├── results.json               # Threshold results
└── plot_tracts_plotly.py     # Visualization script
```

## Step 4: Run the Visualization Script

Set-Location 'C:\Users\benbe\Research'; & "$env:USERPROFILE\venvs\viz\Scripts\Activate.ps1"; python -m pip install -U numpy; python -c "import numpy as np; print('numpy', np.__version__)"

```powershell
python plot_tracts_plotly.py processed_tract.xyz.ini results.json 3.0 anisotropic output_folder
python .\plot_tracts_plotly.py .\processed_tract.xyz.ini .\results.json 1.0 anisotropic .\output_folder --show_axes
```

Parameters explained:
- `processed_tract.xyz.ini`: Path to your tract file
- `results.json`: Path to your threshold results file
- `3.0`: Voltage limit value
- `anisotropic`: Conductivity type (choose 'anisotropic' or 'isotropic')
- `output_folder`: Directory where visualizations will be saved

## Step 5: View the Visualizations

1. Start a local web server:
```powershell
cd output_folder/plotly
python -m http.server 8000
```

2. Open your web browser and navigate to:
```
http://localhost:8000/activation_pw_0.html
```

## Interacting with the 3D Visualization

- Left click + drag: Rotate the view
- Right click + drag: Zoom in/out
- Middle click + drag: Pan the view
- Double click: Reset the view

## Output Files

The script generates two types of files for each pulse width:
1. Interactive HTML files (`activation_pw_X.html`)
2. Static PNG images (`activation_pw_X.png`)
3. Summary JSON file (`activation_summary.json`)

## Troubleshooting

1. If packages fail to install:
```powershell
python -m pip install --upgrade pip
python -m pip install numpy plotly kaleido --no-cache-dir
```

2. If the web browser won't open local HTML files directly:
Always use the local server method (Step 5) to view the visualizations.

3. If you see import errors:
Make sure you've activated the virtual environment and installed all required packages.

## Script Options

Optional parameters:
- `--interactive_pw INDEX`: Generate visualization for a single pulse width index
  Example: `python plot_tracts_plotly.py processed_tract.xyz.ini results.json 3.0 anisotropic output_folder --interactive_pw 0`
 - `--show_axes`: Show the XYZ axes in the Plotly 3D scene. By default the exporter hides axes for a cleaner visualization. Example:
   `python plot_tracts_plotly.py processed_tract.xyz.ini results.json 3.0 anisotropic output_folder --show_axes`

## Example File Formats

1. Tract file format (`.xyz` or `.xyz.ini`):
```
x1 y1 z1 x2 y2 z2 x3 y3 z3  # Points for fiber 1
x1 y1 z1 x2 y2 z2           # Points for fiber 2
...
```

2. Results JSON format:
```json
{
  "0.06": {                  # Pulse width in seconds (60μs)
    "0": threshold_value,    # Threshold for fiber 0
    "1": threshold_value,    # Threshold for fiber 1
    ...
  },
  "0.075": {                 # Next pulse width (75μs)
    ...
  }
}
```

open interactive images with this link...
cd output_folder; python -m http.server 8000
http://localhost:8000/index.html

## Plotly exporter — recent changes

The Plotly exporter (`plot_tracts_plotly.py`) has been updated. If you are using it, please note the following changes and options:

- **Lead coordinates (Mayavi-derived)**: the script now uses the following `leftLeadPos` by default to match the Mayavi visualizations:

  ```python
  leftLeadPos = [[167, 161], [223, 222], [143, 159]]
  ```

- **Dependencies**: ensure `plotly` and `kaleido` are installed in your environment:

  ```powershell
  python -m pip install -U plotly kaleido
  ```
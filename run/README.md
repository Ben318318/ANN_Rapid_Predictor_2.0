# ANN Rapid Predictor - Run Scripts

This directory contains the main prediction scripts for the ANN Rapid Predictor.

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run predictions using:

```bash
python dti_ann_LUT.py <electrode_file> <tract_file> <model_path> <output_json> <centering_strategy> <tract_type> <conductivity> <regression_mode>
```

### Arguments:
- `electrode_file`: Path to electrode voltage data file
- `tract_file`: Path to DTI tractography file
- `model_path`: Path to trained ANN model directory (e.g., `../models/ann_103_reg`)
- `output_json`: Output file path for results
- `centering_strategy`: Centering strategy for fibers
- `tract_type`: Type of tract (e.g., `stn`, `gpi`)
- `conductivity`: Conductivity type (e.g., `anisotropic`, `isotropic`)
- `regression_mode`: Either `reg` for regression or `class` for classification

### Example:
```bash
python dti_ann_LUT.py ../electrodes/medtronic_3387/monopolar/3387_anisotropic_monopolar_0.txt tracts.txt ../models/ann_103_reg results.json min_ecs stn anisotropic reg
```

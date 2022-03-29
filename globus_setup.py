from pathlib import Path


DATA_DIR = Path(r"F:\Globus")
DATE_BASELINE = "1900/01/01"

# dir_name, var_name, start_date, max_values
VARIABLES = (
    ("sea-ice", "siconc", "1850/01/01"),
    ("atmos-near-surface-air-temp", "tas", "1900/01/01"),
)
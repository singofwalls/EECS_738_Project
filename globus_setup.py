from pathlib import Path


DATA_DIR = Path(r"F:\Globus")
DATE_BASELINE = "1900/01/01"

# TODO[reece]: Convert var info to class instances and pass around objects instead of specific indices
# dir_name, var_name, is_gridded, start_date, end_date, max_values
VARIABLES = (
    # ("sea-ice", "siconc", True, "1850/01/01"),
    # ("atmos-near-surface-air-temp", "tas", True, "1900/01/01"),
    # ("specific-humidity", "huss", True, "1900/01/01"),
    # ("solar-vars", "f107", False, "1850/01/01", "2015/01/01"),
    # ("solar-vars", "tsi", False, "1850/01/01", "2015/01/01"),
    # ("solar-vars", "ap", False, "1850/01/01", "2015/01/01"),
    # ("solar-vars", "kp", False, "1850/01/01", "2015/01/01"),
    ("solar-vars", "scnum", False, "1850/01/01", "2015/01/01"),
    ("solar-vars", "scph", False, "1850/01/01", "2015/01/01"),
    ("solar-vars", "ssn", False, "1850/01/01", "2015/01/01"),
)

CSV_NAME = "values.csv"
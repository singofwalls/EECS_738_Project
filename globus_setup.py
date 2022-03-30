from pathlib import Path


DATA_DIR = Path(r"F:\Globus")
DATE_BASELINE = "1900/01/01"

# dir_name, var_name, start_date, end_date, max_values
VARIABLES = (
    # TODO[reece]: Reprocess siconc data to handle leap days using the datetime lib
    ("sea-ice", "siconc", "1850/01/01"),
    # TODO[reece]: Reprocess tas data to mean days instead of current method of truncating
    ("atmos-near-surface-air-temp", "tas", "1900/01/01"),
    # ("specific-humidity", "huss", "1900/01/01"),
    # TODO[reece]: Figure out how to process vars from solar forcings (?)
)

CSV_NAME = "values.csv"
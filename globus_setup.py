from collections import namedtuple
from pathlib import Path


DATA_DIR = Path(r"F:\Globus")
DATE_BASELINE = "1900/01/01"

# TODO[reece]: Convert var info to class instances and pass around objects instead of specific indices
# dir_name, var_name, is_gridded, start_date, end_date, max_values
Variable = namedtuple('Variable', "dir_name, var_name, is_gridded, start_date, end_date, max_values")
VARIABLES = (
    Variable("sea-ice", "siconc", True, "1850/01/01", None, None),
    Variable("atmos-near-surface-air-temp", "tas", True, "1900/01/01", None, None),
    Variable("specific-humidity", "huss", True, "1900/01/01", None, None),
    Variable("solar-vars", "f107", False, "1850/01/01", "2015/01/01", None),
    Variable("solar-vars", "tsi", False, "1850/01/01", "2015/01/01", None),
    Variable("solar-vars", "ap", False, "1850/01/01", "2015/01/01", None),
    Variable("solar-vars", "kp", False, "1850/01/01", "2015/01/01", None),
    Variable("solar-vars", "scnum", False, "1850/01/01", "2015/01/01", None),
    Variable("solar-vars", "scph", False, "1850/01/01", "2015/01/01", None),
    Variable("solar-vars", "ssn", False, "1850/01/01", "2015/01/01", None),
    Variable("solar-vars", "iprp", True, "1850/01/01", "2015/01/01", None),
    Variable("solar-vars", "iprg", True, "1850/01/01", "2015/01/01", None),
    Variable("solar-vars", "iprm", True, "1850/01/01", "2015/01/01", None),
)

CSV_NAME = "values.csv"
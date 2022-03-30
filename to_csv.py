from collections import defaultdict
from itertools import groupby
from typing import Any
from datetime import datetime

import csv
import io

import netCDF4 as nc
import numpy as np

from alive_progress import alive_it

from globus_setup import *


def _nc_to_var(dir_name: str, var_name: str, day_offset: int = 0, max_values: int = None) -> dict[int, float]:
    """
    Convert a directory of .nc dataset files to a dict by averaging the grid cells at 
    each time step.

    dir_name: The sub-directory within DATA_DIR containing the .nc files to process.
    var_name: The target variable from which to retrieve each day's value.
    day_offset: The difference in days between 1900/01/01 and the .nc files' start date.
    max_values: Cap the number of values read in at this number if given.
    """
    values = {}
    for file_name in (DATA_DIR / dir_name).iterdir():
        ds = nc.Dataset(file_name)

        # Get a list of time_steps and the mean value for that day
        time_steps = ds.variables["time"]
        means = [np.mean(x) for x in ds.variables[var_name]]
        records = zip(time_steps, means)

        # iterate the records in groups of days
        # TODO[reece]: Include end date after which to crop data (for future predictions we don't care about)
        for day, records in groupby(records, lambda r: int(r[0])):
            # Get a mean value for each day from all the records from that day
            values[day + day_offset] = np.mean([r[1] for r in records])

            if max_values and len(values) > max_values:
                break
        if max_values is not None and len(values) > max_values:
                break

    return values


def _csv_to_dict(csv_name: str) -> dict[int, dict[str, Any]]:
    """
    Convert a csv file to a mapping of days to a dictionary of variables and 
    values for each day.
    
    csv_name: The csv file to load.
    """
    current_values = defaultdict(lambda: {})
    try:
        with open(csv_name, "r") as f:
            csv_reader = csv.DictReader(f)
            try:
                fieldnames = csv_reader.fieldnames
                if fieldnames is not None:
                    current_values = defaultdict(lambda: {k: None for k in fieldnames})
                    # Convert rows of dicts with day key to mapping from days to other vars
                    # e.g. [{'day': 1, 'var': 3}] -> {1: {'var': 3}}
                    for row in csv_reader:
                        day = int(row["day"])
                        current_values[day] = {k: v for k, v in row.items() if k != "day"}
            except io.UnsupportedOperation:
                # occurs when CSV is empty
                pass
    except FileNotFoundError:
        # occurs when CSV is missing
        pass

    return current_values


def _var_to_csv(csv_name: str, var_name: str, variable: dict[int, Any], var_display_name: str = None):
    """
    If csv exists, add each day's value to existing days in csv,
    creating new days for those not already present.

    csv_name: The csv file to create or update.
    var_name: The target variable from which to retrieve each day's value.
    variable: A mapping from day numbers to the value for the given day.
    var_display_name: How to name the variable in the csv file for humans to read.
    """
    if var_display_name is None:
        var_display_name = var_name

    # Load current values for each day from the csv
    day_values = _csv_to_dict(csv_name)

    # Add new values to current values
    for day in variable:
        day_values[day][var_display_name] = variable[day]

    # Write all values back to csv
    fields_from_csv = set(tuple(day_values.values())[0].keys())
    field_names = {"day", var_display_name} | fields_from_csv
    with open(csv_name, "w", newline='') as f:
        csv_writer = csv.DictWriter(f, field_names)
        csv_writer.writeheader()
        for day in day_values:
            other_vars = {k: v for k, v in day_values[day].items() if k != "day"}
            csv_writer.writerow({'day': day, **other_vars})


def day_delta(start_date: str, end_date: str):
    """Return the number of days between two dates."""
    start = datetime.strptime(start_date, "%Y/%m/%d")
    end = datetime.strptime(end_date, "%Y/%m/%d")
    return (end - start).days


def process_var(csv_name: str, dir_name: str, var_name: str, start_date: str = DATE_BASELINE, max_values: int = None):
    """
    Get variable values from .nc file and place in .csv.

    csv_name: The csv file to create or update.
    dir_name: The sub-directory within DATA_DIR containing the .nc files to process.
    var_name: The target variable from which to retrieve each day's value.
    start_date: The date (formatted %Y/%m/%d) baseline for the day offset.
    max_values: Cap the number of values read in at this number if given.
    """

    # TODO[reece]: Get metadata for files from .nc file directly instead of hardcoding
    day_offset = day_delta(DATE_BASELINE, start_date)
    var_values = _nc_to_var(dir_name, var_name, day_offset, max_values)
    _var_to_csv(csv_name, var_name, var_values, dir_name)


if __name__ == "__main__":
    for var in alive_it(VARIABLES):
        process_var("values.csv", *var)

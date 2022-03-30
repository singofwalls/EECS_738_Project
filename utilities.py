"""Various utility functions for manipulating the data."""

import os
import csv

import netCDF4 as nc
import numpy as np

from pathlib import Path
from datetime import datetime, timedelta

from globus_setup import *


all_dirs = [f for f in DATA_DIR.iterdir() if f.is_dir()]
target_dirs = [DATA_DIR / Path(x) for x in ("solar-vars", )]


def get_metadata():
    """Print various metadata from the .nc files in the target_dirs."""
    for directory_name in target_dirs:
        first_file = os.listdir(directory_name)[0]
        ds = nc.Dataset(directory_name / first_file)

        print()
        print(directory_name)
        # print("\n".join([f"{x}, {ds.variables[x].long_name}" for x in ds.variables]))
        print(ds.variables["time"][-1])


def date_range():
    """Print the first several days in each .nc file in the target_dirs."""
    for directory_name in target_dirs:
        for file_name in directory_name.iterdir():
            ds = nc.Dataset(directory_name / file_name)
            days = ds.variables["time"]

            print()
            print(directory_name)
            print(days[:10])


def sort_csv_by_days():
    """Put all the rows in order by day."""
    rows = []
    with open(CSV_NAME, "r") as f:
        csv_reader = csv.DictReader(f)
        rows = sorted(csv_reader, key=lambda r: r["day"])

    csv_fields = set(rows[0].keys())
    with open(CSV_NAME, "w", newline='') as f:
        csv_writer = csv.DictWriter(f, csv_fields)
        csv_writer.writeheader()
        csv_writer.writerows(rows)


def reorder_csv_cols():
    """Put the day column first in the CSV and the atmos-near-surface-air-temp last."""
    
    rows = []
    with open(CSV_NAME, "r") as f:
        csv_reader = csv.DictReader(f)
        rows = list(csv_reader)

    csv_fields = set(rows[0].keys())
    if "atmos-near-surface-air-temp" in csv_fields:
        field_names = csv_fields - {"day", "atmos-near-surface-air-temp"}
        field_names = ("day",) + tuple(field_names) + ("atmos-near-surface-air-temp",)
    else:
        field_names = csv_fields - {"day"}
        field_names = ("day",) + tuple(field_names)

    with open(CSV_NAME, "w", newline='') as f:
        csv_writer = csv.DictWriter(f, field_names)
        csv_writer.writeheader()
        csv_writer.writerows(rows)


def remove_column_from_csv():
    """Delete select columns from the csv."""
    delete_cols = ["sea-ice", "atmos-near-surface-air-temp"]

    if input("Are you sure you want to delete these columns? " + str(delete_cols)).lower() != "y":
        return

    rows = []
    with open(CSV_NAME, "r") as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            rows.append({k: v for k, v in row.items() if k not in delete_cols})
    
    field_names = tuple(rows[0].keys())
    with open(CSV_NAME, "w", newline='') as f:
        csv_writer = csv.DictWriter(f, field_names)
        csv_writer.writeheader()
        csv_writer.writerows(rows)


def remove_blank_days_from_csv():
    """Remove days from CSV which have no values other than day"""
    if input("Are you sure you want to delete blank days?").lower() != "y":
        return

    rows = []
    with open(CSV_NAME, "r") as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            active_fields = [f for f in row if row[f] != "" and f != "day"]
            if active_fields:
                rows.append(row)
    
    field_names = tuple(rows[0].keys())
    with open(CSV_NAME, "w", newline='') as f:
        csv_writer = csv.DictWriter(f, field_names)
        csv_writer.writeheader()
        csv_writer.writerows(rows)


def get_date_from_offset():
    """Print the date corresponding to the given day offset."""
    DAY_OFFSET = 17531

    start = datetime.strptime(DATE_BASELINE, "%Y/%m/%d")
    end = start + timedelta(days=DAY_OFFSET)
    print(end.strftime("%Y/%m/%d"))


if __name__ == "__main__":
    get_date_from_offset()
"""Various utility functions for manipulating the data."""

import os
import csv

import netCDF4 as nc
import numpy as np

from pathlib import Path
from datetime import datetime, timedelta

from globus_setup import *


target_dirs = [f for f in DATA_DIR.iterdir() if f.is_dir()]
# target_dirs = [DATA_DIR / Path(x) for x in ("specific-humidity", )]


def get_date_range():
    """Print the start and end dates for the datasets."""
    for directory_name in target_dirs:
        start_baseline = "1900/01/01"
        end_cutoff = None
        for var in VARIABLES:
            if var.dir_name == directory_name.name:
                start_baseline = var.start_date
                if var.end_date is not None:
                    end_cutoff = (datetime.strptime(var.end_date, "%Y/%m/%d") - timedelta(days=1)).strftime("%Y/%m/%d")

        files = sorted(os.listdir(directory_name))
        first_file = files[0]
        last_file = files[-1]
        ds1 = nc.Dataset(directory_name / first_file)
        ds2 = nc.Dataset(directory_name / last_file)

        print()
        print(directory_name)
        start = float(ds1.variables["time"][0])
        end = float(ds2.variables["time"][-1])

        start_date = get_date_from_offset(start, start_baseline)
        end_date = get_date_from_offset(end, start_baseline)

        if end_cutoff is not None:
            print(start_date, "to", end_cutoff, "with future predictions to", end_date)
        else:
            print(start_date, "to", end_date)


def sort_csv_by_days():
    """Put all the rows in order by day."""
    rows = []
    with open(CSV_NAME, "r") as f:
        csv_reader = csv.DictReader(f)
        rows = sorted(csv_reader, key=lambda r: float(r["day"]))

    csv_fields = set(rows[0].keys())
    with open(CSV_NAME, "w", newline='') as f:
        csv_writer = csv.DictWriter(f, csv_fields)
        csv_writer.writeheader()
        csv_writer.writerows(rows)


def reorder_csv_cols():
    """Put the day column first in the CSV and the tas field last."""
    
    rows = []
    with open(CSV_NAME, "r") as f:
        csv_reader = csv.DictReader(f)
        rows = list(csv_reader)

    csv_fields = set(rows[0].keys())
    if "tas" in csv_fields:
        field_names = csv_fields - {"day", "tas"}
        field_names = ("day",) + tuple(field_names) + ("tas",)
    else:
        field_names = csv_fields - {"day"}
        field_names = ("day",) + tuple(field_names)

    with open(CSV_NAME, "w", newline='') as f:
        csv_writer = csv.DictWriter(f, field_names)
        csv_writer.writeheader()
        csv_writer.writerows(rows)


def remove_column_from_csv():
    """Delete select columns from the csv."""
    delete_cols = ["siconc", "tas"]

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


DAY_OFFSET = 21548.875
def get_date_from_offset(day_offset=DAY_OFFSET, baseline=DATE_BASELINE):
    """Print the date corresponding to the given day offset."""

    start = datetime.strptime(baseline, "%Y/%m/%d")
    end = start + timedelta(days=day_offset)
    return end.strftime("%Y/%m/%d")


if __name__ == "__main__":
    get_date_range()
    # get_date_from_offset()
    # sort_csv_by_days()
    # reorder_csv_cols()
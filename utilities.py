"""Various utility functions for manipulating the data."""

from collections import defaultdict
import os
import csv
import math

import netCDF4 as nc
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt

from pathlib import Path
from datetime import datetime, timedelta

from globus_setup import *


# target_dirs = [f for f in DATA_DIR.iterdir() if f.is_dir()]
target_dirs = [DATA_DIR / Path(x) for x in ("atmos", )]


def plot_temps():
    """Plot a surface temp trend line."""
    with open(CSV_NAME, "r") as f:
        csv_reader = csv.DictReader(f)
        rows = sorted(csv_reader, key=lambda r: float(r["day"]))
        y = np.array([float(r["tas"]) for r in rows])
        x = np.array([int(r["day"]) for r in rows])
    

    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.scatter(x, y, s=3, alpha=.1)
    xyears = np.array([int(get_date_from_offset(int(r), output_format="%Y")) for r in x])
    xticks = np.arange(0, len(x), step=365*7)
    yticks = np.arange(np.min(y), np.max(y), step=0.1)
    ytemps = [round(unnormalize(yt), 2) for yt in yticks]
    plt.xticks(x[xticks], xyears[xticks])
    plt.yticks(yticks, ytemps)

    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    ax.plot(x,p(x),"r--")
    
    plt.title("Global Average Surface Temperature Trend")
    plt.ylabel("Global Average Surface Temp K")
    plt.xlabel("Year")
    fig.canvas.draw()
    fig.canvas.flush_events()

    return fig, ax


def plot_temps_by_month():
    """Plot average temp by month."""
    with open(CSV_NAME, "r") as f:
        csv_reader = csv.DictReader(f)
        rows = sorted(csv_reader, key=lambda r: float(r["day"]))
        y = np.array([float(r["tas"]) for r in rows])
        x = np.array([int(r["day"]) for r in rows])
    
    months = np.array([int(get_date_from_offset(int(r), output_format="%m")) for r in x])
    monthly_temps = {month: [] for month in np.unique(months)}
    for temp, month in zip(y, months):
        monthly_temps[month].append(temp)

    xmonths = sorted(monthly_temps.keys())
    avg_temps = np.array([unnormalize(np.mean(monthly_temps[month])) for month in xmonths])

    fig = plt.figure()
    ax = fig.add_subplot(111)

    ax.scatter(xmonths, avg_temps)
    # xticks = np.arange(0, len(x), step=365*7)
    # yticks = np.arange(np.min(y), np.max(y), step=0.1)
    # ytemps = [round(unnormalize(yt), 2) for yt in yticks]
    # plt.xticks(x[xticks], xyears[xticks])
    # plt.yticks(yticks, ytemps)

    # z = np.polyfit(x, y, 1)
    # p = np.poly1d(z)
    # ax.plot(x,p(x),"r--")
    
    plt.title("Average Global Average Surface Temperature By Month")
    plt.ylabel("Average Global Average Surface Temp K")
    plt.xlabel("Month")
    fig.canvas.draw()
    fig.canvas.flush_events()

    return fig, ax


def get_dates(days=None, output_format=None):
    """Convert days to dates."""
    dates = []
    if days is None:
        days = []
        with open(CSV_NAME, "r") as f:
            csv_reader = csv.DictReader(f)
            rows = sorted(csv_reader, key=lambda r: float(r["day"]))
            for r in rows:
                days.append(int(r["day"]))

    for day in days:
        dates.append(get_date_from_offset(day, output_format=output_format))
    return np.array(dates)


def get_date_range():
    """Print the start and end dates for the datasets."""
    for directory_name in target_dirs:
        start_baseline = "1900/01/01"
        end_cutoff = None
        for var in VARIABLES:
            if var.dir_name == directory_name.name:
                start_baseline = var.start_date
                if var.end_date is not None:
                    # Substract one day from end_date for inclusive end date
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


def remove_incomlete_days_from_csv():
    """Remove days from CSV which have one or more missing values."""
    if input("Are you sure you want to delete incomplete days?").lower() != "y":
        return

    rows = []
    with open(CSV_NAME, "r") as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            empty_fields = [f for f in row if row[f] == ""]
            if not empty_fields:
                rows.append(row)
    
    field_names = tuple(rows[0].keys())
    with open(CSV_NAME, "w", newline='') as f:
        csv_writer = csv.DictWriter(f, field_names)
        csv_writer.writeheader()
        csv_writer.writerows(rows)


def normalize_values_in_csv():
    """Normalize all columns to a range of 0 through 1."""

    remove_incomlete_days_from_csv()
    if input("Are you sure you want to normalize the csv?").lower() != "y":
        return

    cols = defaultdict(list)
    with open(CSV_NAME, "r") as f:
        csv_reader = csv.DictReader(f)
        for row in csv_reader:
            for field_name in row:
                cols[field_name].append(row[field_name])

    for field_name, data in cols.items():
        if field_name == "day":
            continue
        data = np.array([float(d) for d in data])
        max_ = np.max(data)
        min_ = np.min(data)

        normalized = (data - min_) / (max_ - min_)
        cols[field_name] = normalized

    rows = []
    num_rows = len(tuple(cols.values())[0])
    # Put day first and tas last
    field_names = ("day", ) + tuple(set(cols.keys()) - {"day", "tas"}) + ("tas", )
    for i in range(num_rows):
        rows.append({k: cols[k][i] for k in field_names})

    with open(CSV_NAME, "w", newline='') as f:
        csv_writer = csv.DictWriter(f, field_names)
        csv_writer.writeheader()
        csv_writer.writerows(rows)


DAY_OFFSET = 38878
def get_date_from_offset(day_offset=DAY_OFFSET, baseline=DATE_BASELINE, output_format="%Y/%m/%d"):
    """Print the date corresponding to the given day offset."""

    start = datetime.strptime(baseline, "%Y/%m/%d")
    end = start + timedelta(days=day_offset)
    return end.strftime(output_format)


def unnormalize(normed: float):
    """Unnormalize temperature data using the max and min values from the tas column."""

    # Get max and min temps for display of non-normalized values
    try:
        unnormalize.min_temp
    except AttributeError:
        with open("values_complete.csv", "r") as f:
            csv_reader = csv.DictReader(f)
            unnormalize.min_temp = math.inf
            unnormalize.max_temp = -math.inf
            for row in csv_reader:
                if (t := float(row["tas"])) > unnormalize.max_temp:
                    unnormalize.max_temp = t
                if (t := float(row["tas"])) < unnormalize.min_temp:
                    unnormalize.min_temp = t
    
    return normed * (unnormalize.max_temp - unnormalize.min_temp) + unnormalize.min_temp


if __name__ == "__main__":
    # plot_temps()
    # plt.show()
    # get_date_from_offset()
    # sort_csv_by_days()
    # reorder_csv_cols()
    # print(unnormalize(70))
    plt, ax = plot_temps_by_month()
    plt.show()
    input()
"""Print the date corresponding to the given day offset."""

from datetime import datetime, timedelta
from globus_setup import DATE_BASELINE

DAY_OFFSET = -18262

start = datetime.strptime(DATE_BASELINE, "%Y/%m/%d")
end = start + timedelta(days=DAY_OFFSET)
print(end.strftime("%Y/%m/%d"))

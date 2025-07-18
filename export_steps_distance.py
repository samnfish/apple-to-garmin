import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from collections import defaultdict
import csv
import re

def sanitize_filename(name):
    return re.sub(r'[^A-Za-z0-9_]+', '_', name.strip())

def parse_apple_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S %z").astimezone(timezone.utc)

def to_local_date(utc_dt):
    local_dt = utc_dt + timedelta(hours=TIMEZONE_OFFSET_HOURS)
    return local_dt.strftime("%Y-%m-%d")

def extract_unique_devices(xml_root):
    devices = set()
    for record in xml_root.findall("Record"):
        src = record.get("sourceName")
        if src:
            devices.add(src.replace("\xa0", " "))  # Normalize Apple’s weird space
    return sorted(devices)

def device_matches(device_name, targets):
    normalized = device_name.replace('\xa0', ' ')
    for target in targets:
        pattern = target["pattern"]
        if target["regex"]:
            if re.search(pattern, normalized):
                return True
        else:
            if normalized == pattern:
                return True
    return False

def parse_device_selection(input_str, device_list, global_max_date=None):
    selections = input_str.split(",")
    parsed = []

    for sel in selections:
        match = re.match(r"(\d+)(?:-(\d{8})-(\d{8}))?", sel.strip())
        if not match:
            continue

        index = int(match.group(1)) - 1
        if 0 <= index < len(device_list):
            start_date = match.group(2)
            end_date = match.group(3)
            end_date_dt = datetime.strptime(end_date, "%Y%m%d") if end_date else None
            if not end_date_dt and global_max_date:
                end_date_dt = global_max_date

            device_entry = {
                "pattern": device_list[index],
                "regex": False,
                "start_date": datetime.strptime(start_date, "%Y%m%d") if start_date else None,
                "end_date": end_date_dt,
            }
            parsed.append(device_entry)

    return parsed

# ------------------ USER INPUT ------------------

# Timezone offset
print("Enter your timezone offset (e.g., -7 for PDT, 0 for UTC, 1 for CET):")
try:
    TIMEZONE_OFFSET_HOURS = int(input("Timezone Offset: "))
except ValueError:
    print("Invalid input. Defaulting to UTC (0).")
    TIMEZONE_OFFSET_HOURS = 0

# Choose metric
print("\n Choose metric to export:")
print("1. Step Count")
print("2. Distance Walking + Running")
metric_choice = input("Enter 1 or 2: ").strip()

if metric_choice == "1":
    METRICS = ["HKQuantityTypeIdentifierStepCount"]
    output_header = "Steps"
elif metric_choice == "2":
    METRICS = ["HKQuantityTypeIdentifierDistanceWalkingRunning"]
    output_header = "Distance"
else:
    print("Invalid selection. Exiting.")
    exit(1)

# Optional max date limit
max_date_input = input("\n  Enter the date you want data exported UP TO in YYYYMMDD format. You likely want a recent date. (or press Enter to skip): ").strip()
try:
    MAX_DATE_UTC = datetime.strptime(max_date_input, "%Y%m%d") if max_date_input else None
except ValueError:
    print("Invalid format. Skipping date limit.")
    MAX_DATE_UTC = None

# Input Apple Health export file
INPUT_FILE = "export.xml"

# ------------------ PARSE XML ------------------

print("Scanning devices from export.xml...")
tree = ET.parse(INPUT_FILE)
root = tree.getroot()

all_devices = extract_unique_devices(root)

print("\nAvailable Devices:")
for idx, device in enumerate(all_devices, 1):
    print(f"{idx}: {device}")

print("\n Select device(s) and optional date ranges (YYYYMMDD)")
print("Format: index-startdate-enddate, or just index (e.g., 1-20200101-20240101,3)")
print(f"If you omit an end date, it will default to {MAX_DATE_UTC.date() if MAX_DATE_UTC else 'no limit'}")
selection_input = input("Your selection: ")

TARGET_DEVICES = parse_device_selection(selection_input, all_devices, global_max_date=MAX_DATE_UTC)

if not TARGET_DEVICES:
    print("No valid devices selected. Exiting.")
    exit(1)

# ------------------ EXTRACT DATA ------------------

data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

for record in root.findall("Record"):
    metric = record.get("type")
    if metric not in METRICS:
        continue

    device = record.get("sourceName")
    if not device or not device_matches(device, TARGET_DEVICES):
        continue

    value_str = record.get("value")
    if not value_str:
        continue

    try:
        value = float(value_str)
    except ValueError:
        continue

    end_time_utc = parse_apple_date(record.get("endDate"))
    match_found = False
    for target in TARGET_DEVICES:
        pattern = target["pattern"]
        start_limit = target.get("start_date")
        end_limit = target.get("end_date")
        normalized = device.replace('\xa0', ' ')

        if pattern == normalized:
            local_date = end_time_utc + timedelta(hours=TIMEZONE_OFFSET_HOURS)
            if start_limit and local_date.date() < start_limit.date():
                continue
            if end_limit and local_date.date() > end_limit.date():
                continue
            match_found = True
            break

    if not match_found:
        continue

    date_str = to_local_date(end_time_utc)
    data[metric][device][date_str].append(value)

# ------------------ WRITE FILES ------------------

for metric in data:
    for device in data[metric]:
        cleaned_metric = metric.replace("HKQuantityTypeIdentifier", "")
        filename = f"{sanitize_filename(device)}-{cleaned_metric}.csv"
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Date", output_header])
            for date in sorted(data[metric][device]):
                values = data[metric][device][date]
                if "StepCount" in metric:
                    total = int(round(sum(values)))
                else:
                    total = round(sum(values), 2)
                writer.writerow([date, total])
        print(f"Wrote {filename}")

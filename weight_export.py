import re
import csv
import sys
from datetime import datetime
from pathlib import Path

# ─── FILE PATHS ────────────────────────────────────────────────────────────────
EXPORT_FILE = Path(__file__).parent / "export.xml"
OUTPUT_CSV = Path(__file__).parent / "weights_with_bmi.csv"

# Regex patterns to extract weight and date
TYPE_KEYWORD = "BodyMass"
FULL_TYPE = f'HKQuantityTypeIdentifier{TYPE_KEYWORD}'
VALUE_RE = re.compile(r'value="([\d.]+)"')
DATE_RE  = re.compile(r'startDate="([^"]+)"')

def main():
    if not EXPORT_FILE.exists():
        print(f"Cannot find {EXPORT_FILE}. Make sure export.xml is in the same folder.")
        sys.exit(1)

    # Prompt for user height
    try:
        height_input = input("Enter your height in inches (e.g., 70.0): ").strip()
        height_raw = float(height_input)
        if height_raw <= 0:
            raise ValueError
        # Round the height to the nearest tenth.
        HEIGHT_IN_INCHES = round(height_raw, 1)
    except ValueError:
        print("Invalid height entered. Please enter a positive number.")
        sys.exit(1)

    # Read export.xml and extract BodyMass records
    weights_by_date = {}
    with EXPORT_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            if f'type="{FULL_TYPE}"' in line:
                v = VALUE_RE.search(line)
                d = DATE_RE.search(line)
                if not (v and d):
                    continue
                try:
                    weight = float(v.group(1))
                    dt = datetime.strptime(d.group(1), "%Y-%m-%d %H:%M:%S %z")
                    date_key = dt.date().isoformat()
                    # If multiple entries per day, keep the last one
                    weights_by_date[date_key] = weight
                except Exception as e:
                    print(f"Skipping line due to parse error: {e}")

    if not weights_by_date:
        print(f"No records of type={FULL_TYPE} found in {EXPORT_FILE}")
        sys.exit(1)

    # Pre-calc for BMI
    height_sq = HEIGHT_IN_INCHES ** 2
    bmi_factor = 703.0

    # Write CSV with the first two lines (title and header) unquoted.
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as csvfile:
        # Write Garmin-style headers (first two lines unquoted)
        csvfile.write("Body\n")
        csvfile.write("Date,Weight,BMI,Fat,Resting Heart Rate,Exertive Heart Rate,IFTTT\n")

        # Use csv.writer for the data rows (which will be quoted)
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)

        for date in sorted(weights_by_date):
            weight = weights_by_date[date]
            # Round weight to the nearest tenth.
            rounded_weight = round(weight, 1)
            # Compute BMI using the rounded weight.
            bmi = round((rounded_weight / height_sq) * bmi_factor, 2)
            # Format the values explicitly.
            writer.writerow([
                date,
                f"{rounded_weight:.1f}",
                f"{bmi:.2f}",
                "0", "0", "0", "0"
            ])

    print(f"Output saved to: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()

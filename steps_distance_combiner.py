import csv
import sys

if len(sys.argv) != 3:
    print("Usage: python3 merge_steps_distance.py steps.csv distance.csv")
    sys.exit(1)

steps_file = sys.argv[1]
distance_file = sys.argv[2]
output_file = "final-steps-distance.csv"

# Load Steps
steps_data = {}
with open(steps_file, newline="") as f:
    reader = csv.DictReader(f)
    if "Steps" not in reader.fieldnames:
        raise ValueError(f"{steps_file} must contain 'Steps' as second column.")
    for row in reader:
        try:
            steps_data[row["Date"]] = int(round(float(row["Steps"])))
        except (ValueError, KeyError):
            continue

# Load Distance
distance_data = {}
with open(distance_file, newline="") as f:
    reader = csv.DictReader(f)
    if "Distance" not in reader.fieldnames:
        raise ValueError(f"{distance_file} must contain 'Distance' as second column.")
    for row in reader:
        try:
            distance_data[row["Date"]] = round(float(row["Distance"]), 2)
        except (ValueError, KeyError):
            continue

# Union of all unique dates
all_dates = sorted(set(steps_data) | set(distance_data))

# Write Output
with open(output_file, "w", newline="") as f:
    # Write unquoted lines manually
    f.write("Activities\n")
    f.write("Date,Calories Burned,Steps,Distance,Floors,Minutes Sedentary,Minutes Lightly Active,Minutes Fairly Active,Minutes Very Active,Activity Calories\n")

    writer = csv.writer(f, quoting=csv.QUOTE_ALL)
    for date in all_dates:
        steps = steps_data.get(date, 0)
        distance = distance_data.get(date, 0.0)
        row = [
            date,
            "0",
            str(steps),
            f"{distance:.2f}",
            "0", "0", "0", "0", "0", "0"
        ]
        writer.writerow(row)

print(f"Output saved to: {output_file}")


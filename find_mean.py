import sys
import csv

def load_csv(filepath):
    data = {}
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        if len(header) < 2:
            raise ValueError(f"{filepath} must have at least two columns")
        metric_name = header[1].strip()
        for row in reader:
            if len(row) < 2:
                continue
            date = row[0].strip()
            try:
                value = float(row[1].strip())
                data[date] = value
            except ValueError:
                continue
    return metric_name, data

def main():
    if len(sys.argv) < 3:
        print("Usage: python mean_metric.py <file1.csv> <file2.csv> [<file3.csv> ...]")
        sys.exit(1)

    input_files = sys.argv[1:]
    all_data = []
    metric_name = None

    for i, file in enumerate(input_files):
        try:
            name, data = load_csv(file)
            if i == 0:
                metric_name = name
            elif name != metric_name:
                print(f"Column mismatch in {file}: expected '{metric_name}', got '{name}'")
                sys.exit(1)
            all_data.append(data)
        except Exception as e:
            print(f"Error reading {file}: {e}")
            sys.exit(1)

    # Combine all dates
    all_dates = sorted(set().union(*(d.keys() for d in all_data)))
    result = {}

    for date in all_dates:
        values = [d[date] for d in all_data if date in d]
        if not values:
            continue
        avg = sum(values) / len(values)
        if metric_name.lower() == "steps":
            result[date] = int(round(avg))
        else:
            result[date] = round(avg, 2)

    output_file = f"mean-{metric_name}.csv"
    with open(output_file, "w", newline="") as f_out:
        writer = csv.writer(f_out)
        writer.writerow(["Date", metric_name])
        for date in all_dates:
            writer.writerow([date, result[date]])

    print(f"Output written to {output_file}")

if __name__ == "__main__":
    main()

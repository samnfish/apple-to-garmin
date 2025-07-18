# Apple Health to Garmin Connect Migration Scripts

This repo contains Python scripts to help migrate your weight, step count and distance data from **Apple Health** (via the `export.xml` file) to **Garmin Connect**

---

## Disclaimer

- **Initial Workouts Import:**  
  I first imported all my workouts using [RunGap](https://www.rungap.com/) before running these scripts
    - For any Step and Distance data imported *after* the date of your first recorded workout, you may see **large negative calorie numbers** for those dates in Garmin Connect
    - Unsure how to fix or why this happens at this time. Perhaps someone can try importing one day while adjusting the calorie columns for that date and see how Garmin behaves with the adjusted values
- **The scripts are mostly generate with AI. Do what you will with this information**

---

## How It Works

These scripts parse your Apple Health data (`export.xml`) and prepare it for upload to Garmin Connect

**Supports:**
- Steps
- Distance
- Weight

---

## Requirements

- [Python 3](https://www.python.org/)
- Your Apple Health `export.xml` file (export: Health app > Profile > Export All Health Data)
- Download and unzip the export into a device that has python3 installed
- Knowing when you started/stopped using your past Apple device(s) is helpful for more accurate data. If you keep or loan out old iPhones with your Apple ID, they will continue to write into your Health data

---

## Apple Health Data Format Caveats

- This method assumes Apple will **not** change their current health export format, for example:
    ```
    <Record type="HKQuantityTypeIdentifierStepCount" sourceName="iPhone" ... value="46"/>
    ```

---

## Usage Instructions for Migrating Weight Data

To migrate your Apple Health weight data:

1. Place the `export_weight.py` script in the same directory as your `export.xml`
2. Run the script:
    ```
    python3 export_weight.py
    ```
3. Enter your height in inches
4. The script will output a file that is ready to import directly into Garmin Connect
5. Do a spot check with an online BMI calculator to ensure calculations in the file are correct
6. Upload to Garmin Connect
    - Use the [Garmin Connect web uploader](https://connect.garmin.com/modern/import-data) to import the finished file
    - Make sure to correctly select the correct measurement type when uploading to Garmin Connect, i.e. Statute or Metric

---

## Usage Instructions for Migrating Steps/Distance

### **Preamble**
Important _only_ if you were using more than 1 Apple device at a time over a given period as the script aims to take mean values between the multiple devices.

For Steps and Distance, given that you paired an Apple Watch and iPhone over the same time period, both devices will be logging steps and distance walked throughout the time you are using the devices. Apple has its own calculations in its backend that selectively calculates the total number of Steps taken and Distance walked/ran in a day.

For this reason, it's highly recommended that you figure out the time ranges you want to extract data from before starting the extraction.
- Here is an example:
  - User Bob has had 3 Apple devices in the past.
    - Device No. 1: iPhone XS between 2019-01-01 to 2022-12-31, but kept around and used sparingly at home until present day
    - Device No. 2: iPhone 14 between 2023-01-01 to Present
    - Device No. 3: Apple Watch S8 between 2023-02-01 to 2025-06-01
- Ideally, Bob would extract Steps and Distance with the following CLI input:
> \>1-20190101-20221231,2-20230101-20230131,3

This input explained:
- 1-20190101-20221231: Bob is exporting all of his XS metrics until he upgraded to the 14. Nothing past 2022-12-31 as days where the XS records steps will skew the result.
- 2-20230101-20230131: 14 metrics up until the date he starts using his AW
- 3: All of his AW steps as Bob never takes off his AW except to charge

But why not just export all data for all devices?
- You can definitely do this, but if one device has an extremely low amount of steps for one day (i.e., you kept your previous iPhone around and it records a non-zero amount of steps on any given day), it will bring the total mean value for that date down, thus being less accurate to what was actually recorded that day

2. **Prepare**
    - Place all scripts (`export_steps_distance.py`, `find_mean.py`, `steps_distance_combiner.py`, etc.) in the same directory as your `export.xml`.

3. **Run `export_steps_distance.py` (You will need to run this two or more times)**
    > python3 export_steps_distance.py
    - For steps:
        - Select your timezone, this ensures the parsed metrics' timezone aligns with how your Apple Health displays each day's data
        - Choose `1` for steps
        - Optionally choose a max date to export upto
        - Select your device(s) and optionally define the date range for your device(s)
    - For distance:
        - Select your timezone, this ensures the parsed metrics' timezone aligns with how your Apple Health displays each day's data
        - Choose `2` for distance
        - Optionally choose a max date to export upto
        - Again, specify device(s) and *strongly* recommend defining a date range (to reduce skewed data points)
        - The exported distance data will either be in Miles or KM depending on what measurment system is used by your Apple Health
     
5. **Run `find_mean.py`**
    - First, run against all *step* csv files and generate a mean-Steps.csv
      > python3 find_mean.py dev1_steps.csv dev2_steps.csv dev3_steps.csv ...
    - Then, run again against all *distance* csv files and generate a mean-Distance.csv
      > python3 find_mean.py dev1_distance.csv dev2_distance.csv dev3_distance.csv ...

6. **Run `steps_distance_combiner.py`**
    - Use with your final step and distance files, must be in order as such:
      > python3 steps_distance_combiner.py mean-Steps.csv mean-Distance.csv

7. **Review**
    - Carefully cross-check the final csv with your Apple Health (if available) stats for accuracy
    - Manual edits may be required if results look off

8. **Upload to Garmin Connect**
    - Use the [Garmin Connect web uploader](https://connect.garmin.com/modern/import-data) to import the finished file

---

## License

MIT License

---

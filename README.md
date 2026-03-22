# PET Project: Investigation into Cardiac Fitness Through the Analysis of Sympathovagal Balance

This project analyzes ECG (electrocardiogram) and IMU (Inertial Measurement Unit) data collected from 16 subjects performing 7 different physical activities to assess cardiac fitness through RR interval analysis and heart rate variability.

## Project Overview

The study aims to:
- Measure ECG and physical motion data during various activities
- Extract RR intervals from ECG signals using peak detection algorithms
- Analyze heart rate variability across different activities
- Compare cardiac responses between individuals and activities

## Data Structure

The dataset consists of 16 subjects (sample00 to sample15), each with:
- `meta.json`: Subject metadata including age, sex, height, weight, resting heart rate, and activity timestamps
- `recordXX.csv`: Time-series data from Shimmer sensors including ECG channels, accelerometers, gyroscopes, and magnetometers

## Experimental Protocol

The actual experimental protocol followed was:

1. **Sit**: 1 minute
2. **Stand**: 1 minute  
3. **Buffer time / to downstairs EG with elevator**: 3 minutes
4. **Walk upstairs**: 2 minutes
5. **Walk normal**: 1 minute
6. **Walk downstairs**: 2 minutes
7. **Walk normal**: 1 minute
8. **Skipping**: 2 minutes
9. **Walk normal**: 1 minute
10. **Running**: 2 minutes
11. **Walk afterwards normally**: 2 minutes +

Note: The PDF description mentioned 120-second measurements, but the actual protocol included longer durations and a buffer period for transitioning between locations.

## Methodology

1. **Data Loading**: Load metadata and sensor data for each subject
2. **RR Interval Extraction**:
   - Use LA-RA ECG channel for R-peak detection
   - Apply peak detection algorithm with adaptive thresholding
   - Calculate RR intervals as time differences between consecutive R peaks
3. **Statistical Analysis**:
   - Compute mean and standard deviation of RR intervals per activity
   - Generate histograms showing RR interval distributions
   - Calculate heart rates from RR interval means

## Key Findings

- **Resting Activities** (Sitting, Standing): Higher heart rates and lower variability
- **Moderate Activities** (Walking, Climbing): Moderate heart rates with increased variability
- **High-Intensity Activities** (Skipping, Running): Lower heart rates during exertion with higher variability

## Time Series Analysis

The `rr_time_series_example.png` shows how RR intervals change over the course of the experimental protocol, providing insight into the dynamic cardiac response to progressive physical activities. The plot overlays activity segments, allowing visualization of heart rate adaptation throughout the protocol.

## Files

- `main.py`: Main analysis script
- `rr_intervals_histograms.png`: Generated histograms for all activities
- `rr_time_series_example.png`: Time series plot of RR intervals over the experimental protocol for one subject
- `extract_pdf.py`: Utility script for PDF text extraction
- `sampleXX/`: Individual subject data directories
  - `meta.json`: Subject demographics and activity timing
  - `recordXX.csv`: Raw ECG/IMU sensor data (excluded from repository due to size >200MB each)

## Data Availability

**Raw sensor data** (`recordXX.csv` files) are not included in this repository due to their large size (>200MB each). These files contain:

- ECG signals from LA-RA lead (24-bit resolution)
- 3-axis accelerometer data (LN and WR positions)
- Gyroscope data (3-axis)
- Magnetometer data (3-axis)
- Timestamp data (Unix milliseconds)

To reproduce the analysis, you will need access to the original CSV files. The analysis script (`main.py`) is designed to work with the data structure present in these files.

## Requirements

- Python 3.10+
- pandas
- numpy
- matplotlib
- scipy

## Usage

Run the analysis:
```bash
python main.py
```

This will process all subject data and generate statistical summaries and histograms.

## Discussion

The analysis reveals clear differences in cardiac autonomic responses across activities:
- Higher physical exertion correlates with shorter RR intervals (higher heart rates)
- Resting states show more stable heart rhythms
- Individual variations suggest differences in cardiovascular fitness levels

The sympathovagal balance, indicated by RR interval variability, shows activity-dependent modulation, with higher variability during dynamic activities suggesting better autonomic adaptability.
"""
PET Project: Investigation into Cardiac Fitness Through the Analysis of Sympathovagal Balance

This project analyzes ECG data from 16 subjects performing 7 different activities to assess cardiac fitness
through RR interval analysis and heart rate variability.
"""

import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import warnings
warnings.filterwarnings('ignore')

# Constants
SAMPLE_RATE = 512  # Hz
ACTIVITIES = ['Sitting', 'Standing', 'Walking', 'Climb UP', 'Climb DOWN', 'Skipping', 'Running']

def load_sample_data(sample_dir):
    """Load meta.json and record.csv for a sample."""
    meta_path = os.path.join(sample_dir, 'meta.json')
    if not os.path.exists(meta_path):
        meta_path = os.path.join(sample_dir, 'metda.json')  # Handle typo in sample01

    record_path = os.path.join(sample_dir, f'record{os.path.basename(sample_dir)[6:]}.csv')

    with open(meta_path, 'r') as f:
        meta = json.load(f)

    # Load CSV with low_memory=False to handle mixed types, skip first row
    df = pd.read_csv(record_path, sep='\t', low_memory=False, skiprows=1)

    # Detect device ID from timestamp column
    timestamp_col = [col for col in df.columns if 'Timestamp' in col][0]
    ecg_col = [col for col in df.columns if 'ECG_LA-RA_24BIT_CAL' in col][0]

    # Convert numeric columns
    numeric_cols = [timestamp_col, ecg_col]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return meta, df, timestamp_col, ecg_col

def detect_r_peaks(ecg_signal, sample_rate=512):
    """Detect R peaks in ECG signal using scipy find_peaks."""
    # Use LA-RA lead for R peak detection
    ecg = ecg_signal.values

    # Simple peak detection - in practice, might need more sophisticated algorithm
    # Find peaks with minimum height (adjust based on data)
    peaks, _ = find_peaks(ecg, height=np.mean(ecg) + 2*np.std(ecg), distance=sample_rate*0.4)  # min 0.4s between peaks

    return peaks

def extract_rr_intervals(peaks, timestamps):
    """Extract RR intervals from peak indices."""
    if len(peaks) < 2:
        return np.array([])

    rr_intervals = np.diff(timestamps[peaks])  # in seconds
    return rr_intervals

def process_sample(sample_dir):
    """Process a single sample and return RR statistics for each activity."""
    meta, df, timestamp_col, ecg_col = load_sample_data(sample_dir)

    # Convert timestamp to seconds from start
    df['timestamp_sec'] = (df[timestamp_col] - df[timestamp_col].min()) / 1000

    results = {}
    all_rr_times = []
    all_rr_values = []
    
    for activity in meta['activities']:
        name = activity['name']
        start = activity['start_sec']
        end = activity['end_sec']

        # Extract segment
        mask = (df['timestamp_sec'] >= start) & (df['timestamp_sec'] <= end)
        segment = df[mask]

        if len(segment) == 0:
            continue

        # Detect peaks
        peaks = detect_r_peaks(segment[ecg_col])

        # Extract RR intervals
        rr = extract_rr_intervals(peaks, segment['timestamp_sec'].values)

        if len(rr) > 0:
            results[name] = {
                'rr_intervals': rr,
                'mean_rr': np.mean(rr),
                'std_rr': np.std(rr),
                'count': len(rr)
            }
            
            # Collect for time series
            rr_times = segment['timestamp_sec'].values[peaks[:-1]]  # Time of each RR interval
            all_rr_times.extend(rr_times)
            all_rr_values.extend(rr)

    return meta['id'], results, meta, all_rr_times, all_rr_values

def main():
    """Main function to process all samples and create plots."""
    base_dir = 'd:\\Desktop\\PET'

    all_results = {}
    subject_info = {}
    time_series_data = {}

    # Process all samples
    for i in range(16):  # sample00 to sample15
        sample_dir = os.path.join(base_dir, f'sample{i:02d}')
        if os.path.exists(sample_dir):
            print(f"Processing sample {i:02d}")
            subject_id, results, meta, rr_times, rr_values = process_sample(sample_dir)
            all_results[subject_id] = results
            time_series_data[subject_id] = {'times': rr_times, 'rr': rr_values}

            # Load subject info
            subject_info[subject_id] = {
                'sex': meta['sex'],
                'age': meta['age'],
                'height': meta['height'],
                'weight': meta['weight'],
                'rest_bpm': meta['rest_bpm']
            }

    # Collect RR intervals by activity
    activity_rr = {activity: [] for activity in ACTIVITIES}

    for subject, results in all_results.items():
        for activity, stats in results.items():
            if activity in activity_rr:
                activity_rr[activity].extend(stats['rr_intervals'])

    # Plot histograms
    fig, axes = plt.subplots(4, 2, figsize=(15, 20))
    axes = axes.flatten()

    for i, activity in enumerate(ACTIVITIES):
        ax = axes[i]
        if activity_rr[activity]:
            ax.hist(activity_rr[activity], bins=50, alpha=0.7, edgecolor='black')
            ax.set_title(f'{activity} - RR Intervals Distribution')
            ax.set_xlabel('RR Interval (seconds)')
            ax.set_ylabel('Frequency')

            # Add statistics
            mean_rr = np.mean(activity_rr[activity])
            std_rr = np.std(activity_rr[activity])
            ax.axvline(mean_rr, color='red', linestyle='--', label=f'Mean: {mean_rr:.3f}s')
            ax.axvline(mean_rr + std_rr, color='orange', linestyle=':', label=f'+1 STD: {mean_rr+std_rr:.3f}s')
            ax.axvline(mean_rr - std_rr, color='orange', linestyle=':', label=f'-1 STD: {mean_rr-std_rr:.3f}s')
            ax.legend()
        else:
            ax.text(0.5, 0.5, f'No data for {activity}', ha='center', va='center', transform=ax.transAxes)

    plt.tight_layout()
    plt.savefig('rr_intervals_histograms.png', dpi=300, bbox_inches='tight')
    # plt.show()  # Commented out for headless execution

    # Plot time series for sample 00 as example
    example_subject = '00'
    sample_dir = os.path.join(base_dir, 'sample00')
    _, _, _, rr_times, rr_values = process_sample(sample_dir)
    
    plt.figure(figsize=(15, 8))
    plt.plot(rr_times, rr_values, 'b-', alpha=0.7, linewidth=1)
    plt.xlabel('Time (seconds)')
    plt.ylabel('RR Interval (seconds)')
    plt.title(f'RR Intervals Over Time - Subject {example_subject} (Following Experimental Protocol)')
    
    # Add activity markers
    activity_colors = {
        'Sitting': 'red',
        'Standing': 'orange', 
        'Walking': 'green',
        'Climb UP': 'blue',
        'Climb DOWN': 'purple',
        'Skipping': 'brown',
        'Running': 'black'
    }
    
    # Load meta for activity segments
    with open(os.path.join(sample_dir, 'meta.json'), 'r') as f:
        meta = json.load(f)
    
    for activity in meta['activities']:
        name = activity['name']
        start = activity['start_sec']
        end = activity['end_sec']
        color = activity_colors.get(name, 'gray')
        plt.axvspan(start, end, alpha=0.1, color=color, label=name)
    
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('rr_time_series_example.png', dpi=300, bbox_inches='tight')
    # plt.show()  # Commented out for headless execution

    # Print summary statistics
    print("\nSummary Statistics:")
    print("=" * 50)
    for activity in ACTIVITIES:
        if activity_rr[activity]:
            rr_data = activity_rr[activity]
            print(f"{activity}:")
            print(f"  Mean RR: {np.mean(rr_data):.3f}s")
            print(f"  Std RR: {np.std(rr_data):.3f}s")
            print(f"  Total intervals: {len(rr_data)}")
            print(f"  Heart Rate (1/mean): {60/np.mean(rr_data):.1f} bpm")
            print()

    # Discussion
    print("Discussion:")
    print("=" * 50)
    print("1. The histograms show the distribution of RR intervals across all subjects for each activity.")
    print("2. Activities with higher physical exertion (running, skipping) typically show shorter mean RR intervals,")
    print("   indicating higher heart rates and lower heart rate variability.")
    print("3. Resting activities (sitting, standing) show longer RR intervals with higher variability.")
    print("4. The standard deviation indicates the level of sympathovagal balance - higher STD suggests better balance.")
    print("5. Individual differences can be observed in the spread of the histograms.")

if __name__ == "__main__":
    main()
"""
Enhanced Training Data Generator for AI Load Balancer
Includes ALL spike types to improve model performance on diverse traffic patterns

Run this in Google Colab to generate synthetic_k8s_load_enhanced.csv
Then train models and download the .pkl files
"""

import numpy as np
import pandas as pd

# Set random seed for reproducibility
np.random.seed(42)

print("🚀 Enhanced Training Data Generator")
print("=" * 60)

# =====================================================================
# CONFIGURATION
# =====================================================================
TOTAL_DURATION = 10 * 24 * 3600  # 10 days in seconds
BASE_PODS = 5

print(f"⏱️  Total duration: {TOTAL_DURATION // 3600} hours ({TOTAL_DURATION // 86400} days)")
print(f"📊 Expected rows: ~{TOTAL_DURATION:,}")

# =====================================================================
# TRAFFIC PATTERN GENERATORS
# =====================================================================

def daily_baseline_pattern(t):
    """Generate realistic daily traffic pattern with peaks and valleys"""
    hour = (t % 86400) / 3600
    
    # Morning ramp-up (6am-9am)
    if 6 <= hour < 9:
        morning_boost = 20 * ((hour - 6) / 3)
    else:
        morning_boost = 0
    
    # Lunch spike (12pm-1pm)
    if 12 <= hour < 13:
        lunch_boost = 30
    else:
        lunch_boost = 0
    
    # Evening peak (5pm-8pm)
    if 17 <= hour < 20:
        evening_boost = 40 * np.sin(np.pi * (hour - 17) / 3)
    else:
        evening_boost = 0
    
    # Base pattern
    base = 60 + 20 * np.sin(2 * np.pi * t / 86400)
    noise = np.random.normal(0, 5)
    
    return max(10, base + morning_boost + lunch_boost + evening_boost + noise)


def generate_sudden_spikes(duration, count=150):
    """Generate sudden sharp spikes (like sudden_spike test case)"""
    spikes = []
    positions = np.random.choice(duration, count, replace=False)
    
    for pos in positions:
        start = int(pos)
        spike_duration = np.random.randint(30, 80)  # 30-80 seconds
        magnitude = np.random.uniform(3.5, 5.0)  # 3.5x-5x multiplier
        spikes.append(('sudden', start, spike_duration, magnitude))
    
    return spikes


def generate_gradual_ramps(duration, count=80):
    """Generate gradual ramp-ups and ramp-downs"""
    ramps = []
    positions = np.random.choice(duration, count, replace=False)
    
    for pos in positions:
        start = int(pos)
        ramp_duration = np.random.randint(300, 600)  # 5-10 minutes
        peak_magnitude = np.random.uniform(2.0, 3.5)
        ramps.append(('gradual', start, ramp_duration, peak_magnitude))
    
    return ramps


def generate_sustained_bursts(duration, count=60):
    """Generate long sustained high load periods (like extreme_burst)"""
    bursts = []
    positions = np.random.choice(duration, count, replace=False)
    
    for pos in positions:
        start = int(pos)
        burst_duration = np.random.randint(600, 1800)  # 10-30 minutes
        magnitude = np.random.uniform(3.0, 4.5)  # High sustained load
        bursts.append(('sustained', start, burst_duration, magnitude))
    
    return bursts


def generate_oscillating_patterns(duration, count=40):
    """Generate oscillating traffic patterns"""
    oscillations = []
    positions = np.random.choice(duration, count, replace=False)
    
    for pos in positions:
        start = int(pos)
        pattern_duration = np.random.randint(400, 800)
        base_magnitude = np.random.uniform(1.5, 2.5)
        oscillations.append(('oscillating', start, pattern_duration, base_magnitude))
    
    return oscillations


def generate_cascading_spikes(duration, count=30):
    """Generate cascading spikes (sequential spikes getting closer)"""
    cascades = []
    positions = np.random.choice(duration - 1000, count, replace=False)
    
    for pos in positions:
        start = int(pos)
        # Create 3-5 spikes getting closer together
        num_spikes = np.random.randint(3, 6)
        for i in range(num_spikes):
            spike_start = start + i * np.random.randint(100, 200)
            spike_duration = np.random.randint(40, 80)
            magnitude = 2.0 + i * 0.5  # Increasing intensity
            cascades.append(('cascading', spike_start, spike_duration, magnitude))
    
    return cascades


def generate_flash_crowds(duration, count=50):
    """Generate flash crowd scenarios (instant spike + gradual decline)"""
    flash_crowds = []
    positions = np.random.choice(duration, count, replace=False)
    
    for pos in positions:
        start = int(pos)
        spike_duration = 10  # Instant spike
        decline_duration = np.random.randint(300, 600)  # Gradual decline
        magnitude = np.random.uniform(4.0, 5.5)
        flash_crowds.append(('flash_crowd', start, spike_duration + decline_duration, magnitude))
    
    return flash_crowds


def apply_traffic_events(t, base_traffic, all_events):
    """Apply all traffic events to get final request rate"""
    multiplier = 1.0
    additive = 0
    
    for event_type, start, duration, magnitude in all_events:
        if start <= t < start + duration:
            progress = (t - start) / duration
            
            if event_type == 'sudden':
                # Sharp instant spike
                multiplier = max(multiplier, magnitude)
            
            elif event_type == 'gradual':
                # Smooth ramp up then down (bell curve)
                ramp_factor = np.sin(np.pi * progress)
                multiplier = max(multiplier, 1 + (magnitude - 1) * ramp_factor)
            
            elif event_type == 'sustained':
                # Flat high load with slight noise
                multiplier = max(multiplier, magnitude * (1 + np.random.normal(0, 0.05)))
            
            elif event_type == 'oscillating':
                # Fast oscillations
                osc_factor = np.sin(10 * np.pi * progress)
                multiplier = max(multiplier, 1 + magnitude * osc_factor)
            
            elif event_type == 'cascading':
                # Sharp spike
                multiplier = max(multiplier, magnitude)
            
            elif event_type == 'flash_crowd':
                # Instant spike then linear decline
                if progress < 0.1:  # First 10% = spike
                    multiplier = max(multiplier, magnitude)
                else:  # Remaining 90% = decline
                    decline_progress = (progress - 0.1) / 0.9
                    multiplier = max(multiplier, magnitude - (magnitude - 1) * decline_progress)
    
    return base_traffic * multiplier + additive


# =====================================================================
# GENERATE ALL EVENTS
# =====================================================================

print("\n📋 Generating traffic events...")

all_events = []
all_events.extend(generate_sudden_spikes(TOTAL_DURATION, count=150))
all_events.extend(generate_gradual_ramps(TOTAL_DURATION, count=80))
all_events.extend(generate_sustained_bursts(TOTAL_DURATION, count=60))
all_events.extend(generate_oscillating_patterns(TOTAL_DURATION, count=40))
all_events.extend(generate_cascading_spikes(TOTAL_DURATION, count=30))
all_events.extend(generate_flash_crowds(TOTAL_DURATION, count=50))

print(f"✓ Total events: {len(all_events)}")
print(f"  - Sudden spikes: 150")
print(f"  - Gradual ramps: 80")
print(f"  - Sustained bursts: 60")
print(f"  - Oscillating patterns: 40")
print(f"  - Cascading spikes: ~120 (30 cascades)")
print(f"  - Flash crowds: 50")

# =====================================================================
# MAIN SIMULATION LOOP
# =====================================================================

print("\n⚙️  Running simulation...")
print("This may take a few minutes...")

rows = []
rr_index = 0
queue = 0

# Progress tracking
total_steps = TOTAL_DURATION
progress_interval = total_steps // 20

for t in range(TOTAL_DURATION):
    # Progress indicator
    if t % progress_interval == 0:
        progress = (t / total_steps) * 100
        print(f"  Progress: {progress:.0f}% ({t:,}/{total_steps:,} seconds)")
    
    # Generate base traffic pattern
    base_req = daily_baseline_pattern(t)
    
    # Apply all traffic events
    request_rate = apply_traffic_events(t, base_req, all_events)
    request_rate = max(5, min(500, request_rate))  # Clamp to reasonable range
    
    # Other metrics
    payload_kb = np.random.uniform(50, 500)
    pod = rr_index % BASE_PODS
    rr_index += 1
    
    # Simulate system load
    cpu_used = min(100, (request_rate / (BASE_PODS * 15)) * 100)
    memory_used = min(100, cpu_used * 0.8 + np.random.normal(0, 2))
    
    # Queue simulation
    queue = max(0, queue * 0.9 + request_rate * 0.1 - BASE_PODS * 10)
    
    # Latency calculation
    latency = 50 + cpu_used * 0.8
    if cpu_used > 70:
        latency += (cpu_used - 70) * 2
    latency += queue * 0.05
    latency = max(30, latency + np.random.normal(0, 3))
    
    rows.append([
        t,
        request_rate,
        payload_kb,
        queue,
        cpu_used,
        memory_used,
        latency,
        BASE_PODS,
        pod
    ])

print("\n✓ Simulation complete!")

# =====================================================================
# CREATE DATAFRAME
# =====================================================================

print("\n📊 Creating DataFrame...")

df = pd.DataFrame(rows, columns=[
    "timestamp",
    "request_rate",
    "payload_size_kb",
    "queue_length",
    "cpu_used_pct",
    "memory_used_pct",
    "latency_ms",
    "active_pods",
    "rr_pod_index"
])

# =====================================================================
# FEATURE ENGINEERING
# =====================================================================

print("\n🔧 Engineering features...")

# Rolling averages and deltas
for window in [5, 10, 30]:
    df[f"req_avg_{window}s"] = df["request_rate"].rolling(window, min_periods=1).mean()
    df[f"req_delta_{window}s"] = df["request_rate"].diff(window).fillna(0)

print("✓ Rolling features created")

# =====================================================================
# SPIKE LABELS
# =====================================================================

print("\n🏷️  Creating spike labels...")

for horizon in [10, 30, 60]:
    # Future request rate
    df[f"future_req_{horizon}s"] = df["request_rate"].shift(-horizon)
    
    # Spike detection: future > current * threshold
    # Using lower threshold to catch more spikes for better training
    if horizon == 10:
        threshold = 1.5  # 50% increase
    elif horizon == 30:
        threshold = 1.6  # 60% increase
    else:  # 60s
        threshold = 1.7  # 70% increase
    
    df[f"spike_{horizon}s"] = (
        df[f"future_req_{horizon}s"] > df["request_rate"] * threshold
    ).astype(int)
    
    spike_count = df[f"spike_{horizon}s"].sum()
    spike_pct = 100 * df[f"spike_{horizon}s"].mean()
    print(f"  spike_{horizon}s: {spike_count} occurrences ({spike_pct:.2f}%)")

# =====================================================================
# CLEAN AND SAVE
# =====================================================================

print("\n🧹 Cleaning data...")
df.dropna(inplace=True)

print(f"\n💾 Saving to CSV...")
output_file = "synthetic_k8s_load_enhanced.csv"
df.to_csv(output_file, index=False)

# =====================================================================
# SUMMARY
# =====================================================================

print("\n" + "=" * 60)
print("✅ DATASET GENERATION COMPLETE!")
print("=" * 60)
print(f"📁 File: {output_file}")
print(f"📊 Shape: {df.shape}")
print(f"📈 Request rate range: {df['request_rate'].min():.1f} - {df['request_rate'].max():.1f}")
print(f"⏱️  Duration: {len(df) / 3600:.1f} hours")
print(f"\n🎯 Spike Distribution:")
for horizon in [10, 30, 60]:
    count = df[f"spike_{horizon}s"].sum()
    pct = 100 * df[f"spike_{horizon}s"].mean()
    print(f"  spike_{horizon}s: {count:,} ({pct:.2f}%)")

print(f"\n📋 Columns ({len(df.columns)}):")
print(df.columns.tolist())

print("\n" + "=" * 60)
print("🚀 Next Steps:")
print("=" * 60)
print("1. Use this CSV to train your XGBoost models")
print("2. The models will now understand:")
print("   ✓ Sudden spikes (40→180 instant)")
print("   ✓ Gradual ramps (smooth changes)")
print("   ✓ Sustained bursts (long high load)")
print("   ✓ Oscillating patterns (periodic waves)")
print("   ✓ Cascading spikes (sequential spikes)")
print("   ✓ Flash crowds (viral spikes)")
print("3. Download the trained .pkl files")
print("4. Replace old models in ai_load_balancer_test/models/")
print("5. Re-run tests and enjoy better predictions! 🎉")
print("=" * 60)

# Show sample data
print("\n📝 Sample data (first 5 rows):")
print(df.head())

print("\n📝 Sample data (last 5 rows):")
print(df.tail())

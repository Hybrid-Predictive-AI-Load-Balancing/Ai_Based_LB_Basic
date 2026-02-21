"""
Test Case Generator for AI Load Balancer
Generates synthetic load patterns to test model behavior under extreme conditions
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_base_features(request_rate, size=1000):
    """Generate base features from request rate"""
    data = {
        'timestamp': list(range(size)),
        'request_rate': request_rate,
        'payload_size_kb': np.random.uniform(200, 500, size),
        'queue_length': np.maximum(0, (request_rate - 50) * 0.1),
        'cpu_used_pct': np.minimum(100, request_rate * 1.2),
        'memory_used_pct': np.minimum(100, request_rate * 0.8),
        'latency_ms': 50 + request_rate * 0.8,
        'active_pods': 5,
        'rr_pod_index': np.random.randint(0, 5, size)
    }
    
    df = pd.DataFrame(data)
    
    # Add rolling averages
    df['req_avg_5s'] = df['request_rate'].rolling(5, min_periods=1).mean()
    df['req_delta_5s'] = df['request_rate'] - df['req_avg_5s']
    df['req_avg_10s'] = df['request_rate'].rolling(10, min_periods=1).mean()
    df['req_delta_10s'] = df['request_rate'] - df['req_avg_10s']
    df['req_avg_30s'] = df['request_rate'].rolling(30, min_periods=1).mean()
    df['req_delta_30s'] = df['request_rate'] - df['req_avg_30s']
    
    # Add future predictions and spikes
    df['future_req_10s'] = df['request_rate'].shift(-10).ffill()
    df['spike_10s'] = ((df['future_req_10s'] - df['request_rate']) > 20).astype(int)
    df['future_req_30s'] = df['request_rate'].shift(-30).ffill()
    df['spike_30s'] = ((df['future_req_30s'] - df['request_rate']) > 30).astype(int)
    df['future_req_60s'] = df['request_rate'].shift(-60).ffill()
    df['spike_60s'] = ((df['future_req_60s'] - df['request_rate']) > 40).astype(int)
    
    return df

def gradual_ramp_up_down(size=2000):
    """Gradual increase and decrease - tests model's ability to handle slow changes"""
    t = np.linspace(0, 4*np.pi, size)
    # Smooth sine wave ramping up and down
    request_rate = 50 + 100 * (np.sin(t) + 1) / 2
    request_rate = np.clip(request_rate, 20, 200)
    
    df = generate_base_features(request_rate, size)
    return df

def sudden_spike(size=2000):
    """Sudden sharp spike - tests reaction time and prediction accuracy"""
    request_rate = np.ones(size) * 40
    
    # Add multiple sudden spikes at different points
    spike_points = [400, 800, 1200, 1600]
    for sp in spike_points:
        request_rate[sp:sp+50] = 180  # Sudden spike
        request_rate[sp+50:sp+100] = 40  # Drop back down
    
    df = generate_base_features(request_rate, size)
    return df

def oscillating_pattern(size=2000):
    """Oscillating bursts - tests handling of periodic load"""
    t = np.linspace(0, 20*np.pi, size)
    # Fast oscillation with varying amplitude
    base = 60
    oscillation = 40 * np.sin(t) + 20 * np.sin(3*t)
    request_rate = base + oscillation
    request_rate = np.clip(request_rate, 20, 200)
    
    df = generate_base_features(request_rate, size)
    return df

def extreme_burst(size=2000):
    """Extreme sustained burst - tests max capacity handling"""
    request_rate = np.ones(size) * 30
    
    # Long sustained extreme load
    request_rate[500:1500] = 200  # 1000 time steps of extreme load
    
    # Add some noise
    noise = np.random.normal(0, 5, size)
    request_rate = request_rate + noise
    request_rate = np.clip(request_rate, 20, 210)
    
    df = generate_base_features(request_rate, size)
    return df

def low_sustained_traffic(size=2000):
    """Low sustained traffic - tests scale down behavior"""
    # Very low traffic with minor variations
    request_rate = 25 + np.random.normal(0, 5, size)
    request_rate = np.clip(request_rate, 15, 40)
    
    df = generate_base_features(request_rate, size)
    return df

def noisy_irregular(size=2000):
    """Noisy irregular traffic - tests noise filtering"""
    # High frequency random changes
    request_rate = 60 + np.random.normal(0, 30, size)
    
    # Add some random spikes
    spike_indices = np.random.choice(size, 50, replace=False)
    for idx in spike_indices:
        if idx < size - 20:
            request_rate[idx:idx+20] += np.random.uniform(40, 80)
    
    request_rate = np.clip(request_rate, 20, 200)
    
    df = generate_base_features(request_rate, size)
    return df

def multi_stage_spike(size=2000):
    """Multiple spikes with increasing intensity - tests adaptive scaling"""
    request_rate = np.ones(size) * 40
    
    # Stage 1: Small spike
    request_rate[300:400] = 80
    
    # Stage 2: Medium spike
    request_rate[600:700] = 120
    
    # Stage 3: Large spike
    request_rate[900:1000] = 160
    
    # Stage 4: Extreme spike
    request_rate[1200:1300] = 200
    
    # Back to normal
    request_rate[1500:] = 40
    
    df = generate_base_features(request_rate, size)
    return df

def flash_crowd(size=2000):
    """Flash crowd - sudden massive spike then gradual decline"""
    request_rate = np.ones(size) * 35
    
    # Sudden massive spike at 500
    spike_start = 500
    spike_duration = 600
    
    # Instant spike
    request_rate[spike_start:spike_start+10] = 200
    
    # Gradual decline
    decline = np.linspace(200, 40, spike_duration-10)
    request_rate[spike_start+10:spike_start+spike_duration] = decline
    
    df = generate_base_features(request_rate, size)
    return df

def cascading_spikes(size=2000):
    """Cascading spikes - one spike triggers another"""
    request_rate = np.ones(size) * 45
    
    # Cascade pattern: each spike is closer to the next
    spikes = [
        (200, 100, 120),   # (start, duration, intensity)
        (350, 80, 140),
        (470, 70, 160),
        (570, 60, 180),
        (650, 100, 200),   # Final largest spike
    ]
    
    for start, duration, intensity in spikes:
        request_rate[start:start+duration] = intensity
    
    df = generate_base_features(request_rate, size)
    return df

def generate_all_test_cases():
    """Generate all test cases and save to CSV files"""
    test_cases = {
        'gradual_ramp_up_down': {
            'func': gradual_ramp_up_down,
            'description': 'Gradual increase and decrease in traffic to test smooth scaling'
        },
        'sudden_spike': {
            'func': sudden_spike,
            'description': 'Multiple sudden spikes to test reaction time and prediction'
        },
        'oscillating_pattern': {
            'func': oscillating_pattern,
            'description': 'Periodic oscillating load to test handling of rhythmic patterns'
        },
        'extreme_burst': {
            'func': extreme_burst,
            'description': 'Sustained extreme load to test maximum capacity handling'
        },
        'low_sustained_traffic': {
            'func': low_sustained_traffic,
            'description': 'Very low traffic to test aggressive scale-down behavior'
        },
        'noisy_irregular': {
            'func': noisy_irregular,
            'description': 'Highly irregular noisy traffic to test noise filtering'
        },
        'multi_stage_spike': {
            'func': multi_stage_spike,
            'description': 'Progressive spikes with increasing intensity to test adaptive scaling'
        },
        'flash_crowd': {
            'func': flash_crowd,
            'description': 'Sudden massive spike with gradual decline (flash crowd scenario)'
        },
        'cascading_spikes': {
            'func': cascading_spikes,
            'description': 'Cascading spikes getting closer together (stress test)'
        }
    }
    
    print("Generating test case CSV files...")
    print("=" * 60)
    
    for name, info in test_cases.items():
        print(f"\nGenerating: {name}")
        print(f"Description: {info['description']}")
        
        df = info['func']()
        filepath = f"test_cases/{name}.csv"
        df.to_csv(filepath, index=False)
        
        print(f"✓ Saved to {filepath}")
        print(f"  Size: {len(df)} rows")
        print(f"  Request rate range: {df['request_rate'].min():.1f} - {df['request_rate'].max():.1f}")
        print(f"  Spikes detected (30s): {df['spike_30s'].sum()}")
        print(f"  Spikes detected (60s): {df['spike_60s'].sum()}")
    
    print("\n" + "=" * 60)
    print(f"✓ Successfully generated {len(test_cases)} test cases!")
    print("\nTest cases saved in: test_cases/")

if __name__ == "__main__":
    generate_all_test_cases()

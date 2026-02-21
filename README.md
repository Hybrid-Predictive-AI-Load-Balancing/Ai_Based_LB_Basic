# AI Load Balancer - Comprehensive Testing Framework

A comprehensive testing framework for the AI-powered load balancer that tests model performance under extreme and varied traffic conditions with real-time visualization and detailed metrics.

## 🎯 Overview

This framework tests the AI load balancer's ability to handle:
- **Gradual ramp-up/down** - Smooth traffic changes
- **Sudden spikes** - Sharp traffic increases
- **Oscillating patterns** - Periodic load variations
- **Extreme bursts** - Sustained high load
- **Low sustained traffic** - Scale-down behavior
- **Noisy irregular traffic** - Random variations
- **Multi-stage spikes** - Progressive intensity increases
- **Flash crowd** - Sudden massive spike with gradual decline
- **Cascading spikes** - Sequential spikes getting closer together

## 📁 Directory Structure

```
ai_load_balancer_test/
├── models/                      # Pre-trained XGBoost models
│   ├── xgb_spike_10s.pkl
│   ├── xgb_spike_30s.pkl
│   └── xgb_spike_60s.pkl
├── test_cases/                  # Generated test CSV files
│   ├── gradual_ramp_up_down.csv
│   ├── sudden_spike.csv
│   ├── oscillating_pattern.csv
│   ├── extreme_burst.csv
│   ├── low_sustained_traffic.csv
│   ├── noisy_irregular.csv
│   ├── multi_stage_spike.csv
│   ├── flash_crowd.csv
│   └── cascading_spikes.csv
├── results/                     # Test results and reports
│   ├── *_detailed_log.csv      # Per-test detailed logs
│   ├── *_state_changes.csv     # Scaling action logs
│   ├── *_plot.png              # Visualization plots
│   └── SUMMARY_REPORT_*.csv    # Aggregate summary
├── main.py                      # Main test runner
├── autoscaler.py               # Enhanced autoscaler with tracking
├── simulator.py                # Enhanced simulator with metrics
├── visualize.py                # Real-time visualization
├── generate_test_cases.py      # Test case generator
└── requirements.txt            # Python dependencies
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate Test Cases (Already Done)

Test cases are pre-generated, but you can regenerate them:

```bash
python generate_test_cases.py
```

### 3. Run All Tests

```bash
python main.py
```

### 4. Run Specific Test

```bash
python main.py test_cases/sudden_spike.csv
```

## 📊 Features

### Real-Time Visualization

The framework provides comprehensive real-time visualization with 5 plots:

1. **Traffic Rate** - Request rate over time with spike indicators
2. **Pod Count** - Active pods with scale action markers (▲ up, ▼ down)
3. **Latency** - Response latency with threshold violations highlighted
4. **CPU & Memory** - Resource utilization with threshold lines
5. **Spike Probabilities** - Model predictions for 30s and 60s spikes

### State Change Logging

Every scaling action is logged with:
- Timestamp
- Action type (SCALE_UP, SCALE_DOWN, HOLD)
- Reason for decision
- Current metrics (CPU, latency, predictions)
- Spike description

### Comprehensive Metrics

Each test tracks:
- **Scaling metrics**: Scale-ups, scale-downs, hold rate
- **Performance metrics**: CPU usage, latency, violations
- **Efficiency metrics**: Underutilization, overload frequency
- **Pod usage**: Average, min, max pod count

## 📈 Output Files

### Detailed Logs (`*_detailed_log.csv`)
Complete time-series data for every simulation step:
- Request rate, pods, CPU, memory, latency
- Model predictions (30s, 60s probabilities)
- Actions and reasons
- Spike descriptions
- Violations

### State Changes (`*_state_changes.csv`)
Log of all scaling actions:
- When actions occurred
- Why decisions were made
- System state at decision time

### Plots (`*_plot.png`)
High-resolution visualization of entire test run

### Summary Report (`SUMMARY_REPORT_*.csv`)
Aggregate statistics across all tests for comparison

## ⚙️ Configuration

Edit the configuration section in `main.py`:

```python
ROWS_PER_SECOND = 10     # Simulation speed (steps/second)
SLEEP_TIME = 1           # Real seconds between updates
SAVE_PLOTS = True        # Save plots after each test
CONSOLE_LOG_INTERVAL = 50  # Console update frequency
```

## 🎮 Test Case Descriptions

| Test Case | Description | Purpose |
|-----------|-------------|---------|
| `gradual_ramp_up_down` | Smooth sine wave traffic pattern | Test smooth scaling behavior |
| `sudden_spike` | Multiple sharp spikes | Test reaction time and prediction |
| `oscillating_pattern` | Periodic load variations | Test handling of rhythmic patterns |
| `extreme_burst` | Sustained 200 req/s load | Test maximum capacity handling |
| `low_sustained_traffic` | Very low traffic (~25 req/s) | Test aggressive scale-down |
| `noisy_irregular` | High-frequency random changes | Test noise filtering capability |
| `multi_stage_spike` | Progressive spikes (80→200 req/s) | Test adaptive scaling |
| `flash_crowd` | Instant spike + gradual decline | Test viral load scenarios |
| `cascading_spikes` | Sequential spikes getting closer | Stress test recovery time |

## 📊 Understanding Results

### Good Performance Indicators:
✅ Low latency violation rate (<5%)
✅ Low CPU overload rate (<10%)
✅ Balanced scale-up/down ratio
✅ Quick response to spikes (visible in plots)
✅ Minimal underutilization

### Warning Signs:
⚠️ High latency violations (>10%)
⚠️ Frequent CPU overload (>20%)
⚠️ Excessive scaling actions (thrashing)
⚠️ Slow spike response

## 🔧 Customization

### Adding New Test Cases

Edit `generate_test_cases.py` and add a new function:

```python
def my_custom_test(size=2000):
    """My custom traffic pattern"""
    request_rate = # ... your pattern logic
    df = generate_base_features(request_rate, size)
    return df
```

Then add it to the `test_cases` dictionary in `generate_all_test_cases()`.

### Tuning Autoscaler

Edit `autoscaler.py` to modify scaling thresholds:

```python
def __init__(self, min_pods=2, max_pods=20, cooldown=10):
    # Adjust these parameters
```

### Adjusting Thresholds

Edit scaling logic in `autoscaler.py`:

```python
if prob_30s >= 0.35:  # Change threshold here
    # Scale up logic
```

## 📝 Example Console Output

```
🧪 RUNNING TEST: sudden_spike
======================================================================
📊 Test data: 2000 time steps
📈 Traffic range: 40.0 - 180.0 req/s

▶️  Starting simulation... (Press Ctrl+C to stop)
⏱️  Update rate: 10 steps/second

⚡ t=0400 | SCALE_UP     | Pods: 7  | CPU:  89.2% | Latency: 167.3ms | High spike probability (30s:0.78, 60s:0.65)
⚡ t=0450 | SCALE_DOWN   | Pods: 6  | CPU:  25.1% | Latency:  70.1ms | Low spike probability (0.12) + Low CPU (25.1%)
⏳ Progress: 500/2000 steps (25.0%) | Pods: 6 | CPU: 48.3% | Latency: 88.7ms

📊 TEST RESULTS: sudden_spike
======================================================================
⏱️  Elapsed time: 205.43s
📈 Steps completed: 2000/2000 (100.0%)

🎯 AUTOSCALER STATISTICS:
   Total scale-ups:     42 ( 2.1%)
   Total scale-downs:   38 ( 1.9%)
   Total holds:       1920 (96.0%)

⚡ PERFORMANCE METRICS:
   Avg CPU:              52.3%
   Max CPU:              96.8%
   Avg Latency:          89.7 ms
   Max Latency:         245.2 ms
   Latency violations:     15 ( 0.8%)
   CPU overload:          23 ( 1.2%)
   Underutilization:     342 (17.1%)

🔢 POD USAGE:
   Average pods:           5.8
   Min pods:                 2
   Max pods:                12
```

## 🎯 Goals

This testing framework helps evaluate:
1. **Response Time** - How quickly does the system react to spikes?
2. **Prediction Accuracy** - Are spikes detected before they cause issues?
3. **Scaling Efficiency** - Is the system avoiding over/under-scaling?
4. **Resource Utilization** - Is CPU/memory usage optimal?
5. **SLA Compliance** - Are latency thresholds maintained?
6. **Stability** - Does the system avoid thrashing?

## 📞 Support

For issues or questions, refer to the main project documentation or check the generated logs in `results/` for detailed information.

---

**Note**: This is a testing framework. Actual production deployment would require additional monitoring, alerting, and integration with Kubernetes or similar orchestration platforms.

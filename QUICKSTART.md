# 🚀 QUICK START GUIDE

## Welcome to AI Load Balancer Testing Framework!

This framework will test your AI load balancer model with 9 different extreme traffic scenarios.

---

## ✅ What's Already Set Up

✓ **9 Test Cases Generated** - Various traffic patterns ready to test
✓ **Models Copied** - XGBoost models for 10s, 30s, and 60s spike prediction
✓ **Real-time Visualization** - 5-panel comprehensive monitoring
✓ **Detailed Logging** - Every action and metric tracked

---

## 🎯 Quick Test (Recommended First Step)

Run a single fast test to see how it works:

```bash
python main.py test_cases/sudden_spike.csv
```

This will:
- Show real-time visualization with 5 plots
- Log all scaling actions to console
- Save detailed results to `results/` folder
- Generate a plot image

**What to watch for:**
- Green ▲ markers = Scale-up actions
- Red ▼ markers = Scale-down actions
- Red dots on latency plot = Violations (>200ms)

---

## 🏃 Run All Tests

To run the comprehensive test suite (takes ~30-40 minutes):

```bash
python main.py
```

Or use the interactive launcher:

```bash
./run_tests.sh
```

**What happens:**
- Runs all 9 test cases sequentially
- Generates detailed logs for each
- Creates visualization plots
- Produces a summary report CSV

---

## 📊 View Results

After running tests, check the `results/` folder:

```
results/
├── sudden_spike_detailed_log.csv      # Time-series data
├── sudden_spike_state_changes.csv     # Scaling actions log
├── sudden_spike_plot.png              # Visualization
└── SUMMARY_REPORT_<timestamp>.csv     # Aggregate stats
```

**Pro Tip:** Open the PNG files to see visual analysis of each test!

---

## 🔍 Compare Test Results

After running multiple tests, compare them:

```bash
python compare_results.py
```

This generates:
- Comparison table in console
- Dashboard with 9 comparison charts
- Saved as `results/COMPARISON_DASHBOARD.png`

---

## 📈 Understanding the Visualization

### Plot 1: Traffic Rate
- Blue line = incoming request rate
- Shows the load pattern being tested

### Plot 2: Pod Count
- Purple line = active pods
- **Green ▲** = Scale-up action
- **Red ▼** = Scale-down action

### Plot 3: Latency
- Orange line = response latency
- **Red dashed line** = 200ms threshold
- **Red dots** = Violations (bad!)

### Plot 4: CPU & Memory
- Red line = CPU usage
- Green dashed = Memory usage
- Threshold lines at 30%, 70%, 90%

### Plot 5: Spike Probabilities
- Red line = 30s spike probability
- Cyan line = 60s spike probability
- Dashed lines = decision thresholds

---

## 🎮 Test Cases Explained

1. **gradual_ramp_up_down** - Smooth changes (tests normal scaling)
2. **sudden_spike** - Sharp spikes (tests reaction speed) ⚡
3. **oscillating_pattern** - Periodic waves (tests pattern recognition)
4. **extreme_burst** - Sustained high load (tests max capacity) 🔥
5. **low_sustained_traffic** - Low traffic (tests scale-down)
6. **noisy_irregular** - Random chaos (tests noise filtering)
7. **multi_stage_spike** - Progressive spikes (tests adaptation)
8. **flash_crowd** - Viral spike (tests burst handling)
9. **cascading_spikes** - Rapid successive spikes (stress test) 💥

**Recommendation:** Start with `sudden_spike` and `extreme_burst` for quick insights!

---

## ⚙️ Configuration Tips

### Make it Faster
Edit `main.py`:
```python
ROWS_PER_SECOND = 20    # Process more rows per second
SLEEP_TIME = 0.5        # Update more frequently
```

### Save Plots Off
```python
SAVE_PLOTS = False      # Don't save PNG files
```

### Adjust Scaling Behavior
Edit `autoscaler.py`:
```python
def __init__(self, min_pods=2, max_pods=20, cooldown=10):
    # Change these values
```

---

## 🎯 What to Look For

### ✅ Good Signs
- Latency violations < 5%
- CPU overload < 10%
- Quick response to spikes (visible in plots)
- Smooth pod count changes

### ⚠️ Warning Signs
- Latency violations > 10%
- Frequent scaling thrashing
- High CPU for extended periods
- Slow spike detection

---

## 📝 Console Output Example

```
⚡ t=0450 | SCALE_UP     | Pods: 7  | CPU:  89.2% | Latency: 167.3ms
   High spike probability (30s:0.78, 60s:0.65)
```

This tells you:
- **t=0450**: Time step 450
- **SCALE_UP**: Action taken
- **Pods: 7**: Scaled to 7 pods
- **CPU/Latency**: Current metrics
- **Reason**: Why this decision was made

---

## 🔧 Troubleshooting

**Problem:** `ModuleNotFoundError`
**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

**Problem:** Font warnings about missing glyphs (emoji)
**Solution:** These are harmless warnings and won't affect the test. The emojis in spike descriptions may not display in the plot titles, but all functionality works fine.

**Problem:** Plots not showing
**Solution:** Check if matplotlib backend is configured
```bash
export MPLBACKEND=TkAgg  # or Qt5Agg
```

**Problem:** Models not found
**Solution:** Make sure you're in the right directory
```bash
cd ai_load_balancer_test
```

---

## 🎓 Next Steps

1. **Run quick test** to familiarize yourself
2. **Run all tests** for comprehensive analysis
3. **Compare results** to identify patterns
4. **Tune parameters** in autoscaler.py
5. **Re-run tests** to see improvements

---

## 💡 Pro Tips

- **Watch the visualization in real-time** - it's more informative than logs
- **Check the spike descriptions** at the top of the plot
- **Look at the action reasons** in the console output
- **Compare multiple test runs** after tuning parameters
- **Focus on latency violations** as the key metric

---

## 📞 Need Help?

Check the full README.md for detailed documentation!

**Happy Testing! 🚀**

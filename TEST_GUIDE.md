# 🎯 TEST CASE GUIDE - What to Expect

This guide tells you **exactly** what happens in each test case and **where to look** in the visualization.

---

## 1️⃣ sudden_spike.csv

### 📋 Pattern Description
Multiple sudden sharp spikes from 40 req/s baseline to 180 req/s

### 📍 Where Spikes Occur
- **Spike 1**: Timestep 400-450 (180 req/s)
- **Spike 2**: Timestep 800-850 (180 req/s)
- **Spike 3**: Timestep 1200-1250 (180 req/s)
- **Spike 4**: Timestep 1600-1650 (180 req/s)

### 👀 What to Watch For
- **Before spike (t=370-399)**: Spike probability should START RISING (30s prediction)
- **At spike (t=400)**: Green ▲ scale-up markers should appear
- **CPU plot**: Should spike up but stay below 90% if scaled properly
- **Latency plot**: Should NOT breach 200ms threshold if scaled in time

### ✅ Good Response Indicators
- Probability rises BEFORE spike hits (at t~370)
- Scale-up action within 10-20 timesteps of spike
- CPU stays below 90%
- Latency stays below 150ms

### ❌ Bad Response Indicators
- Probability stays flat (model not detecting)
- No scale-up actions during spikes
- CPU hits 100%
- Latency exceeds 180ms

---

## 2️⃣ extreme_burst.csv

### 📋 Pattern Description
Sustained extreme load - baseline at 30 req/s, then continuous 200 req/s for 1000 timesteps

### 📍 Where Burst Occurs
- **Baseline**: Timestep 0-500 (30 req/s)
- **BURST START**: Timestep 500
- **Sustained burst**: Timestep 500-1500 (200 req/s continuously)
- **Back to normal**: Timestep 1500-2000 (30 req/s)

### 👀 What to Watch For
- **t=470-499**: Probability should spike to 0.7+ (60s prediction)
- **t=500**: Multiple green ▲ markers (aggressive scale-up)
- **t=500-1500**: Pod count should reach 15-20 (max capacity)
- **t=1520+**: Red ▼ markers (scale-down after burst ends)

### ✅ Good Response
- Probability hits 0.8+ before t=500
- Scales to 15+ pods quickly
- Latency stays below 150ms during burst
- Smooth scale-down after burst ends

---

## 3️⃣ gradual_ramp_up_down.csv

### 📋 Pattern Description
Smooth sine wave: 50→150→50 req/s over entire 2000 timesteps

### 📍 Key Points
- **Peak load**: Around timestep 1000 (150 req/s)
- **Low points**: Timesteps 0 and 2000 (50 req/s)
- **Ramp up**: Timesteps 0-1000
- **Ramp down**: Timesteps 1000-2000

### 👀 What to Watch For
- **Gradual increase** in pod count (no sudden jumps)
- **Smooth probability curve** following the traffic pattern
- **Pods should track** the sine wave shape
- Few scale actions (smooth = fewer adjustments needed)

### ✅ Good Response
- Pod count smoothly increases/decreases
- 3-7 scale actions total (not thrashing)
- No latency violations
- Probability follows traffic trend

---

## 4️⃣ oscillating_pattern.csv

### 📋 Pattern Description
Fast oscillations - traffic swings between 20-103 req/s in periodic waves

### 📍 Pattern
- **Frequency**: Oscillates every ~50-100 timesteps
- **Range**: 20-103 req/s
- **Continues**: Throughout entire test

### 👀 What to Watch For
- **Pod count**: Should have a "staircase" pattern (not following every oscillation)
- **Probability**: May oscillate but should be dampened
- **CPU**: Should stay relatively stable (50-70%)
- **Scale actions**: Moderate number (20-40 total)

### ✅ Good Response
- System doesn't over-react to every oscillation
- Pod count is stable-ish (5-8 range)
- No thrashing (constant scale up/down)

### ❌ Bad Response
- Pod count oscillates wildly (thrashing)
- 100+ scale actions
- Following every tiny fluctuation

---

## 5️⃣ multi_stage_spike.csv

### 📋 Pattern Description
Progressive spikes with increasing intensity: 80→120→160→200 req/s

### 📍 Where Spikes Occur
- **Stage 1**: t=300-400 (80 req/s)
- **Stage 2**: t=600-700 (120 req/s)
- **Stage 3**: t=900-1000 (160 req/s)
- **Stage 4**: t=1200-1300 (200 req/s)

### 👀 What to Watch For
- **Progressive scaling**: Each stage should trigger more scale-ups
- **Learning pattern**: System should anticipate increasing intensity
- **Pod progression**: 2→4→7→10→15 (approximately)
- **Probability**: Should increase with each stage

### ✅ Good Response
- Larger scale-up deltas for bigger spikes
- Proactive scaling (probability rises early)
- Each stage handled well

---

## 6️⃣ flash_crowd.csv

### 📋 Pattern Description
Sudden massive spike to 200 req/s, then gradual linear decline back to 40 over 600 timesteps

### 📍 Key Events
- **Normal**: t=0-500 (35 req/s)
- **INSTANT SPIKE**: t=500-510 (35→200 req/s in 10 steps!)
- **Gradual decline**: t=510-1100 (200→40 req/s linear)
- **Normal**: t=1100-2000 (35 req/s)

### 👀 What to Watch For
- **t=470**: Probability should jump to 0.9+ (spike detection)
- **t=500-510**: Aggressive scale-up (multiple ▲)
- **t=510-1100**: Gradual scale-down following decline
- **Smooth descent**: Pod count decreases gradually

### ✅ Good Response
- Fast scale-up at t=500 (within 20 steps)
- Scales to 18-20 pods
- Smooth scale-down as traffic declines
- No latency violations

---

## 7️⃣ low_sustained_traffic.csv

### 📋 Pattern Description
Very low traffic: 15-40 req/s with minor random variations throughout

### 📍 Pattern
- **Range**: 15-40 req/s (mean ~25)
- **No spikes**: Just random noise
- **Duration**: Entire 2000 timesteps

### 👀 What to Watch For
- **Quick scale-down**: Should reach 2 pods within 50 steps
- **Stay at minimum**: Pods=2 for 95%+ of test
- **Low CPU**: 20-30% throughout
- **Probability**: Should stay near 0 (correctly detecting no spikes)

### ✅ Good Response
- Scales to 2 pods and stays there
- 0-2 scale-ups total
- Demonstrates cost efficiency

---

## 8️⃣ noisy_irregular.csv

### 📋 Pattern Description
High-frequency random chaos: 20-200 req/s with 50 random spikes scattered throughout

### 📍 Pattern
- **Base**: ~60 req/s with ±30 variance
- **Random spikes**: 50 spikes to 100-180 req/s at random times
- **Duration**: 10-20 timesteps each
- **Unpredictable**: No pattern

### 👀 What to Watch For
- **Noise filtering**: System should NOT react to every spike
- **Stable pod count**: Should find a middle ground (7-10 pods)
- **Moderate scaling**: 20-50 scale actions (not 200+)
- **Probability**: Should be noisy but not trigger constantly

### ✅ Good Response
- Maintains stable pod count despite noise
- Doesn't thrash
- Averages out the noise

### ❌ Bad Response
- Constant scaling actions (>100)
- Pod count swinging wildly
- Over-sensitive to noise

---

## 9️⃣ cascading_spikes.csv

### 📋 Pattern Description
Sequential spikes that get closer together - tests recovery time

### 📍 Where Spikes Occur
- **Spike 1**: t=200-300 (120 req/s, 100 steps duration)
- **Spike 2**: t=350-430 (140 req/s, 80 steps duration)
- **Spike 3**: t=470-540 (160 req/s, 70 steps duration)
- **Spike 4**: t=570-630 (180 req/s, 60 steps duration)
- **Spike 5**: t=650-750 (200 req/s, 100 steps duration) ← **LONGEST & STRONGEST**

### 👀 What to Watch For
- **Progressive intensity**: Each spike is stronger
- **Shorter gaps**: Less recovery time between spikes
- **Cumulative scaling**: Pods should accumulate (not fully scale down between)
- **Final spike**: Should handle spike 5 well if learned pattern

### ✅ Good Response
- Maintains higher pod count anticipating next spike
- Doesn't fully scale down between spikes
- Spike 5 handled smoothly

### ❌ Bad Response
- Scales down fully between spikes (wastes time)
- Spike 5 causes latency violations
- Doesn't learn the pattern

---

## 📊 General Viewing Tips

### Top Plot (Traffic)
- **Shape tells the story** - Is it smooth, spiky, or chaotic?
- **Compare to spike locations** above

### Second Plot (Pods)
- **Count the arrows**: Green ▲ = scale-ups, Red ▼ = scale-downs
- **Look for patterns**: Are they proactive or reactive?

### Third Plot (Latency)
- **Red dots = FAILURES** - Each one is a latency violation
- **Goal**: Zero red dots or <5% violation rate

### Fourth Plot (CPU)
- **Should spike at traffic peaks** but stay below 90%
- **Below 30% = wasting resources**

### Fifth Plot (Probabilities)
- **Should LEAD traffic spikes** by 30-60 timesteps
- **Flat line = model not detecting** ⚠️
- **High probability (>0.5) = confident spike prediction**

---

## 🎯 Success Criteria Summary

| Metric | Good | Warning | Critical |
|--------|------|---------|----------|
| Latency violations | <5% | 5-10% | >10% |
| CPU overload | <5% | 5-15% | >15% |
| Scale-up reaction time | <30 steps | 30-60 steps | >60 steps |
| Probability lead time | 20-60 steps | 10-20 steps | <10 steps |
| Total scale actions | <50 | 50-100 | >100 |

---

**Use this guide while watching the visualization to understand what's happening!** 🚀

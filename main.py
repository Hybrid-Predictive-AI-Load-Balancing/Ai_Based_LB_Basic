"""
Main Test Runner for AI Load Balancer
Runs comprehensive tests with real-time visualization and detailed logging
"""

import time
import joblib
import pandas as pd
import os
from datetime import datetime

from autoscaler import EnhancedAutoScaler
from simulator import EnhancedLoadSimulator
from visualize import RealtimeVisualizer

# ==================== CONFIGURATION ====================
ROWS_PER_SECOND = 10     # Speed of simulation (rows processed per second)
SLEEP_TIME = 1           # Real seconds between updates
SAVE_PLOTS = True        # Save plots after each test
CONSOLE_LOG_INTERVAL = 50  # Console update interval
# =======================================================

# Feature columns (exclude targets and timestamp)
EXCLUDED_COLS = [
    "timestamp", "spike_10s", "spike_30s", "spike_60s",
    "future_req_10s", "future_req_30s", "future_req_60s"
]

def get_feature_cols(df):
    """Get feature columns from dataframe"""
    return [c for c in df.columns if c not in EXCLUDED_COLS]

def load_models():
    """Load trained models"""
    print("Loading models...")
    model_30 = joblib.load("models/xgb_spike_30s.pkl")
    model_60 = joblib.load("models/xgb_spike_60s.pkl")
    print("✓ Models loaded successfully")
    return model_30, model_60

def run_test(test_file, test_name, model_30, model_60):
    """
    Run a single test case with real-time visualization
    
    Args:
        test_file: Path to test CSV file
        test_name: Name of the test
        model_30: 30s spike prediction model
        model_60: 60s spike prediction model
    
    Returns:
        dict: Test results and statistics
    """
    print("\n" + "="*70)
    print(f"🧪 RUNNING TEST: {test_name}")
    print("="*70)
    
    # Load test data
    df = pd.read_csv(test_file)
    feature_cols = get_feature_cols(df)
    print(f"📊 Test data: {len(df)} time steps")
    print(f"📈 Traffic range: {df['request_rate'].min():.1f} - {df['request_rate'].max():.1f} req/s")
    
    # Initialize components
    autoscaler = EnhancedAutoScaler(min_pods=2, max_pods=20, cooldown=10)
    simulator = EnhancedLoadSimulator(df, feature_cols)
    visualizer = RealtimeVisualizer(test_name=test_name)
    
    # Initial state
    pods = 5
    t = 0
    
    # Log storage
    detailed_logs = []
    state_changes = []
    
    print(f"\n▶️  Starting simulation... (Press Ctrl+C to stop)")
    print(f"⏱️  Update rate: {ROWS_PER_SECOND} steps/second\n")
    
    start_time = time.time()
    last_action = "HOLD"
    
    try:
        while t < len(df):
            for _ in range(ROWS_PER_SECOND):
                if t >= len(df):
                    break
                
                # Get features
                X = simulator.get_features(t)
                
                # Predict spike probabilities
                prob_30 = model_30.predict_proba(X)[0, 1]
                prob_60 = model_60.predict_proba(X)[0, 1]
                
                # Get spike description
                spike_desc = simulator.get_spike_description(t)
                
                # Make scaling decision
                pods, action, reason = autoscaler.step(
                    prob_30, prob_60, simulator.current_cpu, pods, t, spike_desc
                )
                
                # Simulate system with current pods
                cpu, latency, memory, metrics = simulator.apply_pods(pods, t)
                
                # Update visualization
                visualizer.update(
                    metrics['request_rate'], pods, latency, 
                    cpu, memory, prob_30, prob_60,
                    action, reason, spike_desc
                )
                
                # Log state changes
                if action != last_action or action != "HOLD":
                    change_log = {
                        'time': t,
                        'action': action,
                        'reason': reason,
                        'pods': pods,
                        'spike_desc': spike_desc,
                        'cpu': cpu,
                        'latency': latency,
                        'prob_30s': prob_30,
                        'prob_60s': prob_60
                    }
                    state_changes.append(change_log)
                    
                    # Console log for important changes
                    if action != "HOLD":
                        print(f"⚡ t={t:04d} | {action:12s} | Pods: {pods:2d} | "
                              f"CPU: {cpu:5.1f}% | Latency: {latency:6.1f}ms | {reason}")
                
                last_action = action
                
                # Detailed log
                log_entry = {
                    'time': t,
                    'request_rate': metrics['request_rate'],
                    'pods': pods,
                    'cpu': cpu,
                    'memory': memory,
                    'latency': latency,
                    'prob_30s': prob_30,
                    'prob_60s': prob_60,
                    'action': action,
                    'reason': reason,
                    'spike_desc': spike_desc,
                    'latency_violation': not metrics['latency_ok'],
                    'cpu_overload': not metrics['cpu_ok']
                }
                detailed_logs.append(log_entry)
                
                # Periodic console update
                if t % CONSOLE_LOG_INTERVAL == 0 and t > 0:
                    print(f"⏳ Progress: {t}/{len(df)} steps "
                          f"({100*t/len(df):.1f}%) | Pods: {pods} | "
                          f"CPU: {cpu:.1f}% | Latency: {latency:.1f}ms")
                
                t += 1
            
            time.sleep(SLEEP_TIME)
    
    except KeyboardInterrupt:
        print(f"\n⏸️  Simulation stopped by user at step {t}")
    
    elapsed_time = time.time() - start_time
    
    # Get statistics
    autoscaler_stats = autoscaler.get_statistics()
    simulator_stats = simulator.get_statistics()
    
    # Save results
    print(f"\n💾 Saving results...")
    
    # Save detailed logs
    log_df = pd.DataFrame(detailed_logs)
    log_file = f"results/{test_name}_detailed_log.csv"
    log_df.to_csv(log_file, index=False)
    print(f"✓ Detailed log saved to {log_file}")
    
    # Save state changes
    if state_changes:
        changes_df = pd.DataFrame(state_changes)
        changes_file = f"results/{test_name}_state_changes.csv"
        changes_df.to_csv(changes_file, index=False)
        print(f"✓ State changes saved to {changes_file}")
    
    # Save plot
    if SAVE_PLOTS:
        plot_file = f"results/{test_name}_plot.png"
        visualizer.save_plot(plot_file)
    
    # Close visualizer
    visualizer.close()
    
    # Print statistics
    print(f"\n📊 TEST RESULTS: {test_name}")
    print("="*70)
    print(f"⏱️  Elapsed time: {elapsed_time:.2f}s")
    print(f"📈 Steps completed: {t}/{len(df)} ({100*t/len(df):.1f}%)")
    print(f"\n🎯 AUTOSCALER STATISTICS:")
    print(f"   Total scale-ups:   {autoscaler_stats['total_scale_ups']:4d} ({autoscaler_stats['scale_up_rate']*100:5.1f}%)")
    print(f"   Total scale-downs: {autoscaler_stats['total_scale_downs']:4d} ({autoscaler_stats['scale_down_rate']*100:5.1f}%)")
    print(f"   Total holds:       {autoscaler_stats['total_holds']:4d} ({autoscaler_stats['hold_rate']*100:5.1f}%)")
    print(f"\n⚡ PERFORMANCE METRICS:")
    print(f"   Avg CPU:              {simulator_stats['avg_cpu']:6.1f}%")
    print(f"   Max CPU:              {simulator_stats['max_cpu']:6.1f}%")
    print(f"   Avg Latency:          {simulator_stats['avg_latency']:6.1f} ms")
    print(f"   Max Latency:          {simulator_stats['max_latency']:6.1f} ms")
    print(f"   Latency violations:   {simulator_stats['latency_violations']:4d} ({simulator_stats['latency_violation_rate']*100:5.1f}%)")
    print(f"   CPU overload:         {simulator_stats['cpu_overload_count']:4d} ({simulator_stats['cpu_overload_rate']*100:5.1f}%)")
    print(f"   Underutilization:     {simulator_stats['underutilization_count']:4d} ({simulator_stats['underutilization_rate']*100:5.1f}%)")
    print(f"\n🔢 POD USAGE:")
    print(f"   Average pods:         {simulator_stats['avg_pods']:6.1f}")
    print(f"   Min pods:             {simulator_stats['min_pods']:6.0f}")
    print(f"   Max pods:             {simulator_stats['max_pods']:6.0f}")
    print("="*70)
    
    # Return results
    return {
        'test_name': test_name,
        'steps_completed': t,
        'elapsed_time': elapsed_time,
        'autoscaler_stats': autoscaler_stats,
        'simulator_stats': simulator_stats,
        'detailed_logs': log_df,
        'state_changes': state_changes
    }

def run_all_tests():
    """Run all test cases and generate summary report"""
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "AI LOAD BALANCER TEST SUITE" + " "*25 + "║")
    print("╚" + "="*68 + "╝")
    
    # Load models
    model_30, model_60 = load_models()
    
    # Get all test files
    test_files = [f for f in os.listdir("test_cases") if f.endswith('.csv')]
    test_files.sort()
    
    print(f"\n📋 Found {len(test_files)} test cases")
    
    # Run all tests
    all_results = []
    
    for i, test_file in enumerate(test_files, 1):
        test_name = test_file.replace('.csv', '')
        test_path = os.path.join("test_cases", test_file)
        
        print(f"\n[{i}/{len(test_files)}] Running: {test_name}")
        
        result = run_test(test_path, test_name, model_30, model_60)
        all_results.append(result)
        
        # Wait between tests
        if i < len(test_files):
            print(f"\n⏸️  Waiting 3 seconds before next test...\n")
            time.sleep(3)
    
    # Generate summary report
    print("\n\n" + "="*70)
    print("📊 GENERATING SUMMARY REPORT")
    print("="*70)
    
    summary_data = []
    for result in all_results:
        summary_data.append({
            'test_name': result['test_name'],
            'steps_completed': result['steps_completed'],
            'elapsed_time': result['elapsed_time'],
            'scale_ups': result['autoscaler_stats']['total_scale_ups'],
            'scale_downs': result['autoscaler_stats']['total_scale_downs'],
            'avg_cpu': result['simulator_stats']['avg_cpu'],
            'max_cpu': result['simulator_stats']['max_cpu'],
            'avg_latency': result['simulator_stats']['avg_latency'],
            'max_latency': result['simulator_stats']['max_latency'],
            'latency_violations': result['simulator_stats']['latency_violations'],
            'latency_violation_rate': result['simulator_stats']['latency_violation_rate'],
            'cpu_overload_count': result['simulator_stats']['cpu_overload_count'],
            'cpu_overload_rate': result['simulator_stats']['cpu_overload_rate'],
            'avg_pods': result['simulator_stats']['avg_pods'],
            'min_pods': result['simulator_stats']['min_pods'],
            'max_pods': result['simulator_stats']['max_pods']
        })
    
    summary_df = pd.DataFrame(summary_data)
    summary_file = f"results/SUMMARY_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    summary_df.to_csv(summary_file, index=False)
    
    print(f"\n✓ Summary report saved to {summary_file}")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS COMPLETED!")
    print("="*70)
    print(f"\n📁 Results saved in: results/")
    print(f"   - Detailed logs for each test")
    print(f"   - State change logs")
    print(f"   - Visualization plots")
    print(f"   - Summary report: {summary_file}")

def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) > 1:
        # Run specific test
        test_file = sys.argv[1]
        test_name = os.path.basename(test_file).replace('.csv', '')
        
        model_30, model_60 = load_models()
        run_test(test_file, test_name, model_30, model_60)
    else:
        # Run all tests
        run_all_tests()

if __name__ == "__main__":
    main()

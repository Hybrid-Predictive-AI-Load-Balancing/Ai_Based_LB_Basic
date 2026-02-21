"""
Compare multiple test results and generate comparison report
"""

import pandas as pd
import matplotlib.pyplot as plt
import os
import glob

def load_all_results():
    """Load all detailed log files"""
    log_files = glob.glob("results/*_detailed_log.csv")
    
    results = {}
    for file in log_files:
        test_name = os.path.basename(file).replace('_detailed_log.csv', '')
        results[test_name] = pd.read_csv(file)
    
    return results

def generate_comparison_plots(results):
    """Generate comparison plots across all tests"""
    
    fig, axs = plt.subplots(3, 3, figsize=(18, 12))
    fig.suptitle('AI Load Balancer - Test Comparison Dashboard', 
                 fontsize=16, fontweight='bold')
    
    test_names = list(results.keys())
    colors = plt.cm.tab10(range(len(test_names)))
    
    # Plot 1: Average CPU by test
    ax = axs[0, 0]
    avg_cpus = [results[t]['cpu'].mean() for t in test_names]
    ax.bar(range(len(test_names)), avg_cpus, color=colors)
    ax.set_ylabel('Average CPU (%)')
    ax.set_title('Average CPU Usage')
    ax.set_xticks(range(len(test_names)))
    ax.set_xticklabels(test_names, rotation=45, ha='right', fontsize=8)
    ax.grid(True, alpha=0.3)
    
    # Plot 2: Max Latency by test
    ax = axs[0, 1]
    max_latencies = [results[t]['latency'].max() for t in test_names]
    ax.bar(range(len(test_names)), max_latencies, color=colors)
    ax.axhline(200, color='red', linestyle='--', label='Threshold')
    ax.set_ylabel('Max Latency (ms)')
    ax.set_title('Maximum Latency')
    ax.set_xticks(range(len(test_names)))
    ax.set_xticklabels(test_names, rotation=45, ha='right', fontsize=8)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 3: Latency Violations by test
    ax = axs[0, 2]
    violations = [results[t]['latency_violation'].sum() for t in test_names]
    ax.bar(range(len(test_names)), violations, color=colors)
    ax.set_ylabel('Violation Count')
    ax.set_title('Latency Violations (>200ms)')
    ax.set_xticks(range(len(test_names)))
    ax.set_xticklabels(test_names, rotation=45, ha='right', fontsize=8)
    ax.grid(True, alpha=0.3)
    
    # Plot 4: Average Pods by test
    ax = axs[1, 0]
    avg_pods = [results[t]['pods'].mean() for t in test_names]
    ax.bar(range(len(test_names)), avg_pods, color=colors)
    ax.set_ylabel('Average Pods')
    ax.set_title('Average Pod Count')
    ax.set_xticks(range(len(test_names)))
    ax.set_xticklabels(test_names, rotation=45, ha='right', fontsize=8)
    ax.grid(True, alpha=0.3)
    
    # Plot 5: Scale Actions by test
    ax = axs[1, 1]
    scale_ups = [(results[t]['action'] == 'SCALE_UP').sum() for t in test_names]
    scale_downs = [(results[t]['action'] == 'SCALE_DOWN').sum() for t in test_names]
    
    x = range(len(test_names))
    width = 0.35
    ax.bar([i - width/2 for i in x], scale_ups, width, label='Scale Up', color='green', alpha=0.7)
    ax.bar([i + width/2 for i in x], scale_downs, width, label='Scale Down', color='red', alpha=0.7)
    ax.set_ylabel('Action Count')
    ax.set_title('Scaling Actions')
    ax.set_xticks(x)
    ax.set_xticklabels(test_names, rotation=45, ha='right', fontsize=8)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Plot 6: CPU Overload by test
    ax = axs[1, 2]
    overloads = [results[t]['cpu_overload'].sum() for t in test_names]
    ax.bar(range(len(test_names)), overloads, color=colors)
    ax.set_ylabel('Overload Count')
    ax.set_title('CPU Overload Events (>90%)')
    ax.set_xticks(range(len(test_names)))
    ax.set_xticklabels(test_names, rotation=45, ha='right', fontsize=8)
    ax.grid(True, alpha=0.3)
    
    # Plot 7: Traffic Range by test
    ax = axs[2, 0]
    min_traffic = [results[t]['request_rate'].min() for t in test_names]
    max_traffic = [results[t]['request_rate'].max() for t in test_names]
    
    for i, test in enumerate(test_names):
        ax.plot([i, i], [min_traffic[i], max_traffic[i]], 
                marker='o', linewidth=3, color=colors[i], markersize=8)
    
    ax.set_ylabel('Request Rate (req/s)')
    ax.set_title('Traffic Range (Min-Max)')
    ax.set_xticks(range(len(test_names)))
    ax.set_xticklabels(test_names, rotation=45, ha='right', fontsize=8)
    ax.grid(True, alpha=0.3)
    
    # Plot 8: Average Latency by test
    ax = axs[2, 1]
    avg_latencies = [results[t]['latency'].mean() for t in test_names]
    ax.bar(range(len(test_names)), avg_latencies, color=colors)
    ax.set_ylabel('Average Latency (ms)')
    ax.set_title('Average Latency')
    ax.set_xticks(range(len(test_names)))
    ax.set_xticklabels(test_names, rotation=45, ha='right', fontsize=8)
    ax.grid(True, alpha=0.3)
    
    # Plot 9: Performance Score (custom metric)
    ax = axs[2, 2]
    scores = []
    for test in test_names:
        df = results[test]
        # Score: lower is better
        # Penalty for violations, overloads, and high latency
        score = (
            df['latency_violation'].sum() * 10 +  # Heavy penalty for violations
            df['cpu_overload'].sum() * 5 +        # Moderate penalty for overload
            df['latency'].mean() * 0.1             # Light penalty for avg latency
        )
        scores.append(score)
    
    ax.bar(range(len(test_names)), scores, color=colors)
    ax.set_ylabel('Performance Score')
    ax.set_title('Overall Performance Score (Lower=Better)')
    ax.set_xticks(range(len(test_names)))
    ax.set_xticklabels(test_names, rotation=45, ha='right', fontsize=8)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('results/COMPARISON_DASHBOARD.png', dpi=150, bbox_inches='tight')
    print("✓ Comparison dashboard saved to results/COMPARISON_DASHBOARD.png")
    plt.show()

def print_comparison_table(results):
    """Print a formatted comparison table"""
    
    print("\n" + "="*100)
    print(" "*35 + "TEST COMPARISON TABLE")
    print("="*100)
    
    print(f"{'Test Name':<25} {'Avg CPU':<10} {'Max Lat':<10} {'Violations':<12} "
          f"{'Avg Pods':<10} {'Scale Ups':<12} {'Scale Downs':<12}")
    print("-"*100)
    
    for test_name in sorted(results.keys()):
        df = results[test_name]
        
        avg_cpu = df['cpu'].mean()
        max_lat = df['latency'].max()
        violations = df['latency_violation'].sum()
        avg_pods = df['pods'].mean()
        scale_ups = (df['action'] == 'SCALE_UP').sum()
        scale_downs = (df['action'] == 'SCALE_DOWN').sum()
        
        print(f"{test_name:<25} {avg_cpu:<10.1f} {max_lat:<10.1f} {violations:<12d} "
              f"{avg_pods:<10.1f} {scale_ups:<12d} {scale_downs:<12d}")
    
    print("="*100)

def main():
    """Main comparison function"""
    print("╔" + "="*98 + "╗")
    print("║" + " "*30 + "TEST RESULTS COMPARISON" + " "*45 + "║")
    print("╚" + "="*98 + "╝")
    
    print("\n📊 Loading test results...")
    results = load_all_results()
    
    if not results:
        print("❌ No test results found. Please run tests first using main.py")
        return
    
    print(f"✓ Loaded {len(results)} test results\n")
    
    # Print comparison table
    print_comparison_table(results)
    
    # Generate comparison plots
    print("\n📈 Generating comparison dashboard...")
    generate_comparison_plots(results)
    
    print("\n✅ Comparison analysis complete!")

if __name__ == "__main__":
    main()

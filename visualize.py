"""
Enhanced Real-time Visualization with detailed metrics and state information
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

class RealtimeVisualizer:
    def __init__(self, test_name="Test"):
        plt.ion()
        
        self.test_name = test_name
        
        # Create figure with 5 subplots
        self.fig, self.axs = plt.subplots(5, 1, figsize=(14, 12))
        self.fig.suptitle(f'AI Load Balancer Test: {test_name}', fontsize=16, fontweight='bold')
        
        # Data storage
        self.traffic_data = []
        self.pods_data = []
        self.latency_data = []
        self.cpu_data = []
        self.memory_data = []
        self.prob_30s_data = []
        self.prob_60s_data = []
        self.actions = []
        self.action_times = []
        
        # State info
        self.current_spike_desc = ""
        self.current_action = "HOLD"
        self.current_reason = ""
        
        # Colors
        self.color_traffic = '#2E86AB'
        self.color_pods = '#A23B72'
        self.color_latency = '#F18F01'
        self.color_cpu = '#C73E1D'
        self.color_memory = '#6A994E'
        self.color_prob = '#BC4B51'
        
        # Setup plots
        self._setup_plots()
    
    def _setup_plots(self):
        """Initialize plot settings"""
        # Plot 1: Traffic Rate
        self.axs[0].set_ylabel('Request Rate\n(req/s)', fontweight='bold')
        self.axs[0].grid(True, alpha=0.3)
        
        # Plot 2: Pod Count
        self.axs[1].set_ylabel('Active Pods', fontweight='bold')
        self.axs[1].grid(True, alpha=0.3)
        
        # Plot 3: Latency
        self.axs[2].set_ylabel('Latency (ms)', fontweight='bold')
        self.axs[2].grid(True, alpha=0.3)
        
        # Plot 4: CPU & Memory
        self.axs[3].set_ylabel('Usage (%)', fontweight='bold')
        self.axs[3].grid(True, alpha=0.3)
        
        # Plot 5: Prediction Probabilities
        self.axs[4].set_ylabel('Spike\nProbability', fontweight='bold')
        self.axs[4].set_xlabel('Time Step', fontweight='bold')
        self.axs[4].grid(True, alpha=0.3)
        
        plt.tight_layout()
    
    def update(self, req, pods, latency, cpu, memory, prob_30s, prob_60s, 
               action, reason, spike_desc):
        """Update all plots with new data"""
        
        # Store data
        self.traffic_data.append(req)
        self.pods_data.append(pods)
        self.latency_data.append(latency)
        self.cpu_data.append(cpu)
        self.memory_data.append(memory)
        self.prob_30s_data.append(prob_30s)
        self.prob_60s_data.append(prob_60s)
        
        # Track actions
        self.current_action = action
        self.current_reason = reason
        self.current_spike_desc = spike_desc
        
        if action != "HOLD":
            self.actions.append(action)
            self.action_times.append(len(self.traffic_data) - 1)
        
        # Clear all axes
        for ax in self.axs:
            ax.cla()
        
        time_steps = range(len(self.traffic_data))
        
        # Plot 1: Traffic Rate
        self.axs[0].plot(time_steps, self.traffic_data, 
                        color=self.color_traffic, linewidth=2, label='Traffic')
        self.axs[0].fill_between(time_steps, self.traffic_data, 
                                 alpha=0.3, color=self.color_traffic)
        self.axs[0].set_ylabel('Request Rate\n(req/s)', fontweight='bold')
        self.axs[0].legend(loc='upper left')
        self.axs[0].grid(True, alpha=0.3)
        self.axs[0].set_title(f'Current Status: {spike_desc}', 
                             fontsize=11, loc='left')
        
        # Plot 2: Pod Count with action markers
        self.axs[1].plot(time_steps, self.pods_data, 
                        color=self.color_pods, linewidth=2.5, 
                        marker='o', markersize=3, label='Pods')
        
        # Mark scale actions
        for i, action_time in enumerate(self.action_times):
            if action_time < len(self.traffic_data):
                action_type = self.actions[i]
                color = 'green' if action_type == 'SCALE_UP' else 'red'
                marker = '^' if action_type == 'SCALE_UP' else 'v'  # Use standard matplotlib markers
                self.axs[1].scatter(action_time, self.pods_data[action_time], 
                                   color=color, s=150, marker=marker, 
                                   zorder=5, edgecolors='black', linewidths=1)
        
        self.axs[1].set_ylabel('Active Pods', fontweight='bold')
        self.axs[1].legend(loc='upper left')
        self.axs[1].grid(True, alpha=0.3)
        self.axs[1].set_title(f'Action: {action} - {reason}', 
                             fontsize=10, loc='left')
        
        # Plot 3: Latency with threshold
        self.axs[2].plot(time_steps, self.latency_data, 
                        color=self.color_latency, linewidth=2, label='Latency')
        self.axs[2].axhline(200, color='red', linestyle='--', 
                           linewidth=2, label='Threshold (200ms)', alpha=0.7)
        
        # Highlight violations
        violations = [l > 200 for l in self.latency_data]
        if any(violations):
            violation_times = [t for t, v in enumerate(violations) if v]
            violation_values = [self.latency_data[t] for t in violation_times]
            self.axs[2].scatter(violation_times, violation_values, 
                               color='red', s=50, zorder=5, alpha=0.6)
        
        self.axs[2].set_ylabel('Latency (ms)', fontweight='bold')
        self.axs[2].legend(loc='upper left')
        self.axs[2].grid(True, alpha=0.3)
        
        # Plot 4: CPU & Memory
        self.axs[3].plot(time_steps, self.cpu_data, 
                        color=self.color_cpu, linewidth=2, label='CPU')
        self.axs[3].plot(time_steps, self.memory_data, 
                        color=self.color_memory, linewidth=2, 
                        linestyle='--', label='Memory')
        self.axs[3].axhline(90, color='red', linestyle=':', 
                           linewidth=1.5, alpha=0.5)
        self.axs[3].axhline(70, color='orange', linestyle=':', 
                           linewidth=1.5, alpha=0.5)
        self.axs[3].axhline(30, color='blue', linestyle=':', 
                           linewidth=1.5, alpha=0.5)
        self.axs[3].set_ylabel('Usage (%)', fontweight='bold')
        self.axs[3].legend(loc='upper left')
        self.axs[3].grid(True, alpha=0.3)
        self.axs[3].set_ylim([0, 105])
        
        # Plot 5: Prediction Probabilities
        self.axs[4].plot(time_steps, self.prob_30s_data, 
                        color='#FF6B6B', linewidth=2, label='30s Spike Prob')
        self.axs[4].plot(time_steps, self.prob_60s_data, 
                        color='#4ECDC4', linewidth=2, label='60s Spike Prob')
        self.axs[4].axhline(0.35, color='orange', linestyle='--', 
                           linewidth=1.5, alpha=0.6, label='Threshold (0.35)')
        self.axs[4].axhline(0.25, color='yellow', linestyle='--', 
                           linewidth=1.5, alpha=0.6, label='Threshold (0.25)')
        self.axs[4].set_ylabel('Spike\nProbability', fontweight='bold')
        self.axs[4].set_xlabel('Time Step', fontweight='bold')
        self.axs[4].legend(loc='upper left', fontsize=8)
        self.axs[4].grid(True, alpha=0.3)
        self.axs[4].set_ylim([0, 1.05])
        
        plt.tight_layout()
        plt.pause(0.01)
    
    def save_plot(self, filename):
        """Save the current plot to file"""
        self.fig.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"✓ Plot saved to {filename}")
    
    def close(self):
        """Close the plot"""
        plt.close(self.fig)

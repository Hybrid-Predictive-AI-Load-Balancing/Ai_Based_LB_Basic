"""
Enhanced Load Simulator with detailed metrics tracking
"""

import numpy as np

class EnhancedLoadSimulator:
    def __init__(self, df, feature_cols):
        self.df = df.reset_index(drop=True)
        self.feature_cols = feature_cols
        
        # Current state
        self.current_cpu = 20.0
        self.current_latency = 50.0
        self.current_memory = 20.0
        
        # Metrics tracking
        self.cpu_history = []
        self.latency_history = []
        self.memory_history = []
        self.pod_history = []
        
        # Performance metrics
        self.latency_violations = 0  # Times latency exceeded threshold
        self.cpu_overload = 0  # Times CPU exceeded 90%
        self.underutilized = 0  # Times CPU was below 20%
        
        # Thresholds
        self.latency_threshold = 200  # ms
        self.cpu_high_threshold = 90  # %
        self.cpu_low_threshold = 20  # %
    
    def get_features(self, t):
        """Get features for time step t"""
        return self.df.loc[t, self.feature_cols].values.reshape(1, -1)
    
    def apply_pods(self, pods, t):
        """
        Simulate the effect of pod count on system metrics
        
        Returns:
            tuple: (cpu, latency, memory, metrics_dict)
        """
        req = self.df.loc[t, "request_rate"]
        load_per_pod = req / pods if pods > 0 else req
        
        # CPU calculation: more realistic model
        # Base CPU + load-dependent component
        base_cpu = 10
        self.current_cpu = min(100, base_cpu + load_per_pod * 1.2)
        
        # Memory calculation: follows CPU but with lag
        self.current_memory = min(100, base_cpu * 0.8 + load_per_pod * 0.95)
        
        # Latency calculation: exponential increase after 70% CPU
        if self.current_cpu < 70:
            self.current_latency = 50 + self.current_cpu * 0.8
        else:
            # Exponential increase for high CPU
            cpu_excess = self.current_cpu - 70
            self.current_latency = 50 + 70 * 0.8 + cpu_excess * 2.5
        
        # Add realistic noise
        self.current_latency += np.random.normal(0, 2)
        self.current_latency = max(30, self.current_latency)
        
        # Track violations
        if self.current_latency > self.latency_threshold:
            self.latency_violations += 1
        if self.current_cpu > self.cpu_high_threshold:
            self.cpu_overload += 1
        if self.current_cpu < self.cpu_low_threshold:
            self.underutilized += 1
        
        # Store history
        self.cpu_history.append(self.current_cpu)
        self.latency_history.append(self.current_latency)
        self.memory_history.append(self.current_memory)
        self.pod_history.append(pods)
        
        # Build metrics dict
        metrics = {
            'request_rate': req,
            'load_per_pod': load_per_pod,
            'cpu': self.current_cpu,
            'memory': self.current_memory,
            'latency': self.current_latency,
            'pods': pods,
            'latency_ok': self.current_latency <= self.latency_threshold,
            'cpu_ok': self.current_cpu <= self.cpu_high_threshold
        }
        
        return self.current_cpu, self.current_latency, self.current_memory, metrics
    
    def get_statistics(self):
        """Get simulator performance statistics"""
        total_steps = len(self.cpu_history)
        
        return {
            'total_steps': total_steps,
            'latency_violations': self.latency_violations,
            'latency_violation_rate': self.latency_violations / total_steps if total_steps > 0 else 0,
            'cpu_overload_count': self.cpu_overload,
            'cpu_overload_rate': self.cpu_overload / total_steps if total_steps > 0 else 0,
            'underutilization_count': self.underutilized,
            'underutilization_rate': self.underutilized / total_steps if total_steps > 0 else 0,
            'avg_cpu': np.mean(self.cpu_history) if self.cpu_history else 0,
            'max_cpu': np.max(self.cpu_history) if self.cpu_history else 0,
            'avg_latency': np.mean(self.latency_history) if self.latency_history else 0,
            'max_latency': np.max(self.latency_history) if self.latency_history else 0,
            'avg_pods': np.mean(self.pod_history) if self.pod_history else 0,
            'max_pods': np.max(self.pod_history) if self.pod_history else 0,
            'min_pods': np.min(self.pod_history) if self.pod_history else 0
        }
    
    def get_spike_description(self, t):
        """Get description of current traffic condition"""
        req = self.df.loc[t, "request_rate"]
        spike_30 = self.df.loc[t, "spike_30s"]
        spike_60 = self.df.loc[t, "spike_60s"]
        
        if spike_60 == 1:
            return f"🔥 MAJOR SPIKE INCOMING (60s) - Current: {req:.0f} req/s"
        elif spike_30 == 1:
            return f"⚠️  SPIKE INCOMING (30s) - Current: {req:.0f} req/s"
        elif req > 150:
            return f"📈 VERY HIGH LOAD - {req:.0f} req/s"
        elif req > 100:
            return f"📊 HIGH LOAD - {req:.0f} req/s"
        elif req > 60:
            return f"📉 MODERATE LOAD - {req:.0f} req/s"
        elif req < 30:
            return f"💤 LOW LOAD - {req:.0f} req/s"
        else:
            return f"✅ NORMAL LOAD - {req:.0f} req/s"

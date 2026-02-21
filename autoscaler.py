"""
Enhanced AutoScaler with detailed state tracking and logging
"""

class EnhancedAutoScaler:
    def __init__(self, min_pods=2, max_pods=20, cooldown=10):
        self.min_pods = min_pods
        self.max_pods = max_pods
        self.cooldown = cooldown
        self.cooldown_timer = 0
        
        # State tracking
        self.scale_history = []
        self.last_action = "HOLD"
        self.last_action_time = 0
        self.total_scale_ups = 0
        self.total_scale_downs = 0
        self.holds = 0
        
        # Decision tracking
        self.decision_reasons = []
    
    def step(self, prob_30s, prob_60s, avg_cpu, current_pods, time_step, spike_description=""):
        """
        Execute one autoscaling decision step
        
        Returns:
            tuple: (new_pods, action, reason)
        """
        action = "HOLD"
        delta = 0
        reason = ""
        
        # Cooldown check
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1
            reason = f"In cooldown ({self.cooldown_timer}s remaining)"
            self.holds += 1
            
            self.scale_history.append({
                'time': time_step,
                'action': action,
                'pods': current_pods,
                'reason': reason,
                'prob_30s': prob_30s,
                'prob_60s': prob_60s,
                'cpu': avg_cpu,
                'spike_desc': spike_description
            })
            
            return current_pods, action, reason
        
        # EMERGENCY: Reactive scaling if CPU critically high (model failure safety net)
        if avg_cpu >= 85:
            delta = 3 if avg_cpu >= 95 else 2
            action = "SCALE_UP"
            reason = f"⚠️ EMERGENCY CPU Override ({avg_cpu:.1f}%) - Model may have missed spike"
            self.cooldown_timer = self.cooldown
            self.total_scale_ups += 1
        
        # Scale up logic (predictive)
        elif prob_30s >= 0.35:
            delta = 2 if prob_60s >= 0.5 else 1
            action = "SCALE_UP"
            reason = f"High spike probability (30s:{prob_30s:.2f}, 60s:{prob_60s:.2f})"
            self.cooldown_timer = self.cooldown
            self.total_scale_ups += 1
            
        elif prob_60s >= 0.25 and avg_cpu >= 70:
            delta = 2 if prob_60s >= 0.5 else 1
            action = "SCALE_UP"
            reason = f"Moderate spike prob ({prob_60s:.2f}) + High CPU ({avg_cpu:.1f}%)"
            self.cooldown_timer = self.cooldown
            self.total_scale_ups += 1
            
        # Scale down logic
        elif prob_30s < 0.15 and avg_cpu <= 30:
            delta = -1
            action = "SCALE_DOWN"
            reason = f"Low spike probability ({prob_30s:.2f}) + Low CPU ({avg_cpu:.1f}%)"
            self.cooldown_timer = self.cooldown
            self.total_scale_downs += 1
        
        else:
            reason = f"Holding: prob_30s={prob_30s:.2f}, prob_60s={prob_60s:.2f}, CPU={avg_cpu:.1f}%"
            self.holds += 1
        
        # Calculate new pods
        new_pods = max(self.min_pods, min(self.max_pods, current_pods + delta))
        
        # Check if we hit limits
        if new_pods == self.max_pods and delta > 0:
            reason += " [HIT MAX LIMIT]"
        elif new_pods == self.min_pods and delta < 0:
            reason += " [HIT MIN LIMIT]"
        
        # Record state
        self.last_action = action
        self.last_action_time = time_step
        
        self.scale_history.append({
            'time': time_step,
            'action': action,
            'pods_before': current_pods,
            'pods_after': new_pods,
            'delta': delta,
            'reason': reason,
            'prob_30s': prob_30s,
            'prob_60s': prob_60s,
            'cpu': avg_cpu,
            'spike_desc': spike_description,
            'cooldown_set': self.cooldown_timer
        })
        
        return new_pods, action, reason
    
    def get_statistics(self):
        """Get autoscaling statistics"""
        total_actions = self.total_scale_ups + self.total_scale_downs + self.holds
        
        return {
            'total_scale_ups': self.total_scale_ups,
            'total_scale_downs': self.total_scale_downs,
            'total_holds': self.holds,
            'total_actions': total_actions,
            'scale_up_rate': self.total_scale_ups / total_actions if total_actions > 0 else 0,
            'scale_down_rate': self.total_scale_downs / total_actions if total_actions > 0 else 0,
            'hold_rate': self.holds / total_actions if total_actions > 0 else 0
        }
    
    def get_scale_history(self):
        """Get complete scaling history"""
        return self.scale_history

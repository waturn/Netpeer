class Statistics:
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.error_requests = 0
        
        self.latencies = []
        self.prev_latency = None
        self.jitter = []
        self.spike = None
        self.spike_count = 0
        
        self.packet_loss_percent = 0.0
        
    def update_ping(self, response):
        # Update the statistics based on the latest ping response
        self.total_requests += 1
        self.spike = False
        
        if response["status"] == "success":
            self.successful_requests += 1
            
            if response["latency_ms"] is not None:
                self.latencies.append(response["latency_ms"])
                
                if self.prev_latency is not None:
                    # Calculate jitter
                    jitter_val = abs(response["latency_ms"] - self.prev_latency)
                    self.jitter.append(jitter_val)
                    
                    # Latency spike detection
                    if (response["latency_ms"] - self.prev_latency) > (self.average_latency() / 3):
                        self.spike = True
                        self.spike_count += 1
                self.prev_latency = response["latency_ms"]
            else:
                self.prev_latency = None
        elif response["status"] == "timeout":
            self.prev_latency = None
            self.failed_requests += 1
        else:
            self.prev_latency = None
            self.error_requests += 1
    
    def get_packet_loss(self):
        valid_packets = self.successful_requests + self.failed_requests
        if valid_packets == 0:
            return None
        # Calculate packet loss percentage based on total requests and failed requests
        self.packet_loss_percent = (self.failed_requests / valid_packets) * 100
        return self.packet_loss_percent
    
    def average_latency(self):
        # Calculate and return the average latency if there were successful requests
        if not self.latencies:
            return None
        return sum(self.latencies) / len(self.latencies)
    
    def average_jitter(self):
        # Calculate and return the average jitter if there were jitter values
        if not self.jitter:
            return None
        return sum(self.jitter) / len(self.jitter)
    
    def determineStatus(self):
        valid_packets = self.successful_requests + self.failed_requests
        spike_rate = self.spike_count / valid_packets if valid_packets > 0 else 0
        packet_loss = self.get_packet_loss() if valid_packets > 0 else None
        
        if valid_packets < 1:
            return "UNKNOWN"
        elif packet_loss == 100:
            return "UNREACHABLE"
        elif packet_loss > 20:
            return "POOR"
        elif packet_loss > 5 or spike_rate > 0.1:
            return "UNSTABLE"
        elif packet_loss > 0 or self.spike_count > 0:
            return "FINE"
        else:
            return "EXCELLENT"
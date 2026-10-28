class Statistics:
    """
    Class to track and manage statistics for ping responses, including total requests, successful requests, failed requests, error requests, latencies, jitter, and spike detection.
    """
    def __init__(self):
        self.total_requests = 0    # Total number of ping requests made
        self.successful_requests = 0    # Number of successful ping responses
        self.failed_requests = 0    # Number of failed ping responses
        self.error_requests = 0    # Number of ping responses that resulted in errors
        
        self.latencies = []    # List of latencies (in milliseconds) for successful ping responses
        self.prev_latency = None    # The latency of the previous successful ping response
        self.jitter = []    # List of jitter values calculated from the differences between consecutive latencies
        self.spike = None   # Flag indicating if a latency spike was detected in the current ping response
        self.spike_count = 0    # Count of detected latency spikes
        
        self.packet_loss_percent = 0.0    # Percentage of packet loss calculated from total requests and failed requests
        
    def update_ping(self, response):
        # Update the statistics instance based on the latest ping response
        self.total_requests += 1
        self.spike = False
        self.curr_jitter = None
        
        if response["status"] == "success":
            self.successful_requests += 1
            
            if response["latency_ms"] is not None:
                self.latencies.append(response["latency_ms"])
                
                if self.prev_latency is not None:
                    # Calculate jitter
                    jitter_val = abs(response["latency_ms"] - self.prev_latency)
                    self.curr_jitter = jitter_val
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
        # Calculate and return the packet loss percentage based on total requests and failed requests
        valid_packets = self.successful_requests + self.failed_requests
        if valid_packets == 0:
            return None
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
        # Determine the overall status of the ping session based on packet loss and spike rate
        valid_packets = self.successful_requests + self.failed_requests
        spike_rate = self.spike_count / valid_packets if valid_packets > 0 else 0
        packet_loss = self.get_packet_loss() if valid_packets > 0 else None
        avg_jitter = self.average_jitter()
        
        if valid_packets == 0:
            return "UNKNOWN"
        elif packet_loss == 100:
            return "UNREACHABLE"
        elif valid_packets < 6:
            return "CALCULATING..."
        elif packet_loss > 20:
            return "POOR"
        elif packet_loss > 5 or spike_rate > 0.1 or (avg_jitter is not None and avg_jitter > 15):
            return "UNSTABLE"
        elif packet_loss > 0 or self.spike_count > 0 or (avg_jitter is not None and avg_jitter > 5):
            return "FINE"
        else:
            return "EXCELLENT"
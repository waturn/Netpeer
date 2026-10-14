class Statistics:
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.error_requests = 0
        
        self.latencies = []
        
        self.packet_loss_percent = 0.0
        
    def update_ping(self, response):
        # Update the statistics based on the latest ping response
        self.total_requests += 1
        
        if response["status"] == "success":
            self.successful_requests += 1
            if response["latency_ms"] is not None:
                self.latencies.append(response["latency_ms"])
        elif response["status"] == "timeout":
            self.failed_requests += 1
        else:
            self.error_requests += 1
    
    def packet_loss(self):
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
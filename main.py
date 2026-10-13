# Author: Grayson Molnar
# version: 0.1.4
import os
from monitor.ping import ping
from time import sleep, monotonic

def clear_terminal():
    # Clear the terminal based on the operating system
    os.system('cls' if os.name == 'nt' else 'clear')

def handle_ping(target, interval):
    # Ping the target at a set interval, format and print the response
    for i in range(5):
        # Start a monotonic timer
        start_time = monotonic()
        
        # Ping the target and get the response
        response = ping(target)
        status = response["status"].upper()
        
        # Format message based on the status of the ping response
        if response["status"] == "success":
            message = f"{response['latency_ms']}ms" if response["latency_ms"] is not None else "Reachable"
        else:
            message = response.get("error", "No response")
        
        # Print the formatted response
        print(f"[{response['timestamp']}] {status} | {message}")
        
        # Calculate the elapsed time since the start of the ping
        elapsed = monotonic() - start_time
        
        if i < 4:
            # Sleep for the remaining time to maintain the interval, but not less than 0
            sleep(max(0, interval - elapsed))

def startup(target, interval):
    # Clear the terminal, print header, and ping target at a set interval
    clear_terminal()
    print("Netpeer v0.1.4")
    print("Target: " + target)
    print("Interval: " + str(interval) + " seconds\n")
    handle_ping(target, interval)

# Main method
def main():
    # Test suite
    startup("google.com", 5)
if __name__ == "__main__":
    main()
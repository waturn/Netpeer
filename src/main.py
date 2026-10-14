import os
import tomllib
from monitor.ping import ping
from monitor.statistics import Statistics
from time import sleep, monotonic
from pathlib import Path

def get_version_number():
    root = Path(__file__).resolve().parent
    with open(root / "pyproject.toml", "rb") as f:
        config = tomllib.load(f)
    return config["project"]["version"]

def clear_terminal():
    # Clear the terminal based on the operating system
    os.system('cls' if os.name == 'nt' else 'clear')

def handle_ping(target, interval):
    # Ping the target at a set interval, format, and feed the response to the Statistics class to print
    # 
    # Runs indefinitely until interrupted by the user (Ctrl+C)
    final_stats = Statistics()
    try:
        while True:
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
            
            # Update the final statistics with the latest ping response
            final_stats.update_ping(response)
            
            # Print the formatted response
            print(f"[{response['timestamp']}] {status} | {message}")
            
            # Calculate the elapsed time since the start of the ping
            elapsed = monotonic() - start_time
            # Sleep for the remaining time to maintain the interval, but not less than 0
            sleep(max(0, interval - elapsed))
    except KeyboardInterrupt:
        print("\n^C")
        # Print the final statistics of the ping session and exit
        sessionStats(final_stats, target)

def sessionStats(stats, target):
    # Print the final statistics of the ping session
    print("\n------- SESSION SUMMARY -------")
    print(f"{'Target:':<20}{target}")
    print(f"{'Checks Attempted:':<20}{stats.total_requests}")
    print(f"{'Ping Attempts:':<20}{stats.successful_requests + stats.failed_requests}")
    print(f"{'Packets Received:':<20}{stats.successful_requests}")
    print(f"{'Packets Lost:':<20}{stats.failed_requests}")
    print(f"{'Packet Errors:':<20}{stats.error_requests}")
    
    # Calculate packet loss percentage based on total requests and failed requests
    packet_loss = stats.packet_loss()
    if packet_loss is not None:
        print(f"{'Packet Loss:':<20}{packet_loss:.2f}%")
    else:
        print(f"{'Packet Loss:':<20}N/A")
    
    print()
    
    # Calculate minimum and maximum latency from all responses
    if stats.latencies:
        min_latency = min(stats.latencies)
        max_latency = max(stats.latencies)
        print(f"{'Minimum Latency:':<20}{min_latency:.2f} ms")
        print(f"{'Maximum Latency:':<20}{max_latency:.2f} ms")
    else:
        print(f"{'Minimum Latency:':<20}N/A")
        print(f"{'Maximum Latency:':<20}N/A")
    
    # Calculate and print the average latency if there were successful requests
    avg_latency = stats.average_latency()
    if avg_latency is not None:
        print(f"{'Average Latency:':<20}{avg_latency:.2f} ms")
    else:
        print(f"{'Average Latency:':<20}N/A")
    print("-------------------------------")

def startup(target, interval):
    # Clear the terminal, print header, and ping target at a set interval
    clear_terminal()
    print("Netpeer v" + get_version_number())
    print("Target: " + target)
    print("Interval: " + str(interval) + " seconds\n")
    handle_ping(target, interval)

# Main method
def main():
    # Test suite
    startup("google.com", 1)
if __name__ == "__main__":
    main()
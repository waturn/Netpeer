# Standard Libraries
import os
import tomllib

from datetime import datetime, timezone
from time import sleep, monotonic
from pathlib import Path

# Local Packages
from monitor.ping import ping
from monitor.statistics import Statistics
from storage.database import init_database, insert_session, insert_ping_result, update_session_end_time, get_sessions, get_session_results


def get_version_number():
    root = Path(__file__).resolve().parent
    with open(root / "pyproject.toml", "rb") as f:
        config = tomllib.load(f)
    return config["project"]["version"]

def clear_terminal():
    # Clear the terminal based on the operating system
    os.system('cls' if os.name == 'nt' else 'clear')

def handle_ping(target, interval, session_id):
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
            
            # Convert stored timestamp to local time
            timestamp = datetime.fromisoformat(response["timestamp"])
            display_time = timestamp.astimezone().strftime("%H:%M:%S")
            
            # Format message based on the status of the ping response
            if response["status"] == "success":
                message = f"{response['latency_ms']}ms" if response["latency_ms"] is not None else "Reachable"
            else:
                message = response.get("error", "No response")
            
            # Update the final statistics with the latest ping response
            final_stats.update_ping(response)
            
            # Insert the ping result into the database
            insert_ping_result(
                session_id,
                timestamp,
                status,
                response.get("latency_ms"),
                final_stats.curr_jitter,
                int(final_stats.spike),
                response.get("error")
            )

            # Print the formatted response
            if final_stats.spike is True:
                print(f"[{display_time}] {status} | {message} SPIKE")
            else:
                print(f"[{display_time}] {status} | {message}")
            
            # Calculate the elapsed time since the start of the ping
            elapsed = monotonic() - start_time
            # Sleep for the remaining time to maintain the interval, but not less than 0
            sleep(max(0, interval - elapsed))
    except KeyboardInterrupt:
        print("\n^C")
        clear_terminal()
        print_menu()
        # Get last session ID from the database and update the database
        update_session_end_time(session_id, datetime.now(timezone.utc).isoformat())
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
    packet_loss = stats.get_packet_loss()
    if packet_loss is not None:
        print(f"{'Packet Loss:':<20}{packet_loss:.2f}%")
    else:
        print(f"{'Packet Loss:':<20}N/A")
    print()
    
    # Calculate minimum and maximum latency from all responses
    if stats.latencies:
        min_latency = min(stats.latencies)
        max_latency = max(stats.latencies)
        print(f"{'Minimum Latency:':<20}{min_latency} ms")
        print(f"{'Maximum Latency:':<20}{max_latency} ms")
    else:
        print(f"{'Minimum Latency:':<20}N/A")
        print(f"{'Maximum Latency:':<20}N/A")
    
    # Calculate and print the average latency if there were successful requests
    avg_latency = stats.average_latency()
    if avg_latency is not None:
        print(f"{'Average Latency:':<20}{avg_latency:.2f} ms")
    else:
        print(f"{'Average Latency:':<20}N/A")
    print()

    # Print the jitter values
    if stats.jitter:
        min_jitter = min(stats.jitter)
        max_jitter = max(stats.jitter)
        print(f"{'Minimum Jitter:':<20}{min_jitter} ms")
        print(f"{'Maximum Jitter:':<20}{max_jitter} ms")
    else:
        print(f"{'Minimum Jitter:':<20}N/A")
        print(f"{'Maximum Jitter:':<20}N/A")
        
    # Calculate and print the average jitter if there were jitter values
    avg_jitter = stats.average_jitter()
    if avg_jitter is not None:
        print(f"{'Average Jitter:':<20}{avg_jitter:.2f} ms")
    else:
        print(f"{'Average Jitter:':<20}N/A")
    print()
    
    print(f"{'Latency Spikes:':<20}{stats.spike_count}")
    print(f"{'Connection Status:':<20}{stats.determineStatus()}")
    print("-------------------------------")

def display_session_results(session_id):
    results = get_session_results(session_id)
    
    if not results:
        print(f"No results found for session ID {session_id}.")
        return
    
    print(f"\n------- SESSION {session_id} DETAILS -------")
    
    print(
        f"{'Time':<12}"
        f"{'Status':<12}"
        f"{'Latency':<12}"
        f"{'Jitter':<12}"
        f"{'Spike':<10}"
    )
    
    print("-" * 58)
    
    for row in results:
        ping_id, sid, timestamp, status, latency, jitter, spike, error = row
        
        # Convert timestamp to local time for display
        time = datetime.fromisoformat(timestamp)
        display_time = time.astimezone().strftime("%H:%M:%S")
        
        # Format additional fields for display
        latency_display = f"{latency}ms" if latency is not None else "N/A"
        jitter_display = f"{jitter}ms" if jitter is not None else "N/A"
        spike_display = "YES" if spike else "NO"
        
        print(
            f"{display_time:<12}"
            f"{status:<12}"
            f"{latency_display:<12}"
            f"{jitter_display:<12}"
            f"{spike_display:<10}"
        )
        
        if error:
            print(f"{'    Error:':<12}{error}")

def display_sessions():
    sessions = get_sessions()
    
    if not sessions:
        print("No previous sessions found.")
        return
    
    print("\n------- PREVIOUS SESSIONS -------")
    
    print(
        f"{'Session ID':<12}"
        f"{'Target':<20}"
        f"{'Started At':<25}"
        f"{'Ended At':<25}"
    )
    
    print("-" * 82)
    
    for session in sessions:
        session_id, target, started_at, ended_at = session
        
        # Convert timestamps to local time for display
        started_time = datetime.fromisoformat(started_at).astimezone().strftime("%Y-%m-%d %H:%M:%S")
        ended_time = datetime.fromisoformat(ended_at).astimezone().strftime("%Y-%m-%d %H:%M:%S") if ended_at else "N/A"
        
        print(
            f"{session_id:<12}"
            f"{target:<20}"
            f"{started_time:<25}"
            f"{ended_time:<25}"
        )

def startup(target, interval):
    # Insert a new session
    session_id = insert_session(target, datetime.now(timezone.utc).isoformat())
    
    # Print the target and interval before starting the ping process
    clear_terminal()
    print_menu()
    print("Target: " + target)
    print("Interval: " + str(interval) + " seconds\n")
    handle_ping(target, interval, session_id)

def print_menu():
    print("========= NETPEER " + get_version_number() + " ==========")
    print("""
    1. Start Monitoring
    2. View Previous Sessions
    3. View Session Details
    0. Exit
          """)
    print("==================================")

# Main method
def main():
    # Initialize the database and create necessary tables if they don't exist
    init_database()
    
    # Clear the terminal and print the main menu
    clear_terminal()
    print_menu()
    
    # Loop to handle user input for menu options
    choice = "-1"
    
    while choice != "0":
        choice = input("\nSelect an option: ")
        match choice:
            # Test suite for the main menu options
            case "0":
                print("Exiting...")
                exit(0)
            case "1":
                clear_terminal()
                print_menu()
                print("------- Start Monitoring -------")
                target = input("Enter target host (IP or domain): ")
                interval = input("Enter interval in seconds: ")
                # 194.29.100.26: AU server
                startup(target, int(interval))
            case "2":
                clear_terminal()
                print_menu()
                # View previous sessions
                display_sessions()
                pass
            case "3":
                clear_terminal()
                print_menu()
                # View session details
                session_id = input("Enter session ID: ")
                display_session_results(session_id)
                pass
if __name__ == "__main__":
    main()
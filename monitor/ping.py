# Author: Grayson Molnar
# version: 0.1.4
import subprocess
import re
from datetime import datetime

def ping(host):
    """
    Ping the host and return a dictionary of the results.
    
    param: host address
    return: dictionary containing timestamp, status, and latency in milliseconds
    """
    
    response = {
        "timestamp": None,
        "status": None,
        "latency_ms": None
    }
    
    # Capture runtime timestamp and format
    time = datetime.now()
    response.update({"timestamp": time.strftime('%H:%M:%S')})
    
    # Check if host value is empty
    if not host or not host.strip():
        response.update({"status": "error", "error": "Host is empty"})
        return response
    
    try:
        # Create and set a variable to store the output of the ping command
        out = subprocess.run(
            ["ping", "-n", "1", "-w", "1000", host], 
            capture_output=True, 
            text=True,
            timeout=2
        ) 
        
        # If subprocess command was successful (== 0)
        if out.returncode == 0:
            # Update the response dictionary with a success status
            response.update({"status": "success"})
            
            # Extract the response time (all after "time=" or "time<") from the output with regex
            match = re.search(r"time[=<]\s*(\d+)\s*ms", out.stdout)
            
            # If response time is found, return it, otherwise return "reachable"
            if match:
                response.update({"latency_ms": int(match.group(1))})
            return response
        
        else:
            full_out = (out.stdout + out.stderr).lower()
            
            # Handle error cases based on the output of the ping command using temp full_out
            if "could not find host" in full_out:
                response["status"] = "error"
                response["error"] = "Unknown host"
            
            elif "request timed out" in full_out:
                response["status"] = "timeout"
                response["error"] = "Request timed out"
            
            elif "unreachable" in full_out:
                response["status"] = "error"
                response["error"] = "Host unreachable"
            
            else:
                response["status"] = "error"
                response["error"] = f"Ping failed (code {out.returncode})"
            
            return response
    
    # Catch exceptions that may get thrown
    except Exception as e:
        response.update({
            "status": "error",
            "error": str(e),
            "latency_ms": None
        })
    
        return response
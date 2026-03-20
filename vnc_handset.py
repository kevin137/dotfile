import os
import time
import subprocess
import tempfile

VNC_PASSWORD='XXXXXXXX'
VNC_PORT=5951
RNDIS_CONN_NAME='XXXXXXXX'
RNDIS_METRIC=700

def find_rndis_device():
    """Find and return the device name for an RNDIS device using nmcli."""
    try:
        # Run nmcli to get the device information
        result = subprocess.check_output(
            ["nmcli", "-f", 
            "GENERAL.product,GENERAL.device,GENERAL.connection,IP4.address,IP4.gateway", 
            "device", "show"], text=True).strip()

        lines = result.splitlines()
        device,name,ipv4,ipv4_gateway = None,None,None,None
        rndis_found = False

        for line in lines:
            fields = line.split(":", 1)  # Split on the first colon

            if len(fields) < 2:
                continue  

            f = fields[0].strip()
            v = fields[1].strip()

            if f == "GENERAL.PRODUCT" and "rndis" in v.lower():
                rndis_found = True
            elif rndis_found and "GENERAL.DEVICE" in f:
                device = v
            elif rndis_found and "GENERAL.CONNECTION" in f:
                name = v
            elif rndis_found and "IP4.ADDRESS" in f:
                ipv4 = v
            elif rndis_found and "IP4.GATEWAY" in f:
                ipv4_gateway = v
            else:
                rndis_found = False

        if device:
            print(f"Found RNDIS device: {device}")
            return device, name, ipv4, ipv4_gateway
        else:
            print("No RNDIS device found.")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error running nmcli: {e}")
        return None

def change_connection_id(old_name, new_name):
    """Ble."""
    try:
        result = subprocess.check_output(["nmcli", "connection", "delete",  
        new_name], text=True).strip()
    
    except subprocess.CalledProcessError as e:
        print(f"Error running nmcli: {e}")

    try:
        result = subprocess.check_output(["nmcli", "connection", "modify",  
        old_name, "connection.id", new_name], text=True).strip()

        result = subprocess.check_output(["nmcli", "connection", "down",  
        new_name], text=True).strip()

        result = subprocess.check_output(["nmcli", "connection", "up",  
        new_name], text=True).strip()

    except subprocess.CalledProcessError as e:
        print(f"Error running nmcli: {e}")
        return None

def change_route_metric(connection_id, metric):
    """Change metric to avoid leaks"""

    try:
        result = subprocess.check_output(["nmcli", "connection", "modify",  
        connection_id, "ipv4.route-metric", str(metric)], text=True).strip()

        result = subprocess.check_output(["nmcli", "connection", "down",  
        connection_id], text=True).strip()

        result = subprocess.check_output(["nmcli", "connection", "up",  
        connection_id], text=True).strip()

    except subprocess.CalledProcessError as e:
        print(f"Error running nmcli: {e}")
        return None

def launch_vncviewer(ip_address, vnc_port, vnc_password):
    """Launch vncviewer with an environment variable VNC_PASSWORD."""
    try:
        # Set the VNC_PASSWORD environment variable
        os.environ["VNC_PASSWORD"] = vnc_password
        
        connection_string = str(ip_address) + ':' + str(vnc_port)
        # Launch vncviewer with the provided IP address
        with open("/dev/null", "w") as devnull:
            subprocess.Popen(
                ["vncviewer", connection_string],
                stdout=devnull,
                stderr=devnull
            )
        print(f"vncviewer launched at : {connection_string}")
    except Exception as e:
        print(f"Error while launching vncviewer: {e}")

def main():
    device, name, ipv4, ipv4_gateway = find_rndis_device()
    if device and name != RNDIS_CONN_NAME:
        change_connection_id(name, RNDIS_CONN_NAME)
        device, name, ipv4, ipv4_gateway = find_rndis_device()
    if device:
        change_route_metric(name, RNDIS_METRIC)
        launch_vncviewer(ipv4_gateway, VNC_PORT, VNC_PASSWORD)

if __name__ == "__main__":
    main()

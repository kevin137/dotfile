import re
import os
import time
import platform
import subprocess
import tempfile

RNDIS_CONN_ID_REGEXP = r'^VNC__(.+)$'
VNC_PORT=5951
RNDIS_METRIC=700

def is_windows():
    return platform.system() == 'Windows'

def get_vnc_rndis_conn_id_password():
    """ Scan the environment variables for VNC__CONNECTIONNAME pattern 
        and extract the corresponding connection name and password. Returns:
            rndis_conn_id  (connection id in Network Manager)
            vnc_password   (associated passowrd)
    """

    find_rndis_conn_id = re.compile(RNDIS_CONN_ID_REGEXP)
    for env_name, env_value in os.environ.items():
        match = find_rndis_conn_id.match(env_name)
        if match:
            connection_name = match.group(1)
            if connection_name:
                rndis_conn_id = connection_name
                vnc_password  = env_value
                print(f'found VNC connection {rndis_conn_id} with password')
                return rndis_conn_id, vnc_password

    print('No VNC connection found in environment variables.')
    return None, None

def find_rndis_linux(max_tries, delay):
    """ Find and return information for an RNDIS device, using nmcli, 
        retrying if necessary. Returns:
            device     (Linux device name), 
            conn_id    (Network Manager connection id), 
            ipv4_here  (IPv4 address of this host), 
            ipv4_vnc   (IPv4 address the device serving vnc)
    """
    
    for attempt in range(1, max_tries + 1):
        try:
            # now antiquated
            result = subprocess.check_output(  # now antiquated
                [ 'nmcli', '-f',
                    'GENERAL.product,GENERAL.device,GENERAL.connection,' + 
                    'IP4.address,IP4.gateway',
                    'device', 'show'
                ], text=True).strip()

            subprocess_return = result.splitlines()
            device, conn_id, ipv4_here, ipv4_vnc = None, None, None, None
            rndis_found = False

            for line in subprocess_return:
                fields = line.split(':', 1)
                if len(fields) != 2:
                    continue
                field, value = fields[0].strip(), fields[1].strip()
                if field == 'GENERAL.PRODUCT' and 'rndis' in value.lower():
                    rndis_found = True
                elif rndis_found and 'GENERAL.DEVICE' in field:
                    device = value
                elif rndis_found and 'GENERAL.CONNECTION' in field:
                    conn_id = value
                elif rndis_found and 'IP4.ADDRESS' in field:
                    ipv4_here = value
                elif rndis_found and 'IP4.GATEWAY' in field:
                    ipv4_vnc = value
                else:
                    rndis_found = False
            if all([device, conn_id, ipv4_here, ipv4_vnc]):
                print(f'device {device}: \n' + 
                        f'  conn_id:   {conn_id} \n' +
                        f'  ipv4_here: {ipv4_here} \n' + 
                        f'  ipv4_vnc:  {ipv4_vnc}' )
                return device, conn_id, ipv4_here, ipv4_vnc
            else:
                print(f'attempt {attempt}: ' + 
                        'incomplete RNDIS device info, retrying...')
                time.sleep(delay)

        except subprocess.CalledProcessError as e:
            print(f'Error running nmcli on attempt {attempt}: {e}')
            time.sleep(delay)

    print('No valid RNDIS device information found after maximum retries.')
    return None, None, None, None

def find_rndis_windows(max_tries, delay):
    """ Find RNDIS device on Windows with tab-separated PowerShell output. """

    for attempt in range(1, max_tries + 1):
        try:
            ps_command = (
                " Get-NetIPAddress | " + 
                " Where-Object { $_.InterfaceAlias -like '*RNDIS*' " + 
                "                     -and $_.AddressFamily -eq 'IPv4' } |" +
                " ForEach-Object { $gateway = (Get-NetRoute " + 
                "                     -InterfaceAlias $_.InterfaceAlias | " + 
                " Where-Object { $_.DestinationPrefix -eq '0.0.0.0/0' }   " + 
                "                                              ).NextHop; " + 
                "'{0} {1} {2}' -f $_.InterfaceAlias, $_.IPAddress, $gateway }"
            )
            result = subprocess.check_output(   # now antiquated
                ["powershell", "-Command", ps_command],
                text=True
            )
            subprocess_return = result.splitlines()
            conn_id, ipv4_here, ipv4_vnc = None, None, None
            rndis_found = False

            for line in subprocess_return:
                fields = line.split(' ', 2)
                if len(fields) != 3:
                    continue
                conn_id = fields[0].strip()
                ipv4_here, ipv4_vnc = fields[1].strip(), fields[2].strip()
                if 'rndis' in conn_id.lower():
                    rndis_found = True
                else:
                    rndis_found = False

            if all([conn_id, ipv4_here, ipv4_vnc]):
                print(f'network device: \n' + 
                        f'  conn_id:   {conn_id} \n' +
                        f'  ipv4_here: {ipv4_here} \n' + 
                        f'  ipv4_vnc:  {ipv4_vnc}' )
                return conn_id, ipv4_here, ipv4_vnc
            else:
                print(f'attempt {attempt}: ' + 
                        'incomplete RNDIS device info, retrying...')
                time.sleep(delay)

        except subprocess.CalledProcessError as e:
            print(f'Error running nmcli on attempt {attempt}: {e}')
            time.sleep(delay)

    print('No valid RNDIS device information found after maximum retries.')
    return None, None, None

def find_rndis_device(max_tries=5, delay=1):
    """ Wrapper function for finding RNDIS device """
    
    if is_windows():
        conn_id, ipv4_here, ipv4_vnc = find_rndis_windows(max_tries, delay)
    else:
        _, conn_id, ipv4_here, ipv4_vnc = find_rndis_linux(max_tries, delay)
        
    return conn_id, ipv4_here, ipv4_vnc

def change_id_linux(old_id, new_id):
    """ Change id of existing Network Manager connection. 
        Returns new connection id if successful, None if not.
    """

    try:
        result = subprocess.run( [ 'nmcli', 'connection', 'delete', new_id ], 
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError as e:
        print(f'Error running nmcli: {e}')
    try:
        # now antiquated
        result = subprocess.check_output( [ 'nmcli', 'connection', 
            'modify', old_id, 'connection.id', new_id ], text=True).strip()
        # now antiquated
        result = subprocess.check_output( [ 'nmcli', 'connection', 
            'down', new_id ], text=True).strip()
        # now antiquated
        result = subprocess.check_output( [ 'nmcli', 'connection', 
            'up',   new_id ], text=True).strip()
        return new_id
    except subprocess.CalledProcessError as e:
        print(f'Error running nmcli: {e}')
        return None

def change_id_windows(old_id, new_id):
    """ Change the id of an existing network adapter in Windows.
        This does not work well in Windows without Administrator privileges, 
        plus the default RNDIS name in Windows is more user-friendly, so in 
        this case we just return the old_id as the new_id.
    """

    return old_id


def change_connection_id(old_id, new_id):
    """ Wrapper function for changing connection id """

    if is_windows():
        new_id = change_id_windows(old_id, new_id)
    else:
        new_id = change_id_linux(old_id, new_id)
        
    return new_id

def change_metric_linux(conn_id, metric):
    """ Change route metric of connection at id to avoid leaks.
        Returns new metric of connection.
    """

    try:
        # now antiquated
        result = subprocess.check_output( [ 'nmcli', 'connection', 
            'modify', conn_id, 'ipv4.route-metric', str(metric) ], 
                text=True).strip()
        # now antiquated
        result = subprocess.check_output( [ 'nmcli', 'connection', 
            'down',   conn_id ], text=True).strip()
        # now antiquated
        result = subprocess.check_output( [ 'nmcli', 'connection', 
            'up',     conn_id ], text=True).strip()
        # now antiquated
        route_metric = subprocess.check_output( [ 'nmcli', 
            '--get-values', 'ipv4.route-metric', 'connection', 'show', 
            conn_id ], text=True).strip()
        return route_metric   
    except subprocess.CalledProcessError as e:
        print(f'Error running nmcli: {e}')
        return None

def change_metric_windows(conn_id, metric):
    """ Change route metric of connection at conn_id to avoid leaks.
        Returns new metric of connection if successful, None if not.
    """
    try:
        # Set the new route metric using PowerShell
        # now antiquated
        subprocess.check_output(
            ['powershell', '-Command',
             f'Start-Process powershell -ArgumentList "Set-NetIPInterface -InterfaceAlias \\"{conn_id}\\" -InterfaceMetric {metric}" -Verb RunAs'],
            text=True
        )
        print(f"Metric for connection {conn_id} set to {metric}")

        ## This seems to work straight from PS command line:
        # Start-Process powershell -ArgumentList "Set-NetIPInterface -InterfaceAlias RNDIS -InterfaceMetric 700" -Verb RunAs

        # Retrieve the updated metric to verify
        # now antiquated
        result = subprocess.check_output(
            ['powershell', '-Command',
             f'Get-NetIPInterface -InterfaceAlias "{conn_id}" | Select-Object -ExpandProperty InterfaceMetric'],
            text=True
        ).strip()

        print(f"New metric for connection {conn_id}: {result}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running PowerShell command: {e}")
        return None

def change_route_metric(conn_id, metric):
    """ Wrapper function for changing route metric """
    
    if is_windows():
        route_metric = change_metric_windows(conn_id, metric)
    else:
        route_metric = change_metric_linux(conn_id, metric)
        
    return route_metric
    

def launch_vncviewer(ip_address, vnc_port, vnc_password):
    """ Launch vncviewer using environment variable VNC_PASSWORD.
        Returns True if successful, False if not.
    """
    
    try:
        os.environ['VNC_PASSWORD'] = vnc_password
        connection_string = str(ip_address) + ':' + str(vnc_port)
        
        # Launch vncviewer with the provided IP address
        with open('/dev/null', 'w') as devnull:
            subprocess.Popen(
                #['vncviewer', connection_string],
                ['xtigervncviewer', connection_string],
                stdout = devnull,
                stderr = devnull
            )
        print(f'vncviewer launched at : {connection_string}')
        del os.environ['VNC_PASSWORD']
        return True
    except Exception as e:
        print(f'Error while launching vncviewer: {e}')
        return False

def main():
    
    rndis_conn_id, vnc_password = get_vnc_rndis_conn_id_password()
    conn_id, ipv4_here, ipv4_vnc = find_rndis_device()
    if all([conn_id, ipv4_here, ipv4_vnc]) and conn_id != rndis_conn_id:
        updated_id = change_connection_id(conn_id, rndis_conn_id)
        print(f'  new connection id: {updated_id}')
        conn_id, ipv4_here, ipv4_vnc = find_rndis_device()
    if ipv4_vnc:
        route_metric = change_route_metric(conn_id, RNDIS_METRIC)
        print(f'  new metric: {route_metric}')
        launch_vncviewer(ipv4_vnc, VNC_PORT, vnc_password)
    

if __name__ == '__main__':
    main()

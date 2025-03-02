import re
import os
import time
import subprocess
import tempfile

RNDIS_CONN_ID_REGEXP = r'^VNC__(.+)$'
VNC_PORT=5951
RNDIS_METRIC=700

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

def find_rndis_device(max_tries=5, delay=1):
    """ Find and return information for an RNDIS device, using nmcli, 
        retrying if necessary. Returns:
            device     (Linux device name), 
            id         (Network Manager connection id), 
            ipv4_here  (IPv4 address of this host), 
            ipv4_vnc   (IPv4 address the device serving vnc)
    """
    
    for attempt in range(1, max_tries + 1):
        try:
            result = subprocess.check_output(
                [ 'nmcli', '-f',
                    'GENERAL.product,GENERAL.device,GENERAL.connection,' + 
                    'IP4.address,IP4.gateway',
                    'device', 'show'
                ], text=True).strip()

            subprocess_return = result.splitlines()
            device, id, ipv4_here, ipv4_vnc = None, None, None, None
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
                    id = value
                elif rndis_found and 'IP4.ADDRESS' in field:
                    ipv4_here = value
                elif rndis_found and 'IP4.GATEWAY' in field:
                    ipv4_vnc = value
                else:
                    rndis_found = False

            if all([device, id, ipv4_here, ipv4_vnc]):
                print(f'device {device}: \n' + 
                        f'  id:        {id} \n' +
                        f'  ipv4_here: {ipv4_here} \n' + 
                        f'  ipv4_vnc:  {ipv4_vnc}' )
                return device, id, ipv4_here, ipv4_vnc
            else:
                print(f'attempt {attempt}: ' + 
                        'incomplete RNDIS device info, retrying...')
                time.sleep(delay)

        except subprocess.CalledProcessError as e:
            print(f'Error running nmcli on attempt {attempt}: {e}')
            time.sleep(delay)

    print('No valid RNDIS device information found after maximum retries.')
    return None, None, None, None

def change_connection_id(old_id, new_id):
    """ Change id of existing Network Manager connection. 
        Returns new connection id if successful, None if not.
    """

    try:
        result = subprocess.check_output( [ 'nmcli', 'connection', 
            'delete', new_id ], text=True).strip()
    except subprocess.CalledProcessError as e:
        print(f'Error running nmcli: {e}')
    try:
        result = subprocess.check_output( [ 'nmcli', 'connection', 
            'modify', old_id, 'connection.id', new_id ], text=True).strip()
        result = subprocess.check_output( [ 'nmcli', 'connection', 
            'down', new_id ], text=True).strip()
        result = subprocess.check_output( [ 'nmcli', 'connection', 
            'up',   new_id ], text=True).strip()
        return new_id
    except subprocess.CalledProcessError as e:
        print(f'Error running nmcli: {e}')
        return None

def change_route_metric(conn_id, metric):
    """ Change route metric of connection at id to avoid leaks.
        Returns new metric of connection.
    """

    try:
        result = subprocess.check_output( [ 'nmcli', 'connection', 
            'modify', conn_id, 'ipv4.route-metric', str(metric) ], 
                text=True).strip()
        result = subprocess.check_output( [ 'nmcli', 'connection', 
            'down',   conn_id ], text=True).strip()
        result = subprocess.check_output( [ 'nmcli', 'connection', 
            'up',     conn_id ], text=True).strip()
        route_metric = subprocess.check_output( [ 'nmcli', 
            '--get-values', 'ipv4.route-metric', 'connection', 'show', 
            conn_id ], text=True).strip()
        return route_metric   
    except subprocess.CalledProcessError as e:
        print(f'Error running nmcli: {e}')
        return None

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
                ['vncviewer', connection_string],
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
    device, id, ipv4_here, ipv4_vnc = find_rndis_device()
    if device and id and id != rndis_conn_id:
        updated_id = change_connection_id(id, rndis_conn_id)
        print(f'  new connection id: {updated_id}')
        device, id, ipv4_here, ipv4_vnc = find_rndis_device()
    if device:
        route_metric = change_route_metric(id, RNDIS_METRIC)
        print(f'  new metric: {route_metric}')
        launch_vncviewer(ipv4_vnc, VNC_PORT, vnc_password)

if __name__ == '__main__':
    main()

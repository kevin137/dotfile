import time
import argparse
import tempfile
import subprocess

def open_remmina_session(remote_host):
  default = """
    [remmina]
    protocol=RDP
    username=
    viewmode=4
    window_maximize=1
    quality=0
    colordepth=24
    resolution_height=
    resolution_width=
    disableclipboard=0
    sound=off
    microphone=0
    console=0
    sharefolder=
    shareprinter=0
    clientname=
    exec=
    execpath=
    precommand=
    postcommand=
    loadbalanceinfo=
    disableautoreconnect=0
    disablepasswordstoring=0
    group=
    password=
    security=
    domain=
    sharesmartcard=0
    cert_ignore=0
    ssh_enabled=0
    ssh_auth=0
    ssh_server=
    ssh_username=
    ssh_privatekey=
    ssh_charset=
    ssh_loopback=0
    gateway_usage=0
    gateway_server=
    gateway_username=
    gateway_password=
    gateway_domain=
    last_success=20200101
  """ 
  c = tempfile.NamedTemporaryFile(suffix=".remmina")
  c.write(str.encode(default))
  c.write(str.encode('server='+remote_host+'\n'))
  c.write(str.encode('name='+remote_host+'\n'))
  c.seek(0)
  pid = subprocess.Popen(["remmina", "-c", c.name]).pid
  time.sleep(1)
  c.close()

def customize_cmdline_parser(p):
  p.add_argument('remote_host', nargs='?')

cmdline_parser = argparse.ArgumentParser()
customize_cmdline_parser(cmdline_parser)
cmdline_args=cmdline_parser.parse_args()

if cmdline_args.remote_host:
  print('a remote host was specified: ' + cmdline_args.remote_host)
  open_remmina_session(cmdline_args.remote_host)


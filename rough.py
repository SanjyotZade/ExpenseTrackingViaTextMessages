import os
import socket
from time import sleep
from config import MAX_NET_WAIT
from config import REMOTE_SERVER
from emailDataProcurement import EmailDataProcurement
from subprocess import call

def is_connected(hostname):
    try:
        # see if we can resolve the host name -- tells us if there is
        # a DNS listening
        host = socket.gethostbyname(hostname)
        # connect to the host -- tells us if the host is actually
        # reachable
        s = socket.create_connection((host, 80), 2)
        s.close()
        return True
    except:
        return False


def restart_network():
    print("\nRestarting internet..")

    call(["nmcli", "networking", "off"])
    #os.system("nmcli  off")
    sleep(5)
    call(["nmcli", "networking", "on"])
    #os.system("nmcli networking on")
    sleep(2)
    print("Done\n")


if __name__ == "__main__":
    restart_network()


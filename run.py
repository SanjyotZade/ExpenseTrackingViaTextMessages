import os
import socket
from time import sleep
from subprocess import call
from config import MAX_NET_WAIT
from config import REMOTE_SERVER
from emailDataProcurement import EmailDataProcurement


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
    print("Restarting internet..")
    call(["nmcli", "networking", "off"])
    #os.system("nmcli  off")
    sleep(10)
    call(["nmcli", "networking", "on"])
    #os.system("nmcli networking on")
    sleep(10)
    print("Done\n")


if __name__ == "__main__":
    while not is_connected(REMOTE_SERVER):
        print("Waiting for internet...")
        sleep(40)
        restart_network()

    process_obj = EmailDataProcurement()
    process_obj.start_the_push_service()
    print(process_obj.start_pubsub_communication())

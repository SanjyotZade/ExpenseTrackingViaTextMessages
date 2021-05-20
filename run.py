import os
import socket
from time import sleep
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
    print("\nRestarting internet..")
    os.system("nmcli networking off")
    sleep(5)
    os.system("nmcli networking on")
    sleep(2)
    print("Done\n")


if __name__ == "__main__":
    attempts = 0
    while not is_connected(REMOTE_SERVER):
        print("Waiting for internet...")
        sleep(60)
        attempts += 1
        if attempts == MAX_NET_WAIT:
            restart_network()
            attempts=0

    process_obj = EmailDataProcurement()
    process_obj.start_the_push_service()
    print(process_obj.start_pubsub_communication())

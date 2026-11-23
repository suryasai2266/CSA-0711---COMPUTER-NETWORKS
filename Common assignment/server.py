"""
server.py - TCP and UDP Client-Server Communication System (Server side)

Runs a multi-client TCP server and a UDP server on the same port number.
(TCP and UDP use separate port spaces, so both can listen on one number -
this is transport-layer multiplexing / demultiplexing.)

Message format received : <client_id>|<seq>|<text>
Acknowledgment sent back: ACK|<client_id>|<seq>|<text>

Usage:  python server.py [--host 0.0.0.0] [--port 5000] [--udp-loss 0.0]
"""
import argparse
import random
import socket
import threading
from datetime import datetime


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {msg}", flush=True)


# ---------------------------- TCP SERVER ----------------------------
def handle_tcp_client(conn, addr):
    log(f"TCP  CONNECTED     : {addr[0]}:{addr[1]}  (3-way handshake complete)")
    with conn, conn.makefile("rb") as stream:
        for line in stream:                       # newline-framed byte stream
            msg = line.decode().strip()
            if not msg:
                continue
            log(f"TCP  RECEIVED      : {msg}")
            conn.sendall(f"ACK|{msg}\n".encode())  # reliable ACK to the client
            log(f"TCP  ACK SENT      : ACK|{msg}")
    log(f"TCP  DISCONNECTED  : {addr[0]}:{addr[1]}  (connection closed)")


def tcp_server(host, port):
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, port))
    srv.listen(20)
    log(f"TCP server listening on {host}:{port}")
    while True:
        conn, addr = srv.accept()                 # one thread per client
        threading.Thread(target=handle_tcp_client, args=(conn, addr),
                         daemon=True).start()


# ---------------------------- UDP SERVER ----------------------------
def udp_server(host, port, loss):
    srv = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    srv.bind((host, port))
    log(f"UDP server listening on {host}:{port}  (simulated loss = {loss:.0%})")
    while True:
        data, addr = srv.recvfrom(4096)           # no connection, no handshake
        msg = data.decode().strip()
        if random.random() < loss:                # optional packet-loss simulation
            log(f"UDP  DROPPED       : {msg}  (simulated loss)")
            continue
        log(f"UDP  RECEIVED      : {msg}  from {addr[0]}:{addr[1]}")
        srv.sendto(f"ACK|{msg}".encode(), addr)
        log(f"UDP  ACK SENT      : ACK|{msg}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="0.0.0.0")
    p.add_argument("--port", type=int, default=5000)
    p.add_argument("--udp-loss", type=float, default=0.0,
                   help="probability (0-1) of dropping a UDP datagram")
    a = p.parse_args()
    threading.Thread(target=tcp_server, args=(a.host, a.port), daemon=True).start()
    threading.Thread(target=udp_server, args=(a.host, a.port, a.udp_loss),
                     daemon=True).start()
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        log("Server stopped.")

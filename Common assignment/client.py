"""
client.py - TCP and UDP Client-Server Communication System (Client side)

Usage:
  python client.py --id C1 --host 127.0.0.1 --port 5000 --proto TCP --msg "Hello" --count 3
"""
import argparse
import socket
import time


def send_tcp(client_id, host, port, messages):
    """Connection-oriented transfer: connect -> send -> wait for ACK -> close."""
    results = []
    t0 = time.perf_counter()
    try:
        s = socket.create_connection((host, port), timeout=3)
    except OSError as e:
        return [dict(seq=0, status=f"Connection failed ({e})", ack="No ACK",
                     rtt_ms=None, reply="")]
    connect_ms = (time.perf_counter() - t0) * 1000
    with s, s.makefile("rb") as stream:
        for seq, text in enumerate(messages, 1):
            payload = f"{client_id}|{seq}|{text}"
            t1 = time.perf_counter()
            s.sendall((payload + "\n").encode())
            reply = stream.readline().decode().strip()
            rtt = (time.perf_counter() - t1) * 1000
            ok = reply.startswith("ACK|")
            results.append(dict(seq=seq, status="Connected", reply=reply,
                                ack="ACK Received" if ok else "No ACK",
                                rtt_ms=rtt, connect_ms=connect_ms))
    return results


def send_udp(client_id, host, port, messages, timeout=1.0):
    """Connectionless transfer: sendto -> wait (with timeout) for ACK."""
    results = []
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(timeout)
    with s:
        for seq, text in enumerate(messages, 1):
            payload = f"{client_id}|{seq}|{text}"
            t1 = time.perf_counter()
            s.sendto(payload.encode(), (host, port))
            try:
                data, _ = s.recvfrom(4096)
                rtt = (time.perf_counter() - t1) * 1000
                results.append(dict(seq=seq, status="Connectionless",
                                    reply=data.decode(), ack="ACK Received",
                                    rtt_ms=rtt, connect_ms=0.0))
            except socket.timeout:
                results.append(dict(seq=seq, status="Connectionless", reply="",
                                    ack="Lost / Timeout", rtt_ms=None,
                                    connect_ms=0.0))
    return results


def send(client_id, host, port, proto, messages):
    fn = send_tcp if proto.upper() == "TCP" else send_udp
    return fn(client_id, host, port, messages)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--id", default="C1")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=5000)
    p.add_argument("--proto", choices=["TCP", "UDP"], default="TCP")
    p.add_argument("--msg", default="Hello Server")
    p.add_argument("--count", type=int, default=1)
    a = p.parse_args()

    print(f"Client ID : {a.id}\nServer    : {a.host}:{a.port}\nProtocol  : {a.proto}\n")
    for r in send(a.id, a.host, a.port, a.proto, [a.msg] * a.count):
        t = f"{r['rtt_ms']:.3f} ms" if r["rtt_ms"] is not None else "N/A"
        print(f"Msg #{r['seq']} | Status: {r['status']:<15} | "
              f"Received: {r['reply'] or '-':<28} | Time: {t:<10} | {r['ack']}")

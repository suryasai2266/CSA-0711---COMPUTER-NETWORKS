"""
compare.py - TCP vs UDP Comparison Report generator
Starts N concurrent clients per protocol, sends M messages each and prints
average / min / max round-trip time, throughput and packet loss.

Usage: python compare.py --host 127.0.0.1 --port 5000 --clients 5 --messages 200
"""
import argparse
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from client import send


def run(proto, host, port, clients, messages):
    msgs = ["Hello from client"] * messages
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=clients) as ex:
        futs = [ex.submit(send, f"C{i+1}", host, port, proto, msgs)
                for i in range(clients)]
        res = [r for f in futs for r in f.result()]
    total = time.perf_counter() - t0
    rtts = [r["rtt_ms"] for r in res if r["rtt_ms"] is not None]
    sent = len(res)
    lost = sent - len(rtts)
    return dict(proto=proto, sent=sent, acked=len(rtts), lost=lost,
                loss=100 * lost / sent if sent else 0,
                avg=statistics.mean(rtts) if rtts else 0,
                mn=min(rtts) if rtts else 0, mx=max(rtts) if rtts else 0,
                thr=len(rtts) / total if total else 0, total=total)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=5000)
    p.add_argument("--clients", type=int, default=5)
    p.add_argument("--messages", type=int, default=200)
    a = p.parse_args()

    rows = [run(pr, a.host, a.port, a.clients, a.messages) for pr in ("TCP", "UDP")]
    print("\n================ TCP vs UDP COMPARISON REPORT ================")
    print(f"Clients: {a.clients}   Messages/client: {a.messages}\n")
    print(f"{'Parameter':<26}{'TCP':>16}{'UDP':>16}")
    print("-" * 58)
    for label, key, fmt in [("Packets sent", "sent", "{:d}"),
                            ("ACKs received", "acked", "{:d}"),
                            ("Packets lost", "lost", "{:d}"),
                            ("Packet loss (%)", "loss", "{:.2f}"),
                            ("Avg round-trip (ms)", "avg", "{:.4f}"),
                            ("Min round-trip (ms)", "mn", "{:.4f}"),
                            ("Max round-trip (ms)", "mx", "{:.4f}"),
                            ("Throughput (msg/s)", "thr", "{:.1f}"),
                            ("Total time (s)", "total", "{:.3f}")]:
        print(f"{label:<26}{fmt.format(rows[0][key]):>16}{fmt.format(rows[1][key]):>16}")

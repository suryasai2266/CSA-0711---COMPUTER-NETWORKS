"""
client_gui.py - Tkinter GUI client showing all required fields:
Client ID, Server IP, Port, Protocol (TCP/UDP), Message Input, Message Received,
Connection Status, Packet Transmission Time, Acknowledgment Status.
Run:  python client_gui.py
"""
import threading
import tkinter as tk
from tkinter import ttk
from client import send


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("TCP / UDP Client")
        self.geometry("520x470")
        self.v = {k: tk.StringVar(value=d) for k, d in
                  dict(id="C1", ip="127.0.0.1", port="5000", proto="TCP",
                       msg="Hello Server", recv="", status="Idle",
                       time="", ack="").items()}
        rows = [("Client ID", "id"), ("Server IP Address", "ip"),
                ("Port Number", "port")]
        for i, (lbl, k) in enumerate(rows):
            ttk.Label(self, text=lbl).grid(row=i, column=0, sticky="w", padx=10, pady=6)
            ttk.Entry(self, textvariable=self.v[k], width=34).grid(row=i, column=1, padx=10)
        ttk.Label(self, text="Protocol Selection").grid(row=3, column=0, sticky="w", padx=10, pady=6)
        ttk.Combobox(self, textvariable=self.v["proto"], values=["TCP", "UDP"],
                     state="readonly", width=31).grid(row=3, column=1, padx=10)
        ttk.Label(self, text="Message Input").grid(row=4, column=0, sticky="w", padx=10, pady=6)
        ttk.Entry(self, textvariable=self.v["msg"], width=34).grid(row=4, column=1, padx=10)
        ttk.Button(self, text="Send", command=self.on_send).grid(row=5, column=1, sticky="w", padx=10, pady=10)
        for i, (lbl, k) in enumerate([("Message Received", "recv"),
                                      ("Connection Status", "status"),
                                      ("Packet Transmission Time", "time"),
                                      ("Acknowledgment Status", "ack")], start=6):
            ttk.Label(self, text=lbl).grid(row=i, column=0, sticky="w", padx=10, pady=6)
            ttk.Label(self, textvariable=self.v[k], foreground="blue").grid(row=i, column=1, sticky="w", padx=10)

    def on_send(self):
        threading.Thread(target=self.worker, daemon=True).start()

    def worker(self):
        r = send(self.v["id"].get(), self.v["ip"].get(), int(self.v["port"].get()),
                 self.v["proto"].get(), [self.v["msg"].get()])[0]
        self.v["recv"].set(r["reply"] or "-")
        self.v["status"].set(r["status"])
        self.v["time"].set(f"{r['rtt_ms']:.3f} ms" if r["rtt_ms"] is not None else "N/A")
        self.v["ack"].set(r["ack"])


if __name__ == "__main__":
    App().mainloop()

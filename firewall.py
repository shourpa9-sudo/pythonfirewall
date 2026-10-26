import ipaddress
import re
import subprocess
import tkinter as tk
from tkinter import messagebox, scrolledtext


def run_command(args):
    """Run a Windows netsh command without invoking a shell."""
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            text=True,
            timeout=20,
            shell=False
        )
        output = (result.stdout or "") + (result.stderr or "")
        return result.returncode == 0, output.strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)


def validate_ip(value):
    try:
        return str(ipaddress.ip_address(value.strip()))
    except ValueError:
        return None


def validate_port(value):
    value = value.strip()
    if not re.fullmatch(r"\d{1,5}", value):
        return None
    port = int(value)
    return port if 1 <= port <= 65535 else None


def add_ip_rule(action):
    ip = validate_ip(ip_entry.get())
    if not ip:
        messagebox.showwarning("Invalid IP", "Enter a valid IPv4 or IPv6 address.")
        return

    rule_name = f"MyFirewall_{action.title()}_{ip.replace(':', '_')}"
    command = [
        "netsh", "advfirewall", "firewall", "add", "rule",
        f"name={rule_name}", "dir=in", f"action={action}",
        f"remoteip={ip}"
    ]
    success, output = run_command(command)
    if success:
        messagebox.showinfo("Firewall", f"Rule created: {action.upper()} traffic from {ip}.")
    else:
        messagebox.showerror("Could not create rule", output or
                             "Run this program as Administrator.")


def block_port():
    port = validate_port(port_entry.get())
    if port is None:
        messagebox.showwarning("Invalid port", "Enter a port number from 1 to 65535.")
        return

    command = [
        "netsh", "advfirewall", "firewall", "add", "rule",
        f"name=MyFirewall_Block_TCP_Port_{port}",
        "dir=in", "action=block", "protocol=TCP", f"localport={port}"
    ]
    success, output = run_command(command)
    if success:
        messagebox.showinfo("Firewall", f"Incoming TCP traffic to port {port} is blocked.")
    else:
        messagebox.showerror("Could not create rule", output or
                             "Run this program as Administrator.")


def show_rules():
    success, output = run_command([
        "netsh", "advfirewall", "firewall", "show", "rule", "name=all"
    ])
    if not success:
        messagebox.showerror("Could not show rules", output or "Unable to read firewall rules.")
        return

    window = tk.Toplevel(root)
    window.title("Windows Firewall Rules")
    window.geometry("760x520")
    text = scrolledtext.ScrolledText(window, wrap=tk.WORD)
    text.pack(fill="both", expand=True, padx=10, pady=10)
    text.insert("1.0", output)
    text.configure(state="disabled")


root = tk.Tk()
root.title("Python Firewall Manager")
root.geometry("500x390")
root.resizable(False, False)

tk.Label(root, text="PYTHON FIREWALL MANAGER",
         font=("Arial", 17, "bold")).pack(pady=(18, 8))
tk.Label(root, text="Manages Windows Defender Firewall rules",
         font=("Arial", 9)).pack(pady=(0, 14))

tk.Label(root, text="IP address (IPv4 or IPv6)").pack()
ip_entry = tk.Entry(root, width=38)
ip_entry.pack(pady=4)

button_frame = tk.Frame(root)
button_frame.pack(pady=6)
tk.Button(button_frame, text="Block Incoming IP", width=18,
          command=lambda: add_ip_rule("block")).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="Allow Incoming IP", width=18,
          command=lambda: add_ip_rule("allow")).grid(row=0, column=1, padx=5)

tk.Label(root, text="TCP port to block (1–65535)").pack(pady=(12, 0))
port_entry = tk.Entry(root, width=18)
port_entry.pack(pady=4)
tk.Button(root, text="Block Incoming TCP Port", width=25,
          command=block_port).pack(pady=5)
tk.Button(root, text="Show Windows Firewall Rules", width=25,
          command=show_rules).pack(pady=5)

tk.Label(root, text="Requires Windows and Administrator privileges to change rules.",
         font=("Arial", 8), fg="gray").pack(pady=(12, 0))

root.mainloop()

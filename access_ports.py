import json
import os

# 📁 Global constant for the file path
USER_HOME = os.path.expanduser("~")
BROWSER_PORTS_FILE = os.path.join(USER_HOME, ".browser_ports.json")

# Global variables
ports = []
current_port_index = 0


class NoPortsAvailableError(Exception):
    """Raised when no ports are available."""
    pass


def clear_browser_ports():
    """🧹 Remove the browser ports file if it exists."""
    if os.path.exists(BROWSER_PORTS_FILE):
        os.remove(BROWSER_PORTS_FILE)


def save_browser_ports(new_ports):
    """💾 Save the given ports to the browser ports file."""
    global ports
    ports = new_ports
    with open(BROWSER_PORTS_FILE, 'w') as f:
        json.dump({'ports': ports}, f)


def load_browser_ports():
    """📂 Load and return the ports from the browser ports file."""
    global ports
    if os.path.exists(BROWSER_PORTS_FILE):
        with open(BROWSER_PORTS_FILE, 'r') as f:
            ports = json.load(f).get('ports', [])
    if not ports:
        raise NoPortsAvailableError("No ports available. Make sure .browser_ports.json is properly configured.")
    return ports


last_used_port_index = -1

def get_server_url():
    global last_used_port_index
    """🔗 Get the next server URL."""

    # FASTER! avoids overlaps on one browser
    port = get_next_available_port(last_used_port_index)

    return f"http://localhost:{port}"


def get_next_available_port(current_port):
    """Get the next available port, skipping the current one."""
    ports = load_browser_ports()
    if current_port in ports:
        index = (ports.index(current_port) + 1) % len(ports)
    else:
        index = 0
    return ports[index]

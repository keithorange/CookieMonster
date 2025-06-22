# # import subprocess
# # import json
# # import time
# # import argparse
# # import os
# # import psutil
# # from tqdm import tqdm
# # from multiprocessing import Pool
# # from pathlib import Path
# # import threading
# # import random
# # from colorama import init, Fore, Style

# # try:
# #     from settings import (
# #         NUM_PARALLEL,
# #         BASE_PORT,
# #         SLEEP_TIME,
# #         FIRST_BROWSER_AGE,
# #         KILL_SPACING_S,
# #         MAX_PARALLEL_PROCESS,
# #         BROWSER_PORTS_FILE,
# #     )
# # except:
# #     from .settings import (
# #         NUM_PARALLEL,
# #         BASE_PORT,
# #         SLEEP_TIME,
# #         FIRST_BROWSER_AGE,
# #         KILL_SPACING_S,
# #         MAX_PARALLEL_PROCESS,
# #         BROWSER_PORTS_FILE,
# #     )

# # # Initialize colorama for cross-platform color support
# # init(autoreset=True)

# # COOKIE_EMOJI = "🍪"
# # MONSTER_EMOJIS = ["😋", "🤤", "😍", "🤯", "🥳"]


# # def print_log(message: str, color=Fore.CYAN):
# #     print(f"\n{color}{COOKIE_EMOJI} {message} {random.choice(MONSTER_EMOJIS)}{Style.RESET_ALL}")

# # def print_warning(message: str):
# #     print(f"\n{Fore.YELLOW}[WARNING] {message} ⚠️{Style.RESET_ALL}")

# # def print_error(message: str):
# #     print(f"\n{Fore.RED}[ERROR] {message} ❌{Style.RESET_ALL}")

# # def print_info(message: str):
# #     print(f"\n{Fore.GREEN}[INFO] {message} ✔️{Style.RESET_ALL}")


# # def load_browser_ports(file_path=None):
# #     if file_path is None:
# #         file_path = Path(os.path.expanduser(BROWSER_PORTS_FILE))
# #     if file_path.exists():
# #         try:
# #             with open(file_path, "r") as f:
# #                 ports = json.load(f)
# #                 if isinstance(ports, list):
# #                     return ports
# #         except Exception as e:
# #             print_error(f"Error loading browser ports: {e}")
# #     return []

# # def save_browser_ports(ports, file_path=None):
# #     if file_path is None:
# #         file_path = Path(os.path.expanduser(BROWSER_PORTS_FILE))
# #     try:
# #         with open(file_path, "w") as f:
# #             json.dump(ports, f)
# #     except Exception as e:
# #         print_error(f"Error saving browser ports: {e}")

# # def clear_browser_ports(file_path=None):
# #     if file_path is None:
# #         file_path = Path(os.path.expanduser(BROWSER_PORTS_FILE))
# #     if file_path.exists():
# #         try:
# #             file_path.unlink()
# #             print_info("Cleared browser ports file.")
# #         except Exception as e:
# #             print_error(f"Error clearing browser ports: {e}")

# # def terminate_process(pid):
# #     try:
# #         proc = psutil.Process(pid)
# #         proc.terminate()
# #         proc.wait(timeout=5)
# #         print_info(f"Terminated process {pid}")
# #     except psutil.TimeoutExpired:
# #         proc.kill()
# #         print_warning(f"Forcefully killed process {pid}")
# #     except psutil.NoSuchProcess:
# #         print_warning(f"Process {pid} no longer exists")

# # def kill_existing_processes():
# #     pids_to_kill = []
# #     for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
# #         try:
# #             if 'python' in proc.info['name'].lower() and 'cookie_proxy_fetcher.py' in ' '.join(proc.info['cmdline']):
# #                 pids_to_kill.append(proc.info['pid'])
# #         except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
# #             continue
# #     if pids_to_kill:
# #         print_info(f"Terminating {len(pids_to_kill)} cookie_proxy_fetcher processes")
# #         with Pool() as pool:
# #             pool.map(terminate_process, pids_to_kill)
# #     else:
# #         print_info("No matching cookie_proxy_fetcher processes found to terminate")

# # # def kill_browser_by_port(port):
# # #     for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
# # #         try:
# # #             if 'python' in proc.info['name'].lower() and f'cookie_proxy_fetcher.py --port {port}' in ' '.join(proc.info['cmdline']):
# # #                 terminate_process(proc.info['pid'])
# # #                 return True
# # #         except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
# # #             continue
# # #     print_warning(f"No process found running on port {port}")
# # #     return False

# # def start_single_instance(port, is_initial_launch=True):
# #     try:
# #         cmd = f"cd ~/Code/cookie_monster/cloudflare_bypasser && python3 cookie_proxy_fetcher.py --port {port}"
# #         subprocess.Popen(cmd, shell=True, cwd=os.getcwd())
# #         wait_time = 2 if is_initial_launch else 5
# #         time.sleep(wait_time)
# #         print_info(f"Launched cookie_proxy_fetcher instance on port {port}")
# #         return True
# #     except Exception as e:
# #         print_error(f"Error launching instance on port {port}: {e}")
# #         return False

# # def start_instances(num_parallel, base_port, sleep_time, is_initial_launch=True):
# #     existing_ports = load_browser_ports()
# #     new_ports = []
# #     for i in tqdm(range(num_parallel), desc=Fore.BLUE + f"{COOKIE_EMOJI} Starting Instances" + Style.RESET_ALL):
# #         port = base_port + i
# #         if start_single_instance(port, is_initial_launch):
# #             new_ports.append(port)
# #         time.sleep(sleep_time)
# #     all_ports = list(set(existing_ports + new_ports))
# #     save_browser_ports(all_ports)
# #     print_info(f"Saved {len(all_ports)} active browser ports")
# #     return new_ports

# # # def check_browser_lifetime(first_browser_age, kill_spacing_s, retry_in_s: float = 1):
# # #     while True:
# # #         try:
# # #             ports = load_browser_ports()
# # #             if not ports:
# # #                 print_warning("No ports found in browser ports file!")
# # #                 time.sleep(retry_in_s)
# # #                 continue
# # #             shuffled_ports = ports.copy()
# # #             random.shuffle(shuffled_ports)
# # #             threads = []
# # #             for index, port in enumerate(shuffled_ports):
# # #                 thread = threading.Thread(
# # #                     target=manage_browser_lifetime,
# # #                     args=(port, first_browser_age, kill_spacing_s, index),
# # #                     daemon=True
# # #                 )
# # #                 thread.start()
# # #                 threads.append(thread)
# # #             for thread in threads:
# # #                 thread.join()
# # #         except Exception as e:
# # #             print_error(f"Error in browser lifetime checker: {e}")
# # #             time.sleep(retry_in_s)

# # # def manage_browser_lifetime(port, first_browser_age, kill_spacing_s, index):
# # #     while True:
# # #         try:
# # #             lifetime = first_browser_age + ((1 + index) * kill_spacing_s)
# # #             print_info(f"Browser on port {port} will restart in {lifetime} seconds")
# # #             time.sleep(lifetime)
# # #             print_info(f"Restarting browser on port {port}")
# # #             kill_browser_by_port(port)
# # #             if start_single_instance(port, is_initial_launch=False):
# # #                 current_ports = load_browser_ports()
# # #                 if port not in current_ports:
# # #                     current_ports.append(port)
# # #                     save_browser_ports(current_ports)
# # #         except Exception as e:
# # #             print_error(f"Error in browser lifetime management for port {port}: {e}")
# # #             time.sleep(0.2)
# # def main():
# #     print_log("Note: Launch with Python 3.13!")

# #     parser = argparse.ArgumentParser(description="Manage cookie_proxy_fetcher instances")
# #     parser.add_argument('--kill', action='store_true', help="Kill existing cookie_proxy_fetcher processes")
# #     parser.add_argument('--num_parallel', type=int, default=NUM_PARALLEL, help="Number of parallel instances")
# #     parser.add_argument('--base_port', type=int, default=BASE_PORT, help="Base port number")
# #     parser.add_argument('--sleep_time', type=float, default=SLEEP_TIME, help="Sleep time between launching instances")
# #     parser.add_argument('--first_browser_age', type=int, default=FIRST_BROWSER_AGE, help="Lifetime of the first browser in seconds")
# #     parser.add_argument('--kill_spacing_s', type=int, default=KILL_SPACING_S, help="Time spacing between browser kills in seconds")
# #     args = parser.parse_args()

# #     if args.num_parallel > MAX_PARALLEL_PROCESS:
# #         raise Exception("TOO MANY PARALLEL PROCESSES! Avoiding overheat and crash from resource-intensive browsers.")

# #     try:
# #         if args.kill:
# #             kill_existing_processes()
# #         else:
# #             kill_existing_processes()
# #             clear_browser_ports()
# #             initial_ports = list(range(args.base_port, args.base_port + args.num_parallel))
# #             save_browser_ports(initial_ports)
# #             start_instances(args.num_parallel, args.base_port, args.sleep_time, is_initial_launch=True)

# #             # No restart / lifetime management here anymore

# #     except KeyboardInterrupt:
# #         print_log("\nShutting down gracefully...")
# #         kill_existing_processes()
# #         clear_browser_ports()
# #     except Exception as e:
# #         print_error(f"Fatal error: {e}")
# #         kill_existing_processes()
# #         clear_browser_ports()

# # if __name__ == "__main__":
# #     main()




# import subprocess
# import json
# import time
# import argparse
# import os
# import psutil
# from tqdm import tqdm
# from multiprocessing import Pool
# from pathlib import Path
# import threading
# import random
# import signal
# from colorama import init, Fore, Style

# # Settings import with fallback
# try:
#     from settings import (
#         NUM_PARALLEL,
#         BASE_PORT,
#         SLEEP_TIME,
#         FIRST_BROWSER_AGE,
#         KILL_SPACING_S,
#         MAX_PARALLEL_PROCESS,
#         BROWSER_PORTS_FILE,
#     )
# except:
#     from .settings import (
#         NUM_PARALLEL,
#         BASE_PORT,
#         SLEEP_TIME,
#         FIRST_BROWSER_AGE,
#         KILL_SPACING_S,
#         MAX_PARALLEL_PROCESS,
#         BROWSER_PORTS_FILE,
#     )

# init(autoreset=True)  # Colorama init

# COOKIE_EMOJI = "🍪"
# MONSTER_EMOJIS = ["😋", "🤤", "😍", "🤯", "🥳"]

# def print_log(message: str, color=Fore.CYAN):
#     print(f"\n{color}{COOKIE_EMOJI} {message} {random.choice(MONSTER_EMOJIS)}{Style.RESET_ALL}")

# def print_warning(message: str):
#     print(f"\n{Fore.YELLOW}[WARNING] {message} ⚠️{Style.RESET_ALL}")

# def print_error(message: str):
#     print(f"\n{Fore.RED}[ERROR] {message} ❌{Style.RESET_ALL}")

# def print_info(message: str):
#     print(f"\n{Fore.GREEN}[INFO] {message} ✔️{Style.RESET_ALL}")

# def load_browser_ports(file_path=None):
#     if file_path is None:
#         file_path = Path(os.path.expanduser(BROWSER_PORTS_FILE))
#     if file_path.exists():
#         try:
#             with open(file_path, "r") as f:
#                 ports = json.load(f)
#                 if isinstance(ports, list):
#                     return ports
#         except Exception as e:
#             print_error(f"Error loading browser ports: {e}")
#     return []

# def save_browser_ports(ports, file_path=None):
#     if file_path is None:
#         file_path = Path(os.path.expanduser(BROWSER_PORTS_FILE))
#     try:
#         with open(file_path, "w") as f:
#             json.dump(ports, f)
#     except Exception as e:
#         print_error(f"Error saving browser ports: {e}")

# def clear_browser_ports(file_path=None):
#     if file_path is None:
#         file_path = Path(os.path.expanduser(BROWSER_PORTS_FILE))
#     if file_path.exists():
#         try:
#             file_path.unlink()
#             print_info("Cleared browser ports file.")
#         except Exception as e:
#             print_error(f"Error clearing browser ports: {e}")

# def terminate_process(pid):
#     try:
#         proc = psutil.Process(pid)
#         proc.terminate()
#         proc.wait(timeout=5)
#         print_info(f"Terminated process {pid}")
#     except psutil.TimeoutExpired:
#         proc.kill()
#         print_warning(f"Forcefully killed process {pid}")
#     except psutil.NoSuchProcess:
#         print_warning(f"Process {pid} no longer exists")

# # def kill_existing_processes():
# #     pids_to_kill = []
# #     for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
# #         try:
# #             if 'python' in proc.info['name'].lower() and 'cookie_proxy_fetcher.py' in ' '.join(proc.info['cmdline']):
# #                 pids_to_kill.append(proc.info['pid'])
# #         except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
# #             continue
# #     if pids_to_kill:
# #         print_info(f"Terminating {len(pids_to_kill)} cookie_proxy_fetcher processes")
# #         with Pool() as pool:
# #             pool.map(terminate_process, pids_to_kill)
# #     else:
# #         print_info("No matching cookie_proxy_fetcher processes found to terminate")

# def kill_existing_processes():
#     pids_to_kill = []
#     for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
#         try:
#             name = proc.info['name']
#             cmdline = proc.info['cmdline']
#             # Check that name is not None and is str
#             if isinstance(name, str) and 'python' in name.lower():
#                 # Make sure cmdline is a list and not None
#                 if isinstance(cmdline, list) and any('cookie_proxy_fetcher.py' in arg for arg in cmdline):
#                     pids_to_kill.append(proc.info['pid'])
#         except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
#             continue
#     if pids_to_kill:
#         print_info(f"Terminating {len(pids_to_kill)} cookie_proxy_fetcher processes")
#         with Pool() as pool:
#             pool.map(terminate_process, pids_to_kill)
#     else:
#         print_info("No matching cookie_proxy_fetcher processes found to terminate")


# # Global container to hold subprocess.Popen instances
# running_processes = []

# # def start_single_instance(port, is_initial_launch=True):
# #     """
# #     Start cookie_proxy_fetcher.py on given port and return the Popen process handle.
# #     This will launch the process *without* going to background in detached mode,
# #     so main script can hold and control it.
# #     """
# #     try:
# #         # Construct command and args
# #         cmd = [
# #             "python3",
# #             "cookie_proxy_fetcher.py",
# #             "--port",
# #             str(port),
# #         ]
# #         cwd = os.path.expanduser("~/Code/cookie_monster/cloudflare_bypasser")
# #         # Launch process without shell=True for safety
# #         proc = subprocess.Popen(
# #             cmd,
# #             cwd=cwd,
# #             stdout=subprocess.PIPE,
# #             stderr=subprocess.PIPE,
# #         )
# #         wait_time = 2 if is_initial_launch else 5
# #         print_info(f"Launched cookie_proxy_fetcher instance on port {port} with PID {proc.pid}")
# #         # Sleep briefly to let it start up; do NOT block main thread otherwise
# #         time.sleep(wait_time)
# #         return proc
# #     except Exception as e:
# #         print_error(f"Error launching instance on port {port}: {e}")
# #         return None

# import threading

# def stream_output(pipe, prefix=""):
#     for line in iter(pipe.readline, b''):
#         print(f"{prefix}{line.rstrip()}")
#     pipe.close()

# def start_single_instance(port, is_initial_launch=True):
#     try:
#         cmd = [
#             "python3",
#             "cookie_proxy_fetcher.py",
#             "--port",
#             str(port),
#         ]
#         cwd = os.path.expanduser("~/Code/cookie_monster/cloudflare_bypasser")
#         proc = subprocess.Popen(
#             cmd,
#             cwd=cwd,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             bufsize=1,
#             universal_newlines=True,
#         )
#         # Start threads to read stdout and stderr asynchronously
#         threading.Thread(target=stream_output, args=(proc.stdout, f"[Port {port} STDOUT] "), daemon=True).start()
#         threading.Thread(target=stream_output, args=(proc.stderr, f"[Port {port} STDERR] "), daemon=True).start()

#         wait_time = 2 if is_initial_launch else 5
#         print_info(f"Launched cookie_proxy_fetcher instance on port {port} with PID {proc.pid}")
#         time.sleep(wait_time)
#         return proc
#     except Exception as e:
#         print_error(f"Error launching instance on port {port}: {e}")
#         return None

# def start_instances(num_parallel, base_port, sleep_time, is_initial_launch=True):
#     """
#     Launch N instances in parallel, collecting subprocess.Popen handles for management.
#     """
#     existing_ports = load_browser_ports()
#     new_ports = []
#     global running_processes
#     for i in tqdm(range(num_parallel), desc=Fore.BLUE + f"{COOKIE_EMOJI} Starting Instances" + Style.RESET_ALL):
#         port = base_port + i
#         proc = start_single_instance(port, is_initial_launch)
#         if proc:
#             running_processes.append(proc)
#             new_ports.append(port)
#         time.sleep(sleep_time)
#     all_ports = list(set(existing_ports + new_ports))
#     save_browser_ports(all_ports)
#     print_info(f"Saved {len(all_ports)} active browser ports")
#     return new_ports

# def graceful_shutdown(signum, frame):
#     """
#     Signal handler to catch CTRL-C (SIGINT) and attempt to gracefully terminate all child processes.
#     """
#     print_log("\n[CTRL-C] Detected! Attempting graceful shutdown...")
    
#     # Terminate all running cookie_proxy_fetcher subprocesses launched by this script
#     global running_processes
#     for proc in running_processes:
#         if proc.poll() is None:  # Process still running
#             print_info(f"Terminating child process PID {proc.pid}...")
#             proc.terminate()
#             try:
#                 proc.wait(timeout=5)
#                 print_info(f"Child process PID {proc.pid} terminated successfully.")
#             except subprocess.TimeoutExpired:
#                 print_warning(f"Child process PID {proc.pid} did not terminate in time. Killing it now.")
#                 proc.kill()
#     running_processes.clear()

#     # Also kill any lingering processes matching cookie_proxy_fetcher.py for robustness
#     kill_existing_processes()

#     clear_browser_ports()
#     print_log("Shutdown complete. Exiting now.")
#     exit(0)

# def main():
#     print_log("Note: Launch with Python 3.13!")

#     parser = argparse.ArgumentParser(description="Manage cookie_proxy_fetcher instances")
#     parser.add_argument('--kill', action='store_true', help="Kill existing cookie_proxy_fetcher processes")
#     parser.add_argument('--num_parallel', type=int, default=NUM_PARALLEL, help="Number of parallel instances")
#     parser.add_argument('--base_port', type=int, default=BASE_PORT, help="Base port number")
#     parser.add_argument('--sleep_time', type=float, default=SLEEP_TIME, help="Sleep time between launching instances")
#     parser.add_argument('--first_browser_age', type=int, default=FIRST_BROWSER_AGE, help="Lifetime of the first browser in seconds")
#     parser.add_argument('--kill_spacing_s', type=int, default=KILL_SPACING_S, help="Time spacing between browser kills in seconds")
#     args = parser.parse_args()

#     if args.num_parallel > MAX_PARALLEL_PROCESS:
#         raise Exception("TOO MANY PARALLEL PROCESSES! Avoiding overheat and crash from resource-intensive browsers.")

#     # Register signal handler for graceful shutdown on CTRL-C
#     signal.signal(signal.SIGINT, graceful_shutdown)

#     try:
#         if args.kill:
#             kill_existing_processes()
#             clear_browser_ports()
#             print_info("Kill flag used; exiting after cleanup.")
#             return

#         # Normal flow: kill any existing, clear ports, save initial ports
#         kill_existing_processes()
#         clear_browser_ports()
#         initial_ports = list(range(args.base_port, args.base_port + args.num_parallel))
#         save_browser_ports(initial_ports)

#         # Start and hold all instances in foreground with handles stored globally
#         start_instances(args.num_parallel, args.base_port, args.sleep_time, is_initial_launch=True)

#         print_log("All instances launched! Press CTRL-C to terminate all running processes.")

#         # Now hold main thread alive to keep child processes running
#         # We do this by waiting on the Popen handles
#         global running_processes
#         while True:
#             all_exited = True
#             for proc in running_processes:
#                 ret = proc.poll()
#                 if ret is None:
#                     all_exited = False
#                 else:
#                     print_warning(f"Child process PID {proc.pid} exited unexpectedly with code {ret}")
#             if all_exited:
#                 print_info("All child processes have exited. Quitting main script.")
#                 break
#             time.sleep(1)

#     except KeyboardInterrupt:
#         # Also handled by signal, but just in case
#         graceful_shutdown(None, None)
#     except Exception as e:
#         print_error(f"Fatal error: {e}")
#         kill_existing_processes()
#         clear_browser_ports()

# if __name__ == "__main__":
#     main()

# import subprocess
# import json
# import time
# import argparse
# import os
# import psutil
# from tqdm import tqdm
# from multiprocessing import Pool
# from pathlib import Path
# import threading
# import random
# from colorama import init, Fore, Style

# try:
#     from settings import (
#         NUM_PARALLEL,
#         BASE_PORT,
#         SLEEP_TIME,
#         FIRST_BROWSER_AGE,
#         KILL_SPACING_S,
#         MAX_PARALLEL_PROCESS,
#         BROWSER_PORTS_FILE,
#     )
# except:
#     from .settings import (
#         NUM_PARALLEL,
#         BASE_PORT,
#         SLEEP_TIME,
#         FIRST_BROWSER_AGE,
#         KILL_SPACING_S,
#         MAX_PARALLEL_PROCESS,
#         BROWSER_PORTS_FILE,
#     )

# # Initialize colorama for cross-platform color support
# init(autoreset=True)

# COOKIE_EMOJI = "🍪"
# MONSTER_EMOJIS = ["😋", "🤤", "😍", "🤯", "🥳"]


# def print_log(message: str, color=Fore.CYAN):
#     print(f"\n{color}{COOKIE_EMOJI} {message} {random.choice(MONSTER_EMOJIS)}{Style.RESET_ALL}")

# def print_warning(message: str):
#     print(f"\n{Fore.YELLOW}[WARNING] {message} ⚠️{Style.RESET_ALL}")

# def print_error(message: str):
#     print(f"\n{Fore.RED}[ERROR] {message} ❌{Style.RESET_ALL}")

# def print_info(message: str):
#     print(f"\n{Fore.GREEN}[INFO] {message} ✔️{Style.RESET_ALL}")


# def load_browser_ports(file_path=None):
#     if file_path is None:
#         file_path = Path(os.path.expanduser(BROWSER_PORTS_FILE))
#     if file_path.exists():
#         try:
#             with open(file_path, "r") as f:
#                 ports = json.load(f)
#                 if isinstance(ports, list):
#                     return ports
#         except Exception as e:
#             print_error(f"Error loading browser ports: {e}")
#     return []

# def save_browser_ports(ports, file_path=None):
#     if file_path is None:
#         file_path = Path(os.path.expanduser(BROWSER_PORTS_FILE))
#     try:
#         with open(file_path, "w") as f:
#             json.dump(ports, f)
#     except Exception as e:
#         print_error(f"Error saving browser ports: {e}")

# def clear_browser_ports(file_path=None):
#     if file_path is None:
#         file_path = Path(os.path.expanduser(BROWSER_PORTS_FILE))
#     if file_path.exists():
#         try:
#             file_path.unlink()
#             print_info("Cleared browser ports file.")
#         except Exception as e:
#             print_error(f"Error clearing browser ports: {e}")

# def terminate_process(pid):
#     try:
#         proc = psutil.Process(pid)
#         proc.terminate()
#         proc.wait(timeout=5)
#         print_info(f"Terminated process {pid}")
#     except psutil.TimeoutExpired:
#         proc.kill()
#         print_warning(f"Forcefully killed process {pid}")
#     except psutil.NoSuchProcess:
#         print_warning(f"Process {pid} no longer exists")

# def kill_existing_processes():
#     pids_to_kill = []
#     for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
#         try:
#             if 'python' in proc.info['name'].lower() and 'cookie_proxy_fetcher.py' in ' '.join(proc.info['cmdline']):
#                 pids_to_kill.append(proc.info['pid'])
#         except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
#             continue
#     if pids_to_kill:
#         print_info(f"Terminating {len(pids_to_kill)} cookie_proxy_fetcher processes")
#         with Pool() as pool:
#             pool.map(terminate_process, pids_to_kill)
#     else:
#         print_info("No matching cookie_proxy_fetcher processes found to terminate")

# # def kill_browser_by_port(port):
# #     for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
# #         try:
# #             if 'python' in proc.info['name'].lower() and f'cookie_proxy_fetcher.py --port {port}' in ' '.join(proc.info['cmdline']):
# #                 terminate_process(proc.info['pid'])
# #                 return True
# #         except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
# #             continue
# #     print_warning(f"No process found running on port {port}")
# #     return False

# def start_single_instance(port, is_initial_launch=True):
#     try:
#         cmd = f"cd ~/Code/cookie_monster/cloudflare_bypasser && python3 cookie_proxy_fetcher.py --port {port}"
#         subprocess.Popen(cmd, shell=True, cwd=os.getcwd())
#         wait_time = 2 if is_initial_launch else 5
#         time.sleep(wait_time)
#         print_info(f"Launched cookie_proxy_fetcher instance on port {port}")
#         return True
#     except Exception as e:
#         print_error(f"Error launching instance on port {port}: {e}")
#         return False

# def start_instances(num_parallel, base_port, sleep_time, is_initial_launch=True):
#     existing_ports = load_browser_ports()
#     new_ports = []
#     for i in tqdm(range(num_parallel), desc=Fore.BLUE + f"{COOKIE_EMOJI} Starting Instances" + Style.RESET_ALL):
#         port = base_port + i
#         if start_single_instance(port, is_initial_launch):
#             new_ports.append(port)
#         time.sleep(sleep_time)
#     all_ports = list(set(existing_ports + new_ports))
#     save_browser_ports(all_ports)
#     print_info(f"Saved {len(all_ports)} active browser ports")
#     return new_ports

# # def check_browser_lifetime(first_browser_age, kill_spacing_s, retry_in_s: float = 1):
# #     while True:
# #         try:
# #             ports = load_browser_ports()
# #             if not ports:
# #                 print_warning("No ports found in browser ports file!")
# #                 time.sleep(retry_in_s)
# #                 continue
# #             shuffled_ports = ports.copy()
# #             random.shuffle(shuffled_ports)
# #             threads = []
# #             for index, port in enumerate(shuffled_ports):
# #                 thread = threading.Thread(
# #                     target=manage_browser_lifetime,
# #                     args=(port, first_browser_age, kill_spacing_s, index),
# #                     daemon=True
# #                 )
# #                 thread.start()
# #                 threads.append(thread)
# #             for thread in threads:
# #                 thread.join()
# #         except Exception as e:
# #             print_error(f"Error in browser lifetime checker: {e}")
# #             time.sleep(retry_in_s)

# # def manage_browser_lifetime(port, first_browser_age, kill_spacing_s, index):
# #     while True:
# #         try:
# #             lifetime = first_browser_age + ((1 + index) * kill_spacing_s)
# #             print_info(f"Browser on port {port} will restart in {lifetime} seconds")
# #             time.sleep(lifetime)
# #             print_info(f"Restarting browser on port {port}")
# #             kill_browser_by_port(port)
# #             if start_single_instance(port, is_initial_launch=False):
# #                 current_ports = load_browser_ports()
# #                 if port not in current_ports:
# #                     current_ports.append(port)
# #                     save_browser_ports(current_ports)
# #         except Exception as e:
# #             print_error(f"Error in browser lifetime management for port {port}: {e}")
# #             time.sleep(0.2)
# def main():
#     print_log("Note: Launch with Python 3.13!")

#     parser = argparse.ArgumentParser(description="Manage cookie_proxy_fetcher instances")
#     parser.add_argument('--kill', action='store_true', help="Kill existing cookie_proxy_fetcher processes")
#     parser.add_argument('--num_parallel', type=int, default=NUM_PARALLEL, help="Number of parallel instances")
#     parser.add_argument('--base_port', type=int, default=BASE_PORT, help="Base port number")
#     parser.add_argument('--sleep_time', type=float, default=SLEEP_TIME, help="Sleep time between launching instances")
#     parser.add_argument('--first_browser_age', type=int, default=FIRST_BROWSER_AGE, help="Lifetime of the first browser in seconds")
#     parser.add_argument('--kill_spacing_s', type=int, default=KILL_SPACING_S, help="Time spacing between browser kills in seconds")
#     args = parser.parse_args()

#     if args.num_parallel > MAX_PARALLEL_PROCESS:
#         raise Exception("TOO MANY PARALLEL PROCESSES! Avoiding overheat and crash from resource-intensive browsers.")

#     try:
#         if args.kill:
#             kill_existing_processes()
#         else:
#             kill_existing_processes()
#             clear_browser_ports()
#             initial_ports = list(range(args.base_port, args.base_port + args.num_parallel))
#             save_browser_ports(initial_ports)
#             start_instances(args.num_parallel, args.base_port, args.sleep_time, is_initial_launch=True)

#             # No restart / lifetime management here anymore

#     except KeyboardInterrupt:
#         print_log("\nShutting down gracefully...")
#         kill_existing_processes()
#         clear_browser_ports()
#     except Exception as e:
#         print_error(f"Fatal error: {e}")
#         kill_existing_processes()
#         clear_browser_ports()

# if __name__ == "__main__":
#     main()




import subprocess
import json
import time
import argparse
import os
import psutil
from tqdm import tqdm
from multiprocessing import Pool
from pathlib import Path
import threading
import random
import signal
from colorama import init, Fore, Style

# Settings import with fallback
try:
    from settings import (
        NUM_PARALLEL,
        BASE_PORT,
        SLEEP_TIME,
        FIRST_BROWSER_AGE,
        KILL_SPACING_S,
        MAX_PARALLEL_PROCESS,
        BROWSER_PORTS_FILE,
    )
except:
    from .settings import (
        NUM_PARALLEL,
        BASE_PORT,
        SLEEP_TIME,
        FIRST_BROWSER_AGE,
        KILL_SPACING_S,
        MAX_PARALLEL_PROCESS,
        BROWSER_PORTS_FILE,
    )

init(autoreset=True)  # Colorama init

COOKIE_EMOJI = "🍪"
MONSTER_EMOJIS = ["😋", "🤤", "😍", "🤯", "🥳"]

def print_log(message: str, color=Fore.CYAN):
    print(f"\n{color}{COOKIE_EMOJI} {message} {random.choice(MONSTER_EMOJIS)}{Style.RESET_ALL}")

def print_warning(message: str):
    print(f"\n{Fore.YELLOW}[WARNING] {message} ⚠️{Style.RESET_ALL}")

def print_error(message: str):
    print(f"\n{Fore.RED}[ERROR] {message} ❌{Style.RESET_ALL}")

def print_info(message: str):
    print(f"\n{Fore.GREEN}[INFO] {message} ✔️{Style.RESET_ALL}")

def load_browser_ports(file_path=None):
    if file_path is None:
        file_path = Path(os.path.expanduser(BROWSER_PORTS_FILE))
    if file_path.exists():
        try:
            with open(file_path, "r") as f:
                ports = json.load(f)
                if isinstance(ports, list):
                    return ports
        except Exception as e:
            print_error(f"Error loading browser ports: {e}")
    return []

def save_browser_ports(ports, file_path=None):
    if file_path is None:
        file_path = Path(os.path.expanduser(BROWSER_PORTS_FILE))
    try:
        with open(file_path, "w") as f:
            json.dump(ports, f)
    except Exception as e:
        print_error(f"Error saving browser ports: {e}")

def clear_browser_ports(file_path=None):
    if file_path is None:
        file_path = Path(os.path.expanduser(BROWSER_PORTS_FILE))
    if file_path.exists():
        try:
            file_path.unlink()
            print_info("Cleared browser ports file.")
        except Exception as e:
            print_error(f"Error clearing browser ports: {e}")

def terminate_process(pid):
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        proc.wait(timeout=5)
        print_info(f"Terminated process {pid}")
    except psutil.TimeoutExpired:
        proc.kill()
        print_warning(f"Forcefully killed process {pid}")
    except psutil.NoSuchProcess:
        print_warning(f"Process {pid} no longer exists")

# def kill_existing_processes():
#     pids_to_kill = []
#     for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
#         try:
#             if 'python' in proc.info['name'].lower() and 'cookie_proxy_fetcher.py' in ' '.join(proc.info['cmdline']):
#                 pids_to_kill.append(proc.info['pid'])
#         except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
#             continue
#     if pids_to_kill:
#         print_info(f"Terminating {len(pids_to_kill)} cookie_proxy_fetcher processes")
#         with Pool() as pool:
#             pool.map(terminate_process, pids_to_kill)
#     else:
#         print_info("No matching cookie_proxy_fetcher processes found to terminate")

def kill_existing_processes():
    pids_to_kill = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            name = proc.info['name']
            cmdline = proc.info['cmdline']
            # Check that name is not None and is str
            if isinstance(name, str) and 'python' in name.lower():
                # Make sure cmdline is a list and not None
                if isinstance(cmdline, list) and any('cookie_proxy_fetcher.py' in arg for arg in cmdline):
                    pids_to_kill.append(proc.info['pid'])
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    if pids_to_kill:
        print_info(f"Terminating {len(pids_to_kill)} cookie_proxy_fetcher processes")
        with Pool() as pool:
            pool.map(terminate_process, pids_to_kill)
    else:
        print_info("No matching cookie_proxy_fetcher processes found to terminate")


# Global container to hold subprocess.Popen instances
running_processes = []

def start_single_instance(port, is_initial_launch=True):
    """
    Start cookie_proxy_fetcher.py on given port and return the Popen process handle.
    This will launch the process *without* going to background in detached mode,
    so main script can hold and control it.
    """
    try:
        # Construct command and args
        cmd = [
            "python3",
            "cookie_proxy_fetcher.py",
            "--port",
            str(port),
        ]
        cwd = os.path.expanduser("~/Code/cookie_monster/cloudflare_bypasser")
        # Launch process without shell=True for safety
        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        wait_time = 2 if is_initial_launch else 5
        print_info(f"Launched cookie_proxy_fetcher instance on port {port} with PID {proc.pid}")
        # Sleep briefly to let it start up; do NOT block main thread otherwise
        time.sleep(wait_time)
        return proc
    except Exception as e:
        print_error(f"Error launching instance on port {port}: {e}")
        return None

# import threading

# def stream_output(pipe, prefix=""):
#     for line in iter(pipe.readline, b''):
#         print(f"{prefix}{line.rstrip()}")
#     pipe.close()

# def start_single_instance(port, is_initial_launch=True):
#     try:
#         cmd = [
#             "python3",
#             "cookie_proxy_fetcher.py",
#             "--port",
#             str(port),
#         ]
#         cwd = os.path.expanduser("~/Code/cookie_monster/cloudflare_bypasser")
#         proc = subprocess.Popen(
#             cmd,
#             cwd=cwd,
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             bufsize=1,
#             universal_newlines=True,
#         )
#         # Start threads to read stdout and stderr asynchronously
#         threading.Thread(target=stream_output, args=(proc.stdout, f"[Port {port} STDOUT] "), daemon=True).start()
#         threading.Thread(target=stream_output, args=(proc.stderr, f"[Port {port} STDERR] "), daemon=True).start()

#         wait_time = 2 if is_initial_launch else 5
#         print_info(f"Launched cookie_proxy_fetcher instance on port {port} with PID {proc.pid}")
#         time.sleep(wait_time)
#         return proc
#     except Exception as e:
#         print_error(f"Error launching instance on port {port}: {e}")
#         return None

def start_instances(num_parallel, base_port, sleep_time, is_initial_launch=True):
    """
    Launch N instances in parallel, collecting subprocess.Popen handles for management.
    """
    existing_ports = load_browser_ports()
    new_ports = []
    global running_processes
    for i in tqdm(range(num_parallel), desc=Fore.BLUE + f"{COOKIE_EMOJI} Starting Instances" + Style.RESET_ALL):
        port = base_port + i
        proc = start_single_instance(port, is_initial_launch)
        if proc:
            running_processes.append(proc)
            new_ports.append(port)
        time.sleep(sleep_time)
    all_ports = list(set(existing_ports + new_ports))
    save_browser_ports(all_ports)
    print_info(f"Saved {len(all_ports)} active browser ports")
    return new_ports

def graceful_shutdown(signum, frame):
    """
    Signal handler to catch CTRL-C (SIGINT) and attempt to gracefully terminate all child processes.
    """
    print_log("\n[CTRL-C] Detected! Attempting graceful shutdown...")
    
    # Terminate all running cookie_proxy_fetcher subprocesses launched by this script
    global running_processes
    for proc in running_processes:
        if proc.poll() is None:  # Process still running
            print_info(f"Terminating child process PID {proc.pid}...")
            proc.terminate()
            try:
                proc.wait(timeout=5)
                print_info(f"Child process PID {proc.pid} terminated successfully.")
            except subprocess.TimeoutExpired:
                print_warning(f"Child process PID {proc.pid} did not terminate in time. Killing it now.")
                proc.kill()
    running_processes.clear()

    # Also kill any lingering processes matching cookie_proxy_fetcher.py for robustness
    kill_existing_processes()

    clear_browser_ports()
    print_log("Shutdown complete. Exiting now.")
    exit(0)

def main():
    print_log("Note: Launch with Python 3.13!")

    parser = argparse.ArgumentParser(description="Manage cookie_proxy_fetcher instances")
    parser.add_argument('--kill', action='store_true', help="Kill existing cookie_proxy_fetcher processes")
    parser.add_argument('--num_parallel', type=int, default=NUM_PARALLEL, help="Number of parallel instances")
    parser.add_argument('--base_port', type=int, default=BASE_PORT, help="Base port number")
    parser.add_argument('--sleep_time', type=float, default=SLEEP_TIME, help="Sleep time between launching instances")
    parser.add_argument('--first_browser_age', type=int, default=FIRST_BROWSER_AGE, help="Lifetime of the first browser in seconds")
    parser.add_argument('--kill_spacing_s', type=int, default=KILL_SPACING_S, help="Time spacing between browser kills in seconds")
    args = parser.parse_args()

    if args.num_parallel > MAX_PARALLEL_PROCESS:
        raise Exception("TOO MANY PARALLEL PROCESSES! Avoiding overheat and crash from resource-intensive browsers.")

    # Register signal handler for graceful shutdown on CTRL-C
    signal.signal(signal.SIGINT, graceful_shutdown)

    try:
        if args.kill:
            kill_existing_processes()
            clear_browser_ports()
            print_info("Kill flag used; exiting after cleanup.")
            return

        # Normal flow: kill any existing, clear ports, save initial ports
        kill_existing_processes()
        clear_browser_ports()
        initial_ports = list(range(args.base_port, args.base_port + args.num_parallel))
        save_browser_ports(initial_ports)

        # Start and hold all instances in foreground with handles stored globally
        start_instances(args.num_parallel, args.base_port, args.sleep_time, is_initial_launch=True)

        print_log("All instances launched! Press CTRL-C to terminate all running processes.")

        # Now hold main thread alive to keep child processes running
        # We do this by waiting on the Popen handles
        global running_processes
        while True:
            all_exited = True
            for proc in running_processes:
                ret = proc.poll()
                if ret is None:
                    all_exited = False
                else:
                    print_warning(f"Child process PID {proc.pid} exited unexpectedly with code {ret}")
            if all_exited:
                print_info("All child processes have exited. Quitting main script.")
                break
            time.sleep(1)

    except KeyboardInterrupt:
        # Also handled by signal, but just in case
        graceful_shutdown(None, None)
    except Exception as e:
        print_error(f"Fatal error: {e}")
        kill_existing_processes()
        clear_browser_ports()

if __name__ == "__main__":
    main()
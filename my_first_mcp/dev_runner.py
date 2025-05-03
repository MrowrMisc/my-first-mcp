import signal
import subprocess
import sys
import time

from watchfiles import watch

PROCESSES = []


def start_servers():
    print("[dev] Starting servers...")
    api_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "my_first_mcp.mcp:app", "--port", "9000"],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    mcp_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "my_first_mcp.mcp:sse_mcp", "--port", "8000"],
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    PROCESSES[:] = [api_proc, mcp_proc]


def stop_servers():
    print("[dev] Stopping servers...")
    for proc in PROCESSES:
        if proc.poll() is None:
            proc.terminate()
    for proc in PROCESSES:
        if proc.poll() is None:
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
    PROCESSES.clear()


def watch_and_reload():
    start_servers()
    for changes in watch("my_first_mcp"):
        print(f"[dev] File change detected: {changes}")
        stop_servers()
        time.sleep(0.5)  # Let ports be released
        start_servers()


def handle_sigint(sig, frame):
    print("\n[dev] Caught Ctrl+C, shutting down...")
    stop_servers()
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_sigint)
    watch_and_reload()

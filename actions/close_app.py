"""Close a named desktop application."""

import platform
import subprocess

try:
    import psutil
except ImportError:
    psutil = None

from actions.open_app import _normalize


def close_app(parameters=None, response=None, player=None) -> str:
    app_name = (parameters or {}).get("app_name", "").strip()
    if not app_name:
        return "Please specify which application to close, sir."

    if platform.system() != "Windows":
        return "Closing named applications is currently supported on Windows only, sir."

    process_name = _normalize(app_name)
    if not process_name.lower().endswith(".exe"):
        process_name += ".exe"

    if player:
        player.write_log(f"[close_app] {app_name}")

    if psutil is not None:
        target = process_name.lower()
        matches = []
        for process in psutil.process_iter(["name"]):
            try:
                name = (process.info.get("name") or "").lower()
                if name == target:
                    matches.append(process)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if matches:
            closed = 0
            for process in matches:
                try:
                    process.terminate()
                    closed += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            if closed:
                return f"Closed {app_name} successfully, sir."

    try:
        result = subprocess.run(
            ["taskkill", "/IM", process_name, "/T", "/F"],
            capture_output=True,
            text=True,
            timeout=8,
        )
        if result.returncode == 0:
            return f"Closed {app_name} successfully, sir."
    except (OSError, subprocess.TimeoutExpired) as error:
        return f"Failed to close {app_name}, sir: {error}"

    return f"{app_name} is not running, sir."

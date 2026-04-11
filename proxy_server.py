import subprocess
import sys
import os

_proxy_process = None


def start_proxy(port=8080):
    """
    Запускает mitmproxy в прозрачном режиме на указанном порту.
    Возвращает объект subprocess.Popen или None при ошибке.
    """
    global _proxy_process

    if _proxy_process is not None and _proxy_process.poll() is None:
        return _proxy_process

    mitmdump_path = _find_mitmdump()
    if not mitmdump_path:
        raise RuntimeError(
            "mitmdump не найден. Установите mitmproxy: pip install mitmproxy"
        )

    cmd = [
        mitmdump_path,
        "--mode", "transparent",
        "--listen-host", "0.0.0.0",
        "--listen-port", str(port),
        "--ssl-insecure",
    ]

    _proxy_process = subprocess.Popen(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    return _proxy_process


def stop_proxy():
    """Останавливает запущенный прокси-сервер."""
    global _proxy_process

    if _proxy_process is None:
        return

    if _proxy_process.poll() is None:
        _proxy_process.terminate()
        try:
            _proxy_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _proxy_process.kill()

    _proxy_process = None


def is_running():
    """Возвращает True, если прокси-сервер в данный момент запущен."""
    global _proxy_process
    return _proxy_process is not None and _proxy_process.poll() is None


def _find_mitmdump():
    """Ищет исполняемый файл mitmdump в PATH и рядом с текущим интерпретатором."""
    # Ищем рядом с текущим Python (виртуальное окружение / pip install)
    scripts_subdir = "Scripts" if sys.platform == "win32" else "bin"
    executable_name = "mitmdump.exe" if sys.platform == "win32" else "mitmdump"
    candidate = os.path.join(os.path.dirname(sys.executable), scripts_subdir, executable_name)
    if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
        return candidate

    # Затем ищем в PATH через which/where
    which_cmd = "where" if sys.platform == "win32" else "which"
    result = subprocess.run(
        [which_cmd, "mitmdump"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode == 0:
        path = result.stdout.decode().strip().splitlines()[0]
        if path:
            return path

    return None

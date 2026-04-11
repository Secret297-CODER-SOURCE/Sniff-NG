"""
proxy_server.py — запуск/остановка mitmproxy в прозрачном режиме.

Используется совместно с:
  - ARP-спуфингом (arp_spoof.py)  — перенаправление трафика через наш хост
  - iptables-правилами (dependency_manager.py) — редирект портов 80/443 → 8080
  - IP-форвардингом (dependency_manager.py)   — пересылка пакетов

После запуска перехваченный трафик пишется в DEFAULT_LOG.
"""

import subprocess

_mitmproxy_process = None
_log_fd = None
DEFAULT_PORT = 8080
DEFAULT_LOG = "/tmp/sniff-ng-traffic.log"


def start_mitmproxy(port=DEFAULT_PORT, log_file=DEFAULT_LOG):
    """
    Запускает mitmdump в прозрачном режиме.

    Возвращает True при успехе, False если mitmdump не найден или уже запущен.
    """
    global _mitmproxy_process, _log_fd

    if _mitmproxy_process is not None and _mitmproxy_process.poll() is None:
        return True  # уже работает

    try:
        if log_file:
            _log_fd = open(log_file, "w")
            stdout = _log_fd
            stderr = _log_fd
        else:
            stdout = subprocess.DEVNULL
            stderr = subprocess.DEVNULL

        _mitmproxy_process = subprocess.Popen(
            [
                "mitmdump",
                "--mode", "transparent",
                "--showhost",
                "-p", str(port),
            ],
            stdout=stdout,
            stderr=stderr,
        )
        return True
    except FileNotFoundError:
        _close_log_fd()
        return False
    except Exception:
        _close_log_fd()
        return False


def stop_mitmproxy():
    """
    Останавливает запущенный процесс mitmdump.

    Возвращает True если процесс был остановлен, False если он не был запущен.
    """
    global _mitmproxy_process

    if _mitmproxy_process is None:
        return False

    if _mitmproxy_process.poll() is None:
        _mitmproxy_process.terminate()
        try:
            _mitmproxy_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _mitmproxy_process.kill()
            _mitmproxy_process.wait()

    _mitmproxy_process = None
    _close_log_fd()
    return True


def _close_log_fd():
    global _log_fd
    if _log_fd is not None:
        try:
            _log_fd.close()
        except Exception:
            pass
        _log_fd = None


def is_running():
    """Возвращает True, если mitmproxy сейчас активен."""
    return _mitmproxy_process is not None and _mitmproxy_process.poll() is None


def get_log_file():
    return DEFAULT_LOG


def get_port():
    return DEFAULT_PORT

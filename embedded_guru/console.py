import sys


def _supports_colour() -> bool:
    if sys.platform == "win32":
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            return True
        except Exception:
            return False
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


_USE_COLOUR = _supports_colour()


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _USE_COLOUR else text


def info(msg: str)    -> None: print(f"  {_c('36', '→')} {msg}")
def ok(msg: str)      -> None: print(f"  {_c('32', '✓')} {msg}")
def warn(msg: str)    -> None: print(f"  {_c('33', '⚠')} {msg}")
def err(msg: str)     -> None: print(f"  {_c('31', '✗')} {msg}", file=sys.stderr)
def header(msg: str)  -> None: print(f"\n{_c('1', msg)}")
def bold(text: str)   -> str:  return _c('1', text)
def red(text: str)    -> str:  return _c('31', text)
def yellow(text: str) -> str:  return _c('33', text)

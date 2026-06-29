from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("embedded-guru")
except PackageNotFoundError:
    __version__ = "dev"

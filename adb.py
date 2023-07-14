import os
import subprocess


class Adb:
    def __init__(self, path: str, port: int = 16384):
        self.__path: str | None = None
        self.path = path
        self.__port: int = 16384
        self.port = port
        self.connect()

    @property
    def path(self) -> str:
        return self.__path

    @path.setter
    def path(self, path: str):
        if not isinstance(path, str):
            raise TypeError(f"Invalid type: {type(path)}")
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File not found: {path}")
        if not path.endswith("adb.exe"):
            raise ValueError(f"Invalid executable: {path}")
        if not os.access(path, os.X_OK):
            raise PermissionError(f"Permission denied: {path}")
        self.__path = path

    @property
    def port(self) -> int:
        return self.__port

    @port.setter
    def port(self, port: int):
        if not isinstance(port, int):
            raise TypeError(f"Invalid type: {type(port)}")
        if port < 1024 or port > 65535:
            raise ValueError(f"Invalid port: {port}")
        self.__port = port

    def __create_process(self, command: str, universal_newlines: bool = True) -> subprocess.Popen:
        return subprocess.Popen(
            args=f"{self.__path} " + command, universal_newlines=universal_newlines,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )

    def connect(self):
        conn = self.__create_process(f"connect 127.0.0.1:{self.__port}")
        print(conn.stdout.read())
        print(conn.stderr.read())
        return self

    def _exec(self, command: str) -> tuple[str, str]:
        process = self.__create_process(f"shell {command}")
        return process.stdout.read(), process.stderr.read()

    def click(self, x: int, y: int):
        if not isinstance(x, int) or not isinstance(y, int):
            raise TypeError(f"Invalid type: {type(x)}, {type(y)}")
        return self._exec(f"input tap {x} {y}")

    def screenshot(self, save_path: str):
        if not isinstance(save_path, str):
            raise TypeError(f"Invalid type: {type(save_path)}")
        if not save_path.endswith(".png"):
            raise ValueError(f"Invalid file type: {save_path}")
        with open(save_path, 'wb') as img:
            img.write(self.__create_process('exec-out screencap -p', False).stdout.read())
        return os.path.abspath(save_path)

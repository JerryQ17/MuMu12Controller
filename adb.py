import os
import subprocess


class Adb:
    def __init__(self, path: str, port: int = 16384):
        # 设置adb.exe的路径和端口号
        self.__path: str | None = None
        self.path = path
        self.__port: int = 16384
        self.port = port
        # 连接adb
        self.start_server().connect()

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

    def _exec(self, command: str, **kwargs) -> subprocess.Popen:
        if not isinstance(command, str):
            raise TypeError(f"Invalid type: {type(command)}")
        for key in ('stdin', 'stdout', 'stderr'):
            if key not in kwargs:
                kwargs.update({key: subprocess.PIPE})
        return subprocess.Popen(f"{self.__path} {command}", **kwargs)

    def start_server(self):
        self._exec("start-server").wait()
        return self

    def kill_server(self):
        self._exec("kill-server").wait()
        return self

    def connect(self):
        self._exec(f"connect 127.0.0.1:{self.__port}").wait()
        return self

    def disconnect(self):
        self._exec(f"disconnect 127.0.0.1:{self.__port}").wait()
        return self

    def click(self, x: int, y: int):
        if not isinstance(x, int) or not isinstance(y, int):
            raise TypeError(f"Invalid type: {type(x)}, {type(y)}")
        return self._exec(f"shell input tap {x} {y}")

    def screenshot(self, save_path: str):
        if not isinstance(save_path, str):
            raise TypeError(f"Invalid type: {type(save_path)}")
        if not save_path.endswith(".png"):
            raise ValueError(f"Invalid file type: {save_path}")
        with open(save_path, 'wb') as img:
            img.write(self._exec('exec-out screencap -p', universal_newlines=False).stdout.read())
        return os.path.abspath(save_path)

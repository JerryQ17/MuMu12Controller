import os
import cv2
import subprocess


def compare(img_name: str, sub_img_name: str):
    """
    compare函数会在img_name图片中寻找最接近sub_img_name图片的坐标，并返回该位置坐标
    :param img_name: 要查找的图片
    :param sub_img_name: 要查找的图片的子图片
    :return: x, y
    """
    if not os.path.isfile(img_name):
        raise FileNotFoundError(f"File not found: {img_name}")
    if not os.path.isfile(sub_img_name):
        raise FileNotFoundError(f"File not found: {sub_img_name}")

    img = cv2.imread(img_name)
    sub_img = cv2.imread(sub_img_name)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    sub_img_gray = cv2.cvtColor(sub_img, cv2.COLOR_BGR2GRAY)
    result = cv2.matchTemplate(img_gray, sub_img_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    top_left = max_loc
    bottom_right = (top_left[0] + sub_img.shape[1], top_left[1] + sub_img.shape[0])
    x = int((top_left[0] + bottom_right[0]) / 2)
    y = int((top_left[1] + bottom_right[1]) / 2)
    print(f"在{os.path.basename(img_name)}与{os.path.basename(sub_img_name)}最接近的位置是({x},{y})")
    return x, y


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

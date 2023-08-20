import os
import adb
import cv2
import time
import pickle
import logging
from typing import TextIO


class AzureLane:

    def __init__(
            self,
            adb_path: str, pos_path: str, retire_path: str, encore_path: str, temp_path: str = r'.\image\sc.png',
            port: int = 16384, max_count: int = -1,
            *,
            enable_logging: bool = False, log_stream: TextIO | None = None, log_file: str | None = None
    ):
        # 初始化adb
        self.__adb: adb.Adb = adb.Adb(adb_path, port)
        # 初始化计数器、图片路径和位置列表
        self.__max_count: int = -1
        self.max_count = max_count
        self.__retire_count: int = 0
        self.__retire_path: str = ''
        self.retire_path = retire_path
        self.__retire_position: list[tuple[int, int]] = []

        self.__encore_count: int = 0
        self.__encore_path: str = ''
        self.encore_path = encore_path
        self.__encore_position: list[tuple[int, int]] = []
        # 设置pos文件路径
        self.__pos_path: str = ''
        self.pos_path = pos_path
        self.load(pos_path)
        # 设置日志
        self.__enable_logging: bool = bool(enable_logging)
        if self.__enable_logging:
            self.__logger: logging.Logger = logging.getLogger(str(self))
            self.__logger.setLevel(logging.DEBUG)
            if log_stream is not None:
                self.__logger.addHandler(logging.StreamHandler(log_stream))
            if log_file is not None:
                self.__logger.addHandler(logging.FileHandler(log_file))
            self.__logger.info(f"{self} initialized")
        # 设置临时图片路径
        self.__temp_path: str = ''
        self.temp_path = temp_path

    def __del__(self):
        if hasattr(self, f'_{self.__class__.__name__}__enable_logging') and self.__enable_logging:
            self.__logger.handlers.clear()
        self.__adb.disconnect().kill_server()

    def __str__(self):
        return f"{self.__class__.__name__}(port={self.__adb.port}," \
               f" max_count={self.__max_count}," \
               f" enable_logging={self.__enable_logging})"

    @property
    def adb(self) -> adb.Adb:
        return self.__adb

    @property
    def max_count(self) -> int:
        return self.__max_count

    @max_count.setter
    def max_count(self, max_count: int):
        if not isinstance(max_count, int):
            try:
                max_count = int(float(max_count))
            except ValueError as error:
                raise TypeError(f"Invalid type: {type(max_count)}") from error
        if max_count < -1:
            raise ValueError(f"Invalid value: {max_count}")
        self.__max_count = max_count

    @property
    def retire_count(self) -> int:
        return self.__retire_count

    @property
    def retire_path(self) -> str:
        return self.__retire_path

    @retire_path.setter
    def retire_path(self, retire_path: str):
        self.__retire_path = self._check_file(retire_path)

    def _check_retire_position(self, retire_position: list[tuple[int, int]]):
        if not isinstance(retire_position, list):
            raise TypeError(f"Invalid type: {type(retire_position)}")
        if len(retire_position) != 10:
            raise ValueError(f"Invalid value: {retire_position}")
        for position in retire_position:
            self._check_position(position)

    @property
    def retire_position(self) -> list[tuple[int, int]]:
        self._check_retire_position(self.__retire_position)
        return self.__retire_position

    @retire_position.setter
    def retire_position(self, retire_position: list[tuple[int, int]]):
        self._check_retire_position(retire_position)
        self.__retire_position = retire_position

    @property
    def encore_count(self) -> int:
        return self.__encore_count

    @property
    def encore_path(self) -> str:
        return self.__encore_path

    @encore_path.setter
    def encore_path(self, encore_path: str):
        self.__encore_path = self._check_file(encore_path)

    def _check_encore_position(self, encore_position: list[tuple[int, int]]):
        if not isinstance(encore_position, list):
            raise TypeError(f"Invalid type: {type(encore_position)}")
        for position in encore_position:
            self._check_position(position)

    @property
    def encore_position(self) -> list[tuple[int, int]]:
        self._check_encore_position(self.__encore_position)
        return self.__encore_position

    @encore_position.setter
    def encore_position(self, encore_position: list[tuple[int, int]]):
        self._check_encore_position(encore_position)
        self.__encore_position = encore_position

    @property
    def pos_path(self) -> str:
        return self.__pos_path

    @pos_path.setter
    def pos_path(self, pos_path: str):
        self.__pos_path = self._check_file(pos_path)

    @property
    def temp_path(self) -> str:
        return self.__temp_path

    @temp_path.setter
    def temp_path(self, temp_path: str):
        if not isinstance(temp_path, str):
            raise TypeError(f"Invalid type: {type(temp_path)}")
        self.__temp_path = temp_path

    @staticmethod
    def _check_file(file: str):
        if not isinstance(file, str):
            raise TypeError(f"Invalid type: {type(file)}")
        if not os.path.isfile(file):
            raise FileNotFoundError(f"Invalid file: {file}")
        return file

    @staticmethod
    def _check_position(position: tuple[int, int]):
        if not isinstance(position, tuple):
            raise TypeError(f"Invalid type: {type(position)}")
        if len(position) != 2:
            raise ValueError(f"Invalid value: {position}")
        if not isinstance(position[0], int) or not isinstance(position[1], int):
            raise TypeError(f"Invalid type: ({type(position[0])} , {type(position[1])})")
        return position

    def load(self, path: str):
        with open(self._check_file(path), "rb") as file:
            self.__retire_position, self.__encore_position = pickle.load(file)
        return self

    def save(self, path: str):
        if not isinstance(path, str):
            raise TypeError(f"Invalid type: {type(path)}")
        with open(path, "wb") as file:
            pickle.dump((self.__retire_position, self.__encore_position), file)
        return self

    def _check_retire_and_exec(self, x: int, y: int, sleep: float = 1.5):
        if x == self.__retire_position[0][0] and y == self.__retire_position[0][1]:
            if self.__enable_logging:
                self.__logger.info(f"第{self.__retire_count}次退役舰船")
            for x, y in self.__retire_position:
                self.__adb.click(x, y)
                time.sleep(sleep)
            self.__retire_count += 1
        return self

    def _check_encore_and_exec(self, x: int, y: int, sleep: float = 1.5):
        for ex, ey in self.__encore_position:
            if x == ex and y == ey:
                if self.__enable_logging:
                    self.__logger.info(f"第{self.__encore_count}次再次出击")
                self.__adb.click(x, y)
                time.sleep(sleep)
                self.__encore_count += 1
                break
        return self

    def _compare(self, img_name: str, sub_img_name: str):
        """
        在img_name图片中寻找最接近sub_img_name图片的坐标，并返回该位置坐标
        :param img_name: 要查找的图片
        :param sub_img_name: 要查找的图片的子图片
        :return: x, y
        """
        img = cv2.imread(self._check_file(img_name))
        sub_img = cv2.imread(self._check_file(sub_img_name))
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        sub_img_gray = cv2.cvtColor(sub_img, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(img_gray, sub_img_gray, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        top_left = max_loc
        bottom_right = (top_left[0] + sub_img.shape[1], top_left[1] + sub_img.shape[0])
        x = int((top_left[0] + bottom_right[0]) / 2)
        y = int((top_left[1] + bottom_right[1]) / 2)
        if self.__enable_logging:
            self.__logger.info(f"{os.path.basename(img_name)}与{os.path.basename(sub_img_name)}最接近的位置是({x},{y})")
        return x, y

    def d3(self, sleep: float = 1.5):
        start_time = time.time()
        try:
            cur = 0
            while True if self.__max_count == -1 else self.__encore_count < self.__max_count:
                cur += 1
                if self.__enable_logging:
                    self.__logger.info(f"第{cur}次循环")
                sc_path = self.__adb.screenshot(self.__temp_path)
                self._check_encore_and_exec(*self._compare(sc_path, self.__encore_path), sleep=sleep)
                self._check_retire_and_exec(*self._compare(sc_path, self.__retire_path), sleep=sleep)
                time.sleep(sleep)
        except Exception as error:
            if self.__enable_logging:
                self.__logger.warning(f"\n脚本终止：{error}")
        finally:
            try:
                os.remove(self.__temp_path)
            except FileNotFoundError:
                pass
            if self.__enable_logging:
                self.__logger.info(f'''最终局数为{self.__encore_count}，退役次数为{self.__retire_count}
D3脚本结束运行：{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}
脚本运行时长：{time.time() - start_time:.2f}秒''')

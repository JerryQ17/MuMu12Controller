import adb
import time

if __name__ == "__main__":
    print('-' * 50)
    start_time = time.time()
    print("D3脚本开始运行：", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    max_num = 999
    while_num = 0
    again_num = 0
    clean_num = 0
    try:
        opr = adb.Adb(r"E:\MuMuPlayer-12.0\shell\adb.exe")
        while again_num < max_num:
            print('-' * 50)
            while_num += 1
            print("本轮循环次数为", while_num)
            opr.screenshot(r".\image\ScreenShot.png")
            time.sleep(0.5)
            x, y = adb.compare(r".\image\ScreenShot.png", r".\image\clean.png")
            if x == 881 and y == 1024:
                opr.click(x, y)  # 整理
                time.sleep(1.5)

                opr.click(1452, 1349)  # 一键退役
                time.sleep(1.5)

                opr.click(2025, 1292)  # 确定
                time.sleep(1.5)

                opr.click(1583, 995)  # 选择角色有SR以上，确定
                time.sleep(1.5)
                opr.click(1583, 995)
                time.sleep(1.5)

                opr.click(1909, 1108)  # 装备确定
                time.sleep(1.5)

                opr.click(1617, 1149)  # 确定
                time.sleep(1.5)
                opr.click(1617, 1149)
                time.sleep(1.5)

                opr.click(1880, 1335)  # 取消
                time.sleep(1.5)

                opr.click(2467, 1113)  # 自动
                clean_num += 1
                print(f"识别到船坞已满，自动退役舰船，当前退役次数为{clean_num}")
                continue
            x, y = adb.compare(r".\image\ScreenShot.png", r".\image\again.png")
            if (x == 1689 or x == 1829) and y == 1247:
                again_num += 1
                opr.click(x, y)
                print(f"识别到一局游戏结束，自动点击'再次前往'，当前局数为{again_num}")
            else:
                time.sleep(2)
            time.sleep(2)
    except KeyboardInterrupt:
        print(f"\n脚本Ctrl+C终止\n最终局数为{again_num}，退役次数为{clean_num}")
    finally:
        print('-' * 50)
        try:
            import os
            os.remove(r".\image\ScreenShot.png")
        except FileNotFoundError:
            pass
        print("D3脚本结束运行：", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        stop_time = time.time()
        print(f"运行时长：{stop_time - start_time:.2f}秒")
        print('-' * 50)

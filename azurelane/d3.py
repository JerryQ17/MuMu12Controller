import os
import sys

sys.path.append(os.path.abspath(r".."))

import AzureLane

if __name__ == "__main__":
    al = AzureLane.AzureLane(r"E:\MuMuPlayer-12.0\shell\adb.exe", r"..\config\test.pkl", r".\image\retire.png",
                             r".\image\encore.png", enable_logging=True, log_stream=sys.stdout)
    al.d3(5)

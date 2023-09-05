import sys

sys.path.append("../..")

from src.azurelane.assistant import AzureLaneAssistant

if __name__ == "__main__":
    AzureLaneAssistant.run_with_json("config/config.json")

# Backend/ImageWorker.py
from ImageGeneration import GenerateImages
from dotenv import dotenv_values
import sys
import os

# Add root dir to Python path (so `Backend` can be found)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller runtime
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main():
    data_file = resource_path("Frontend/Files/ImageGeneration.data")

    try:
        with open(data_file, "r", encoding="utf-8") as f:
            data = f.read().strip()
    except Exception as e:
        sys.exit(f"Failed to read ImageGeneration.data: {e}")

    if "," not in data:
        sys.exit("Invalid ImageGeneration.data format")

    parts = data.split(",")
    if len(parts) < 2:
        sys.exit("Invalid data structure. Expected: prompt,status[,size]")

    prompt = parts[0].strip()
    status = parts[1].strip().lower()
    size = parts[2].strip() if len(parts) >= 3 else "1024x1024"

    # Prevent accidental re-trigger with "False" or empty prompt
    if status != "true" or prompt.lower() == "false" or not prompt.strip():
        print("Nothing to generate. Exiting...")
        return

    # Reset status BEFORE generation to avoid accidental re-triggering
    try:
        with open(data_file, "w", encoding="utf-8") as f:
            f.write("False, False")
    except Exception as e:
        print(f"Warning: Failed to reset ImageGeneration.data: {e}")

    print(f"Generating Images with size {size} and prompt: {prompt}")
    GenerateImages(prompt, size)

if __name__ == "__main__":
    main()

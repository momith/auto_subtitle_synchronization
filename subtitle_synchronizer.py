import os
import json
import subprocess
from pathlib import Path
import time

WATCH_FOLDERS = os.getenv("WATCH_FOLDERS", "/media/mo/Linux1/PlexData001/Test")
WATCH_FOLDERS = [d.strip() for d in WATCH_FOLDERS.split(",") if d.strip()]
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "10"))

DB_FILE = "synced_sub_files.json"


VIDEO_EXTS = [".mkv", ".mp4", ".avi", ".mov"]
SUB_EXTS = [".srt", ".ass", ".ssa"]


# --- Tracking ---
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        processed_files = json.load(f)  # Dictionary: {filepath: status}
else:
    processed_files = {}

def save_db():
    with open(DB_FILE, "w") as f:
        json.dump(processed_files, f, indent=2)

# --- Processing ---
def find_video_for_sub(sub_path: Path):
    for ext in VIDEO_EXTS:
        candidate = sub_path.with_suffix(ext)
        if candidate.exists():
            return candidate

    videos = []
    for ext in VIDEO_EXTS:
        videos.extend(sub_path.parent.glob(f"*{ext}"))

    if len(videos) == 0:
        return None
    if len(videos) > 1:
        print(f"Multiple videos found for {sub_path}, using first: {videos[0]}")
    return videos[0]

def process_subtitle(sub_path: Path):
    print(f"Processing subtitle {sub_path}")
    status = "success"
    try:
        video_file = find_video_for_sub(sub_path)
        if not video_file:
            print(f"No matching video found for {sub_path}")
            status = "no_video"
        else:
            synced_output = sub_path.with_name(sub_path.stem + "_synced" + sub_path.suffix)
            if synced_output.exists():
                print(f"Already synced: {synced_output} – skipping")
                status = "already_synced"
            else:
                print(f"Running alass on {video_file} + {sub_path}")
                subprocess.run(
                    ["alass", str(video_file), str(sub_path), str(synced_output)],
                    check=True
                )
                print(f"Created synced subtitle: {synced_output}")
    except subprocess.CalledProcessError as e:
        print(f"Error when processing {sub_path}: {e}")
        status = "error"
    finally:
        processed_files[str(sub_path)] = status
        save_db()

# --- Folder scanning ---
def scan_folders():
    for watch_dir in WATCH_FOLDERS:
        for root, dirs, files in os.walk(watch_dir):
            for file in files:
                if any(file.lower().endswith(ext) for ext in SUB_EXTS) and "_synced" not in Path(file).stem:
                    full_path = os.path.abspath(os.path.join(root, file))
                    if full_path not in processed_files:
                        process_subtitle(Path(full_path))

# --- Main ---
if __name__ == "__main__":
    print(f"Watching folders: {WATCH_FOLDERS}")
    while True:
        scan_folders()
        time.sleep(CHECK_INTERVAL)

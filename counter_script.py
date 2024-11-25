from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

class UploadHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            print(f"New file detected: {file_path}")
            process_file(file_path)

def process_file(file_path):
    print(f"Processing file: {file_path}")
    # Example processing logic  (Insert the CV code and datafrane generation here)
    new_path = os.path.join(PROCESSED_FOLDER, os.path.basename(file_path))
    os.rename(file_path, new_path)
    print(f"File moved to: {new_path}")

if __name__ == "__main__":
    event_handler = UploadHandler()
    observer = Observer()
    observer.schedule(event_handler, UPLOAD_FOLDER, recursive=False)
    observer.start()
    print("Monitoring uploads folder with Watchdog...")
    try:
        while True:
            pass  # Keep running
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import cv2
import numpy as np
import pandas as pd

UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
METADATA_FILE = "submissions.csv"
UPDATED_METADATA_FILE = "updated_metadata.csv"
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

class UploadHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            file_path = event.src_path
            print(f"New file detected: {file_path}")
            process_file(file_path)

def process_file(file_path):
    print(f"Processing file: {file_path}")
    
    # Read the image
    image = cv2.imread(file_path)

    # Check if the image was loaded properly
    if image is None:
        print(f"Failed to load image: {file_path}")
        return

    # Convert to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define the range of red color in HSV
    lower_red1 = np.array([0, 50, 50])   # Lower range of red
    upper_red1 = np.array([10, 255, 255])  # Upper range of red
    lower_red2 = np.array([170, 50, 50])  # Lower range for red in higher hue values
    upper_red2 = np.array([180, 255, 255])

    # Create masks for red color
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 + mask2

    # Find contours of the red dots
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Draw bounding boxes around detected dots
    for contour in contours:
        if cv2.contourArea(contour) > 10:  # Filter small noise by area
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # Count the number of red dots
    red_dots_count = len(contours)

    print("Number of red dots:", red_dots_count)

    # Save the processed image to the processed folder
    processed_file_path = os.path.join(PROCESSED_FOLDER, os.path.basename(file_path))
    cv2.imwrite(processed_file_path, image)

    # Move the processed file to the processed directory
   # new_path = os.path.join(PROCESSED_FOLDER, os.path.basename(file_path))
   # os.rename(file_path, new_path)
    #print(f"File moved to: {new_path}")

    # Read the metadata CSV file
    metadata_df = pd.read_csv(METADATA_FILE)

    # Extract the image filename without extension to match the metadata row
    image_name = os.path.splitext(os.path.basename(file_path))[0]

    # Filter to find the row corresponding to the current image
    image_metadata = metadata_df[metadata_df['image_name'] == image_name]

    if not image_metadata.empty:
        # If metadata row exists, update it with the dot count
        image_metadata['dot_count'] = red_dots_count

        # Append the updated row to the updated metadata CSV
        if os.path.exists(UPDATED_METADATA_FILE):
            image_metadata.to_csv(UPDATED_METADATA_FILE, mode='a', header=False, index=False)
        else:
            image_metadata.to_csv(UPDATED_METADATA_FILE, index=False)
        
        print(f"Updated metadata for {image_name} with {red_dots_count} red dots.")
    else:
        print(f"No metadata found for {image_name} in {METADATA_FILE}.")

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



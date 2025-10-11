import cv2
import numpy as np
import pandas as pd
import os

# User-Adjusted Settings
VIDEO_FILE = "../Data/Video_10-10-2025_13-29-22.mp4"
OUTPUT_FILE = "../Data/MergedData_TESTING.csv"
SAVE_DEBUG = False

def measure_diameter(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Detect edges.
    edges = cv2.Canny(blur, 50, 150)

    # Detect contours.
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if len(contours) == 0:
        return None
    
    # Assuming the largest contour is the tube,
    c = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(c)

    # Tube width [pixels]
    return w

def process_video(video_path, output_file, save_debug=False):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Error: Cannot open video {video_path}")
    
    frame_idx = 0
    diameters = []
    out_writer = None

    if save_debug:
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out_writer = cv2.VideoWriter("debug_output.avi", fourcc, 20.0, (
            int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        ))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        d = measure_diameter(frame)
        if d is not None:
            diameters.append(d)
            if save_debug:
                # Drawing rectangle for visualation:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                blur = cv2.GaussianBlur(gray, (5, 5), 0)
                edges = cv2.Canny(blur, 50, 150)
                contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                c = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(c)
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                out_writer.write(frame)
        else:
            diameters.append(np.nan)
        
        frame_idx += 1

    cap.release()
    if out_writer:
        out_writer.release()

    df = pd.DataFrame({"Frame": range(len(diameters)), "Diameter [pixels]": diameters})
    df.to_csv(output_file, index=False)
    print(f"Saved diameters to {output_file}")

if __name__ == "__main__":
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    process_video(VIDEO_FILE, OUTPUT_FILE, SAVE_DEBUG)

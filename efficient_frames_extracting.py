import cv2
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

# Function to process each video
def extract_frames(video_path, video_frames):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}.")
        return

    frame_numbers = video_frames['new_frame_number'].tolist()
    participant = video_frames['participant'].iloc[0]
    session = video_frames['session'].iloc[0]

    for frame_number in frame_numbers:
        # Directly jump to the frame of interest
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = cap.read()
        if not ret:
            break  # Break if the frame can't be read
        frame_filename = f'frames_to_recognize/set{participant}_session{session}_frame_{frame_number}.jpg'
        cv2.imwrite(frame_filename, frame)
        print(f'Saved {frame_filename}')

    cap.release()

# Read the CSV file
frames = pd.read_csv('/Users/varya/Desktop/Julia/frame_numbers_corrected_with_tokens.csv')
set_session = frames.groupby('video_path')

# Use ThreadPoolExecutor to process videos in parallel
with ThreadPoolExecutor(max_workers=4) as executor:  # Adjust max_workers based on your CPU
    for video_path, video_frames in set_session:
        executor.submit(extract_frames, video_path, video_frames)
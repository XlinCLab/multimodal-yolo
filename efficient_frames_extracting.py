# this code extracts frames from videos of a matcher by numbers from the .csv file with corrected target frames
# later we will use them for object recognition

import argparse
import logging
import os
from concurrent.futures import ThreadPoolExecutor

import cv2
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def extract_frames(video_path: str, video_frames: pd.DataFrame, outdir: str = ""):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logger.error(f"Could not open video {video_path}.")
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
        #the frames will be saved in the folder 'frames_to_recognize' in the root folder
        frame_filename = os.path.join(outdir, f'/data/images/set{participant}_session{session}_frame_{frame_number}.jpg')
        frame_dirname = os.path.dirname(frame_filename)
        os.makedirs(frame_dirname, exist_ok=True)
        cv2.imwrite(frame_filename, frame)
        logger.info(f'Saved {frame_filename}')

    cap.release()


def main(input_csv: str, outdir: str, max_workers: int = 4, sep: str = ","):
    # Read the CSV file with corrected frame numbers (at least 5 April tags)
    # path to you root folder (as in Julia pipeline)
    frames = pd.read_csv(os.path.abspath(input_csv), sep=sep)
    set_session = frames.groupby('video_path')

    # Use ThreadPoolExecutor to process videos in parallel
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for video_path, video_frames in set_session:
            executor.submit(extract_frames, video_path, video_frames, outdir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("Extract video frames of interest.")  # TODO improve description
    parser.add_argument('--input_csv', help='Path to input CSV file with (corrected) frame numbers')
    parser.add_argument('--outdir', help='Path to directory where files should be output')
    parser.add_argument('--max_workers', default=4, help='Max workers for parallelization (adjust according to available CPU)')
    args = parser.parse_args()
    main(
        input_csv=args.input_csv, 
        outdir=args.outdir,
        max_workers=args.max_workers
    )

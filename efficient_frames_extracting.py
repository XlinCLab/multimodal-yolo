#!./.venv/bin/python

# this code extracts frames from videos of a matcher by numbers from the .csv file with corrected target frames
# later we will use them for object recognition

import argparse
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import cv2
import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


OUTSUBDIR = "frames"


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
        frame_filename = os.path.join(outdir, OUTSUBDIR, f'set{participant}_session{session}_frame_{frame_number}.jpg')
        frame_dirname = os.path.dirname(frame_filename)
        os.makedirs(frame_dirname, exist_ok=True)
        cv2.imwrite(frame_filename, frame)
        logger.info(f'Saved {frame_filename}')

    cap.release()


def create_outdir(outdir) -> None:
    """Create a new outdir and verify that it will not unintentionally overwrite an existing outdir."""
    if os.path.exists(outdir):
        if os.path.isdir(outdir):
            contents = os.listdir(outdir)
            if OUTSUBDIR in contents and len(os.listdir(os.path.join(outdir, OUTSUBDIR))) > 0:
                logger.warning(f"Specified outdir {outdir} already exists and is not empty!")
                overwrite = ""
                while overwrite not in ["y", "n"]:
                    overwrite = input("Continue? Note that this may overwrite existing data! [Y/N]")
                    overwrite = overwrite.lower().strip()
                    if len(overwrite) > 0:
                        overwrite = overwrite[0]
                if overwrite == "y":
                    os.makedirs(outdir, exist_ok=True)
                else:
                    raise FileExistsError

            else:
                os.makedirs(outdir, exist_ok=True)
        else:
            raise FileExistsError(f"Specified outdir {outdir} already exists and is a file")
    else:
        os.makedirs(outdir)


def main(input_csv: str, outdir: str, max_workers: int = 4, sep: str = ","):
    # Create outdir and check that results will not be accidentally overwritten
    try:
        create_outdir(outdir)
    except FileExistsError as e:
        raise FileExistsError("Aborting. Please rerun with a different specified outdir.") from e

    # Initialize logging to log file
    file_handler = logging.FileHandler(os.path.join(outdir, "frame_extraction.log"))
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    logger.addHandler(file_handler)

    # Read the CSV file with corrected frame numbers (at least 5 April tags)
    # path to you root folder (as in Julia pipeline)
    frames = pd.read_csv(os.path.abspath(input_csv), sep=sep)
    set_session = frames.groupby('video_path')

    # Use ThreadPoolExecutor to process videos in parallel
    futures = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for video_path, video_frames in set_session:
            logger.info(f"Submitting job <extract_frames> with:\n\tvideo_path={video_path}")
            future = executor.submit(
                extract_frames, video_path, video_frames, outdir
            )
            futures[future] = video_path

    for future in as_completed(futures):
        video_path = futures[future]
        try:
            result = future.result()
            logger.info(f"Frame extraction completed successfully for video {video_path}")
        except Exception as e:
            logger.error(f"Frame extraction failed for video {video_path}\nFull error:", e)


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

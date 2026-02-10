# Introduction
This repository contains tools for video frame extraction and `YOLO` computer vision object detection from video frames. It is designed to be used as a component of the `julia` pipeline for the [`multimodal`](https://github.com/XlinCLab/multimodal) project for processing multimodal, naturalistic data from DGAME experiments. See more in the main project's README [here](https://github.com/XlinCLab/multimodal/blob/main/README.md).

# Setup
To use these tools you need to have the following installed on your machine:
- [Docker](https://www.docker.com)
    
    - NB: If using MacOS or Windows, you must explicitly open the Docker or Docker Desktop application before running `docker` commands.
- [Python 3](https://www.python.org/downloads/) [tested with Python 3.12.3]

Provided that these have been installed, the setup script `setup.sh` then creates a Python virtual environment and fetches files in `git lfs` (large file storage, see more detailed instructions below for manual setup). This can be achieved by running the following command:
```bash
./setup.sh && source .venv/bin/activate
```

To reactivate the virtual environment after it has been created the first time:
```bash
source .venv/bin/activate
```

## Downloading weights for pretrained models
Weights for pretrained models are saved using [Git LFS (Large File Storage)](https://git-lfs.com/) in the `models/` directory.

After cloning this repository, make sure Git LFS is installed on your system:
```
git lfs install
```

To fetch and download all LFS-tracked files, run:
```
git lfs fetch --all
git lfs pull
```

You can verify which files are managed by LFS using:
```
git lfs ls-files
```

# Training a new object recognition model
If you want to train your own object recognition model, you will need to annotate around 250 pictures in [YOLO format](https://roboflow.com/formats/yolo), for example using [this annotator from LabelStudio](https://hub.docker.com/r/heartexlabs/label-studio). Run the annotator in Docker using the following commands:
```
docker pull heartexlabs/label-studio:latest

docker run -it -p 8080:8080 -v `pwd`/mydata:/label-studio/data heartexlabs/label-studio:latest
```
Then open http://0.0.0.0:8080/ in a web browser to access the annotator. Note that you may first need to create an account with [LabelStudio](http://0.0.0.0:8080/user/login/).

To train the model on your annotated data, run:
```
docker compose -f docker-compose.train.yml build                                               
docker compose -f docker-compose.train.yml up
```

# Running model components
## Video frames extraction
The [Python frame extraction module](./extract_video_frames.py) is intended to be used after running the [main `multimodal` pipeline's first component](https://github.com/XlinCLab/multimodal?tab=readme-ov-file#part-1-data-preprocessing-identification-of-relevant-time-windows-and-optimal-video-frame-selection) and having generated a `frame_numbers_corrected_with_tokens.csv` file with aggregated data on all timepoints of interest. Typically, these are the timepoints corresponding with the onset of a target object's name pronounced by the "Director". (For more background, see main project's README [here](https://github.com/XlinCLab/multimodal/blob/main/README.md).)

Once this file is ready, pass its path as the `--input_csv` input argument to `extract_video_frames.py`, e.g.
```bash
python extract_video_frames.py --input_csv /path/to/your/frame_numbers_corrected_with_tokens.csv --outdir /path/to/data/output/directory --max_workers 4
```
This script will extract the frames from the videos in parallel (specify more or less parallelization according to your available CPU with the `--max_workers` argument), and save them to a directory `frames` below a specified output directory (`--outdir` argument).

## Object recognition
Ensure your `docker-compose.detect.yml` file has the correct path to the directory containing the extracted frames (`--outdir` argument to the [Python script](#video-frames-extraction)) under the `volumes` section. Likewise, ensure the `docker-compose.detect.yml` file points to the pretrained YOLO model directory, which should contain a `model.yaml` file defining the model's output labels as well as the model's `weights.pt` file produced from model training.

Simply replace `<yourdatadir>` and `<youryolomodel>` with the respective real paths. For example:
```yml
    volumes:
      - /path/to/your/outdir:/data
      - /path/to/your/pretrained/yolo/model:/yolo_model
```

Object positions can then be detected in these video frames using the specified pretrained YOLO computer vision model. To start detection, run the following two commands:

 ```bash
 docker compose -f docker-compose.detect.yml build
 docker compose -f docker-compose.detect.yml up
```

Note that (depending on your machine) running the `build` command may take upwards of 40 minutes to complete. 

This will create a subfolder `yolo_results` within the same directory where the input data are located. The path to this folder is then required for [part 3 of the main `multimodal` pipeline](https://github.com/XlinCLab/multimodal?tab=readme-ov-file#part-3-object-position-detection-and-postprocessing). Within this folder are copies of the input video frames (`.jpg` files) with detected objects labeled and inside bounding boxes, as well as a  `labels` subfolder containing text files with pixel object coordinates for all detected objects in each video frame.

# Video tutorial
See this [this video walkthrough](https://youtu.be/bWNy26O7Sow) for a tutorial/demo and further details by the original author. 

NB: Some details in the video may be outdated due to subsequent code revisions.

# Introduction
This repository has a Python script to extract frames of interest, recognize objects on a DGAME shelf, and get pixel coordinates for each object.
We will get object positions by matching object pixel coordinates to surface coordinates in the main pipeline in Julia.

# Setup
To run the model you need to have the following installed on your machine:
- [Docker](https://www.docker.com)
- [Python 3](https://www.python.org/downloads/)

A setup script is provided which then sets up a Python virtual environment and initializes and pulls files in `git lfs` (large file storage, see more detailed instructions below for manual setup). This can be achieved by running the following command:
```bash
./setup.sh && source .venv/bin/activate
```

To reactivate the virtual environment after it has been created the first time:
```bash
source .venv/bin/activate
```

## Downloading weights for pretrained models
Weights for pretrained models are saved using [Git LFS (Large File Storage)](https://git-lfs.com/) under `pretrained_weights`.

After cloning the repository, make sure Git LFS is installed on your system:
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
The Python frame extraction module is used after you have created the `frame_numbers_corrected_with_tokens.csv` file with the aggregated data on all points of interest that you have in the experiment. Initially, these are moments of the target object onset pronounced by the director. 

Once this file is ready, pass its path as the `--input_csv` input argument to `efficient_frames_extracting.py`, e.g.
```bash
python efficient_frames_extracting.py --input_csv /path/to/your/frame_numbers_corrected_with_tokens.csv --outdir /path/to/data/output/directory --max_workers 4
```
This script will extract the frames from the videos in parallel (specify more or less parallelization according to your available CPU with the `--max_workers` argument), and save them to a directory `frames` below a specified output directory (`--outdir` argument).

Ensure your `docker-compose.detect.yml` file has the correct path to the directory containing these frames (`--outdir` argument to the Python script) under the `volumes` section, e.g.:
```yml
    volumes:
      - /path/to/your/outdir:/data
```
Likewise, ensure the `docker-compose.detect.yml` file points to the (pretrained) weights `.pt` file which model training produced. The simplest way to achieve this is to copy this file into the `pretrained_weights` subfolder of this repo (if not already there), whose contents are automatically mounted as a volume to the Docker container.

## Object recognition
Then object positions can be detected in these video frames using the YOLO computer vision model. Ensure that the `docker-compose.detect.yml` has the right path to the weights for the model and the right path to your folder with the frames.

 To start detection, run the following two commands in the Terminal:

 ```bash
 docker compose -f docker-compose.detect.yml build
 docker compose -f docker-compose.detect.yml up
```

Note that (depending on your machine) running the `build` command may take upwards of 40 minutes to complete. 

This will create a folder `labels` which will contain text files with pixel object coordinates for all objects for all frames. You will then need to insert the path to this folder into the `main.jl` file of the main pipeline.

# Video tutorial
See this [this video walkthrough](https://youtu.be/bWNy26O7Sow) for a tutorial/demo and further details.

# Introduction
This repository has a Python script to extract frames of interest, recognize objects on a DGAME shelf, and get pixel coordinates for each object.
We will get object positions by matching object pixel coordinates to surface coordinates in the main pipeline in Julia.

# Setup
To run the model you need to have installed Docker. Please find the instructions here: https://www.docker.com

## Pretrained model
The weights for the pretrained model are in the `last.pt` file available [here on Google Drive](https://drive.google.com/file/d/1mdHN0H1R7he6FCpdLfH9jY5eXgwWjVr2/view?usp=sharing).

## Training a new model
If you want to train your own model, you will need to annotate around 250 pictures in Yolo format, for example using [this annotator](https://hub.docker.com/r/heartexlabs/label-studio). Run in Docker using the following commands:
```
docker pull heartexlabs/label-studio:latest

docker run -it -p 8080:8080 -v `pwd`/mydata:/label-studio/data heartexlabs/label-studio:latest
```
Then open http://0.0.0.0:8080/ in a web browser and there is your annotator!

## Python setup
To run the Python script, you need to install the dependencies into a virtual environment. To achieve this, run the following command:
```bash
./setup_venv.sh && source .venv/bin/activate
```

# Running model components
## Frames extraction
The Python frame extraction module is used after you have created the `frame_numbers_corrected_with_tokens.csv` file with the aggregated data on all points of interest that you have in the experiment. Initially, these are moments of the target object onset pronounced by the director. 

Once this file is ready, pass its path as the `--input_csv` input argument to `efficient_frames_extracting.py`, e.g.
```
python efficient_frames_extracting.py --input_csv /path/to/your/frame_numbers_corrected_with_tokens.csv --outdir /path/to/data/output/directory --max_workers 4
```
This script will extract the frames from the videos in parallel (specify more or less parallelization according to your available CPU with the `--max_workers` argument), and save them to the folder `/data/images` below a specified output directory (`--outdir` argument).

Ensure your `docker-compose.detect.yml` file has the correct path to these frames (it is by default).

## Object recognition
Then object positions can be detected in these video frames using the YOLO computer vision model. Ensure that the `docker-compose.detect.yml` has the right path to the weights for the model and the right path to your folder with the frames.

 To start detection, run the following two commands in the Terminal:

 ```bash
 docker compose -f docker-compose.detect.yml build
 docker compose -f docker-compose.detect.yml up
```
The commands are also saved in the `commands` file. The first pair of commands is used to train the model, and the second pair (same as above) is used to detect objects with an already trained model.

This will create a folder `labels` which will contain text files with pixel object coordinates for all objects for all frames. You will then need to insert the path to this folder into the `main.jl` file of the main pipeline.

# Video tutorial
See this [this video walkthrough](https://youtu.be/bWNy26O7Sow) for a tutorial/demo and further details.

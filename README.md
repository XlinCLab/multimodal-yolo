This repository has a python script to extract frames of interest, recognize objects on the shelf and get pixel coordinates for each object.
We will get object positions by matching object pixel coordinates to surface coordinates in the main pipeline in Julia.
## Installation
To be able to use the model you would need to install Docker, please find the instructions here:
https://www.docker.com

The weights for the pretrained model are in the last.pt file available here:
((https://drive.google.com/file/d/1mdHN0H1R7he6FCpdLfH9jY5eXgwWjVr2/view?usp=sharing))
If you want to train your own model, you will need to annotate around 250 pictures in Yolo format, you may consider using this annotator for example:
https://hub.docker.com/r/heartexlabs/label-studio
It runs in docker:
 copy the docker pull command, run it in the terminal, then run the container:
    docker pull heartexlabs/label-studio:latest
    docker run -it -p 8080:8080 -v `pwd`/mydata:/label-studio/data heartexlabs/label-studio:latest

go to the http://0.0.0.0:8080/ - and there is you annotator!

To be able to run the python script, you would need to install pandas and OpenCV libraries for Python.

You would have to use this module after you have created the "frame_numbers_corrected_with_tokens.csv" file with the aggregated data on all points of interest that you have in the experiment. Initially these are moments of the target object onset pronounced by the director. 

## Run the frames extraction
When you have this file ready, put the path to it into the "efficient_frames_extracting.py" into thi line at the end of the file:

```python
frames = pd.read_csv('PATH TO YOUR ROOT FOLDER')
```
This script will extract the frames from the videos, the frames will be saved in the folder '/data/images' in the root folder of this module (not in the main pipeline module). Make sure your "docker-compose.detect.yml" file has the correct path to these frames (it is by default).

## Run the object recognition
 Then you will recognize object positions on these frames using YOLO computer vision model. Check if the "docker-compose.detect.yml" has the right path to the weights for the model and the right path to your folder with the frames.

 To start detection, run the following two commands in the Terminal:

 ```bash
 docker compose -f docker-compose.detect.yml build
 docker compose -f docker-compose.detect.yml up
```
The commande are also saved in the "commands" file - the first pair is to train the model, and the second pair (like the above) is to detect objects with a ready model.

 This will create te folder 'labels' for you, with text files having pixel object coordinates for all objects for all frames. You will need then to put the path to thos folder into the 'main.jl' file of the main pipeline.

Detailed explanations in this video walkthrough:
https://youtu.be/bWNy26O7Sow

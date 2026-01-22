# Base Python image
FROM python:3.9-slim

# installing the dependancies 
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# NB: as of January 2026, YOLOv7 has still not been updated to be compatible with PyTorch >=2.6
# Incompatible due to change in weights_only argument for torch.load in torch=2.6
# Modify the requirements.txt line specifying torch and torchivision versions
# to restrict to a version before the incompatibility
# This workaround can be removed if YOLOv7 is updated such that the incompatibility is fixed  
# see for example: https://github.com/WongKinYiu/yolov7/issues/2119
COPY yolov7 /yolov7
WORKDIR /yolov7
RUN sed -i 's|^torch.*|torch>=1.7.0,<2.6.0,!=1.12.0|' requirements.txt \
 && sed -i 's|^torchvision.*|torchvision>=0.8.1,<0.20,!=0.13.0|' requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# install opencv
RUN pip install --no-cache-dir opencv-python-headless

# working directory
WORKDIR /yolov7

# copy the current directory contents into the container at /yolov7
COPY . .

ENTRYPOINT ["python"]

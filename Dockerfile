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
# Explicitly install the desired (compatible versions) and then remove the lines of requirements.txt specifying torch and torchivision versions
# Then install remaining dependencies as normal
# This workaround can be removed if YOLOv7 is updated such that the incompatibility is fixed  
# see for example: https://github.com/WongKinYiu/yolov7/issues/2119
COPY yolov7 /yolov7
WORKDIR /yolov7
RUN pip install --no-cache-dir \
    torch==2.5.0+cpu \
    torchvision==0.20.0+cpu \
    torchaudio==2.5.0+cpu \
    --index-url https://download.pytorch.org/whl/cpu
RUN sed -i '/torch/d;/torchvision/d;/torchaudio/d' requirements.txt \
    && pip install --no-cache-dir -r requirements.txt

# install opencv
RUN pip install --no-cache-dir opencv-python-headless

# working directory
WORKDIR /yolov7

# copy the current directory contents into the container at /yolov7
COPY . .

ENTRYPOINT ["python"]

# Project 1

# Elastic Face Recognition with AWS IaaS

## Overview
This project implements an elastic face recognition application leveraging Infrastructure-as-a-Service (IaaS) provided by Amazon Web Services (AWS). The application dynamically scales based on user request demand, efficiently handling image recognition tasks using a scalable backend infrastructure.

## Architecture
The solution consists of three primary tiers:

### Web Tier
- **Instance:** Single EC2 instance (`web-instance`) acting as an interface for user interactions.
- **Functionality:**
  - Receives image files (`.jpg`) via HTTP POST requests.
  - Forwards images to the App Tier via AWS Simple Queue Service (SQS).
  - Returns recognition results to users as plain text.

### AWS Resources:
- Single EC2 instance named **web-tier-instance**.
- SQS Queues:
  - **<ASU_ID>-req-queue** for sending requests.
  - **<ASU_ID>-resp-queue** for receiving responses.

## App Tier
- Dynamically scales EC2 instances based on request load.
- Performs inference using a provided face recognition deep learning model.

### Autoscaling:
- Managed by a controller implemented within the Web Tier (custom autoscaling logic).
- Scales out when request load increases and scales in when the load decreases.

### EC2 Instances:
- Custom Amazon Machine Image (AMI) pre-installed with:
  - PyTorch
  - torchvision
  - torchaudio
- Instances named sequentially as **app-tier-instance-<#>**.

## Data Persistence
- AWS Simple Storage Service (S3) for persistent storage:
  - **Input Bucket:** Stores images received from users.
  - **Output Bucket:** Stores corresponding face recognition results.

### AWS Buckets:
- **<ASU_ID>-in-bucket**: Stores image files.
- **<ASU_ID>-out-bucket**: Stores classification results.

## Testing & Performance
- Tested using a provided workload generator to simulate user traffic.
- Successfully handled 100 concurrent requests within ~80 seconds (benchmark performance).
- Validated with a provided grading script ensuring full functionality with IAM credentials.

## Technologies Used
- **AWS EC2** for compute resources
- **AWS SQS** for asynchronous message handling
- **AWS S3** for persistent storage
- **PyTorch** for deep learning inference

## Deployment Region
- All AWS resources deployed in **US-East-1**.

---

This project demonstrates the practical use of cloud infrastructure for scalable, real-time face recognition, highlighting the efficient integration and management of AWS services.


---

# Project 2

# Elastic Video Analysis Application using AWS Lambda

## Overview
This project implements an elastic, serverless video-analysis pipeline using AWS Lambda and Amazon S3, leveraging Platform-as-a-Service (PaaS) technologies. The pipeline processes user-uploaded videos by splitting them into frames and performing facial recognition through a multi-stage, auto-scalable cloud architecture.

## Application Workflow

### Stage 1: Video Splitting
- Users upload `.mp4` videos to an S3 input bucket.
- A Lambda function (`video-splitting`) is automatically triggered.
- Each video is processed using FFmpeg to extract a single frame.
- Extracted frames are stored in an intermediate S3 bucket (`stage-1`).

### Stage 2: Face Recognition
- Triggered automatically after Stage 1 completes.
- Utilizes OpenCV for face extraction and ResNet-34 CNN for facial recognition.
- Matches extracted faces against pre-stored embeddings.
- Recognition results (identified names) are saved as text files in the S3 output bucket.

## AWS Infrastructure Components

### AWS Lambda Functions
- **`video-splitting` Function:** Extracts one frame per video using FFmpeg.
- **`face-recognition` Function:** Recognizes faces using ResNet-34 and outputs identification results.

### AWS S3 Buckets
- **Input Bucket (`<ASU ID>-input`):** Stores original uploaded videos.
- **Intermediate Bucket (`<ASU ID>-stage-1`):** Stores JPG frames extracted from videos.
- **Output Bucket (`<ASU ID>-output`):** Stores face recognition results in `.txt` format.

## Key Technologies Used
- **AWS Lambda:** For scalable, event-driven function execution.
- **AWS S3:** Persistent storage for input videos, intermediate images, and recognition outputs.
- **OpenCV:** Face detection and extraction.
- **PyTorch (ResNet-34):** Facial recognition with pre-trained CNN models.
- **FFmpeg:** Video processing and frame extraction.

## Deployment
- Functions deployed within the AWS `us-east-1` region.
- IAM permissions are configured to allow automated grading and streamlined function execution.

## Testing and Validation
- Thoroughly tested using a provided workload generator and automated grading scripts.
- Achieved end-to-end processing of 100 concurrent video requests within performance benchmarks.

---

This project demonstrates proficiency with serverless computing, scalable architecture, and advanced video-processing techniques within the AWS cloud ecosystem.



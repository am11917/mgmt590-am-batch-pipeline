# mgmt590-am-batch-pipeline
# Containerized batch pipeline using DockerHub and Pachyderm
## About this Repository
This repository contains the pipeline specifications and code for making batch pipelines for the processing the data using the [Hugging  Face Transformers](https://huggingface.co/models) based question answer models.

## Purpose
This repository contains the batch processing pipeline which runs on pachyderm.
 
### Pipeline 1 : Download the csv files placed on Google Cloud Storage Bucket 
The CSVs uploaded on the GCS bucket contains a list of questions and contexts. The pipeline after downloading the files, processes these question and context pairs to infer the answers using the default BERT model of the transformers library. Answers of these questions and context pairs are appended to the CSV and the file is written to the Pachyderm File System's output directory.

### Pipeline 2: Push the answers inferred by first pipeline to a PostgreSQL database on GOOGLE CLOUD 
The goal of this pipeline is to store the information processed by the pipeline into a relational database i.e. PostgreSQL database.
The pipeline automates the data storage process by picking up the files committed by the first pipeline post successful answer inference.

Below is a high-level diagram to show how the pipelines fit in the overall framework:</br>

![image](https://user-images.githubusercontent.com/69768815/121788467-78ae7280-cb9b-11eb-9956-ca049685f0d9.png)

### Pipeline 1 Operation:
![image](https://user-images.githubusercontent.com/69768815/121788843-d09aa880-cb9e-11eb-912d-6b0f412187f5.png)
Based on the diagram its clear that this pipeline takes multiple .csv files as an input, processes them using the available Hugging Face models and generates the respective answers as an output. The pipeline is pushed in a docker container and the docker container is referenced in the pachyderm pipeline. We also store the secrets for authenticated requests to the GCS bucket in the pachyderm pipeline. Output is stored in '/pfs/out/' - temporary directory before being committed to the output repository of the pipeline.

### Pipeline 2 Operation: 
![image](https://user-images.githubusercontent.com/69768815/121789032-6edb3e00-cba0-11eb-823d-89950cb3b604.png)
Based on the diagram its clear that this pipeline takes output files as input from the question_answer repository of pachyderm pipeline 1, processes them and inserts the records of the files in PostgreSQL database on Google Cloud. The secrets to connect to PostgreSQL are stored in the pachyderm pipeline. Files are then moved from the input <pipeline 1> repository to the output repository of pipeline 2.

## Deploying these pipelines by yourself

### Prerequisites 
- All the prerequisites for building the REST API pipeline. [Prerequisities](https://github.com/am11917/mgmt590-am-rest-api)
- Must have a valid account on dockerhub 
- Must have a google cloud storage already set up 
- Must have access to pachyderm - [Pachyderm](https://hub.pachyderm.com/landing)

### Below are the steps to deploy your pipelines via Pachyderm:
Once the above pre-requisites are confirmed ,checkout this repository and proceed as below:
### 1. Build and deploy the docker images to DockerHub
- Add secret DOCKERHUB_USERNAME = <Your dockerhub username> in github secrets
        - Add secret DOCKERHUB_TOKEN = <Your dockerhub access token> in github secrets </br>
```Note: Acces tokens can be generated from the docker hub security settings``` [DockerHub](https://hub.docker.com/settings/security)
- Change your ``<your-dockerhub-username>/<docker-imaeg-name>`` in  .github/workflows/main.yml </br>
  ``` 
      name: Build and push
      run: |-
        cd pachyderm_01 && docker build -t <your-dockerhub-username>/<docker-imaeg-name>:${{  github.sha }} .
        docker push <your-dockerhub-username>/<docker-imaeg-name>:${{  github.sha }} && cd ../
        cd pachyderm_02 && docker build -t <your-dockerhub-username>/<docker-imaeg-name>:${{  github.sha }} .
        docker push <your-dockerhub-username>/<docker-imaeg-name>:${{  github.sha }}
   
   ```
### 2. Create pachyderm workspace
#### 2.1 Sign-in to Pachyderm
#### [Link to Pachyderm](https://hub.pachyderm.com/landing)
#### 2.2 Create a new workspace as shown below
   <img width="309" alt="1" src="https://user-images.githubusercontent.com/84465734/121768778-fb98e400-cb2d-11eb-91c4-46e1946636f2.PNG">
        
#### 2.3 Install pachctl on your machine
     The pachctl or pach control is a command line tool that you can use to interact with a Pachyderm cluster in your terminal. For a Debian based Linux 64-bit or Windows 10
        or later running on WSL run the following code:
        
   ```
   curl -o /tmp/pachctl.deb -L https://github.com/pachyderm/pachyderm/releases/download/v1.13.2/pachctl_1.13.2_amd64.deb && sudo dpkg -i /tmp/pachctl.deb
   ```
   For macOS use the below command:
   ```
   brew tap pachyderm/tap && brew install pachyderm/tap/pachctl@1.13
   ```
   For all other Linux systems use below command:
   ```
   curl -o /tmp/pachctl.tar.gz -L https://github.com/pachyderm/pachyderm/releases/download/v1.13.2/pachctl_1.13.2_linux_amd64.tar.gz && tar -xvf /tmp/pachctl.tar.gz -C /tmp && sudo cp /tmp/pachctl_1.13.2_linux_amd64/pachctl /usr/local/bin
   ```
#### 3. Connect to your Pachyderm workspace
   Click "Connect" on your Pachyderm workspace and follow the below listed steps to connect to your workspace via the machine:
   
   <img width="306" alt="2" src="https://user-images.githubusercontent.com/84465734/121769024-50892a00-cb2f-11eb-8546-97b039618abb.PNG">
    
#### 4. Create a new pachctl repo using the below command
   ```
    pachctl create repo <<repo-name-here>>
   ```
#### 5. Verify that the repo was created using the below command
```
    pachctl list repo
```
An output like below listing the new repo should be generated:
    
    <img width="309" alt="4" src="https://user-images.githubusercontent.com/84465734/121769279-b0cc9b80-cb30-11eb-9171-04baba75e032.PNG">
    
#### 6. Now add data to Pachyderm using the command like shown below
   ```
   pachctl put file images@master:liberty.png -f http://imgur.com/46Q8nDz.png
   ```
   Here "images" is the repo name and "masters" is the branch name, therefore those need to be changed appropriately. Similarly the link/path to the datais (which is the part    after -f) should be updated as well.
   
#### 7. Create your JSON pipeline spec like the one shown below for each of the two pipelines
  ```{
  "pipeline": {
    "name": "edges"
  },
  "description": "A pipeline that performs image edge detection by using the OpenCV library.",
  "input": {
    "pfs": {
      "glob": "/*",
      
      "repo": "images"
    }
  },
  "transform": {
    "cmd": [ "python3", "/edges.py" ],
    "image": "pachyderm/opencv"
  }
}
```
Refer to [this helpful tutorial](https://docs.pachyderm.com/latest/getting_started/beginner_tutorial/) to make your pipeline spec. 
#### 8. Create your pipeline 
Following is a template command to make your pipeline
 
```
pachctl create pipeline -f https://raw.githubusercontent.com/pachyderm/pachyderm/1.13.x/examples/opencv/edges.json
```
or 
```
pachctl create pipeline -f pipeline_spec1.json     
```

#### 9. Output of Pipeline on Pachyderm Dash
        

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

### Architecture of the Product
![image](https://user-images.githubusercontent.com/69768815/121792053-80334300-cbbe-11eb-93cb-6f621b7cf14e.png)

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
- Any docker container image would contain your code to download file from GCS bucket and read it to answer the questions using the context and default hugging face model.
- Docker file that would tell the commands to run during the docker image build. Sample docker file
```
FROM python

ADD requirements.txt .

RUN pip install -r requirements.txt

COPY question_answer.py /app/question_answer.py
```
- Add secret DOCKERHUB_USERNAME = ``<Your dockerhub username>`` in github secrets
- Add secret DOCKERHUB_TOKEN = <Your dockerhub access token> in github secrets </br>
```Note: Acces tokens can be generated from the docker hub security settings``` [Generate Access Tokens](https://hub.docker.com/settings/security)
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
   
   ![image](https://user-images.githubusercontent.com/69768815/121792149-67775d00-cbbf-11eb-92b6-afd91f01bdb1.png)

    
#### 4. Create a new repository using pachctl command 
```
    pachctl create repo <<repo-name-here>>
   ```
#### 5. Configure Secrets in Pachyderm
Once we are connected to pachyderm, we need to configure the secrets that would authenticate the connection between Pachyderm Kubernetes cluster and your Google Cloud applications - GCS bucket and PostgreSQL </br>
   - Create environment variables in the terminal/linux or cloud shell you are using to connect to pachyderm</br>
   - Run the following commands to create the environment variables </br>
     
```
     EXPORT PG_HOST= <<host_address for PostgreSQL>>
     EXPORT PG_USER= <<user_name>>
     EXPORT PG_PASSWORD= <<password>>
     EXPORT PG_DBNAME= <<database_name>>
     EXPORT PG_SSLROOTCERT= <<Path to SSL server-ca.pem>>
     EXPORT PG_SSLCLIENT_CERT= <<Path to SSL client-cert.pem>>
     EXPORT PG_SSL_CLIENT_KEY= <<Path to SSL client-key.pem>>
     EXPORT GOOGLE_APPLICATION_CREDENTIALS= <<Path to the service account credentials.json>>
```
   - Once the environment variables are created, we'll encode those and create a secret.json that will be deployed to pachyderm
   - Template for the secret.json
```
{
   "apiVersion": "v1",
   "kind": "Secret",
   "metadata": {
      "name": "gcsaccess"
   },
   "type": "Opaque",
   "stringData": {
      "creds": "REPLACE_GCS_CREDS"
   }
}

```
  - Next step would be to replace the environment variables into the secret.json which we'll do with this bash script
```

#!/bin/bash

# Make a copy of our secrets template
cp secret_template.json secret.json
cp secret_template_db.json secret_db.json

# Encode our GCS creds
GCS_ENCODED=$(cat $GOOGLE_APPLICATION_CREDENTIALS | base64 -w 0)

# Substitute those creds into our secrets file
sed -i -e 's|'REPLACE_GCS_CREDS'|'"$GCS_ENCODED"'|g' secret.json
sed -i -e 's|'REPLACE_STORAGE_BUCKET'|'"$STORAGE_BUCKET"'|g' secret.json

# Encode our SSL certs
SSLROOTCERT_ENCODED=$(cat $PG_SSLROOTCERT | base64 -w 0)
SSLCERT_ENCODED=$(cat $PG_SSLCERT | base64 -w 0)
SSLKEY_ENCODED=$(cat $PG_SSLKEY | base64 -w 0)

# Substitute those creds into our secrets file
sed -i -e 's|'REPLACE_PG_HOST'|'"$PG_HOST"'|g' secret_db.json
sed -i -e 's|'REPLACE_PG_PASSWORD'|'"$PG_PASSWORD"'|g' secret_db.json
sed -i -e 's|'REPLACE_PG_DBNAME'|'"$PG_DBNAME"'|g' secret_db.json
sed -i -e 's|'REPLACE_PG_USER'|'"$PG_USER"'|g' secret_db.json
sed -i -e 's|'REPLACE_PG_SSLROOTCERT'|'"$SSLROOTCERT_ENCODED"'|g' secret_db.json
sed -i -e 's|'REPLACE_PG_SSLCERT'|'"$SSLCERT_ENCODED"'|g' secret_db.json
sed -i -e 's|'REPLACE_PG_SSLKEY'|'"$SSLKEY_ENCODED"'|g' secret_db.json

# Create our secrets
pachctl create secret -f secret.json
pachctl create secret -f secret_db.json

```
   - This creates and deploys the secret.json and secret_db.json required for the pipeline's authentication with Google Cloud

#### 6. Now you need to create the pipeline specification JSON that will create a DAG in Pachyderm and run the Pipelines

There are two pipelines that needs to be created and the specification json for both the pipelines is given below
##### Pipeline 1 - Pull Files from GCS and Answer Questions
  - You can see that the secrets we created in the previous step are being called here in the pipeline specification as well.
  - We are referring to the docker images we pushed in the first step as our image
```
  {
   "pipeline":{
      "name":"question_answer"
   },
   "description":"A pipeline that dowloads files from GCS and answers questions.",
   "transform":{
      "cmd":[
         "/bin/bash"
      ],
      "stdin":[
         "echo $GCS_ACCESS > /app/rawcreds.txt",
         "base64 --decode /app/rawcreds.txt > /app/creds.json",
         "export GOOGLE_APPLICATION_CREDENTIALS=/app/creds.json",
         "python /app/question_answer_pd.py"
      ],
      "image":"am11917/mgmt590-gcs:4050f86d6f99a184ffe53d55f6972ff675d1ed76",
      "secrets":[
         {
            "name":"gcsaccess",
            "env_var":"GCS_ACCESS",
            "key":"creds"
         },
                 {
            "name":"gcsaccess",
            "env_var":"STORAGE_BUCKET",
            "key":"storage_bucket"
         }
      ]
   },
   "input":{

            "cron":{
               "name":"tick",
               "spec":"@every 60s"
            }


   }
}  
```
##### Pipeline 2 - Push Answers to SQL
  - You can see that the secrets we created in the previous step are being called here in the pipeline specification as well.
  - We are referring to the docker images we pushed in the first step as our image
```
{
   "pipeline":{
      "name":"push-answers-to-sql"
   },
   "description":"A pipeline that pushes answers to the database",
   "transform":{
      "cmd":[
         "python",
         "/app/answer_insert.py"
      ],
      "image":"am11917/mgmt590-db:f181c0c64dc1907b6f963ed6eace6ad4798f1865",
      "secrets":[
         {
            "name":"dbaccess",
            "env_var":"PG_HOST",
            "key":"host"
         },
         {
            "name":"dbaccess",
            "env_var":"PG_PASSWORD",
            "key":"password"
         },
         {
            "name":"dbaccess",
            "env_var":"PG_USER",
            "key":"user"
         },
         {
            "name":"dbaccess",
            "env_var":"PG_DBNAME",
            "key":"dbname"
         },
         {
            "name":"dbaccess",
            "env_var":"PG_SSLROOTCERT",
            "key":"sslrootcert"
         },
         {
            "name":"dbaccess",
            "env_var":"PG_SSLCLIENT_CERT",
            "key":"sslcert"
         },
         {
            "name":"dbaccess",
            "env_var":"PG_SSL_CLIENT_KEY",
            "key":"sslkey"
         }
      ]
   },
   "input":{
      "pfs":{
         "repo":"question_answer",
         "glob":"/"
      }
   }
}

```
    
#### 6. Create Pipeline from Spec JSON
Once the specification json is created, we will now create the pipelines
   ```
   pachctl create pipeline -f pipeline1.json
   pachctl create pipeline -f pipeline2.json
   ```
Refer to [this helpful tutorial](https://docs.pachyderm.com/latest/getting_started/beginner_tutorial/) to make your pipeline spec. 

#### 7. Output of Pipeline on Pachyderm Dash
  - Pipelines on Dashboard </br>
![image](https://user-images.githubusercontent.com/69768815/121792043-65f96500-cbbe-11eb-9341-fe85e5f72b98.png)
  - Logs of the running jobs </br>
![image](https://user-images.githubusercontent.com/69768815/121792458-f3d74f00-cbc2-11eb-93a7-86a199b70c59.png)

# Hope you'll be able to easily replicate the process of creating this batch processing pipeline
# Reach out to me in case of any questions or concerns

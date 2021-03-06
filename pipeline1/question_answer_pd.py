import pandas as pd
import os
import io
from io import BytesIO
import time
import logging
from google.cloud import storage
from transformers.pipelines import pipeline

#initizalizing the distilled-bert model
hg_comp = pipeline('question-answering', model="distilbert-base-uncased-distilled-squad", tokenizer="distilbert-base-uncased-distilled-squad")

# function to read file from input directory
# answer the questions and write it to output directory
def question_answer(fileName, data):
   
    answer_intmd = []
    df_intmd = pd.DataFrame()
    df_final = pd.DataFrame()
    print("file_read")
    # reading the content of the file in pandas df
    df = pd.read_csv(io.BytesIO(data), encoding = 'utf-8',sep = ',')
    print("file_aded to intmd")
    df_intmd = df_intmd.append(df,ignore_index = True)
    #processing every row of the file and getting question and answer
    for fileName,row in df.iterrows():
        context = row['context']
        question = row['question']
        answer = hg_comp({'question': question, 'context': context})['answer']
        answer_intmd.append(answer)

    df_final['context'] = df_intmd['context']
    df_final['question'] = df_intmd['question']
    df_final['answer'] = answer_intmd
    timestamp = str(int(time.time()))
    print("writing file to location")
    #writing the output to the /pfs/out/ repository which will commit it to the pipeline repo
    df_final.to_csv("/pfs/out/question_answer_"+timestamp+".csv", index=False, header=True,  encoding="utf-8")
    
if __name__ == '__main__':
    #connecting with GCS bucket
    bucket_name = os.environ.get('STORAGE_BUCKET')
    print("bucket_name")
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(bucket_name)
    print("Downloading Files")
    #listing the files in the bucket
    files = bucket.list_blobs()
    
    #looping to read through the list of files generated from the gcs bucket
    fileList = [file.name for file in files if '.' in file.name]
    for fileName in fileList:
        print("Inside the File List Loop")
        am_blob = bucket.blob(fileName)
        print("Blob Created")
        #downloading the content of the csv file
        data = am_blob.download_as_string()
        print("File Downloaded as string")
        print("Calling the Question Answer Function")
        question_answer(fileName,data)
        print("question_answer completed")
        print("calling delete function")
        bucket.delete_blob(fileName)
        print("delete completed")

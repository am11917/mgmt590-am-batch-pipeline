import os
import io
from io import BytesIO
from transformers.pipelines import pipeline
from google.cloud import storage
import pandas as pd

hg_comp = pipeline('question-answering', model="distilbert-base-uncased-distilled-squad", tokenizer="distilbert-base-uncased-distilled-squad")

storage_client = storage.Client()
bucket = storage_client.get_bucket('mgmt590-prd-file-upload')

files = bucket.list_blobs()
fileList = [file.name for file in files if '.' in file.name]

answer_intmd = []
df_intmd = pd.DataFrame()
df_final = pd.DataFrame()
for fileName in fileList:
    am_blob = bucket.blob(fileName)
    data = am_blob.download_as_string()
    df = pd.read_csv(io.BytesIO(data), encoding = 'utf-8',sep = ',')
    df_intmd = df_intmd.append(df,ignore_index = True)
    bucket.delete_blob(fileName)
    for fileName,row in df.iterrows():
        context = row['context']
        question = row['question']
        answer = hg_comp({'question': question, 'context': context})['answer']
        answer_intmd.append(answer)
#print(answer_li)
df_final['context'] = df_intmd['context']
df_final['question'] = df_intmd['question']
df_final['answer'] = answer_intmd
df_final.to_csv("pfs/out/answers.csv", index=False, header=True)

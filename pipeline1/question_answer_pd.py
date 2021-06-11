import pandas as pd
import os
import time
from transformers.pipelines import pipeline

# function to read file from input directory
# answer the questions and write it to output directory
def question_answer(qa_file):
    #importing the file using pandas library
    data = pd.read_csv(qa_file)
   
    hg_comp = pipeline('question-answering', model="distilbert-base-uncased-distilled-squad", tokenizer="distilbert-base-uncased-distilled-squad")
    answer = []
    score = []
    questions = []
    for idx, row in data.iterrows():
        context = row['context']
        question = row['question']
        questions.append(question)
        answer.append(hg_comp({'question': question, 'context': context})['answer'])
        score.append(hg_comp({'question': question, 'context': context})['score'])
    
    data["answer"] = answer
    timestamp = str(int(time.time()))
    data.to_csv('/pfs/out/'+"question_answer"+timestamp+".csv", index=False)    

    
# walk /pfs/question_answer and call question_answer on every file found
for dirpath, dirs, files in os.walk("/pfs/question"):
   for name in files:
       print("We are looping in the files")
       print("File Name: "+name)
       print(os.path.join(dirpath,name))
       question_answer(os.path.join(dirpath,name))

    

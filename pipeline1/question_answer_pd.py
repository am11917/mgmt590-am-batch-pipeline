import pandas as pd
import os
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
    data.to_csv('/pfs/question_answer/'+qa_file, index=False)    

    
# walk /pfs/question_answer and call question_answer on every file found
for dirpath, dirs, files in os.walk("/pfs/question"):
   for file in files:
       question_answer(os.path.join(dirpath, file))

    

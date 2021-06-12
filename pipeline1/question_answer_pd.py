import csv
import os
import time
from transformers.pipelines import pipeline

# function to read file from input directory
# answer the questions and write it to output directory
def question_answer(qa_file):
    #importing the file using pandas library
    #data = pd.read_csv(qa_file)
    final_answer = []
       
    hg_comp = pipeline('question-answering', model="distilbert-base-uncased-distilled-squad", tokenizer="distilbert-base-uncased-distilled-squad")
    answer = []
    questions = []
    contexts = []
    
    with open(qa_file,'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            context = row['context']
            question = row['question']
            answer.append(hg_comp({'question': question, 'context': context})['answer'])
            questions.append(question)
            contexts.append(context)
        final_answer.append(questions)
        final_answer.append(contexts)
        final_answer.append(answer)
        print (final_answer)
    #for idx, row in data.iterrows():
    #    context = row['context']
    #    question = row['question']
    #    questions.append(question)
    #    answer.append(hg_comp({'question': question, 'context': context})['answer'])
    timestamp = str(int(time.time()))
    with open('/pfs/out/'+"question_answer_"+timestamp+".csv","wb") as f:
        fileWriter = csv.writer(f, delimiter=',')
        for row in zip(*final_answer):
            fileWriter.writerow(row)
 
    
    #data["answer"] = answer
    #data.to_csv("/pfs/out/"+"question_answer"+timestamp+".csv", index=False)    

    
# walk /pfs/question_answer and call question_answer on every file found
for dirpath, dirs, files in os.walk("/pfs/question"):
   for file in files:
       print("We are looping in the files")
       print("File Name: "+file)
       print(os.path.join(dirpath,file))
       question_answer(os.path.join(dirpath,file))

    

import time
import os
import stat
import psycopg2
import datetime
from datetime import timezone
import pandas as pd
import base64
import shutil

def insert_records (conn, question, answer, context, model_name):
    #create an sql cursor for execution of sql queries    
    cur = conn.cursor()
    #convert unix epoch timestamp into YYYY-MM-DD HH:MM:SS format for inserting into table
    timestamp = round(time.time())
    time_struct = time.localtime(timestamp) # get struct_time
    time_string = time.strftime("%Y-%m-%d %H:%M:%S", time_struct)
    #insert command
    insert_cmd = ('''insert into question_answer(question,answer,context,model,qa_timestamp) values (%s,%s,%s,%s,%s)''')    
    qa_pair = (question,answer,context,model_name,time_string)
    #execute the insert command
    cur.execute(insert_cmd, qa_pair)
    #commit the changes in database
    conn.commit()
    #return the timestamp of insertion of record in table to show as output
    return timestamp

def create_connection (dbconnect):
    conn = None
    try:
        print("Initiating the connnection")
        conn = psycopg2.connect(dbconnect)
        print("Connection created to Postgres")
    except Error as e:
        print(e)
    
    return conn
    

if __name__ == '__main__':

    sslmode="sslmode=verify-ca"
    
    if not os.path.exists('.ssl'):
        os.makedirs('.ssl')
    
    filecontents = os.environ.get('PG_SSLROOTCERT')
    decoded_sslrootcert = base64.b64decode(filecontents)
    with open('.ssl/server-ca.pem', 'wb') as f:
        f.write(decoded_sslrootcert)
    
    filecontents = os.environ.get('PG_SSLCLIENT_CERT')
    decoded_sslclientcert = base64.b64decode(filecontents)
    with open('.ssl/client-cert.pem', 'wb') as f:
        f.write(decoded_sslclientcert)
    
    filecontents = os.environ.get('PG_SSL_CLIENT_KEY')
    decoded_sslclientkey = base64.b64decode(filecontents)
    with open('.ssl/client-key.pem', 'wb') as f:
        f.write(decoded_sslclientkey)
           
    os.chmod(".ssl/server-ca.pem", 0o600)
    os.chmod(".ssl/client-cert.pem", 0o600)
    os.chmod(".ssl/client-key.pem", 0o600)
    hostaddr="hostaddr={}".format(os.environ.get('PG_HOST'))
    port="port=5432"
    user="user={}".format(os.environ.get('PG_USER'))
    dbname="dbname={}".format(os.environ.get('PG_DBNAME'))
    password="password={}".format(os.environ.get('PG_PASSWORD'))
    
    sslrootcert="sslrootcert=.ssl/server-ca.pem"
    sslcert="sslcert=.ssl/client-cert.pem"
    sslkey="sslkey=.ssl/client-key.pem"
    
    dbconnect = " ".join([
    sslmode,
    sslrootcert,
    sslcert,
    sslkey,
    hostaddr,
    port,
    user,
    password,
    dbname
    ])
    
    # connect to db
    print("Starting the connection to SQL")
    conn = create_connection(dbconnect)
    
    for dirpath, dirs, files in os.walk("/pfs/question_answer"):
        for file in files:
            print("We are looping in the files")
            print("File Name: "+file)
            data = pd.read_csv(os.path.join(dirpath,file))
            for idx, row in data.iterrows():
                context = row['context']
                question = row['question']
                answer = row['answer']
                model_name='distilled-bert'
                print("inserting records into the table")
                insert_records(conn, question, answer, context,model_name) 
                print("Insert records successful")
            shutil.move(os.path.join(dirpath,file), '/pfs/out/'+file)
            print("File successfully moved to: "+"/pfs/out/"+file+" location")

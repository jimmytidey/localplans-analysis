
import PyPDF2
import os, json,re,hashlib
import psycopg2
from psycopg2 import extras
from nltk.tokenize import sent_tokenize
from langchain.embeddings import SentenceTransformerEmbeddings
import pprint

def pdf_to_text(source_pdf_folder_path, file_name):

    try:
        source_file_path = source_pdf_folder_path + "/" + file_name
  
        with open(source_file_path, 'rb') as pdf_file:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Initialize an empty string to store the text
            text = ''
            
            # Iterate through each page of the PDF
            for page_num in range(len(pdf_reader.pages)):
                # Get the page object
                page = pdf_reader.pages[page_num]
                
                # Extract text from the page
                text += page.extract_text()
            
            print('finished reading')
            print(text[0:20])   
            return text

    except Exception as e: 
        print(file_name)
        print(e)

def chunk_embed_send_to_db(text, filename, metadata):
   

    # Split text
    split_texts_list = sent_tokenize(text)

    # Only keep sentences with more than 6 words
    proper_sentences = [i for i in split_texts_list if i.count(" ") >= 6]
    print("Number of sentences", len (proper_sentences))
    print('sentences')
    pprint.pprint(proper_sentences)

    # Group sentences into triplets
    n = 3  # group size
    m = 2  # overlap size
    triplets = [
        " ".join(proper_sentences[i: i + n])
        for i in range(0, len(proper_sentences), n - m)
    ]
    pprint.pprint(triplets)

    print('number of triplets ', len(triplets)) 
    # Truncate triplets to 1000 characters
    triplets_trucated = [i[:1000] for i in triplets][0:100]

    print('number of triplets truncated', len(triplets_trucated)) 
    pprint.pprint(triplets_trucated)
    # Insert into Postgres
    postgres_connection = Postgres()
    embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    print('inserting text fragments into db...')

    batch_size = 10
    text_batches = [triplets_trucated[x:x+batch_size] for x in range(0, len(triplets_trucated), batch_size)]
   
    print("number of batches", len(text_batches))
    print("First batch length", len(text_batches[0]))

    for text_batch in text_batches:
        print("Text batch", text_batch)
        print("Text batch length", len(text_batch))
    
    for text_batch in text_batches[5]:
        text_fragments = []
        for text in text_batch[5]:
            vector = embedding_model.embed_documents(text)
            hash = hashlib.sha256(text.encode()).hexdigest()
            text_fragments.append((text, text, metadata, vector, filename, hash))
            print("Text fragment batch", text_fragments[0:5])
            print('...')
            print("Text fragment batch", text_fragments[-5:])

        #postgres_connection.insert_text_fragments(text_fragments)


class Postgres:

    def __init__(self):
        try:
            DATABASE_URL = os.environ["DATABASE_URL"]
            self.conn = psycopg2.connect(DATABASE_URL, sslmode="require")

        except psycopg2.Error as e:
            print("Error:", e)

    def query(self, query):
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            self.conn.close()
            return result

        except psycopg2.Error as e:
            print("Error:", e)

    def insert_text_fragments(self, batch):

        try:
            cursor = self.conn.cursor()
            print("Inserting text fragment", batch[0:10])           
            #interpolated_query = cursor.mogrify(insert_query, (text, text, json.dumps(metadata), vector[0], filename, hash))
            #print("Interpolated SQL query:", interpolated_query.decode("utf-8"))  
            cursor.execute(insert_query, (text, text,json.dumps(metadata),vector[0],filename, hash))
            extras.execute_batch(cursor, insert_query, batch)
            self.conn.commit()
            cursor.close()

        except psycopg2.Error as e:
            print("Error:", e)

    def close(self):
        self.conn.close()



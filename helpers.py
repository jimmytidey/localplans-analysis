
import PyPDF2
import os, json,re,hashlib, pprint
import psycopg2
from psycopg2 import extras
from nltk.tokenize import sent_tokenize
from langchain.embeddings import SentenceTransformerEmbeddings
import pprint

from unstructured.partition.pdf import partition_pdf
from unstructured.chunking.title import chunk_by_title
from unstructured.cleaners.core import clean
import nltk
import ssl,re

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt')    

def pdf_to_chunks(file_path): 
    elements = partition_pdf(filename=file_path, strategy='fast', url=None)
    
    chunks = chunk_by_title(elements, max_characters=1000)
    total_word_count = 0 
    for chunk in chunks:
        words = chunk.text.split()
        word_count = len(words) 
        total_word_count += word_count
    print("total wordcount after chunking " + str(total_word_count))    

    print(chunks[5].text)
    return chunks 
    

def embed_send_to_db(chunks, filename, metadata):
   
    print('inserting text fragments into db...')

    #Batch 
    batch_size = 10
    chunk_batches = [chunks[x:x+batch_size] for x in range(0, len(chunks), batch_size)]

    pg = Postgres()
    embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")


    for chunk_batch in chunk_batches:
        text_fragments = []
        for chunk in chunk_batch:
            clean_text = clean(chunk.text,extra_whitespace=True, dashes=True,bullets=True,trailing_punctuation=True)
            vector = embedding_model.embed_documents(clean_text)
            hash = hashlib.sha256(clean_text.encode()).hexdigest()
            text_fragment = (clean_text, clean_text, metadata, vector[0], filename, hash)
            text_fragments.append(text_fragment)
    
            pprint.pp((clean_text,metadata, vector[0][0:3], filename, hash))

        pg.insert_text_fragments(text_fragments)

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
            insert_query = "INSERT INTO text_fragments (plain_text, full_text, metadata, vector, filename, hash) VALUES (%s, to_tsvector('english', %s), %s, %s, %s, %s)"     
            #interpolated_query = cursor.mogrify(insert_query, (text, text, json.dumps(metadata), vector, filename, hash))
            #print("Interpolated SQL query:", interpolated_query.decode("utf-8"))  
            extras.execute_batch(cursor, insert_query, batch)
            self.conn.commit()
            cursor.close()

        except psycopg2.Error as e:
            print("Error:", e)

    def close(self):
        self.conn.close()


def list_files(path):
    # Get the list of entries in the directory
    entries = os.listdir(path)

    # Filter out only files
    files = [entry for entry in entries if os.path.isfile(os.path.join(path, entry))]

    return sorted(files) 

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



def plain_text_chunker():

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


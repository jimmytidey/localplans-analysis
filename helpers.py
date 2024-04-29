
import PyPDF2
import os, json,re,hashlib
import psycopg2
from nltk.tokenize import sent_tokenize
from langchain.embeddings import SentenceTransformerEmbeddings

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
    cleaner_string = text.replace("\n", " ").replace("\r", "")

    clean_string = re.sub("\s\s+", " ", cleaner_string)

    # Split text
    split_texts_list = sent_tokenize(clean_string)

    # Only keep sentences with more than 6 words
    proper_sentences = [i for i in split_texts_list if i.count(" ") >= 6]

    print("number of sentences to embed")
    print(len(proper_sentences))

    # Group sentences into triplets
    n = 3  # group size
    m = 2  # overlap size
    triplets = [
        " ".join(proper_sentences[i: i + n])
        for i in range(0, len(proper_sentences), n - m)
    ]

    # Truncate triplets to 1000 characters
    triplets_trucated = [i[:1000] for i in triplets]

    # Insert into Postgres
    postgres_connection = Postgres()
    for triplet in triplets_trucated:
        postgres_connection.insert_text_fragment(
            triplet, filename, metadata=metadata
        )    


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

    def insert_text_fragment(self, text, filename, metadata):
        print("Inserting text fragment", text[:100])
        embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        vector = embedding_model.embed_documents(text)
        hash = hashlib.sha256(text.encode()).hexdigest()

        try:
            cursor = self.conn.cursor()
            insert_query = "INSERT INTO text_fragments (plain_text, full_text, metadata, vector, filename, hash) VALUES (%s, to_tsvector('english', %s), %s, %s, %s, %s)"
            interpolated_query = cursor.mogrify(insert_query, (text, text, json.dumps(metadata), vector[0], filename, hash))
            print("Interpolated SQL query:", interpolated_query.decode("utf-8"))  
            cursor.execute(insert_query, (text, text,json.dumps(metadata),vector[0],filename, hash))
            self.conn.commit()
            cursor.close()

        except psycopg2.Error as e:
            print("Error:", e)

    def close(self):
        self.conn.close()



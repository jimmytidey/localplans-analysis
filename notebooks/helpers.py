import uuid
import PyPDF2
import os 

def embed(collection, embedding_model, chunk_list, LPA):
    # Embed text
    embedded_texts = embedding_model.embed_documents(
        texts=chunk_list)

    # add vectors to collection
    ids = [str(uuid.uuid4()) for sent in chunk_list]

    total = 0

    for line in chunk_list:
        total += len(line)

    print(total)

    metadatas = [{"LPA": LPA}
                 for sent in chunk_list]
    print(len(ids))
    print(len(metadatas))
    print(len(chunk_list))

    collection.add(
        embeddings=embedded_texts,
        documents=chunk_list,
        ids=ids,
        metadatas=metadatas
    )

    print('number of embeddings ')
    print(collection.count())


def pinecone_embed(collection, embedding_model, chunk_list, metadata):
    # Embed text
    embedded_texts = embedding_model.embed_documents(
        texts=chunk_list)

    # add vectors to collection
    ids = [str(hash(sent)) for sent in chunk_list]

    print(len(ids))
    print(len(chunk_list))

    upsert_list = []

    #TODO: I think it would be better to just zip these lists together
    for index, val in enumerate(ids):
        metadata['text'] = chunk_list[index]
        print(metadata)
        record_tuple = (ids[index], embedded_texts[index], metadata)
        upsert_list.append(record_tuple)

    collection.upsert(upsert_list)


def pinecone_connect():
    from pinecone import Pinecone, ServerlessSpec
    import os
    from dotenv import load_dotenv
    pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY')) 
    pc.describe_index("localplans")
    index = pc.Index("localplans")
    return index

def pdf_to_text(source_pdf_folder_path, target_text_folder_path, file_name):

    try:
        source_file_path = source_pdf_folder_path + "/" + file_name
        target_file_name = os.path.splitext(file_name)[0] + '.txt'
        target_file_path = target_text_folder_path + "/" + target_file_name
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
                print(text[0:100])   
        # Write the extracted text to a text file
        with open(target_file_path, 'w', encoding='utf-8') as text_file:
            text_file.write(text)

    except Exception as e: 
        print(file_name)
        print(e)

import psycopg2
import os


class Postgres:

    def __init__(self):
        try:
            DATABASE_URL = os.environ["DATABASE_URL"]

            self.conn = psycopg2.connect(DATABASE_URL, sslmode="require")

            # Create a cursor object using the connection
            first_query = """
                    -- !!!! Installing the vector extension took nearly two hours.  
                    -- !!!! It would probably be best to run it from Heroku dataclips
                    CREATE EXTENSION IF NOT EXISTS vector;

                    CREATE TABLE IF NOT EXISTS text_corpus (
                    id SERIAL PRIMARY KEY,
                    metadata JSONB,
                    pgvector_data VECTOR(384),
                    text TEXT
                    
                    );
                    
                    -- Create a text search configuration for English
                    CREATE TEXT SEARCH CONFIGURATION english_simple_config ( COPY = simple );
                    
                    ALTER TEXT SEARCH CONFIGURATION english_simple_config
                        ALTER MAPPING FOR asciiword, asciihword, hword_asciipart, word, hword, hword_part
                        WITH english_stem;

                    -- Alter the text column to use the English full-text search configuration
                    ALTER TABLE text_corpus
                        ALTER COLUMN text
                        SET DATA TYPE tsvector
                        USING to_tsvector('english_simple_config', text);

                    -- Create an index on the tsvector column for faster full-text searches
                    CREATE INDEX text_tsvector_index
                        ON text_corpus
                        USING gin(text);

                    -- DON'T UNDERSTAND WHAT THIS IS FOR. Optionally, you can create a trigger to automatically update the tsvector column
                    -- CREATE TRIGGER update_text_tsvector
                    --    BEFORE INSERT OR UPDATE ON text_corpus
                    --     FOR EACH ROW EXECUTE FUNCTION tsvector_update_trigger(text, 'english_full_text', text);

                
                """
            cursor = self.conn.cursor()

            # Execute SQL queries using the cursor
            cursor.execute(first_query)

            # Close the cursor and connection
            cursor.close()

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

    def close(self):
        self.conn.close()



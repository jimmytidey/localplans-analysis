from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.embeddings import SentenceTransformerEmbeddings
import chromadb


def compare_lpas(topic):
    persistent_client = chromadb.PersistentClient()

    print(persistent_client.list_collections())

    collection = persistent_client.get_or_create_collection(
        "all-MiniLM-L6-v2_1000_split")

    embedding_model = SentenceTransformerEmbeddings(
        model_name="all-MiniLM-L6-v2")

    embedding_model = SentenceTransformerEmbeddings(
        model_name="all-MiniLM-L6-v2")

    # Create context string
    query = embedding_model.embed_documents(
        [topic],
    )

    southwark_results = collection.query(
        query_embeddings=query,
        where={"LPA": "London_Borough_of_Southwark"},
        n_results=5,
    )

    southwark_results_string = '\n\n'.join(
        southwark_results['documents'][0][0:4])

    th_results = collection.query(
        query_embeddings=query,
        where={"LPA": "London_Borough_of_Tower_Hamlets"},
        n_results=5,
    )
    th_results_string = '\n\n'.join(th_results['documents'][0][0:4])

    islington_results = collection.query(
        query_embeddings=query,
        where={"LPA": "London_Borough_of_Islington"},
        n_results=5,
    )
    islington_results_string = '\n\n'.join(
        islington_results['documents'][0][0:4])

    context = '''
    Context from Southwark: 
    {southwark_results}

    Context from Tower Hamlets: 
    {th_results}

    Context from Islington: 
    {islington_results}

    '''.format(southwark_results=southwark_results_string,
               th_results=th_results_string, islington_results=islington_results_string)

    print(context)

    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=1)

    query_string = '''
    Compare the way Southwark, Tower Hamlets and Islington approach to the topic of {topic}, listing the three biggest differences. 

    {context} 
    '''. format(context=context, topic=topic)

    result = llm.call_as_llm(query_string)

    return result

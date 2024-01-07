import uuid


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


def pinecone_embed(collection, embedding_model, chunk_list, LPA):
    # Embed text
    embedded_texts = embedding_model.embed_documents(
        texts=chunk_list)

    # add vectors to collection
    ids = [str(hash(sent)) for sent in chunk_list]

    metadatas = [{"LPA": LPA, "text": sent}
                 for sent in chunk_list]
    print(len(ids))
    print(len(metadatas))
    print(len(chunk_list))

    upsert_list = []

    for index, val in enumerate(ids):
        record_tuple = (ids[index], embedded_texts[index], metadatas[index])
        upsert_list.append(record_tuple)

    collection.upsert(upsert_list)


def pinecone_connect():
    import pinecone
    import os
    from dotenv import load_dotenv
    pinecone.init(api_key=os.getenv('PINECONE_API_KEY'),
                  environment="eu-west4-gcp")
    pinecone.describe_index("localplans")
    index = pinecone.Index("localplans")
    return index

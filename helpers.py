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

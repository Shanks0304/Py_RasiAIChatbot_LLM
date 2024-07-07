from dotenv import load_dotenv, find_dotenv

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_openai import OpenAIEmbeddings
from langchain.indexes import index

from app.vectors_store.utilities.utilities import get_qdrant_vectorstore_client, get_qdrant_langchain_client, get_record_manager_client

from qdrant_client.http import models as rest

load_dotenv(find_dotenv())

def ingest_txt(file_path: str, index_name: str = "random_index_name"):
    """
    Ingests text data from a file and indexes it in a Weaviate vector store.

    Parameters:
        file_path (str): The path to the text file to ingest.
        index_name (str, optional): The name of the Weaviate index to use. Defaults to "random_index_name".

    Returns:
        dict: A dictionary containing statistics about the indexing process.
    """
 
    loader = TextLoader(file_path=file_path)
    doc = loader.load()
    
    print(doc)
    
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        model_name="gpt-4o", chunk_size=4000, chunk_overlap=200
    )
    
    chunks = text_splitter.split_documents(doc)
        
    embedding = OpenAIEmbeddings(model="text-embedding-3-small")
    client = get_qdrant_vectorstore_client()
    
    if not client.collection_exists(collection_name=index_name):
        client.create_collection(
            collection_name=index_name,
            vectors_config= {
                index_name: rest.VectorParams(
                    distance=rest.Distance.COSINE,
                    size=1536,
                ),
            },
        )
        
    vectorstore = get_qdrant_langchain_client(index_name=index_name, embedding=embedding, vector_name=index_name)
    
    record_manager = get_record_manager_client(index_name=index_name)
        
    indexing_stats = index(
        chunks,
        record_manager,
        vectorstore,
        cleanup="incremental",
        source_id_key="source",
        )
        
    print("-----TXT FILE INGESTED -----")
    return indexing_stats

if __name__ == "__main__":
    
    print("Hello wold")    
   
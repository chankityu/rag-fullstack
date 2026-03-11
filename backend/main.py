from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import os
import time
import requests
from tqdm import tqdm

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_community.llms import LlamaCpp

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain


# ----------------------------
# CONFIG
# ----------------------------

MODEL_PATH = "../llama-2-7b-chat.Q4_K_M.gguf"
MODEL_URL = "https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/resolve/main/llama-2-7b-chat.Q4_K_M.gguf"

DOCS_DIR = "../docs"
CHROMA_DIR = "../chroma_db"


# ----------------------------
# REQUEST MODEL
# ----------------------------

class Message(BaseModel):
    message: str


# ----------------------------
# UTILITIES
# ----------------------------

def download_model():
    if os.path.exists(MODEL_PATH):
        return

    print("Downloading model...")
    response = requests.get(MODEL_URL, stream=True)
    total = int(response.headers.get("content-length", 0))

    with open(MODEL_PATH, "wb") as f:
        for chunk in tqdm(response.iter_content(chunk_size=1024), total=total // 1024):
            f.write(chunk)


def load_documents():
    os.makedirs(DOCS_DIR, exist_ok=True)

    documents = []

    for file in os.listdir(DOCS_DIR):

        path = os.path.join(DOCS_DIR, file)

        if file.endswith(".pdf"):
            loader = PyPDFLoader(path)
            documents.extend(loader.load())

        elif file.endswith(".txt"):
            loader = TextLoader(path)
            documents.extend(loader.load())

    return documents


def build_vectorstore():

    docs = load_documents()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50
    )

    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2"
    )

    return Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_DIR
    )


def build_llm():

    return LlamaCpp(
        model_path=MODEL_PATH,
        temperature=0.7,
        max_tokens=300,
        n_ctx=4096,
        verbose=False
    )


def build_rag():

    vectorstore = build_vectorstore()
    llm = build_llm()

    template = """
    Answer the question based on the context below.

    {context}

    Question: {input}
    Answer:
    """

    prompt = PromptTemplate(
        template=template,
        input_variables=["context", "input"]
    )

    combine_docs_chain = create_stuff_documents_chain(llm, prompt)

    rag_chain = create_retrieval_chain(
        vectorstore.as_retriever(search_kwargs={"k": 3}),
        combine_docs_chain
    )

    return rag_chain


# ----------------------------
# INITIALIZATION
# ----------------------------

download_model()
rag_pipeline = build_rag()


# ----------------------------
# FASTAPI APP
# ----------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------------------------
# API ROUTES
# ----------------------------

@app.post("/chat")
async def chat(message: Message):

    start = time.time()

    result = rag_pipeline.invoke({
        "input": message.message
    })

    duration = time.time() - start

    return {
        "reply": result["answer"],
        "time": round(duration, 2)
    }
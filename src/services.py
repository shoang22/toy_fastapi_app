import time
from fastapi.concurrency import run_in_threadpool
from langchain.text_splitter import RecursiveCharacterTextSplitter 

from src.loggers import logger


async def nonblocking_call(text: str, task_id):
    splitter = RecursiveCharacterTextSplitter()
    text_chunks = await run_in_threadpool(splitter.split_text, text=text)
    
    n_chunks = 0
    for _ in text_chunks:
        n_chunks += 1

    logger.info(f"Task {task_id} completed - N chunks: {n_chunks}")

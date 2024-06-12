import time
from functools import partial

import tiktoken
from semantic_text_splitter import TextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.utils import RecursiveCharacterTextStreamer


# TODO: Test Anthropic library (Claude tokenizer might be the bottleneck)


def count_tokens(text):
    counter = tiktoken.get_encoding("cl100k_base")
    return len(counter.encode(text))


def naive_splitter(text, chunk_size, overlap):
    n_tokens = len(text)
    for i in range(0, n_tokens - overlap, chunk_size - overlap):
        yield text[i : i + chunk_size]


def test_splitter():
    chunk_size = 10_000
    chunk_overlap = int(max(chunk_size * 0.10, 200))

    with open("tests/files/test_long.txt", "r") as f:
        text = f.read()[:10_000_000]

    n_tokens = count_tokens(text)
    print(f"N_tokens: {n_tokens}")
    simple_splitter = partial(
        naive_splitter, chunk_size=chunk_size, overlap=chunk_overlap
    )
    simple_splitter.__name__ = naive_splitter.__name__

    splitters = [
        RecursiveCharacterTextSplitter(
            length_function=count_tokens,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        ).split_text,
        RecursiveCharacterTextStreamer(
            length_function=count_tokens,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        ).split_text_stream,
        # TextSplitter.from_callback(
        #     callback=count_tokens,
        #     capacity=chunk_size,
        #     overlap=chunk_overlap,
        # ).chunks,
        simple_splitter,
    ]

    for splitter in splitters:
        b = time.perf_counter()
        text_chunks = splitter(text)
        e = time.perf_counter()
        text_chunks = (
            list(text_chunks) if not isinstance(text_chunks, list) else text_chunks
        )
        print(
            f"Time for {splitter.__module__}.{splitter.__name__} to complete: {e - b} seconds yielding {len(text_chunks)} splits."
        )

        for chunk in text_chunks:
            assert count_tokens(chunk) <= chunk_size

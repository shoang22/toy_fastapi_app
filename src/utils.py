import re
from typing import Any, List, Optional, Generator, Iterable
from langchain.text_splitter import RecursiveCharacterTextSplitter
from src.loggers import logger


class RecursiveCharacterTextStreamer(RecursiveCharacterTextSplitter):
    def __init__(
        self, 
        separators: Optional[List[str]] = None, 
        keep_separator: bool = True, 
        is_separator_regex: bool = False, 
        **kwargs: Any
    ) -> None:
        super().__init__(separators, keep_separator, is_separator_regex, **kwargs)

    
    def _merge_splits_stream(self, splits: Iterable[str], separator: str) -> Generator[str, None, None]:
        # We now want to combine these smaller pieces into medium size
        # chunks to send to the LLM.

        # We want to yield a valid chunk to _split_text, which will return it to the caller immediately
        # Create a helper function that yields the equivalent to what is returned in _join_docs 

        separator_len = self._length_function(separator)

        current_doc: List[str] = []
        total = 0
        for d in splits:
            _len = self._length_function(d)
            if (
                total + _len + (separator_len if len(current_doc) > 0 else 0)
                > self._chunk_size
            ):
                if total > self._chunk_size:
                    logger.warning(
                        f"Created a chunk of size {total}, "
                        f"which is longer than the specified {self._chunk_size}"
                    )
                if len(current_doc) > 0:
                    # Problem here is that _join_docs needs a list of strings 
                    # Creating chunk here
                    # I do not want to have to provide a list of strings
                    doc = self._join_docs_stream(current_doc, separator)
                    if doc is not None:
                        yield doc
                    # Keep on popping if:
                    # - we have a larger chunk than in the chunk overlap
                    # - or if we still have any chunks and the length is long
                    while total > self._chunk_overlap or (
                        total + _len + (separator_len if len(current_doc) > 0 else 0)
                        > self._chunk_size
                        and total > 0
                    ):
                        # Creating overlap here
                        total -= self._length_function(current_doc[0]) + (
                            separator_len if len(current_doc) > 1 else 0
                        )
                        current_doc = current_doc[1:]
            current_doc.append(d)
            total += _len + (separator_len if len(current_doc) > 1 else 0)
        doc = self._join_docs(current_doc, separator)
        if doc is not None:
            yield doc


    def _join_docs_stream(self, docs: List[str], separator: str) -> Optional[str]:
        text = ""

        text = separator.join(docs)
        if self._strip_whitespace:
            text = text.strip()
        if text == "":
            return None
        else:
            return text

    def _split_text_stream(self, text: str, separators: List[str]) -> Generator[str, None, None]:
        """Split incoming text and return chunks."""
        # Get appropriate separator to use
        separator = separators[-1]
        new_separators = []
        for i, _s in enumerate(separators):
            _separator = _s if self._is_separator_regex else re.escape(_s)
            if _s == "":
                separator = _s
                break
            if re.search(_separator, text):
                separator = _s
                new_separators = separators[i + 1 :]
                break

        _separator = separator if self._is_separator_regex else re.escape(separator)
        # Returns chunks of text split by separator
        splits = _split_text_with_regex_stream(text, _separator, self._keep_separator)

        # Now go merging things, recursively splitting longer texts.
        _good_splits = []
        _separator = "" if self._keep_separator else separator
        for s in splits:
            if self._length_function(s) < self._chunk_size:
                _good_splits.append(s)
            else:
                if _good_splits:
                    merged_text = self._merge_splits_stream(_good_splits, _separator)
                    yield from merged_text
                    _good_splits = []
                if not new_separators:
                    yield s
                else:
                    other_info = self._split_text_stream(s, new_separators)
                    yield from other_info
        if _good_splits:
            merged_text = self._merge_splits_stream(_good_splits, _separator)
            yield from merged_text

    def split_text_stream(self, text: str) -> Generator[str, None, None]:
        return self._split_text_stream(text, self._separators)

    
def _split_text_with_regex_stream(
    text: str, separator: str, keep_separator: bool
) -> Generator[str, None, None]:
    # Now that we have the separator, split the text
    if separator:
        if keep_separator:
            # The parentheses in the pattern keep the delimiters in the result.
            _splits = re.split(f"({separator})", text)
            splits = [_splits[i] + _splits[i + 1] for i in range(1, len(_splits), 2)]
            if len(_splits) % 2 == 0:
                splits += _splits[-1:]
            splits = [_splits[0]] + splits
        else:
            splits = re.split(separator, text)
    else:
        splits = list(text)

    for s in splits:
        if s != "":
            yield s
    
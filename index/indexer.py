from index.term import Term
from index.partial_index.partial_index import PartialIndex
from index.partial_index.partial_index_builder import PartialIndexBuilder
from index.posting import Posting
from utils import get_tokens, index_log
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning, MarkupResemblesLocatorWarning
import json
from pathlib import Path
import os
import warnings
from collections import Counter
from index.partial_index.partial_index_merging import PartialIndexMerger
import time

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)


class Indexer:
    """
    Indexes a directory of webpages downloaded from project specifications.
    Stores partial indexes to disk, the polyphase merges them at the end.

    This class should be a singleton; it will only be created and constructed once per program execution.
    """

    def __init__(self, webpages_dir: Path, partial_index_dir: Path, index_dir: Path):
        # validate directories
        if not webpages_dir.is_dir():
            raise ValueError(
                f"Webpages directory {webpages_dir} is not a valid directory.")
        if partial_index_dir.is_dir() and partial_index_dir.exists() and any(partial_index_dir.iterdir()):
            raise ValueError(
                f"Partial index directory must be empty.")
        partial_index_dir.mkdir(exist_ok=True)
        if index_dir.is_dir() and index_dir.exists() and any(index_dir.iterdir()):
            raise ValueError(f"Inverted Index directory must be empty.")
        index_dir.mkdir(exist_ok=True)

        self._webpages_dir = webpages_dir
        self._partial_index_dir = partial_index_dir
        self._index_dir = index_dir

    def _build_partial_indexes(self) -> None:
        """Constructs partial indexes from a directory of webpages."""
        index_log.info(f"Building partial indexes from {self._webpages_dir}")
        builder = PartialIndexBuilder(
            self._webpages_dir, self._partial_index_dir, self._index_dir)
        builder.build()

    def _merge_partial_indexes(self) -> None:
        """
        Merges all partial indexes into a single InvertedIndex object.
        Partial indexes are stored in self._partial_index_dir directory. 
        Should not be called before first constructing the partial indexes.
        """
        index_log.info(
            f"Merging partial indexes from {self._partial_index_dir}")
        merger = PartialIndexMerger(self._partial_index_dir, self._index_dir)
        merger.merge()

    def construct(self) -> None:
        """Construct a full inverted index from a collection of webpages specified in the constructor."""
        index_log.info(f"Indexing documents from {self._webpages_dir}")

        index_start_time = time.time()
        self._build_partial_indexes()
        index_finish_time = time.time()

        # mundane logging
        index_log.info(
            f"Finished indexing all documents and created object {self}")
        partial_index_size = sum(f.stat().st_size for f in self._partial_index_dir.glob(
            '**/*') if f.is_file()) / 1024
        summary = f"Indexer summary:\n"
        summary += \
            f"Total size of partial indexes on disk: {f"{partial_index_size}KB at {self._partial_index_dir}" or "NOT FOUND"}\n" + \
            f"Time elapsed (indexing): {(index_finish_time - index_start_time):.2f}s"
        print("-"*80)
        print(summary)
        index_log.info(summary)

        merge_start_time = time.time()
        self._merge_partial_indexes()
        merge_finish_time = time.time()

        # more logging
        index_log.info(
            f"Finished merging all partial indexes.")
        index_size = sum(f.stat().st_size for f in self._index_dir.glob(
            '**/*') if f.is_file()) / 1024
        summary = \
            f"Total size of inverted index on disk: {f"{index_size}KB at {self._partial_index_dir}" or "NOT FOUND"}\n" + \
            f"Time elapsed (merge): {(merge_finish_time - merge_start_time):.2f}s\n" + \
            f"Time elapsed (total): {(merge_finish_time - index_start_time):.2f}s"
        print(summary)
        index_log.info(summary)
        print("-"*80)

    def __str__(self):
        return f"<Indexer for {self._webpages_dir}>"

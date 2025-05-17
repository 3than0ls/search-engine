# TODO

- Implement polyphase merging for merging the partial indexes into one index. (`merge.py`)

- Add term importance to Posting (or however else) when processing documents; headers should be more important than regular text (`posting.py`,`tokenize.py`, `indexer.py`). Will probably need to make major changes to how documents are loaded and processed in `indexer.py`

- Add tf-idf score to Posting (`posting.py`,`tokenize.py`, `indexer.py`). Will probably need to make major changes to how documents are loaded and processed in `indexer.py`

- Token stemming, Porter stemmer? (`tokenize.py`)

KEEP IT SIMPLE

InvertedIndex is the interface for accessing ALL data in the index; regardless of how it is handled in the backend

Indexer will construct several PartialIndex-es, merge them, and then produce a full InvertedIndex

InvertedIndex will have 2 files on disk:  the serialized inverted index (post partial index merge), and a auxiliary secondary index to seek terms, which can be loaded into memory (see lecture 18)
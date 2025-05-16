# TODO

- Implement polyphase merging for merging the partial indexes into one index. (`merge.py`)

- Add term importance to Posting (or however else) when processing documents; headers should be more important than regular text (`posting.py`,`tokenize.py`, `indexer.py`). Will probably need to make major changes to how documents are loaded and processed in `indexer.py`

- Add tf-idf score to Posting (`posting.py`,`tokenize.py`, `indexer.py`). Will probably need to make major changes to how documents are loaded and processed in `indexer.py`

- Token stemming, Porter stemmer? (`tokenize.py`)

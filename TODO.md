# TODO

- Boolean retrieval (`inverted_index.py`)

- Add tf-idf score to Posting (`posting.py`,`tokenize.py`, `indexer.py`). `tokenize.py`'s `get_postings` function takes a bs4 soup and outputs a mapping of terms to postings. Add td-idf score and pointers to posting. Additionally, add token stemming.

- CLI and web interface

- implement a document ID (currently just an incrementing integer) to document hash (whihc is also the file name) map

- implement a term to index file position mapping so you can f.seek()
# Search Engine

See `TODO.md` for things that mut still be done

## Getting started

Install dependencies with `python -m pip install -r requirements.txt`, or however else your environment needs to be set up.

If on Windows, check `config.toml` and run `python main.py` or `python -m unittests discover ./unittest`

If on Linux, config variables are exported as environment variables. Run `./launch.sh` or `./test.sh`. This assumes your virtual environment is stored in .venv of the CWD.

## Code

### High level overview

Program starts at `main.py`, where it creates an `Indexer` instance and runs `.construct()`, which does all the work.

The `Indexer` constructs a `InvertedIndex`, which goes through the webpages to construct `PostingList`s, which are containers for `Posting`s. The `InvertedIndex` is stored in partial indexes, which are serialized and saved in batches, which will then be merged together later (this is a requirement)

### Serialization

`InvertedIndex` will store partial indexes in disk in the function `_dump_partial_index`. It relies on `Posting` and `PostingList` both have a serialization method, joined by delimeters found in `index/delimeters.py`.

They're serialized in a text format and stored in .txt files, nothing shelves no json. It'll literally look something like

```py
[term1]:posting_1_doc_id|posting_1_attr,posting_2_doc_id|posting_2_attr,...
[term2]:posting_1_doc_id|posting_1_attr,posting_2_doc_id|posting_2_attr,...
...
```

This will make it easy to read one line at a time, easy to split (their delimeters are known), and easy to merge.

### Directory `index`

#### `posting.py`

A dataclass representing a posting

#### `posting_list.py`

A class representing a list of postings, with an algorithm to add postings to the correct location.

#### `inverted_index.py`

A class representing the entire inverted index. During creation, it will periodically serialize and dump partial indexes. When adding postings, run it using a context manager, as seen in `Indexer.construct`. Also keeps track of number of postings and number of terms processed, used for M1 analytics.

#### `indexer.py`

A class representing the responsible for loading, processing, and indexing documents and adding postings to `InvertedIndex`. Also responsible for outputting M1 analytics.

### Directory `utils`

#### config.py

Exports `load_config`, which loads in config settings from config.toml

#### logger.py

Exports `index_log` and `engine_log`, which are used to log important information in respective .log files.

#### merge.py

Exports `merge`, which will eventually be implemented to polyphase merge the partial indexes.

#### tokenize.py

Exports `get_tokens`, which returns a Pythoun Counter object of tokens to their token count.

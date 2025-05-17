# Search Engine

See `TODO.md` for things that mut still be done.

## Getting started

Install dependencies with `python -m pip install -r requirements.txt`, or however else your environment needs to be set up. `python -m venv .venv` might work, selecting it as your virtual environment, then activating, or however. See <https://docs.python.org/3/library/venv.html#creating-virtual-environments>.

If on Windows, check `config.toml` and run `python main.py` or `python -m unittests discover ./unittest`

If on Linux, config variables are exported as environment variables. Run `./launch.sh` or `./test.sh`. This assumes your virtual environment is stored in .venv of the CWD.

## Code

### High level overview

Program starts at `main.py`, where it creates an `Indexer` instance and runs `.construct()`, which does all the work.

The `Indexer` works by processing webpages to construct several `PartialIndex`es, which are containers for `PostingList`s, which are containers for `Posting`s. The `PartialIndex`es are serialized and stored in a directory temporarily, then merged all together to output into another directory (specification requirements)

The `InvertedIndex` is created as a interface for that directory, nothing more. Eventually, `InvertedIndex` will be used to query the index data for searches.

### Serialization

`InvertedIndex` will store partial indexes in disk in the function `_dump_partial_index`. It relies on `Posting` and `PostingList` both have a serialization method, joined by delimeters found in `index/delimeters.py`.

They're serialized in a text format and stored in .txt files, nothing shelves no json. It'll literally look something like

```py
[term1]:posting_1_doc_id|posting_1_attr,posting_2_doc_id|posting_2_attr,...
[term2]:posting_1_doc_id|posting_1_attr,posting_2_doc_id|posting_2_attr,...
...
```

This will make it easy to read one line at a time, easy to split (their delimeters are known), and easy to merge.

How it is serialized isn't actually important; in fact we'll probably have to change the serialization A LOT. Add more info like pointers and td-idf scores, and then make it smaller and more compressed. Then maybe document ID mappings; serialization must be worked on.

### Directory `index`

#### `posting.py`

A dataclass representing a posting

#### `posting_list.py`

A class representing a list of postings, with an algorithm to add postings to the correct location.

#### `inverted_index.py`

2am i'm too tired to write docs just ask me

#### `partial_index.py`

2am i'm too tired to write docs just ask me

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

# Search Engine

## Project Information

Indexing starts in `index.py`, where the indexer builds several partial indexes, then merges them into a single inverted index.

Building partial indexes: To build a partial index, a document is loaded then processed. To process a document, it is tokenized, then a mapping of postings is created for the document, then added to the partial index. After a certain size threshold, the partial index is serialized to binary and stored on disk. See `partial_index_builder.py`.

Merging partial indexes: To merge the partial indexes, a polyphase merge algorithms is used, merging two partial indexes at a time. Partial indexes maintain sorted posting lists, making it easy to merge lists. After the partial indexes are merged, the next run is added to the queue and polyphase merge continues until only one partial index remains (the entire inverted index). See `partial_index_merger.py`.

Document scoring: We score documents solely using tf-idf. Each posting element stores the document ID and the term frequency, and the tf-idf score is computed during query time.

Query optimziation: To optimize queries, we take 2 approaches, a speed optimization and a ranking optimization. For speed, we utilize `seek()` in the inverted index file to find the exact location of the posting list for a term. For ranking, we utilize a soft conjunction heuristic. If a document is missing several terms in a query, it's score is decreased.

Important words: We treat headers and bolded words as more important than regular text, and increase their weight (by simply artificially increasing the term frequency in the posting).

Extra credit: We created a web GUI and and index anchor words for taget pages.

Fun fact! Our inverted index uses a custom binary serializations, allowing it to have a size of 76M. To compare, the DEV index is 2.8G.

## Getting started

Install dependencies with `python -m pip install -r requirements.txt`, or however else your environment needs to be set up. `python -m venv .venv` might work, selecting it as your virtual environment, then activating, or however. See <https://docs.python.org/3/library/venv.html#creating-virtual-environments>.

If on Windows, check `config.toml` and run `python main.py` or `python -m unittests discover ./unittest`

If on Linux, config variables are exported as environment variables. Run `./launch.sh` or `./test.sh`. This assumes your virtual environment is stored in .venv of the CWD.

## Running the Search Engine Web Interface

To run the complete search engine with web interface:

### 1. Start the Backend Server
From the root directory, run:
```bash
python server.py
```
This will start the Flask server on `http://localhost:8080` that handles search API requests.

### 2. Start the Frontend Client
In another terminal, navigate to the client directory and start the development server:
```bash
cd client
npm run dev
```
This will start the Next.js frontend on `http://localhost:3000`.

The frontend provides a Google-like search interface that communicates with the Python backend to perform searches and display results.

## High level overview

Program starts at `index.py`, where it creates an `Indexer` instance and runs `.construct()`, which constructs the inverted index. From then, the class `InvertedIndex` can be used to interface with the serialized disk data.

The `Indexer` works by processing webpages to construct several `PartialIndex`es, which are map containers for stemmed `Term`s to `PostingList`s, which are themselves are containers for `Posting`s. The `PartialIndex`es are serialized and stored in a directory temporarily, then merged all together with polyphase merge to produce the file for the inverted index along with auxiliary data files (such as the document ID to URL mapping)

The `InvertedIndex` is created as a interface for the inverted index disk data. nothing more. `InvertedIndex` will be used to query the data, but not modify it.

## Configuration

`config.toml` stores key configurations as to where to search or place files.

Webpages are stored in `WEBPAGES_DIR`, Partial indexes are stored in `PARTIAL_INDEX_DIR`, and inverted indexes and it's auxiliary files are stored in `INDEX_DIR`.

## Index Creation

### Index Creation Graph

A graph of the process looks something like this:

```mermaid
graph LR;
    webpages@{ shape: circle, label: "Webpages\n(ANALYST or DEV)" }
    partial_indexes@{ shape: docs, label: "Partial Indexes" }
    inverted_index@{ shape: lin-cyl, label: "Inverted Index\nAuxiliary Files" }

    webpages -- Indexer (PartialIndexBuilder) --> partial_indexes;
    partial_indexes -- Indexer (PartialIndexMerger) --> inverted_index;
```

### Serialization

Everything from `PartialIndex` down has a `serialize()` method that serializes it in binary. Utilizes Python's `struct` library's `.pack()`, some string encoding, and then deserialization involves `struct` library's `.unpack()` and some manual parsing.

## Index Querying

The search component is implemented in `search.py`. It loads the inverted index and the document ID to URL mapping. It supports boolean AND queries. Query terms are tokenized and stemmed before lookup.

To run the search interface, execute:

```bash
python search.py
```

The program will prompt you for queries. Enter terms separated by spaces (e.g., `machine learning`). The top 5 retrieved URLs that contain all the stemmed query terms will be displayed.

## Directory `utils`

### config.py

Exports `load_config`, which loads in config settings from config.toml

### logger.py

Exports `index_log` and `engine_log`, which are used to log important information in respective .log files.

### tokenize.py

Exports `get_postings`, which returns a mapping of stemmed terms to posting lists to be stored in the inverted index.

## Unit testing

To run unit testing, run `python -m unittests discover ./unittest`. Not required to write unit tests, I just write them because it makes it easier in the long run.

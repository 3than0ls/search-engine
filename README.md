# Search Engine

See `TODO.md` for things that mut still be done.

## Getting started

Install dependencies with `python -m pip install -r requirements.txt`, or however else your environment needs to be set up. `python -m venv .venv` might work, selecting it as your virtual environment, then activating, or however. See <https://docs.python.org/3/library/venv.html#creating-virtual-environments>.

If on Windows, check `config.toml` and run `python main.py` or `python -m unittests discover ./unittest`

If on Linux, config variables are exported as environment variables. Run `./launch.sh` or `./test.sh`. This assumes your virtual environment is stored in .venv of the CWD.

## Code

### High level overview

Program starts at `main.py`, where it creates an `Indexer` instance and runs `.construct()`, which does all the work.

The `Indexer` works by processing webpages to construct several `PartialIndex`es, which are map containers for `Term`s to `PostingList`s, which are themselves are containers for `Posting`s. The `PartialIndex`es are serialized and stored in a directory temporarily, then merged all together to output into another directory (specification requirements)

The `InvertedIndex` is created as a interface for that directory, nothing more. `InvertedIndex` is used to query the index data for searches.

### Serialization

Everything from `PartialIndex` down has a `serialize()` method that serializes it in binary. I can explain it if your interested but it just uses Python's `struct` library's `.pack()`, some string encoding, and then deserialization involves `struct` library's `.unpack()` and some manual parsing.

### Directory `utils`

#### config.py

Exports `load_config`, which loads in config settings from config.toml

#### logger.py

Exports `index_log` and `engine_log`, which are used to log important information in respective .log files.


#### tokenize.py

Exports `get_tokens`, which returns a Pythoun Counter object of tokens to their token count.

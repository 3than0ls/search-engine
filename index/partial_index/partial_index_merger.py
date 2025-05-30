from pathlib import Path
from collections import deque
from index.partial_index.partial_index import PartialIndexResource
from index.posting_list import PostingList
from index.term import Term
from typing import Deque, Iterator
from utils import index_log
import json


class PartialIndexMerger:
    """Utilize polyphase merge to merge the partial indexes into a single index."""

    def __init__(self, partial_index_dir: Path, index_dir: Path) -> None:
        self._partial_index_dir = partial_index_dir
        self._index_dir = index_dir
        self._term_to_ii_position_fp = self._index_dir / "term_to_ii_position.json"

        self._runs: Deque[Path] = deque()

    def _merge_postings_lists(self, left: PostingList, right: PostingList) -> PostingList:
        i, j = 0, 0
        out = []
        while i < len(left) and j < len(right):
            assert left[i] != right[j], \
                f"Found two identical posting objects which should not happen: {left[i]}"
            if left[i] < right[j]:
                out.append(left[i])
                i += 1
            else:
                out.append(right[j])
                j += 1

        if i < len(left):
            out.extend(left[i:])

        if j < len(right):
            out.extend(right[j:])

        posting_list = PostingList()
        posting_list._postings = out
        assert len(out) == (len(left) + len(right))
        return posting_list

    def _merge_partial_index_resources(self, left_resource: PartialIndexResource, right_resource: PartialIndexResource) -> Iterator[bytes]:
        """
        Simple merge algorithm that reads from two serialized partial indexes and writes to a new one.

        This code can be optimized and made cleaner and more of a pure functional style by having left and right be generators for partial index resources, and returning a generator to write..
        Maybe I'll do that later.
        """
        left = iter(left_resource)
        right = iter(right_resource)
        # flags to determine whether or not to get the next() value from the respective iterator after a loop iteration
        _load_left, _load_right = True, True
        left_value, right_value = None, None
        leftover = left
        while True:
            # load new values
            try:
                left_value = next(left) if _load_left else left_value
            except StopIteration:
                left_value = None
                leftover = right

            try:
                right_value = next(right) if _load_right else right_value
            except StopIteration:
                right_value = None
                leftover = left

            if left_value is None or right_value is None:
                break

            _load_left, _load_right = False, False

            # merge new values
            left_term, left_postings = left_value
            right_term, right_postings = right_value

            if left_term == right_term:  # merge and then serialize
                new_postings = self._merge_postings_lists(
                    left_postings, right_postings)
                serialization = left_term.serialize() + new_postings.serialize()
                _load_left, _load_right = True, True
            else:
                # serialize smaller term, move on
                if left_term < right_term:
                    serialization = left_term.serialize() + left_postings.serialize()
                    _load_left = True
                else:
                    serialization = right_term.serialize() + right_postings.serialize()
                    _load_right = True
            yield serialization

        # after breaking, left_value or right_value may still contain an already-read item that we must serialize
        if left_value is not None:
            yield left_value[0].serialize() + left_value[1].serialize()
        if right_value is not None:
            yield right_value[0].serialize() + right_value[1].serialize()

        for term, postings_list in leftover:
            yield term.serialize() + postings_list.serialize()

    def _merge_partial_indexes(self, output_path: Path, left_path: Path, right_path: Path, _final_merge=False) -> None:
        # only is used in the final merge; is a term to pointer in the inverted index file mapping, so in InvertedIndex, .seek() can be used
        term_to_ii_position = {}
        with PartialIndexResource(left_path) as left, PartialIndexResource(right_path) as right, open(output_path, "wb") as out:
            for line in self._merge_partial_index_resources(left, right):
                if _final_merge:
                    term = Term.deserialize(line).term
                    term_to_ii_position[term] = out.tell()
                out.write(line)

        if _final_merge:
            term_to_ii_position_fp = self._index_dir / "term_to_ii_position.json"
            with open(term_to_ii_position_fp, 'w') as f:
                json.dump(term_to_ii_position, f, indent=4)
            index_log.info(f"Saved term to inverted index binary data position mapping to {term_to_ii_position_fp}")

    def merge(self) -> None:
        """
        Utilize polyphase merge to merge the partial indexes (already sorted) into a single inverted index.
        """
        for p in self._partial_index_dir.iterdir():
            self._runs.append(p)

        run = 0
        while len(self._runs) > 1:
            one = self._runs.popleft()
            two = self._runs.popleft()
            run_name = self._partial_index_dir / f"tmp_merge_run_{run}.bin"
            index_log.info(f"Merging {one} and {two} to {run_name}")
            self._merge_partial_indexes(run_name, one, two)
            self._runs.append(run_name)
            run += 1

        fully_merged = self._runs.popleft()
        fully_merged.rename(self._index_dir / "inverted_index.bin")
        index_log.info(
            f"Placing inverted index at {self._index_dir / "inverted_index.bin"}")

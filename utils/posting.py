from dataclasses import dataclass


@dataclass(order=True)
class Posting:
    doc_id: str  # hash
    term_frequency: int

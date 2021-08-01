from dataclasses import dataclass


@dataclass
class Movie:
    title: str
    original_title: str
    year: str
    date_published: str
    imdb_id: str

from dataclasses import dataclass


@dataclass
class CitiesCountDTO:
    name: str
    count: int
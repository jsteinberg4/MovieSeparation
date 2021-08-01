from dataclasses import dataclass


@dataclass(eq=False)
class Person:
    name: str

    def __eq__(self, other):
        return (self is other
                or (isinstance(other, Person) and self.name == other.name))
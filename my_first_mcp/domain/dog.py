from pydantic import BaseModel


class Dog(BaseModel):
    name: str
    breed: str

    def bark(self):
        return f"{self.name} says Woof!"
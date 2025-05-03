
from fastapi import Depends

from my_first_mcp.db import DB
from my_first_mcp.depends import get_db
from my_first_mcp.domain.dog import Dog


# "DB" is simpley a dict[str, Dog] and we're faking a real database :)
class DogRepository:
    def __init__(self, db: DB = Depends(get_db)):
        self.db = db
        
    def create(self, dog: Dog):
        self.db[dog.name] = dog
        return dog
        
    def get(self, name: str) -> Dog | None:
        return self.db.get(name, None)
        
    def get_all(self) -> list[Dog]:
        return list(self.db.values())
        
    def update(self, name: str, dog: Dog) -> Dog | None:
        if name in self.db:
            self.db[name] = dog
            return dog
        return None
        
    def delete(self, name: str) -> Dog | None:
        if name in self.db:
            return self.db.pop(name)
        return None
from fastapi import APIRouter, Depends

from my_first_mcp.db import DB
from my_first_mcp.depends import get_db
from my_first_mcp.domain.dog import Dog
from my_first_mcp.repositories.dog_repository import DogRepository


router = APIRouter()

def get_repo(db: DB = Depends(get_db)):
    return DogRepository(db=db)

@router.get("/dog/{dog_name}")
async def get(dog_name: str, repo: DogRepository = Depends(get_repo)):
    return repo.get(name=dog_name)
    
@router.get("/dogs")
async def get_all(repo: DogRepository = Depends(get_repo)):
    return repo.get_all()
    
@router.post("/dog")
async def create(dog: Dog, repo: DogRepository = Depends(get_repo)):
    return repo.create(dog=dog)
    
@router.put("/dog/{dog_name}")
async def update(dog_name: str, dog: Dog, repo: DogRepository = Depends(get_repo)):
    return repo.update(name=dog_name, dog=dog)
    
@router.delete("/dog/{dog_name}")
async def delete(dog_name: str, repo: DogRepository = Depends(get_repo)):
    return repo.delete(name=dog_name)

    
# Fake database
# Required running uvicorn with one worker!
# And any --reload will reset the database.



from my_first_mcp.domain.dog import Dog

DB = dict[str, Dog]

db: DB = {}

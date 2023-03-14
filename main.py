from fastapi import FastAPI
from schema import crud

app = FastAPI()           

app.include_router(crud.crud)

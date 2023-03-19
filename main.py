from fastapi import FastAPI
from schema import crud
from starlette.middleware.cors import CORSMiddleware


app = FastAPI()           

app.include_router(crud.crud)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

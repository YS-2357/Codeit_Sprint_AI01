from fastapi import FastAPI,HTTPException,Query,Path,Body
from typing import Annotated
from pydantic import BaseModel, Field
from typing import  List

app = FastAPI()

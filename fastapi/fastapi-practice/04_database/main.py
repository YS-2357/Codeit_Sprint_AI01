from fastapi import FastAPI,HTTPException,Query,Path
from typing import Annotated,Optional,Dict
from pydantic import BaseModel, Field
from typing import  List
import os
from fastapi import Depends, FastAPI, HTTPException, Query , Body
from sqlmodel import Field, Session, SQLModel, create_engine, select, and_
from contextlib import asynccontextmanager


"""
사전에 저장된 테이블을 불러와서 쿼리날려보기

"""

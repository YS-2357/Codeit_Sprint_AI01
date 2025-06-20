from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"messages": "hello world!"}

@app.get("/sync")
def root():
    return {"messages": "sync test"}
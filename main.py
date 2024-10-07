from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello" : "Froyo"}

@app.get("/test")
def read_test():
    return {"Hello" : "Test"}
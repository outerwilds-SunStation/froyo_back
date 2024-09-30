from fastapi import fastAPI

app = fastAPI()

@app.get("/")
def read_root():
    return {"Hello" : "World"}
from fastapi import FastAPI

from src.pic.ImageMaker import ImageMaker

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello" : "Froyo"}

@app.get("/test")
def read_test():
    return {"Hello" : "Test"}

@app.post("/gen_img")
def gen_img(data: dict):
    try:
        image_data = data.get("image")
        if not image_data:
            return {"error": "No image data provided"}
        maker = ImageMaker(image_data)
        result = maker.gen_quiz_image()
        return result
    except Exception as e:
        return {"error": f"Error : {str(e)}"}
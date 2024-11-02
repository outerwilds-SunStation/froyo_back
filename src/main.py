from fastapi import FastAPI

from src.manager.DBManager import DBManager
from src.pic.ImageMaker import ImageMaker

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello" : "Froyo"}

@app.get("/test")
def read_test():
    return {"Hello" : "Test"}

@app.get("/get_nickname")
def get_nickname(email: str):
    db_manager = DBManager.get_db_client()
    return db_manager.get_user_nickname(email)

@app.post("/set_nickname")
def set_nickname(email: str, nickname: str):
    db_manager = DBManager.get_db_client()
    if db_manager.check_nickname_exist(email, nickname):
        return {"error": "Nickname already exists"}
    return db_manager.set_user_nickname(email, nickname)


@app.post("/gen_img")
def gen_img(data: dict, email: str):
    db_manager = DBManager.get_db_client()
    if not db_manager.user_role_check(email):
        return {"error": "User not authorized"}
    try:
        image_data = data.get("image")
        if not image_data:
            return {"error": "No image data provided"}
        maker = ImageMaker(image_data)
        result = maker.gen_quiz_image()
        return result
    except Exception as e:
        return {"error": f"Error : {str(e)}"}
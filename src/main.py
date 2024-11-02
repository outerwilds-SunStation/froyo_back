from fastapi import FastAPI, HTTPException, Request

from src.manager.DBManager import DBManager
from src.models import *
from src.pic.ImageMaker import ImageMaker

app = FastAPI(
    title="Froyo API",
    description="Froyo 서비스를 위한 API 정리 문서",
    version="0.0.1"
)

@app.get("/")
def read_root():
    return {"Hello" : "Froyo"}

@app.get("/get_nickname")
async def get_nickname(request: get_nickname):
    email = request.email
    if email == None:
        raise HTTPException(status_code=400, detail="json으로 email 데이터 전달 필요")

    db_manager = DBManager.get_db_client()
    nickname = db_manager.get_user_nickname(email)
    if nickname is None:
        raise HTTPException(status_code=400, detail="Nickname not found")
    return {"nickname": nickname}

@app.post("/set_nickname")
async def set_nickname(request: set_nickname):
    email = request.email
    nickname = request.nickname
    if email == None or nickname == None:
        raise HTTPException(status_code=400, detail="json으로 email, nickname 데이터 전달 필요")

    db_manager = DBManager.get_db_client()
    if db_manager.check_nickname_exist(email, nickname):
        raise HTTPException(status_code=400, detail="Nickname already exists")
    return db_manager.set_user_nickname(email, nickname)


@app.post("/generate_image")
async def generate_image(request: generate_image):
    email = request.email
    nickname = request.nickname
    image_data = request.image_data
    if email == None or nickname == None or image_data == None:
        raise HTTPException(status_code=400, detail="json으로 email, image 데이터 전달 필요")

    db_manager = DBManager.get_db_client()
    if not db_manager.user_role_check(request.email):
        raise HTTPException(status_code=400, detail="User not authorized")
    try:
        maker = ImageMaker(image_data)
        result = maker.gen_quiz_image()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"이미지 생성중 애러 : {str(e)}")

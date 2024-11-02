from fastapi import FastAPI, HTTPException, Request

from src.manager.DBManager import DBManager
from src.pic.ImageMaker import ImageMaker

app = FastAPI(
    title="Froyo API",
    description="Froyo 서비스를 위한 API 정리 문서",
    version="0.0.1"
)

@app.get("/",
         summary="기본 환영 메시지",
         description="API 서버 활성 테스트용. 아무 기능 없음")
def read_root():
    return {"Hello" : "Froyo"}

@app.get("/get_nickname",
         summary="유저 닉네임 조회",
         description="유저 이메일을 통해 닉네임 조회, 리턴",
         response = {
             200 : { "description": "닉네임 조회 성공", "content": { "nickname": str }},
             400 : { "description": "닉네임 조회 실패", "content": { "error": str }}
         })
async def get_nickname(request: Request):
    """
    유저 이메일을 통해 닉네임 조회, 리턴
    
    Args:
        email (str): 유저 이메일
    Returns:
        string: 닉네임
    """
    data = await request.json()
    email = data.get("email", "")
    if email == "":
        raise HTTPException(status_code=400, detail="json으로 email 데이터 전달 필요")

    db_manager = DBManager.get_db_client()
    nickname = db_manager.get_user_nickname(email)
    if nickname is None:
        raise HTTPException(status_code=400, detail="Nickname not found")
    return {"nickname": nickname}

@app.post("/set_nickname",
         summary="유저 닉네임 설정",
         description="유저 이메일과 닉네임을 통해 닉네임 설정, 리턴",
         response = {
             200 : { "description": "닉네임 설정 성공", "content": { "result": bool }},
             400 : { "description": "닉네임 설정 실패", "content": { "error": str }}
         })
async def set_nickname(request: Request):
    """
    유저 이메일과 닉네임을 통해 닉네임 설정, 리턴
    
    Args:
        email (str): 유저 이메일
        nickname (str): 닉네임
    Returns:
        bool: 닉네임 설정 성공 여부. 성공했을 때에만 True 리턴
    """
    data = await request.json()
    email = data.get("email", "")
    nickname = data.get("nickname", "")
    if email == "" or nickname == "":
        raise HTTPException(status_code=400, detail="json으로 email, nickname 데이터 전달 필요")

    db_manager = DBManager.get_db_client()
    if db_manager.check_nickname_exist(email, nickname):
        raise HTTPException(status_code=400, detail="Nickname already exists")
    return db_manager.set_user_nickname(email, nickname)


@app.post("/gen_img",
         summary="이미지 생성",
         description="이미지 생성 요청, 리턴",
         response = {
             200 : { "description": "이미지 생성 성공", "content": { "result": str }},
             400 : { "description": "이미지 생성 실패", "content": { "error": str }}
         })
async def gen_img(request: Request):
    """
    이미지 생성 요청, 리턴
    
    Args:
        data (dict): 이미지 생성 요청 데이터
        email (str): 유저 이메일
    Returns:
        string: 이미지 생성 결과
    """
    data = await request.json()
    email = data.get("email", "")
    image_data = data.get("image", "")
    if email == "" or image_data == "":
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

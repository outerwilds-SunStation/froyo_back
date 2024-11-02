from pydantic import BaseModel, Field, create_model


class User(BaseModel):
    email: str
    nickname: str
    role: str
    
class ImageData(BaseModel):
    image: str
    
get_nickname = create_model(
    "get_nickname",
    email = (str, None, Field(description="유저 이메일"))
)

set_nickname = create_model(
    "set_nickname",
    email = (str, None, Field(description="유저 이메일")),
    nickname = (str, None, Field(description="유저 닉네임"))
)

generate_image = create_model(
    "generate_image",
    email = (str, None, Field(description="유저 이메일")),
    nickname = (str, None, Field(description="유저 닉네임")),
    image_data = (str, None, Field(description="Base64 인코딩된 이미지 데이터"))
)
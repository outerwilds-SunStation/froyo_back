from pydantic import BaseModel, Field, create_model


class User(BaseModel):
    email: str
    nickname: str
    role: str
    
class ImageData(BaseModel):
    image: str
    
get_nickname = create_model(
    "get_nickname",
    email = (str, None)
)

set_nickname = create_model(
    "set_nickname",
    email = (str, None),
    nickname = (str, None)
)

generate_image = create_model(
    "generate_image",
    email = (str, None),
    nickname = (str, None),
    image_data = (str, None)
)
# Froyo Back-end API

Froyo 서비스를 위한 백엔드 API 서버입니다.  
이 프로젝트는 **FastAPI** 기반으로 동작하며, **Google Cloud Firestore**를 이용한 사용자 정보 관리와 **OpenCV / Pillow** 기반의 이미지 생성 기능을 제공합니다.

---

## 프로젝트 한줄 소개

> **Firestore 기반 사용자 권한 관리와 OpenCV 이미지 처리를 결합한 FastAPI 백엔드 서비스**

---

## 프로젝트 개요

이 서버는 다음과 같은 역할을 수행합니다.

- 사용자 닉네임 조회
- 사용자 닉네임 설정
- 권한이 있는 사용자만 이미지 생성 가능
- base64 이미지 입력을 받아 퀴즈용 이미지 생성
- 개발 환경에서는 테스트 이미지로 빠르게 검증 가능

단순 CRUD API가 아니라 **DB 연동 + 이미지 처리 + 권한 검증 + API 응답 생성**이 결합된 백엔드 프로젝트입니다.

---

## 주요 기능

### 1) 사용자 닉네임 조회
- 이메일을 기준으로 Firestore의 `users` 컬렉션에서 닉네임을 조회합니다.

### 2) 사용자 닉네임 설정
- 이메일과 닉네임을 받아 Firestore에 저장합니다.
- 기존 닉네임이 이미 동일하게 존재하면 중복으로 처리합니다.

### 3) 이미지 생성
- base64 형식의 이미지를 입력받아 퀴즈 이미지로 가공합니다.
- 이미지에서 contour를 추출하고 일부 영역을 마스크 처리한 뒤 inpainting으로 변형 이미지를 생성합니다.
- 생성 결과는 base64 문자열로 반환됩니다.

### 4) 권한 체크
- Firestore의 사용자 문서에서 `role` 값을 확인합니다.
- `config.py`의 `ACCESS_ROLE` 목록에 포함된 사용자만 이미지 생성이 가능합니다.

---

## 기술 스택

- Python 3.9
- FastAPI
- Uvicorn
- Pydantic
- Google Cloud Firestore
- Docker
- Google Cloud Build

---

## 프로젝트 구조

```bash
froyo_back-main/
├── config.py
├── Dockerfile
├── cloudbuild.yaml
├── req.txt
├── run.bat
├── src/
│   ├── main.py
│   ├── models.py
│   ├── manager/
│   │   └── DBManager.py
│   └── pic/
│       └── ImageMaker.py
├── keys/
│   └── datastore-access-key.json
├── test_base64.txt
└── result.jpg
```

### 핵심 파일 설명

- `src/main.py`  
  FastAPI 엔드포인트 정의

- `src/models.py`  
  요청 바디용 Pydantic 모델 정의

- `src/manager/DBManager.py`  
  Firestore 연결 및 사용자 데이터 조회/저장 로직

- `src/pic/ImageMaker.py`  
  base64 이미지를 받아 퀴즈 이미지 생성

- `config.py`  
  개발 모드 및 권한 설정

- `Dockerfile`  
  컨테이너 실행 환경 설정

- `cloudbuild.yaml`  
  Google Cloud Build용 이미지 빌드 설정

---

## API 명세

### 1. Root

#### `GET /`
서버 동작 확인용 엔드포인트입니다.

**Response**
```json
{
  "Hello": "Froyo"
}
```

---

### 2. 닉네임 조회

#### `GET /get_nickname`
이메일로 닉네임을 조회합니다.

**Request body**
```json
{
  "email": "user@example.com"
}
```

**Response**
```json
{
  "nickname": "froyo_user"
}
```

**Error**
- `400`: 이메일 미전달
- `400`: 닉네임을 찾지 못한 경우

---

### 3. 닉네임 설정

#### `POST /set_nickname`
이메일과 닉네임을 저장합니다.

**Request body**
```json
{
  "email": "user@example.com",
  "nickname": "froyo_user"
}
```

**Response**
```json
true
```

**Error**
- `400`: 이메일 또는 닉네임 미전달
- `400`: 이미 같은 닉네임이 존재하는 경우

---

### 4. 이미지 생성

#### `POST /generate_image`
base64 이미지 데이터를 받아 퀴즈 이미지를 생성합니다.

**Request body**
```json
{
  "email": "admin@example.com",
  "nickname": "froyo_user",
  "image_data": "<base64 이미지 문자열>"
}
```

**Response**
```json
{
  "src": "<base64>",
  "dst": "<base64>",
  "ref": "<base64>",
  "t": [x_offset, y_offset],
  "pts": [[x1, y1], [x2, y2], ...]
}
```

**필드 설명**
- `src`: 원본 이미지
- `dst`: 일부 영역이 바뀐 틀린 그림 이미지
- `ref`: 정답 표시용 이미지
- `t`: 중앙 정렬 시 이동한 좌표
- `pts`: 선택된 문제 영역 좌표

**Error**
- `400`: 이메일 / 이미지 데이터 미전달
- `400`: 권한 없는 사용자
- `400`: 이미지 처리 중 예외 발생

---

## 동작 방식 요약

### 사용자 관련 처리
`src/main.py`에서 요청을 받으면 `DBManager`를 통해 Firestore의 `users` 컬렉션을 조회합니다.

- `get_user_nickname(email)`  
  닉네임 조회

- `set_user_nickname(email, nickname)`  
  닉네임 저장

- `user_role_check(email)`  
  이미지 생성 권한 확인

### 이미지 처리 흐름
`ImageMaker`는 다음 순서로 이미지를 처리합니다.

1. 입력 이미지 로드
2. 흑백 변환 및 이진화
3. 형태학적 연산을 이용한 엣지 추출
4. contour 후보 선택
5. 선택된 영역을 마스크 처리
6. inpainting으로 변화된 이미지 생성
7. 이미지들을 base64로 변환해 응답 반환

---

## 개발 환경 설정

### 1) 의존성 설치
```bash
pip install -r req.txt
```

### 2) 서버 실행
```bash
uvicorn src.main:app --reload
```

### 3) Swagger UI 접속
```text
http://127.0.0.1:8000/docs
```

---

## Docker 실행

```bash
docker build -t froyo-back .
docker run -p 8080:8080 froyo-back
```

---

## Google Cloud 배포

이 프로젝트는 `cloudbuild.yaml`을 통해 Google Cloud Build 환경에서 컨테이너 이미지를 빌드할 수 있도록 구성되어 있습니다.

### 빌드 이미지
- `asia-east1-docker.pkg.dev/froyo-436105/froyo-back-artifact/froyo-back-server:last`

---

## 개발 모드

`config.py`에서 `DEV_MOD` 값을 통해 개발 모드를 전환할 수 있습니다.

```python
DEV_MOD = False
```

- `True`일 경우: `src/pic/test_images/` 내의 랜덤 테스트 이미지 사용
- `False`일 경우: base64 입력 이미지를 실제로 처리

---

## 인증 및 권한

Firestore의 사용자 문서에서 `role` 값을 확인하여 이미지 생성 가능 여부를 판단합니다.

허용 역할은 `config.py`에서 다음과 같이 관리됩니다.

```python
ACCESS_ROLE = ["admin", "user"]
```

즉, `role`이 `admin` 또는 `user`인 사용자만 이미지 생성 API를 사용할 수 있습니다.

---

## 참고 파일

- `keys/datastore-access-key.json`  
  Firestore 서비스 계정 키
- `test_base64.txt`  
  base64 이미지 테스트 샘플
- `result.jpg`  
  이미지 처리 결과 예시


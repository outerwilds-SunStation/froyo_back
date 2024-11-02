from google.cloud import firestore
from google.cloud.firestore import Client

from config import ACCESS_ROLE


class DBManager:
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            credentials_path = "keys/datastore-access-key.json"
            cls._instance.db = firestore.Client.from_service_account_json(credentials_path, database="froyo-db")
        return cls._instance
    
    @classmethod
    def get_db_client(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def set_user_nickname(self, email: str, nickname: str) -> bool:
        self.db.collection('users').document(email).set({"nickname": nickname})
        return True
    
    def check_nickname_exist(self, email: str, nickname: str) -> bool:
        data = self._find_data_from_email(email)
        if data is None:
            return False
        if data["nickname"] == nickname:
            return True
        return False
    
    def get_user_nickname(self, email: str):
        data = self._find_data_from_email(email)
        if data is None:
            return None
        return data["nickname"]

    def user_role_check(self, email: str):
        data = self._find_data_from_email(email)
        if data is None:
            return False
        if data["role"] in ACCESS_ROLE:
            return True
        return False
    
    def _find_data_from_email(self, email: str):
        user_ref = self.db.collection('users').document(email)
        user = user_ref.get()
        if user.exists:
            return user.to_dict()
        return None
    
    
    
    def get_document(self, collection_name: str, document_id: str):
        doc_ref = self.db.collection(collection_name).document(document_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None
    
    def get_all_documents(self, collection_name: str):
        docs = self.db.collection(collection_name).stream()
        return [doc.to_dict() for doc in docs]
    
    def query_documents(self, collection_name: str, field: str, operator: str, value: any):
        docs = self.db.collection(collection_name).where(field, operator, value).stream()
        return [doc.to_dict() for doc in docs]

firestore_manager = DBManager()
    
    # 단일 문서 가져오기
user = firestore_manager.get_document('users', 'qwerty61441@gmail.com')
print("단일 사용자:", user)
    
    # 모든 문서 가져오기
all_users = firestore_manager.get_all_documents('users')
print("모든 사용자:", all_users)
    
    # 조건 검색
# active_users = firestore_manager.query_documents('users', 'is_active', '==', True)
# print("활성 사용자:", active_users)
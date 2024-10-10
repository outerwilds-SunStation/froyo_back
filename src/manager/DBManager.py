from google.cloud import datastore

# 서비스 계정 키 파일 경로
service_account_key = 'keys/datastore-access-key.json'

# 서비스 계정을 사용하여 클라이언트 생성
client = datastore.Client.from_service_account_json(service_account_key)

# Datastore에 데이터를 저장하는 함수
def send_data(kind, id, param1, param2):
    key = client.key(kind, id)
    entity = datastore.Entity(key=key)
    entity.update({
        'intensity': param1,
        'seconds': param2
    })
    client.put(entity)
    print(f"데이터 저장 완료: {entity}")

def get_data(kind, id):
    key = client.key(kind, id)
    entity = client.get(key)
    if entity:
        print(f"데이터 조회 완료: {entity}")
        return entity
    else:
        print(f"데이터를 찾을 수 없습니다: kind='{kind}', id='{id}'")
        return None

# 'test' 종류에 ID 5634161670881280인 데이터 추가
# send_data('is-2-II', 5634161670881280, 'qq', 'ww')
fetched_data = get_data('is-2-II', 5634161670881280)
from fastapi.testclient import TestClient
from server.main import app
from server import auth

client = TestClient(app)
app.dependency_overrides[auth.get_current_user] = lambda: {'sub': '000000000000000000000000'}

def run(topic: str):
    payload = {
        'topic': topic,
        'difficulty': 'Beginner',
        'subject': 'General',
        'contentType': 'Study Notes',
        'learningObjectives': []
    }
    r = client.post('/content/generate', json=payload)
    print('TOPIC', topic)
    print('STATUS', r.status_code)
    try:
        d = r.json()
    except Exception:
        print('BODY (non-json)', r.text)
        return
    print('ID', d.get('id'))
    content = d.get('content', '')
    print('CONTENT_LEN', len(content))
    print('CONTENT_HEAD', content[:120].replace('\n',' '))
    print('-'*60)

if __name__ == '__main__':
    for t in ['Photosynthesis basics', 'World War II overview', 'Machine learning introduction']:
        run(t)

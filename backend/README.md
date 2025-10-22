
# İcra Takip API (FastAPI)

## Geliştirme
```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```
- Varsayılan olarak SQLite (icra.db) ile başlar. Docker ile Postgres kullanılır.

## Auth
- Token alma:
  ```
  POST /auth/token
  form: username=ADMIN_EMAIL, password=ADMIN_PASSWORD
  ```
- .env'den admin otomatik seed edilir.

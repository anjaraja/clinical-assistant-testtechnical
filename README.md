# Clinical Assistant - Test Technical Anjar Pratama

## Tools
```
- Docker
	- Python
	- Postgresql with pgvector extension
```

## Library
```
- fastapi
- uvicorn
- openai
- httpx
- sqlalchemy
- psycopg2-binary
- pgvector
- python-docx
- pydantic
- psycopg[binary]
- python-multipart
```

## Project Configuration
```
- copy .env.example and rename to .env
- Login into google account
- Create Gemini API Key using this link https://aistudio.google.com/api-keys
- Input name for this API Key, Choose 'Default Gemini Project'
- Copy value from "API Key" section. or click "Copy Key" at the bottom of popup window.
- Paste to .env as value of GEMINI_API_KEY
```

## Run

### Go to app directory
```
cd clinical_assistant
```

### Run App using Docker
```
docker compose build

docker compose up -d
```
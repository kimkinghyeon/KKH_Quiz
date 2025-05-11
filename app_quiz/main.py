from fastapi import FastAPI
from app.db.base import Base
from app.db.session import engine
from app.api import auth, admin_quiz, quiz

# 모델 메타데이터에 맞춰 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Quiz 응시 시스템")

# 라우터 등록
app.include_router(auth.router)
app.include_router(admin_quiz.router)
app.include_router(quiz.router)
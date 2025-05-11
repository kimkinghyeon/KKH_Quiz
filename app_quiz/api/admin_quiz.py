from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app import schemas, crud, models
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/quiz", tags=["quiz"])

@router.get("/", response_model=List[schemas.QuizRead])
def list_quizzes(
    status: str = Query("all", enum=["all","submitted","not_submitted"]),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    return crud.get_user_quiz_status(user.id, status, db)

@router.get("/{quiz_id}", response_model=schemas.QuizRead)
def get_quiz(quiz_id: UUID, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    # 페이징 포함 상세
    pass

@router.post("/{quiz_id}/start")
def start_quiz(quiz_id: UUID, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    # 랜덤 문제 캐싱
    pass

@router.post("/{quiz_id}/submit", response_model=schemas.SubmissionRead)
def submit_quiz(quiz_id: UUID, submission_in: schemas.SubmissionCreate, db: Session = Depends(get_db), user: models.User = Depends(get_current_user)):
    # 저장 및 채점
    pass
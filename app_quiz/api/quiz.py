from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app_quiz import schemas, crud, models
from app_quiz.dependencies import get_db, get_current_user

router = APIRouter(prefix="/quiz", tags=["quiz"])

# 1) 사용자 퀴즈 목록 및 응시 상태 조회
@router.get("/", response_model=List[schemas.QuizStatus])
def list_quizzes(
    status: str = Query("all", enum=["all", "submitted", "not_submitted"]),
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    return crud.get_user_quiz_status(user.id, status, db)

# 2) 퀴즈 상세 조회
@router.get("/{quiz_id}", response_model=schemas.QuizRead)
def get_quiz_detail(
    quiz_id: UUID,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    quiz = crud.get_quiz(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

# 3) 퀴즈 응시 시작
@router.post("/{quiz_id}/start", response_model=schemas.QuizSessionRead)
def start_quiz(
    quiz_id: UUID,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    session, questions = crud.start_quiz_session(db, quiz_id, user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return schemas.QuizSessionRead(session_id=session.id, questions=questions)

# 4) 답안 제출 및 채점
@router.post("/{quiz_id}/submit", response_model=schemas.SubmissionRead)
def submit_quiz(
    quiz_id: UUID,
    submission_in: schemas.SubmissionCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user)
):
    submission = crud.submit_quiz(db, submission_in.session_id, user.id, submission_in.answers)
    if not submission:
        raise HTTPException(status_code=400, detail="Invalid session or already submitted")
    return submission
import random
from uuid import UUID
from sqlalchemy.orm import Session
from typing import List, Tuple
from app_quiz import models, schemas

# 사용자별 퀴즈 응시 상태 조회
def get_user_quiz_status(user_id: UUID, status: str, db: Session):
    all_quizzes = db.query(models.Quiz).all()
    result = []
    for quiz in all_quizzes:
        sub = db.query(models.Submission).filter_by(user_id=user_id, quiz_id=quiz.id).first()
        is_sub = sub is not None
        if status == 'submitted' and not is_sub:
            continue
        if status == 'not_submitted' and is_sub:
            continue
        result.append(schemas.QuizStatus(
            quiz_id=quiz.id,
            title=quiz.title,
            submitted=is_sub,
            submitted_at=sub.created_at if is_sub else None,
            score=sub.score if is_sub else None
        ))
    return result

# 퀴즈 상세 조회
def get_quiz(db: Session, quiz_id: UUID):
    return db.query(models.Quiz).filter(models.Quiz.id == quiz_id).first()

# 퀴즈 응시 세션 시작: 문제/선택지 순서 DB 저장
def start_quiz_session(db: Session, quiz_id: UUID, user_id: UUID) -> Tuple[models.QuizSession, List[schemas.QuestionRead]]:
    quiz = get_quiz(db, quiz_id)
    if not quiz:
        return None, []
    qs = db.query(models.Question).filter_by(quiz_id=quiz_id).all()
    if quiz.randomize:
        random.shuffle(qs)
    selected = qs[: quiz.question_limit]
    q_order = [str(q.id) for q in selected]
    c_order = {}
    for q in selected:
        choices = db.query(models.Choice).filter_by(question_id=q.id).all()
        if quiz.randomize:
            random.shuffle(choices)
        c_order[str(q.id)] = [str(c.id) for c in choices]
    session = models.QuizSession(user_id=user_id, quiz_id=quiz_id, question_order=q_order, choices_order=c_order)
    db.add(session)
    db.commit()
    db.refresh(session)
    # 반환할 QuestionRead 리스트 생성
    output = []
    for qid in q_order:
        q = db.query(models.Question).get(qid)
        choices = []
        for cid in c_order[qid]:
            c = db.query(models.Choice).get(cid)
            choices.append(schemas.ChoiceRead(id=c.id, text=c.text))
        output.append(schemas.QuestionRead(id=q.id, text=q.text, choices=choices))
    return session, output

# 답안 제출 및 채점
def submit_quiz(db: Session, session_id: UUID, user_id: UUID, answers: List[schemas.AnswerCreate]):
    session = db.query(models.QuizSession).filter_by(id=session_id, user_id=user_id).first()
    if not session:
        return None
    submission = models.Submission(user_id=user_id, quiz_id=session.quiz_id)
    db.add(submission)
    db.commit()
    db.refresh(submission)
    correct = 0
    for ans in answers:
        db.add(models.Answer(submission_id=submission.id, question_id=ans.question_id, choice_id=ans.choice_id))
        choice = db.query(models.Choice).filter_by(id=ans.choice_id).first()
        if choice and choice.is_answer:
            correct += 1
    submission.score = correct / len(answers) * 100
    db.commit()
    return submission
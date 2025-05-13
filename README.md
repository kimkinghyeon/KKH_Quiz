# Quiz 응시 시스템

## 📋 개요
Quiz 응시 시스템은 관리자와 사용자가 퀴즈를 생성·수정·삭제하고, 사용자는 실제로 퀴즈를 응시하고 채점 결과를 확인할 수 있는 API 서비스입니다. FastAPI, PostgreSQL를 사용하여 모듈화된 설계로 구현되었습니다.

---

## 💻 주요 기능

1. **인증/인가 (JWT 기반)**
   - 회원 가입, 로그인
   - 관리자(Admin) / 일반 사용자(User) 역할 분리

2. **관리자 기능**
   - 퀴즈 생성/수정/삭제
   - 문제(Question) 및 선택지(Choice) CRUD
   - 퀴즈별 문제 출제 수 및 랜덤 배치 설정

3. **사용자 기능**
   - 퀴즈 목록 조회(응시 여부 포함)
   - 퀴즈 상세 조회(문제 페이징)
   - 퀴즈 응시 시작(랜덤 문제 및 선택지 캐싱)
   - 답안 제출 및 자동 채점
   - 응시 이력 확인(API: `/quiz/me`)

4. **문서화**
   - OpenAPI(Swagger)를 통한 자동 문서 제공 (`/docs`, `/redoc`)

5. **최적화**
   - **DB 기반 세션 저장**: 응시 시작 시 생성된 문제 배치 및 선택지 순서를 PostgreSQL 테이블에 저장하여 새로고침해도 동일 구성 유지

## 1. 인증 및 인가 (Auth)

### 1.1 회원 가입

- **경로**: POST /auth/signup

- **권한**: 공개

- **설명**: 이메일과 비밀번호로 신규 사용자(관리자/일반) 계정을 생성하고 JWT 토큰을 발급합니다.

| 구분              | 내용                                                       |
|-------------------|------------------------------------------------------------|
| Request Body      | UserCreate```json
{

"email": "user@example.com",

"password": "your_password"

}

### 1.2 로그인 (토큰 발급)

- **경로**: `POST /auth/token`
- **권한**: 공개
- **설명**: 기존 사용자 자격 증명으로 JWT 액세스 토큰을 발급합니다.

| 구분              | 내용                                                       |
|-------------------|------------------------------------------------------------|
| Request Form      | `OAuth2PasswordRequestForm`<br>```
username: user@example.com
password: your_password
```        |
| Response (200)    | `Token` (회원가입 응답과 동일)                              |

---

## 2. 관리자 전용 API (/admin/quiz)
관리자 계정만 접근 가능합니다.

### 2.1 퀴즈 생성

- **경로**: `POST /admin/quiz/`
- **권한**: 관리자
- **설명**: 새 퀴즈(시험지)를 문제 및 선택지와 함께 생성합니다.

| 구분              | 내용                                                          |
|-------------------|---------------------------------------------------------------|
| Request Body      | `QuizCreate`<br>```json
{
  "title": "Python 기초 테스트",
  "description": "기본 문법 및 자료구조",
  "question_limit": 10,
  "randomize": true,
  "questions": [
    {
      "text": "파이썬의 리스트 리터럴 표기법은?",
      "choices": [
        {"text": "(1, 2, 3)", "is_answer": false},
        {"text": "[1, 2, 3]", "is_answer": true},
        {"text": "{1, 2, 3}", "is_answer": false}
      ]
    }
    // ...더 많은 문제
  ]
}
```        |
| Response (200)    | `QuizRead` (생성된 퀴즈 ID 포함)                              |

### 2.2 퀴즈 수정

- **경로**: `PUT /admin/quiz/{quiz_id}`
- **권한**: 관리자
- **설명**: 퀴즈 제목, 설명, 문제 수 제한, 랜덤 배치 설정을 변경합니다.

| 구분              | 내용           |
|-------------------|----------------|
| Path Parameter    | `quiz_id` (UUID) |
| Request Body      | `QuizBase`<br>```json
{
  "title": "새 제목",
  "description": "변경된 설명",
  "question_limit": 5,
  "randomize": false
}
```|
| Response (200)    | `QuizRead`     |

### 2.3 퀴즈 삭제

- **경로**: `DELETE /admin/quiz/{quiz_id}`
- **권한**: 관리자
- **설명**: 지정한 퀴즈를 삭제합니다.

| 구분           | 내용            |
|----------------|-----------------|
| Path Parameter | `quiz_id` (UUID) |
| Response (204) | No Content      |

### 2.4 퀴즈 목록 조회

- **경로**: `GET /admin/quiz/`
- **권한**: 관리자
- **설명**: 페이징된 전체 퀴즈 목록을 조회합니다.

| 구분              | 내용                       |
|-------------------|----------------------------|
| Query Parameter   | `page`, `limit` (선택)     |
| Response (200)    | `List[QuizRead]`           |

---

## 3. 사용자 API (/quiz)
관리자 및 일반 사용자 공통 사용 가능.

### 3.1 퀴즈 목록 및 응시 상태

- **경로**: `GET /quiz/`
- **권한**: 로그인된 사용자
- **설명**: 사용자가 `응시한`/`응시하지 않은` 퀴즈를 상태별로 필터링하여 조회합니다.

| 구분              | 내용                                    |
|-------------------|-----------------------------------------|
| Query Parameter   | `status`: `all`/`submitted`/`not_submitted` (기본: `all`) |
| Response (200)    | `List[QuizStatus]`<br>```json
[
  {
    "quiz_id": "...",
    "title": "Python 기초",
    "submitted": true,
    "submitted_at": "2025-05-12T10:00:00",
    "score": 85.0
  },
  {
    "quiz_id": "...",
    "title": "FastAPI 심화",
    "submitted": false,
    "submitted_at": null,
    "score": null
  }
]
```|

### 3.2 퀴즈 상세 조회

- **경로**: `GET /quiz/{quiz_id}`
- **권한**: 로그인된 사용자
- **설명**: 퀴즈 제목·설명·총 문제 수·랜덤 설정 등을 반환합니다. 문제는 `/start`를 통해 발급.

| 구분              | 내용                                |
|-------------------|-------------------------------------|
| Path Parameter    | `quiz_id` (UUID)                    |
| Response (200)    | `QuizRead`<br>```json
{
  "id": "...",
  "title": "...",
  "description": "...",
  "question_limit": 10,
  "randomize": true
}
```|

### 3.3 퀴즈 응시 시작

- **경로**: `POST /quiz/{quiz_id}/start`
- **권한**: 로그인된 사용자
- **설명**: DB에 세션(`QuizSession`)을 생성하고, 랜덤 문제 및 선택지 순서를 반환합니다.

| 구분              | 내용                                      |
|-------------------|-------------------------------------------|
| Path Parameter    | `quiz_id` (UUID)                          |
| Response (200)    | `QuizSessionRead`<br>```json
{
  "session_id": "...",
  "questions": [
    {"id": "q1","text":"...","choices":[...]},
    // ...
  ]
}
```|

### 3.4 답안 제출 및 자동 채점

- **경로**: `POST /quiz/{quiz_id}/submit`
- **권한**: 로그인된 사용자
- **설명**: 세션 ID와 사용자 답안을 저장하고 자동으로 채점 후 점수를 반환합니다.

| 구분              | 내용                                                        |
|-------------------|-------------------------------------------------------------|
| Path Parameter    | `quiz_id` (UUID)                                            |
| Request Body      | `SubmissionCreate`<br>```json
{
  "session_id": "...",
  "answers": [
    {"question_id":"q1","choice_id":"c2"},
    // ...
  ]
}
```|
| Response (200)    | `SubmissionRead`<br>```json
{
  "id": "...",
  "created_at": "2025-05-13T14:00:00",
  "score": 90.0
}
```|

---

### 참고
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

from fastapi import FastAPI, Form, UploadFile, File
from sqlalchemy.exc import IntegrityError
from database import SessionLocal, engine
import models
from auth import hash_password, verify_password
from rag import generate_answers
from fastapi.responses import FileResponse
from export import export_answers_to_docx

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post("/signup")
def signup(email: str = Form(...), password: str = Form(...)):
    db = SessionLocal()

    user = models.User(
        email=email,
        password=hash_password(password)
    )

    db.add(user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return {"error": "Email already registered"}

    return {"message": "User created successfully"}


@app.post("/login")
def login(email: str = Form(...), password: str = Form(...)):
    db = SessionLocal()
    user = db.query(models.User).filter_by(email=email).first()

    if not user or not verify_password(password, user.password):
        return {"error": "Invalid credentials"}

    return {"message": "Login successful"}


@app.post("/upload_reference")
def upload_reference(file: UploadFile = File(...)):
    content = file.file.read().decode()

    db = SessionLocal()

    doc = models.Document(
        filename=file.filename,
        content=content,
        user_id=1
    )

    db.add(doc)
    db.commit()

    return {"message": "Reference uploaded"}


@app.post("/upload_questionnaire")
def upload_questionnaire(file: UploadFile = File(...)):
    content = file.file.read().decode()

    db = SessionLocal()

    questionnaire = models.Questionnaire(
        content=content,
        user_id=1
    )

    db.add(questionnaire)
    db.commit()

    return {"message": "Questionnaire uploaded"}


@app.post("/generate")
def generate():
    db = SessionLocal()

    questionnaire = db.query(models.Questionnaire).first()

    if not questionnaire:
        return {"error": "No questionnaire uploaded"}

    questions = questionnaire.content.split("\n")
    reference_docs = db.query(models.Document).all()

    if not reference_docs:
        return {"error": "No reference documents uploaded"}

    results = generate_answers(questions, reference_docs)

    answered_count = 0
    not_found_count = 0

    for r in results:
        if r["citation"] == "None":
            not_found_count += 1
        else:
            answered_count += 1

        ans = models.Answer(
            question=r["question"],
            answer=r["answer"],
            citation=r["citation"],
            confidence=r["confidence"],
            questionnaire_id=questionnaire.id
        )
        db.add(ans)

    db.commit()

    total_questions = len(results)

    coverage_percentage = (
        round((answered_count / total_questions) * 100, 2)
        if total_questions > 0 else 0
    )

    summary = {
        "total_questions": total_questions,
        "answered": answered_count,
        "not_found": not_found_count,
        "coverage_percentage": coverage_percentage
    }

    return {
        "summary": summary,
        "results": results
    }

@app.get("/answers")
def get_answers():
    db = SessionLocal()
    answers = db.query(models.Answer).all()

    return [
        {
            "id": a.id,
            "question": a.question,
            "answer": a.answer,
            "citation": a.citation,
            "confidence": a.confidence
        }
        for a in answers
    ]


@app.put("/answers/{answer_id}")
def update_answer(answer_id: int, new_answer: str = Form(...)):
    db = SessionLocal()

    answer = db.query(models.Answer).filter_by(id=answer_id).first()

    if not answer:
        return {"error": "Answer not found"}

    answer.answer = new_answer
    db.commit()

    return {"message": "Answer updated successfully"}

@app.post("/export")
def export_document():
    file_path = export_answers_to_docx()
    return FileResponse(
        path=file_path,
        filename="Questionnaire_Answers.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
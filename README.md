# Structured Questionnaire Answering Tool
GTM Engineering Internship Assignment

## Overview

This project is a Structured Questionnaire Answering Tool designed to automate the process of completing vendor, security, or compliance questionnaires using internal documentation as the source of truth.

The system allows authenticated users to upload:

- A structured questionnaire
- Reference documents (internal policies, security docs, operational manuals)

It then automatically:

- Parses questions
- Retrieves relevant reference content
- Generates grounded answers
- Attaches citations
- Calculates answer coverage
- Allows manual review and editing
- Exports a structured document preserving the original format

The solution is built as a backend-first system focusing on workflow clarity and reliability.

---
## Core Workflow

### Phase 1 – AI-Powered Answer Generation

1. User signs up and logs in.
2. User uploads:
   - A questionnaire document (text-based)
   - Reference documents (source-of-truth content)
3. The system:
   - Splits questionnaire into individual questions
   - Chunks reference documents
   - Generates embeddings using a local embedding model
   - Performs semantic similarity search (FAISS)
   - Retrieves relevant context
   - Generates a grounded answer for each question
   - Attaches citations
   - Returns “Not found in references.” when unsupported
   - Calculates coverage metrics

Output includes:
- Question
- Generated Answer
- Citation(s)
- Confidence
- Coverage summary

---

### Phase 2 – Review & Export

After generation:

- Users can retrieve all generated answers.
- Users can manually edit answers before export.
- The system generates a downloadable `.docx` file.
- The exported file:
  - Preserves original question order
  - Keeps questions unchanged
  - Inserts answers directly below each question
  - Includes citations

This ensures structured, production-ready output.

---

## Technical Architecture

### Backend
- FastAPI
- SQLite (persistent storage)

### AI & Retrieval
- Sentence Transformers (`all-MiniLM-L6-v2`)
- FAISS vector store
- Retrieval-based grounded answering

### Document Export
- python-docx

---

## Database Structure

- Users
- Questionnaires
- Reference Documents
- Generated Answers

Answers are stored persistently and editable before export.

---

## Assumptions

- Questionnaire is newline-separated questions.
- Reference documents are trusted source-of-truth.
- Only one active questionnaire per user session.
- Simple text format is sufficient for demonstration.
- Authentication is session-less and simplified.

---

## Trade-offs

1. Retrieval-based answering instead of generative LLM
   - Chosen for stability, reproducibility, and offline capability.
   - Avoids external API dependencies and quota issues.

2. Simplified questionnaire parsing
   - Assumes clean question formatting.
   - Does not include complex PDF parsing logic.

3. SQLite instead of production database
   - Suitable for demo and local testing.
   - Easily replaceable with PostgreSQL in production.

4. Minimal UI
   - Swagger used for interaction.
   - Focused on workflow clarity rather than UI polish.

---

## Coverage Metrics

The system calculates:

- Total questions
- Answered questions
- Unsupported questions
- Coverage percentage

This provides transparency into answer completeness.

---

## What I Would Improve With More Time

- Multi-user session isolation
- Role-based access control
- Advanced PDF parsing
- True generative answer synthesis with citation alignment
- Frontend dashboard for review
- Version history for edited answers
- Cloud deployment with PostgreSQL
- Audit logs for compliance traceability

---

## How to Run Locally

1. Create virtual environment
2. Install dependencies:
   pip install -r requirements.txt
3. Run server:
   uvicorn main:app --reload
4. Visit:
   http://127.0.0.1:8000/docs

---

## Conclusion

This project demonstrates:

- End-to-end workflow design
- AI-assisted document retrieval
- Grounded answer generation
- Structured data handling
- Editable review pipeline
- Export-ready formatting

The focus was on building a reliable, structured, and explainable system rather than a UI-heavy prototype.
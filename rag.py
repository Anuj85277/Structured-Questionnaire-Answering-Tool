from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings



def generate_answers(questions, reference_docs):

    # Local embedding model (FREE)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )

    docs = []

    for doc in reference_docs:
        chunks = splitter.split_text(doc.content)

        for chunk in chunks:
            docs.append(
                Document(
                    page_content=chunk,
                    metadata={"source": doc.filename}
                )
            )

    # Create vector store
    vectorstore = FAISS.from_documents(docs, embeddings)

    results = []

    for question in questions:

        retrieved = vectorstore.similarity_search(question, k=3)

        context = "\n\n".join([r.page_content for r in retrieved])
        sources = list(set([r.metadata["source"] for r in retrieved]))

        # Simple grounded answer generation (no LLM)
        if not context.strip():
            answer = "Not found in references."
            citation = "None"
            confidence = "Low"
        else:
            answer = context[:400]  # Simple extraction-based answer
            citation = ", ".join(sources)
            confidence = "Medium"

        results.append({
            "question": question,
            "answer": answer,
            "citation": citation,
            "confidence": confidence,
            "evidence": context[:300]
        })

    return results
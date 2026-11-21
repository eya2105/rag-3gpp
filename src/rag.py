from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from config import EMBEDDING_MODEL, FAISS_DIR
from src.llm import get_groq_model


def get_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        encode_kwargs={"normalize_embeddings": True},
    )


def chunks_to_documents(chunks) -> list[Document]:
    return [
        Document(
            page_content=chunk.text,
            metadata={
                "id": chunk.id,
                "spec": chunk.spec,
                "release": chunk.release,
                "version": chunk.version,
                "section": chunk.section,
                "title": chunk.title,
                "breadcrumb": chunk.breadcrumb,
            },
        )
        for chunk in chunks
    ]


def build_faiss_index(chunks) -> FAISS:
    documents = chunks_to_documents(chunks)
    index = FAISS.from_documents(documents, get_embeddings())
    FAISS_DIR.mkdir(parents=True, exist_ok=True)
    index.save_local(str(FAISS_DIR))
    return index


def load_faiss_index() -> FAISS:
    if not (FAISS_DIR / "index.faiss").exists():
        raise FileNotFoundError(
            f"FAISS index not found at {FAISS_DIR}. Run scripts/build_index.py first."
        )
    return FAISS.load_local(
        str(FAISS_DIR),
        get_embeddings(),
        allow_dangerous_deserialization=True,
    )


def answer_question(
    question: str,
    limit: int = 5,
    model: str | None = None,
) -> str:
    answer, _ = answer_question_with_sources(question, limit, model)
    return answer


def answer_question_with_sources(
    question: str,
    limit: int = 5,
    model: str | None = None,
    history: list[dict[str, str]] | None = None,
) -> tuple[str, list[Document]]:
    index = load_faiss_index()
    documents = index.similarity_search(question, k=limit)
    context = "\n\n".join(
        f"[{document.metadata['id']}] "
        f"{document.metadata['spec']} {document.metadata['release']} "
        f"{document.metadata['section']} - {document.metadata['title']}:\n"
        f"{document.page_content}"
        for document in documents
    )

    history_text = ""
    if history:
        history_text = "\n".join(
            f"{message['role'].capitalize()}: {message['content']}"
            for message in history[-6:]
        )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "Answer using only the provided 3GPP context. "
            "If the context is insufficient, say so. "
            "Cite relevant chunk IDs in square brackets.",
        ),
        (
            "human",
            "Conversation history:\n{history}\n\n"
            "Context:\n{context}\n\nQuestion:\n{question}",
        ),
    ])
    chain = prompt | get_groq_model(model) | StrOutputParser()
    answer = chain.invoke({
        "history": history_text or "No previous messages.",
        "context": context,
        "question": question,
    })
    return answer, documents

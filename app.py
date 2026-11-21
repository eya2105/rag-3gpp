import html
import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT))

from src.database import (
    add_message,
    create_conversation,
    get_messages,
    init_db,
    list_conversations,
    update_conversation_title,
)
from src.rag import answer_question_with_sources


st.set_page_config(
    page_title="3GPP Knowledge",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

st.markdown(
    """
    <style>
    :root {
        --ink: #17191d;
        --muted: #6b7078;
        --line: #e8eaee;
        --surface: #f7f8fa;
        --accent: #2457d6;
    }

    [data-testid="stAppViewContainer"] {
        background: #ffffff;
    }

    [data-testid="stSidebar"] {
        background: #f7f8fa;
        border-right: 1px solid var(--line);
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.35rem;
    }

    [data-testid="stSidebarUserContent"] {
        padding: 0 0.55rem;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    .block-container {
        max-width: 860px;
        padding-top: 2.4rem;
        padding-bottom: 8rem;
    }

    .sidebar-title {
        color: var(--ink);
        font-size: 0.78rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin: 0.1rem 0.25rem 1rem 0.25rem;
    }

    [data-testid="stSidebar"] [data-testid="stButton"] button {
        width: 100%;
        min-height: 42px;
        justify-content: flex-start;
        border: 1px solid transparent;
        border-radius: 9px;
        background: transparent;
        color: #4d5259;
        font-size: 0.86rem;
        text-align: left;
        box-shadow: none;
        padding: 0.5rem 0.75rem;
    }

    [data-testid="stSidebar"] [data-testid="stButton"] button:hover {
        border: 1px solid var(--line);
        background: #ffffff;
        color: var(--ink);
    }

    [data-testid="stSidebar"] [data-testid="stButton"] button:focus-visible {
        outline: 3px solid rgba(36, 87, 214, 0.16);
        outline-offset: 1px;
    }

    .new-chat [data-testid="stButton"] button {
        border: 1px solid var(--line) !important;
        background: #ffffff !important;
        color: var(--ink) !important;
        font-weight: 700;
        margin-bottom: 1rem;
    }

    [data-testid="stChatMessage"] {
        border: 0;
        background: transparent;
        padding-left: 0;
        padding-right: 0;
    }

    [data-testid="stChatMessage"]:nth-of-type(odd) {
        background: transparent;
    }

    [data-testid="stChatMessageContent"] {
        border-radius: 12px;
        color: var(--ink);
    }

    [data-testid="stChatInput"] {
        max-width: 860px;
        margin: 0 auto;
    }

    [data-testid="stChatInput"] textarea {
        border: 1px solid var(--line) !important;
        border-radius: 14px !important;
        background: #ffffff !important;
        box-shadow: 0 10px 36px rgba(20, 25, 35, 0.08) !important;
    }

    [data-testid="stChatInput"] textarea:focus {
        border-color: #bac7e8 !important;
        box-shadow: 0 0 0 3px rgba(36, 87, 214, 0.08),
                    0 10px 36px rgba(20, 25, 35, 0.08) !important;
    }

    .empty-state {
        max-width: 620px;
        margin: 14vh auto 0 auto;
        text-align: left;
    }

    .empty-state h1 {
        color: var(--ink);
        font-size: 2.7rem;
        line-height: 1.05;
        letter-spacing: -0.045em;
        margin: 0 0 1rem 0;
    }

    .empty-state p {
        color: var(--muted);
        line-height: 1.65;
        max-width: 520px;
    }

    .source-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 0.65rem;
        margin-top: 0.9rem;
    }

    .source {
        background: var(--surface);
        border: 1px solid #eff0f2;
        border-radius: 9px;
        padding: 0.75rem 0.85rem;
        min-height: 96px;
    }

    .source-id {
        color: var(--accent);
        font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
        font-size: 0.72rem;
        font-weight: 750;
        margin-bottom: 0.35rem;
    }

    .source-title {
        color: var(--ink);
        font-size: 0.82rem;
        font-weight: 720;
        line-height: 1.35;
        margin-bottom: 0.25rem;
    }

    .source-text {
        color: var(--muted);
        font-size: 0.75rem;
        line-height: 1.42;
    }

    @media (max-width: 720px) {
        .block-container {
            padding: 1.1rem 0.75rem 7rem 0.75rem;
        }

        .empty-state {
            margin-top: 8vh;
        }

        .empty-state h1 {
            font-size: 2.1rem;
        }

        .source-grid {
            grid-template-columns: 1fr;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def source_cards(sources: list[dict]) -> str:
    cards = []
    for source in sources:
        metadata = source.get("metadata", {})
        excerpt = source.get("text", "").replace("\n", " ")
        if len(excerpt) > 190:
            excerpt = excerpt[:187].rstrip() + "..."
        cards.append(
            '<div class="source">'
            f'<div class="source-id">{html.escape(str(metadata.get("id", "")))}</div>'
            f'<div class="source-title">'
            f'{html.escape(str(metadata.get("spec", "")))}'
            f' · {html.escape(str(metadata.get("section", "")))}</div>'
            f'<div class="source-text">'
            f'{html.escape(str(metadata.get("title", "")))}<br>'
            f'{html.escape(excerpt)}</div>'
            '</div>'
        )
    return '<div class="source-grid">' + "".join(cards) + "</div>"


def conversation_title(question: str) -> str:
    title = " ".join(question.split())
    return title[:48] + ("..." if len(title) > 48 else "")


if "active_conversation_id" not in st.session_state:
    st.session_state.active_conversation_id = None

conversations = list_conversations()

with st.sidebar:
    st.markdown('<div class="sidebar-title">Conversations</div>', unsafe_allow_html=True)
    st.markdown('<div class="new-chat">', unsafe_allow_html=True)
    if st.button("+ New conversation", use_container_width=True):
        st.session_state.active_conversation_id = None
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    if not conversations:
        st.caption("No saved conversations")
    else:
        for conversation in conversations:
            selected = (
                st.session_state.active_conversation_id == conversation["id"]
            )
            label = conversation["title"]
            if st.button(
                label,
                key=f"conversation-{conversation['id']}",
                use_container_width=True,
                type="primary" if selected else "secondary",
            ):
                st.session_state.active_conversation_id = conversation["id"]
                st.rerun()


active_id = st.session_state.active_conversation_id

if active_id is None:
    st.markdown(
        '<div class="empty-state">'
        '<h1>Ask across the 5G specifications.</h1>'
        '<p>Questions are grounded in TS 23.501 and TS 24.501, '
        'with the retrieved source sections attached to each answer.</p>'
        '</div>',
        unsafe_allow_html=True,
    )
else:
    messages = get_messages(active_id)
    if not messages:
        st.markdown(
            '<div class="empty-state">'
            '<h1>Start this conversation.</h1>'
            '<p>Ask a technical question about the 5G core or NAS protocol.</p>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        for message in messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message["role"] == "assistant" and message["sources"]:
                    st.markdown(
                        source_cards(message["sources"]),
                        unsafe_allow_html=True,
                    )


prompt = st.chat_input("Ask about the 3GPP specifications")

if prompt:
    prompt = prompt.strip()
    if prompt:
        if active_id is None:
            active_id = create_conversation(conversation_title(prompt))
            st.session_state.active_conversation_id = active_id
            history = []
        else:
            history = [
                {"role": message["role"], "content": message["content"]}
                for message in get_messages(active_id)
            ]

        add_message(active_id, "user", prompt)

        with st.spinner("Searching specifications"):
            try:
                answer, documents = answer_question_with_sources(
                    prompt,
                    limit=5,
                    history=history,
                )
                sources = [
                    {
                        "metadata": document.metadata,
                        "text": document.page_content,
                    }
                    for document in documents
                ]
                add_message(active_id, "assistant", answer, sources)
                if len(history) == 0:
                    update_conversation_title(
                        active_id,
                        conversation_title(prompt),
                    )
            except Exception as error:
                add_message(
                    active_id,
                    "assistant",
                    f"I could not answer this question: {error}",
                )

        st.rerun()

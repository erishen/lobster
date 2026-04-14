"""Lobster Web UI - Streamlit Application"""

import streamlit as st
from datetime import datetime
from pathlib import Path
import json
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

st.set_page_config(
    page_title="Lobster - OpenClaw Assistant",
    page_icon="🦞",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🦞 Lobster - OpenClaw Assistant")
st.markdown("---")

MEMORY_STORE_PATH = Path.cwd() / ".lobster_memory"
HISTORY_DIR = Path.cwd() / ".lobster_history"


def init_session_state():
    """Initialize session state variables"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "model" not in st.session_state:
        st.session_state.model = "ollama/gemma3"
    if "with_memory" not in st.session_state:
        st.session_state.with_memory = False
    if "llm" not in st.session_state:
        try:
            from langchain_llm_toolkit import LLMIntegration

            st.session_state.llm = LLMIntegration()
            st.session_state.llm.set_model(st.session_state.model)
        except Exception:
            st.session_state.llm = None


def get_available_models():
    """Get list of available models"""
    try:
        import requests

        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [f"ollama/{m['name']}" for m in models]
    except Exception:
        pass
    return ["ollama/gemma3", "ollama/llama3.1:8b", "ollama/deepseek-r1:7b"]


def chat_page():
    """Chat interface page"""
    st.header("💬 Chat with OpenClaw")

    col1, col2 = st.columns([3, 1])
    with col2:
        st.session_state.model = st.selectbox(
            "Model", get_available_models(), index=0, key="model_select"
        )
        st.session_state.with_memory = st.checkbox(
            "Enable Memory", value=st.session_state.with_memory
        )

        if st.button("Clear Chat", key="clear_chat"):
            st.session_state.messages = []
            st.rerun()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Type your message..."):
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")

            try:
                if st.session_state.llm is None:
                    from langchain_llm_toolkit import LLMIntegration

                    st.session_state.llm = LLMIntegration()
                    st.session_state.llm.set_model(st.session_state.model)

                enhanced_prompt = prompt

                if st.session_state.with_memory:
                    try:
                        from langchain_llm_toolkit import RAGSystem

                        index_file = MEMORY_STORE_PATH / "index.faiss"
                        if index_file.exists():
                            rag_system = RAGSystem(
                                vector_store_type="faiss",
                                embedding_type="ollama",
                                embedding_model="nomic-embed-text",
                                llm_model=st.session_state.model,
                            )
                            rag_system.load_vector_store(str(MEMORY_STORE_PATH))
                            memories = rag_system.retrieve_documents(prompt, k=3)

                            if memories:
                                memory_context = "\n\n[Relevant Memories]\n"
                                for i, mem in enumerate(memories, 1):
                                    memory_context += f"{i}. {mem.page_content}\n"
                                memory_context += "\n"
                                enhanced_prompt = f"{memory_context}[Current Question]\n{prompt}"
                    except Exception:
                        pass

                response = st.session_state.llm.generate(enhanced_prompt)
                message_placeholder.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

            except Exception as e:
                message_placeholder.markdown(f"❌ Error: {str(e)}")


def memory_page():
    """Memory management page"""
    st.header("🧠 Memory Management")

    tab1, tab2, tab3 = st.tabs(["Add Memory", "List Memories", "Search Memories"])

    with tab1:
        st.subheader("Add New Memory")
        content = st.text_area("Memory Content", height=100, key="memory_content")
        col1, col2 = st.columns(2)
        with col1:
            category = st.text_input("Category", value="general", key="memory_category")
        with col2:
            tags = st.text_input("Tags (comma-separated)", key="memory_tags")

        if st.button("Add Memory", key="add_memory_btn"):
            if content:
                try:
                    from langchain_llm_toolkit import RAGSystem
                    from langchain_core.documents import Document

                    MEMORY_STORE_PATH.mkdir(parents=True, exist_ok=True)

                    memory_id = datetime.now().strftime("%Y%m%d_%H%M%S")
                    timestamp = datetime.now().isoformat()

                    metadata = {
                        "id": memory_id,
                        "timestamp": timestamp,
                        "category": category,
                        "tags": [t.strip() for t in tags.split(",")] if tags else [],
                        "type": "memory",
                    }

                    rag_system = RAGSystem(
                        vector_store_type="faiss",
                        embedding_type="ollama",
                        embedding_model="nomic-embed-text",
                        llm_model="ollama/gemma3",
                    )

                    document = Document(page_content=content, metadata=metadata)

                    index_file = MEMORY_STORE_PATH / "index.faiss"
                    if index_file.exists():
                        rag_system.load_vector_store(str(MEMORY_STORE_PATH))
                        rag_system.add_documents([document])
                    else:
                        rag_system.create_vector_store([document])

                    rag_system.save_vector_store(str(MEMORY_STORE_PATH))

                    memory_index_file = Path.cwd() / ".lobster_memory_index.json"
                    if memory_index_file.exists():
                        with open(memory_index_file, "r") as f:
                            index_data = json.load(f)
                    else:
                        index_data = {"memories": []}

                    index_data["memories"].append(
                        {
                            "id": memory_id,
                            "content": content,
                            "timestamp": timestamp,
                            "category": category,
                            "tags": [t.strip() for t in tags.split(",")] if tags else [],
                        }
                    )

                    with open(memory_index_file, "w") as f:
                        json.dump(index_data, f, indent=2)

                    st.success(f"✅ Memory added successfully! ID: {memory_id}")
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("Please enter memory content")

    with tab2:
        st.subheader("Memory List")
        try:
            memory_index_file = Path.cwd() / ".lobster_memory_index.json"
            if memory_index_file.exists():
                with open(memory_index_file, "r") as f:
                    index_data = json.load(f)

                memories = index_data.get("memories", [])

                if memories:
                    for mem in reversed(memories):
                        with st.expander(
                            f"**{mem['id']}** - {mem['content'][:50]}...", expanded=False
                        ):
                            st.markdown(f"**Content:** {mem['content']}")
                            st.markdown(f"**Category:** {mem.get('category', 'general')}")
                            st.markdown(f"**Tags:** {', '.join(mem.get('tags', []))}")
                            st.markdown(f"**Timestamp:** {mem['timestamp']}")
                else:
                    st.info("No memories found")
            else:
                st.info("No memories found")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

    with tab3:
        st.subheader("Search Memories")
        query = st.text_input("Search Query", key="memory_search_query")

        if st.button("Search", key="search_memory_btn"):
            if query:
                try:
                    from langchain_llm_toolkit import RAGSystem

                    index_file = MEMORY_STORE_PATH / "index.faiss"
                    if index_file.exists():
                        rag_system = RAGSystem(
                            vector_store_type="faiss",
                            embedding_type="ollama",
                            embedding_model="nomic-embed-text",
                            llm_model="ollama/gemma3",
                        )
                        rag_system.load_vector_store(str(MEMORY_STORE_PATH))
                        results = rag_system.retrieve_documents(query, k=5)

                        if results:
                            st.markdown(f"**Found {len(results)} matching memories:**")
                            for i, doc in enumerate(results, 1):
                                metadata = doc.metadata
                                with st.expander(
                                    f"**Result {i}** - {doc.page_content[:50]}...", expanded=False
                                ):
                                    st.markdown(f"**Content:** {doc.page_content}")
                                    st.markdown(
                                        f"**Category:** {metadata.get('category', 'general')}"
                                    )
                                    st.markdown(
                                        f"**Tags:** {', '.join(metadata.get('tags', []))}"
                                    )
                                    st.markdown(
                                        f"**Timestamp:** {metadata.get('timestamp', 'N/A')}"
                                    )
                        else:
                            st.info("No matching memories found")
                    else:
                        st.info("No memories stored yet")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.warning("Please enter a search query")


def history_page():
    """Conversation history page"""
    st.header("📜 Conversation History")

    try:
        if not HISTORY_DIR.exists():
            st.info("No conversation history found")
            return

        conversations = []
        for file in HISTORY_DIR.glob("conversation_*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                conversations.append(
                    {
                        "filename": file.name,
                        "timestamp": data.get("timestamp", "Unknown"),
                        "message_count": len(data.get("messages", [])),
                        "preview": data.get("messages", [{}])[0].get("content", "")[:50]
                        if data.get("messages")
                        else "",
                        "data": data,
                    }
                )
            except Exception:
                continue

        conversations.sort(key=lambda x: x["timestamp"], reverse=True)

        if conversations:
            for conv in conversations:
                with st.expander(
                    f"**{conv['timestamp'][:19]}** - {conv['message_count']} messages - {conv['preview']}...",
                    expanded=False,
                ):
                    for msg in conv["data"].get("messages", []):
                        role = msg.get("role", "unknown")
                        content = msg.get("content", "")

                        if role == "user":
                            st.markdown(f"**👤 You:** {content}")
                        else:
                            st.markdown(f"**🤖 Assistant:** {content}")
                        st.markdown("---")
        else:
            st.info("No conversation history found")

    except Exception as e:
        st.error(f"❌ Error: {str(e)}")


def main():
    """Main application"""
    init_session_state()

    page = st.sidebar.radio(
        "Navigation",
        ["💬 Chat", "🧠 Memory", "📜 History"],
        index=0,
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Settings")
    st.sidebar.markdown(f"**Model:** {st.session_state.model}")
    st.sidebar.markdown(f"**Memory:** {'Enabled' if st.session_state.with_memory else 'Disabled'}")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.markdown(
        """
    **Lobster** is an AI assistant CLI tool
    built with LangChain and Ollama.

    - 📝 Memory Management
    - 💬 Interactive Chat
    - 📜 Conversation History
    - 🔍 RAG-based Search
    """
    )

    if page == "💬 Chat":
        chat_page()
    elif page == "🧠 Memory":
        memory_page()
    elif page == "📜 History":
        history_page()


if __name__ == "__main__":
    main()

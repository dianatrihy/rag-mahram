import streamlit as st
from database import GraphDatabaseDriver
from text_to_cypher import TextToCypher
from response_generator import ResponseGenerator
from detectors import (
    detect_type_1, detect_type_2, detect_type_3, detect_type_4
)
from extractors import extract_one_name, extract_two_names
from handlers.type1_handler import handle_type_1
from handlers.type2_handler import handle_type_2
from handlers.type3_handler import handle_type_3
from handlers.type4_handler import handle_type_4

def llm_reasoning(generator, data):
    question = data["question"]
    query = data["query"]
    query_result_str = data["result"]

    return generator(question, query, query_result_str)

# Page Configuration
st.set_page_config(page_title="Mahram Knowledge Graph", layout="centered")
st.title("🕌 Sistem Tanya Jawab Mahram")
st.markdown("Tanyakan tentang hukum pernikahan, daftar mahram, atau jalur kekerabatan.")

@st.cache_resource
def load_resources():
    # Load Schema
    with open("schema_mahram.txt") as fp:
        schema = fp.read().strip()
    
    # Init AI Components
    ttc = TextToCypher(schema)
    generator = ResponseGenerator(schema)
    
    # Init Database Driver
    driver = GraphDatabaseDriver() 
    
    return driver, ttc, generator

try:
    driver, ttc, generator = load_resources()
except Exception as e:
    st.error(f"Error connecting to database or loading models: {e}")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if question := st.chat_input("Masukkan pertanyaan Anda..."):
    st.chat_message("user").write(question)
    st.session_state.messages.append({"role": "user", "content": question})

    response_text = ""
    processed = False

    try:
        # TIPE 1 - CEK BOLEH MENIKAH
        if detect_type_1(question):
            name1, name2 = extract_two_names(driver, question)
            if name1 and name2:
                data = handle_type_1(driver, name1, name2)
                response_text = llm_reasoning(generator, data)
                processed = True
            else:
                response_text = "Maaf, dua nama tidak terdeteksi. Mencoba menggunakan RAG murni."
                processed = False

        # TIPE 4 - MAHRAM PERSUSUAN
        elif detect_type_4(question):
            name = extract_one_name(driver, question)
            if name:
                data = handle_type_4(driver, name)
                response_text = llm_reasoning(generator, data)
                processed = True
            else:
                response_text = "Maaf, dua nama tidak terdeteksi. Mencoba menggunakan RAG murni."
                processed = False

        # TIPE 2 - DAFTAR MAHRAM UMUM
        elif detect_type_2(question):
            name = extract_one_name(driver, question)
            if name:
                data = handle_type_2(driver, name)
                response_text = llm_reasoning(generator, data)
                processed = True
            else:
                response_text = "Maaf, dua nama tidak terdeteksi. Mencoba menggunakan RAG murni."
                processed = False

        # TIPE 3 - PENJELASAN HUBUNGAN MAHRAM
        elif detect_type_3(question):
            name1, name2 = extract_two_names(driver, question)
            if name1 and name2:
                data = handle_type_3(driver, name1, name2)
                response_text = llm_reasoning(generator, data)
                processed = True
            else:
                response_text = "Maaf, dua nama tidak terdeteksi. Mencoba menggunakan RAG murni."
                processed = False

        # FALLBACK: RAG MURNI (LLM + CYPHER)
        if not processed:
            with st.spinner('Sedang menganalisis pertanyaan...'):
                query = ttc(question)
                results = driver.execute_query(query)

                if len(results) > 0:
                    query_result_str = "\n".join([str(x) for x in results])
                else:
                    query_result_str = "(no result)"

                response_text = generator(question, query, query_result_str)

    except Exception as e:
        response_text = f"Terjadi kesalahan sistem: {str(e)}"

    with st.chat_message("assistant"):
        st.markdown(response_text)

    st.session_state.messages.append({"role": "assistant", "content": response_text})

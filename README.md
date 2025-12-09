## Cara Menjalankan Aplikasi RAG Mahram

Ikuti langkah-langkah berikut untuk menjalankan sistem Retrieval-Augmented Generation (RAG) Mahram di komputer lokal.

### 1. Membuat Virtual Environment
```bash
python -m venv venv
```

### 2. Mengaktifkan Virtual Environment
Windows:
```bash
venv\Scripts\activate
```
Linux / macOS:
```bash
source venv/bin/activate
```

### 3. Menginstall Seluruh Dependency
```bash
pip install -r requirements.txt
```

### 4. Konfigurasi Database Neo4j
Atur koneksi Neo4j di file `config.py` atau `database.py`:
```python
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password"
```
Pastikan service Neo4j sudah berjalan sebelum aplikasi dijalankan.

### 5. Konfigurasi API Key LLM
Buat API Key pada console.groq.com
Masukkan API key pada dua file berikut:

File `response_generator.py`:
```python
GROQ_API_KEY = "your_key"
```

File `text_to_cypher.py`:
```python
GROQ_API_KEY = "your_key"
```

### 6. Menjalankan Aplikasi Streamlit
```bash
streamlit run web_app.py
```

Jika berhasil, aplikasi akan terbuka otomatis di browser pada:
```
http://localhost:8501
```

✅ Sistem RAG Mahram siap digunakan.

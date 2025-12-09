import os
# import google.generativeai as genai
from groq import Groq

# GEMINI_API_KEY = "your_key"
GROQ_API_KEY = "your_key"

PROMPT_TEMPLATE = """
<SCHEMA>

Question:
<QUESTION>

Query:
<QUERY>

Query result:
<QUERY-RESULT-STR>

Answer:
""".strip()

# genai.configure(api_key=GEMINI_API_KEY)


# class ResponseGenerator:
#     def __init__(self, schema: str, model="llama3-8b-8192"):
#         self._schema = schema
#         self._model = genai.GenerativeModel(model)

#     def __call__(self, question: str, query: str, query_result_str: str):

#         # Anti-halusinasi: jika graph kosong, jangan minta LLM ngarang
#         if query_result_str.strip() in ["", "(no result)"]:
#             return "Data tidak ditemukan dalam graf."

#         prompt = PROMPT_TEMPLATE
#         prompt = prompt.replace("<SCHEMA>", self._schema)
#         prompt = prompt.replace("<QUESTION>", question)
#         prompt = prompt.replace("<QUERY>", query)
#         prompt = prompt.replace("<QUERY-RESULT-STR>", query_result_str)

#         system_prompt = (
#             "You are a helpful assistant. "
#             "Answer the user question using ONLY the provided Neo4j query result. "
#             "Do NOT add any external knowledge."
#         )

#         full_prompt = f"{system_prompt}\n\n{prompt}"

#         try:
#             response = self._model.generate_content(full_prompt)
#             return response.text.strip()
#         except Exception as e:
#             return f"[ERROR Gemini] {str(e)}"

class ResponseGenerator:
    def __init__(self, schema: str):
        self._schema = schema

        self.client = Groq(
            api_key=GROQ_API_KEY
        )
        self.model_name = "llama-3.1-8b-instant"

    def __call__(self, question: str, query: str, query_result_str: str):
        # ============================
        # ✅ 1. CEK DATA KOSONG DULU
        # ============================
        if (
            not query_result_str
            or query_result_str.strip() == ""
            or query_result_str.strip() == "(no result)"
            or query_result_str.strip() == "[]"
        ):
            return (
                "Maaf, data yang Anda tanyakan tidak ditemukan "
                "di dalam basis pengetahuan (schema) sistem."
            )

        # ============================
        # ✅ 2. BARU PANGGIL LLM JIKA ADA DATA
        # ============================
        prompt = PROMPT_TEMPLATE
        prompt = prompt.replace("<SCHEMA>", self._schema)
        prompt = prompt.replace("<QUESTION>", question)
        prompt = prompt.replace("<QUERY>", query)
        prompt = prompt.replace("<QUERY-RESULT-STR>", query_result_str)

        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert in Islamic mahram law. "
                        "Answer ONLY based on the Neo4j query result. "
                        "If the result is unclear, say the data is not available."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.2,
            max_tokens=512
        )

        return completion.choices[0].message.content.strip()
    
# TEST STANDALONE 
if __name__ == "__main__":
    with open("schema_mahram.txt") as fp:   
        schema = fp.read().strip()

    print("Preparing pipeline ....")
    generator = ResponseGenerator(schema)

    # Contoh pertanyaan domain mahram
    question = "Apakah Budi boleh menikahi Ila?"

    # Contoh query hasil dari sistem graf (Tipe 1)
    query = """
MATCH p = shortestPath(
  (a:Person {name: "Budi"})-
  [:PARENT_OF|NURSED|MARRIED_TO*1..6]-
  (b:Person {name: "Ila"})
)
WITH p,
     [r IN relationships(p)
      WHERE type(r) = "MARRIED_TO" AND r.consummated = true] AS valid_marriage,
     [r IN relationships(p)
      WHERE type(r) IN ["PARENT_OF", "NURSED"]] AS blood_or_milk
RETURN
CASE
  WHEN size(blood_or_milk) > 0 THEN true
  WHEN size(valid_marriage) > 0 THEN true
  ELSE false
END AS is_mahram
    """.strip()

    # ✅ Contoh hasil query dari Neo4j
    query_result_str = """
{'is_mahram': true}
    """.strip()

    print("Generating ...")
    response = generator(question, query, query_result_str)
    print(response)


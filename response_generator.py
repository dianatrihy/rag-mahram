import os
from groq import Groq

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

class ResponseGenerator:
    def __init__(self, schema: str):
        self._schema = schema

        self.client = Groq(
            api_key=GROQ_API_KEY
        )
        self.model_name = "llama-3.1-8b-instant"

    def __call__(self, question: str, query: str, query_result_str: str):
        # HARD STOP JIKA DATA KOSONG
        if (
            not query_result_str
            or query_result_str.strip() == ""
            or query_result_str.strip() == "(no result)"
            or query_result_str.strip() == "[]"
        ):
            return "Data tidak ditemukan dalam schema sistem."

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
                        "You MUST answer ONLY using the provided Neo4j query result.\n"
                        "You are STRICTLY FORBIDDEN to:\n"
                        "- generate new queries\n"
                        "- explain hypothetical conditions\n"
                        "- make assumptions\n"
                        "- infer relationships not present in the result\n"
                        "- add procedural steps\n\n"
                        "If the query result does NOT explicitly contain the answer, "
                        "you MUST reply ONLY with:\n"
                        "'Data tidak ditemukan dalam schema sistem.'\n\n"
                        "Your answer MUST be SHORT, DIRECT, and FINAL."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.0,
            max_tokens=128
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

    # Contoh hasil query dari Neo4j
    query_result_str = """
{'is_mahram': true}
    """.strip()

    print("Generating ...")
    response = generator(question, query, query_result_str)
    print(response)


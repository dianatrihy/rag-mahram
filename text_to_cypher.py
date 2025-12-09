import os
from groq import Groq

GROQ_API_KEY = "your_key"

class TextToCypher:
    def __init__(self, schema: str, model="llama-3.1-8b-instant"):
        self._schema = schema
        self._model_name = model

        self._client = Groq(
            api_key=GROQ_API_KEY
        )

    def __call__(self, question: str):
        prompt = f"""
You are a Neo4j Cypher query generator for a Knowledge Graph about Islamic family relations.

SCHEMA (DO NOT VIOLATE THIS):
{self._schema}

USER QUESTION:
{question}

STRICT RULES (MANDATORY):
1. Output ONLY pure Cypher query. NO markdown. NO ``` NO explanation.
2. Use ONLY these relationships:
   - PARENT_OF
   - NURSED
   - MARRIED_TO
   - MAHRAM
3. DO NOT use wildcard [*] or variable-length paths unless the question EXPLICITLY asks for "jalur", "hubungan", "rantai", or "path".
4. For direct lookup questions, use EXACTLY ONE hop (no *1.., no *0..).
5. DO NOT generate marriage legality, halal/haram, or permission queries.
6. DO NOT return boolean decisions.
7. ALWAYS include a RETURN clause with specific properties (e.g., name, gender).
8. DO NOT hallucinate labels, relationships, or properties.
9. Direction of relation MUST match the schema semantics:
   - (:Person)-[:PARENT_OF]->(:Person) means parent → child
   - (:Person)-[:MARRIED_TO]->(:Person) means spouse
   - (:Person)-[:NURSED]->(:Person) means wet-nurse → child
10. If the question is unclear or illegal under these rules, return:
    MATCH (p:Person) RETURN p.name LIMIT 5
"""

        try:
            response = self._client.chat.completions.create(
                model=self._model_name,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                max_tokens=256
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"[ERROR Groq - TextToCypher] {str(e)}"



# TEST STANDALONE
if __name__ == "__main__":
    with open("schema_mahram.txt") as fp: 
        schema = fp.read().strip()

    print("Preparing pipeline ....")
    ttc = TextToCypher(schema)

    # Contoh pertanyaan domain mahram
    question = "Siapa orang tua Ali?"

    print("Generating ...")
    cypher = ttc(question)
    print(cypher)

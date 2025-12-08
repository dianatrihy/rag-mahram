from rag_queries import build_explain_mahram_path_query
from interpreters import interpret_mahram_path

def handle_type_3(driver, name1, name2):
    if not name1 or not name2:
        return "Dua nama tidak terdeteksi dengan baik."

    query = build_explain_mahram_path_query(name1, name2)
    results = driver.execute_query(query)

    if len(results) == 0 or "p" not in results[0]:
        return f"Tidak ditemukan jalur hubungan antara {name1} dan {name2}."

    path = results[0]["p"]
    explanation = interpret_mahram_path(path, name1, name2)

    return explanation

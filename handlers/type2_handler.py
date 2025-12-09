from rag_queries import build_list_mahram_query

def get_gender(driver, name):
    query = """
    MATCH (p:Person {name: $name})
    RETURN p.gender AS gender
    """
    results = driver.execute_query(query, {"name": name})
    if len(results) == 0:
        return None
    return results[0]["gender"]


def handle_type_2(driver, name):
    user_gender = get_gender(driver, name)

    # ============================
    # ✅ HARD STOP: NAMA TIDAK ADA
    # ============================
    if not user_gender:
        return {
            "type": "type_2",
            "question": f"Siapa saja mahram {name}?",
            "query": "(name validation)",
            "result": "(no result)",
            "extra": {
                "error": "Nama tidak ditemukan di dalam schema graf.",
                "name": name,
                "count": 0
            }
        }

    query = build_list_mahram_query(name)
    results = driver.execute_query(query)

    if len(results) == 0:
        return {
            "type": "type_2",
            "question": f"Siapa saja mahram {name}?",
            "query": query,
            "result": "(no result)",
            "extra": {
                "name": name,
                "count": 0
            }
        }

    # ============================
    # ✅ FILTER ANTI SE-GENDER
    # ============================
    filtered = [
        row["mahram_name"]
        for row in results
        if row.get("mahram_gender") and row["mahram_gender"] != user_gender
    ]

    return {
        "type": "type_2",
        "question": f"Siapa saja mahram {name}?",
        "query": query,
        "result": str(filtered),
        "extra": {
            "name": name,
            "count": len(filtered),
            "list": filtered
        }
    }

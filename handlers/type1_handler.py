from rag_queries import build_check_marriage_query

def get_gender(driver, name):
    query = """
    MATCH (p:Person {name: $name})
    RETURN p.gender AS gender
    """
    results = driver.execute_query(query, {"name": name})

    if len(results) == 0:
        return None

    return results[0]["gender"]


def handle_type_1(driver, name1, name2):
    gender1 = get_gender(driver, name1)
    gender2 = get_gender(driver, name2)

    # ============================
    # ✅ HARD STOP: NAMA TIDAK ADA
    # ============================
    if not gender1 or not gender2:
        return {
            "type": "type_1",
            "question": f"Apakah {name1} boleh menikahi {name2}?",
            "query": "(name validation)",
            "result": "(no result)",
            "extra": {
                "error": "Nama tidak ditemukan di dalam schema graf.",
                "found_name_1": bool(gender1),
                "found_name_2": bool(gender2)
            }
        }

    # ============================
    # ✅ HARD STOP: FILTER SE-GENDER
    # ============================
    if gender1 == gender2:
        return {
            "type": "type_1",
            "question": f"Apakah {name1} boleh menikahi {name2}?",
            "query": "(same gender filter)",
            "result": f"{name1} dan {name2} memiliki gender yang sama.",
            "extra": {
                "gender1": gender1,
                "gender2": gender2,
                "allowed": False,
                "reason": "same_gender"
            }
        }

    # ============================
    # ✅ QUERY GRAF MAHRAM
    # ============================
    query = build_check_marriage_query(name1, name2)
    results = driver.execute_query(query)

    # ============================
    # ✅ HARD STOP: QUERY TIDAK ADA HASIL
    # ============================
    if len(results) == 0:
        return {
            "type": "type_1",
            "question": f"Apakah {name1} boleh menikahi {name2}?",
            "query": query,
            "result": "(no result)",
            "extra": {
                "error": "Relasi tidak ditemukan di graf."
            }
        }

    # ============================
    # ✅ HASIL VALID DARI GRAF
    # ============================
    return {
        "type": "type_1",
        "question": f"Apakah {name1} boleh menikahi {name2}?",
        "query": query,
        "result": str(results[0])
    }

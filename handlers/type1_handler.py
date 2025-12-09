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

    # Jika salah satu nama tidak ada
    if not gender1 or not gender2:
        return {
            "type": "type_1",
            "question": f"Apakah {name1} boleh menikahi {name2}?",
            "query": "(gender not found)",
            "result": "(no result)",
            "extra": {
                "error": "Nama tidak ditemukan di graf."
            }
        }

    # FILTER SE-GENDER 
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

    # LANJUT KE QUERY GRAF
    query = build_check_marriage_query(name1, name2)
    results = driver.execute_query(query)

    if len(results) == 0:
        return {
            "type": "type_1",
            "question": f"Apakah {name1} boleh menikahi {name2}?",
            "query": query,
            "result": "(no result)"
        }

    return {
        "type": "type_1",
        "question": f"Apakah {name1} boleh menikahi {name2}?",
        "query": query,
        "result": str(results[0])
    }

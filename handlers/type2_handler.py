from rag_queries import build_list_mahram_query

def handle_type_2(driver, name):
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

    # Ambil hanya nama dari hasil query
    names = [row["mahram_name"] for row in results]

    return {
        "type": "type_2",
        "question": f"Siapa saja mahram {name}?",
        "query": query,
        "result": str(names),
        "extra": {
            "name": name,
            "count": len(names),
            "list": names
        }
    }

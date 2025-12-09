from rag_queries import build_list_milk_mahram_query

def handle_type_4(driver, name):
    query = build_list_milk_mahram_query(name)
    results = driver.execute_query(query)

    if len(results) == 0:
        return {
            "type": "type_4",
            "question": f"Siapa saja mahram karena persusuan {name}?",
            "query": query,
            "result": "(no result)",
            "extra": {
                "name": name,
                "count": 0
            }
        }

    names = [row["milk_mahram_name"] for row in results]

    return {
        "type": "type_4",
        "question": f"Siapa saja mahram karena persusuan {name}?",
        "query": query,
        "result": str(names),
        "extra": {
            "name": name,
            "count": len(names),
            "list": names
        }
    }

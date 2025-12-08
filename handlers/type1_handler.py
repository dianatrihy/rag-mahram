from rag_queries import build_check_marriage_query

def handle_type_1(driver, name1, name2):
    if not name1 or not name2:
        return "Nama tidak terdeteksi dengan baik."

    query = build_check_marriage_query(name1, name2)
    results = driver.execute_query(query)

    if len(results) == 0:
        return "Data tidak ditemukan dalam graf."

    row = results[0]
    is_mahram = row.get("is_mahram", False)

    if is_mahram:
        return f"Tidak, {name1} tidak boleh menikahi {name2} karena terdapat hubungan mahram."
    else:
        return f"Ya, {name1} boleh menikahi {name2} karena tidak ditemukan hubungan mahram."

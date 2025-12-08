from rag_queries import build_list_mahram_query

def handle_type_2(driver, name):
    if not name:
        return "Nama tidak terdeteksi."

    query = build_list_mahram_query(name)
    results = driver.execute_query(query)

    if len(results) == 0:
        return f"Tidak ditemukan data mahram untuk {name}."

    nama_list = [row["mahram_name"] for row in results]

    daftar = ", ".join(nama_list)
    return f"Mahram {name} adalah: {daftar}"

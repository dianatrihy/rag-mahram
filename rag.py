from database import GraphDatabaseDriver
from response_generator import ResponseGenerator
from text_to_cypher import TextToCypher
from rag_queries import build_check_marriage_query

import re

def detect_type_1(question: str):
    """
    Deteksi pertanyaan Tipe 1: Cek Kebolehan Nikah
    Contoh:
    - Apakah Budi boleh menikahi Ila?
    - Bolehkah Ahmad menikah dengan Siti?
    """
    pattern = r"(apakah|bolehkah).*(menikah|nikah).*"
    return re.search(pattern, question.lower())

def detect_type_2(question: str):
    """
    KHUSUS untuk daftar mahram UMUM (bukan persusuan, bukan penjelasan)
    Contoh valid:
    - Siapa saja mahram Budi?
    - Daftar mahram Ani
    """
    q = question.lower()

    is_question = "siapa" in q or "daftar" in q
    has_mahram = "mahram" in q

    # KECUALIKAN TIPE 4 (persusuan)
    if "susuan" in q or "persusuan" in q or "radha" in q:
        return False

    # KECUALIKAN TIPE 3 (penjelasan)
    if "kenapa" in q or "jelaskan" in q:
        return False

    return is_question and has_mahram


def detect_type_3(question: str):
    """
    HANYA untuk pertanyaan penjelasan hubungan,
    BUKAN daftar mahram dan BUKAN persusuan.
    """
    q = question.lower()
    return (
        ("kenapa" in q or "jelaskan" in q)
        and "mahram" in q
        and "susuan" not in q
        and "persusuan" not in q
    )


def detect_type_4(question: str):
    """
    Deteksi pertanyaan mahram karena persusuan:
    - Siapa saja mahram persusuan Budi?
    - Siapa mahram karena susuan Ali?
    """
    return re.search(r"(susuan|persusuan|radha)", question.lower())


def extract_two_names(question: str):
    """
    Ambil dua nama dari pertanyaan Nikah:
    Pola wajib: <Nama1> ... menikah ... <Nama2>
    """
    stopwords = {"Apakah", "Bolehkah", "Bisakah", "Maukah", "Siapa", "Siapakah", "Kenapa", "Jelaskan"}
    
    # Ambil semua kata kapital
    candidates = re.findall(r"\b[A-Z][a-z]+\b", question)

    # Buang kata tanya
    names = [x for x in candidates if x not in stopwords]

    if len(names) >= 2:
        return names[0], names[1]

    return None, None

def extract_one_name(question: str):
    """
    Ambil satu nama utama untuk pertanyaan daftar mahram.
    Contoh: 'Siapa saja mahram Budi?' → Budi
    """
    stopwords = {
        "Siapa", "Apa", "Yang", "Saja", "Mahram",
        "Apakah", "Bolehkah", "Bisakah", "Maukah"
    }

    candidates = re.findall(r"\b[A-Z][a-z]+\b", question)
    names = [x for x in candidates if x not in stopwords]

    if len(names) >= 1:
        return names[0]

    return None

def interpret_mahram_path(path_list, name1, name2):
    """
    Mengubah path berbentuk list pipih:
    [node, REL, node, REL, node, ...]
    menjadi narasi kemahraman yang jelas.
    """

    if not isinstance(path_list, list) or len(path_list) < 3:
        return f"Tidak ditemukan jalur hubungan yang menjelaskan kemahraman {name1} dan {name2}."

    relations = []
    narasi = []

    # Ambil semua relasi dari list
    for i in range(1, len(path_list), 2):
        relations.append(path_list[i])

    # Tentukan jenis mahram utama
    if "PARENT_OF" in relations:
        jenis = "mahram karena keturunan"
    elif "NURSED" in relations:
        jenis = "mahram karena persusuan"
    elif "MARRIED_TO" in relations:
        jenis = "mahram karena pernikahan"
    else:
        jenis = "mahram karena hubungan keluarga"

    # Bangun narasi langkah demi langkah
    for i in range(0, len(path_list) - 2, 2):
        start = path_list[i]["name"]
        rel = path_list[i + 1]
        end = path_list[i + 2]["name"]

        if rel == "PARENT_OF":
            kalimat = f"{start} adalah orang tua dari {end}"
        elif rel == "NURSED":
            kalimat = f"{start} adalah orang tua susuan dari {end}"
        elif rel == "MARRIED_TO":
            kalimat = f"{start} pernah menikah dengan {end}"
        else:
            kalimat = f"{start} terhubung dengan {end}"

        narasi.append(kalimat)

    narasi_final = ". ".join(narasi)

    return f"{name1} dan {name2} merupakan {jenis}, karena: {narasi_final}."



with GraphDatabaseDriver() as driver:
    with open("schema_mahram.txt") as fp:
        schema = fp.read().strip()

    print("Preparing text-to-Cypher pipeline ....")
    ttc = TextToCypher(schema)

    print("Preparing response generator pipeline ....")
    generator = ResponseGenerator(schema)

    interrupt = False
    print("(Interrupt to stop.)")

    while not interrupt:
        try:
            question = input("Question: ")
        except KeyboardInterrupt:
            interrupt = True

        if interrupt:
            break

        # ============================
        # TIPE 1: CEK BOLEH MENIKAH
        # ============================
        if detect_type_1(question):
            name1, name2 = extract_two_names(question)

            if not name1 or not name2:
                print("Nama tidak terdeteksi dengan baik.")
                continue

            from rag_queries import build_check_marriage_query

            query = build_check_marriage_query(name1, name2)
            print("\n[QUERY CYPHER FINAL]")
            print(query)

            results = driver.execute_query(query)

            if len(results) == 0:
                print("Data tidak ditemukan dalam graf.")
                continue

            row = results[0]
            is_mahram = row.get("is_mahram", False)
            path = row.get("p", None)

            if is_mahram:
                context = f"Hasil pencarian graf menunjukkan bahwa {name1} dan {name2} memiliki hubungan mahram."
                final_answer = f"Tidak, {name1} tidak boleh menikahi {name2} karena terdapat hubungan mahram."
            else:
                context = f"Hasil pencarian graf menunjukkan bahwa tidak ditemukan hubungan mahram antara {name1} dan {name2}."
                final_answer = f"Ya, {name1} boleh menikahi {name2} karena tidak ditemukan hubungan mahram."

            print("\n[HASIL QUERY GRAF]")
            print(context)

            print("\n[JAWABAN SISTEM]")
            print(final_answer)
            continue

        # ============================
        # TIPE 2: DAFTAR MAHRAM
        # ============================
        if detect_type_2(question):
            name = extract_one_name(question)

            if not name:
                print("Nama tidak terdeteksi.")
                continue

            from rag_queries import build_list_mahram_query

            query = build_list_mahram_query(name)
            print("\n[QUERY CYPHER FINAL]")
            print(query)

            results = driver.execute_query(query)

            if len(results) == 0:
                print(f"Tidak ditemukan data mahram untuk {name}.")
                continue

            print("\n[HASIL QUERY GRAF]")
            for row in results:
                print(f"- {row['mahram_name']}")

            print("\n[JAWABAN SISTEM]")
            nama_list = ", ".join([row["mahram_name"] for row in results])
            print(f"Mahram {name} adalah: {nama_list}")
            continue

        # ============================
        # TIPE 3: PENJELASAN JALUR KEMAHRAMAN (EXPLAINABLE)
        # ============================
        if detect_type_3(question):
            name1, name2 = extract_two_names(question)

            if not name1 or not name2:
                print("Dua nama tidak terdeteksi dengan baik.")
                continue

            from rag_queries import build_explain_mahram_path_query

            query = build_explain_mahram_path_query(name1, name2)
            print("\n[QUERY CYPHER FINAL]")
            print(query)

            results = driver.execute_query(query)

            if len(results) == 0 or "p" not in results[0]:
                print(f"Tidak ditemukan jalur hubungan antara {name1} dan {name2}.")
                continue

            path = results[0]["p"]

            explanation = interpret_mahram_path(path, name1, name2)

            print("\n[HASIL QUERY GRAF]")
            print(path)

            print("\n[JAWABAN SISTEM]")
            print(explanation)
            continue
        
        # ============================
        # TIPE 4: MAHRAM KARENA PERSUSUAN
        # ============================
        if detect_type_4(question):
            name = extract_one_name(question)

            if not name:
                print("Nama tidak terdeteksi.")
                continue

            from rag_queries import build_list_milk_mahram_query

            query = build_list_milk_mahram_query(name)
            print("\n[QUERY CYPHER FINAL]")
            print(query)

            results = driver.execute_query(query)

            if len(results) == 0:
                print(f"Tidak ditemukan hubungan persusuan untuk {name}.")
                continue

            print("\n[HASIL QUERY GRAF]")
            for row in results:
                print(f"- {row['milk_mahram_name']} ({row['milk_mahram_gender']})")

            print("\n[JAWABAN SISTEM]")
            nama_list = ", ".join([row["milk_mahram_name"] for row in results])
            print(f"Mahram karena persusuan {name} adalah: {nama_list}")
            continue



        # ==========================================
        # UNTUK PERTANYAAN LAIN → DEFAULT RAG
        # ==========================================
        print("Generating Cypher query ....")
        query = ttc(question)
        print(query)

        print("Executing Cypher query ....")
        results = driver.execute_query(query)

        if len(results) > 0:
            query_result_str = "\n".join([str(x) for x in results])
        else:
            query_result_str = "(no result)"

        print(query_result_str)

        print("Generating response ....")
        response = generator(question, query, query_result_str)
        print(response)

    print("(Stopped.)")

def interpret_mahram_path(path_list, name1, name2):
    if not isinstance(path_list, list) or len(path_list) < 3:
        return f"Tidak ditemukan jalur hubungan yang menjelaskan kemahraman {name1} dan {name2}."

    relations = []
    narasi = []

    for i in range(1, len(path_list), 2):
        relations.append(path_list[i])

    if "PARENT_OF" in relations:
        jenis = "mahram karena keturunan"
    elif "NURSED" in relations:
        jenis = "mahram karena persusuan"
    elif "MARRIED_TO" in relations:
        jenis = "mahram karena pernikahan"
    else:
        jenis = "mahram karena hubungan keluarga"

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

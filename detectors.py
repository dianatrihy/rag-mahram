import re

def detect_type_1(question: str):
    pattern = r"(apakah|bolehkah).*(menikah|nikah).*"
    return re.search(pattern, question.lower())

def detect_type_2(question: str):
    q = question.lower()
    is_question = "siapa" in q or "daftar" in q
    has_mahram = "mahram" in q

    if "susuan" in q or "persusuan" in q or "radha" in q:
        return False

    if "kenapa" in q or "jelaskan" in q:
        return False

    return is_question and has_mahram

def detect_type_3(question: str):
    q = question.lower()
    return (
        ("kenapa" in q or "jelaskan" in q)
        and "mahram" in q
        and "susuan" not in q
        and "persusuan" not in q
    )

def detect_type_4(question: str):
    return re.search(r"(susuan|persusuan|radha)", question.lower())

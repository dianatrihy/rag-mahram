import re

def extract_two_names(question: str):
    stopwords = {
        "Apakah", "Bolehkah", "Bisakah", "Maukah",
        "Siapa", "Siapakah", "Kenapa", "Jelaskan"
    }

    candidates = re.findall(r"\b[A-Z][a-z]+\b", question)
    names = [x for x in candidates if x not in stopwords]

    if len(names) >= 2:
        return names[0], names[1]

    return None, None

def extract_one_name(question: str):
    stopwords = {
        "Siapa", "Apa", "Yang", "Saja", "Mahram",
        "Apakah", "Bolehkah", "Bisakah", "Maukah"
    }

    candidates = re.findall(r"\b[A-Z][a-z]+\b", question)
    names = [x for x in candidates if x not in stopwords]

    if len(names) >= 1:
        return names[0]

    return None

import re
from typing import List, Tuple
from database import GraphDatabaseDriver

STOPWORDS = {
    "apakah", "bolehkah", "bisakah", "maukah",
    "siapa", "siapakah", "kenapa", "jelaskan",
    "yang", "dan", "dengan", "antara", "ke",
    "di", "dari", "mahrom", "mahram", "nikah",
    "menikah", "orang", "tua", "anak", "istri",
    "suami", "persusuan", "susuan", "ayah",
    "ibu", "kakek", "nenek"
}

def _normalize(text: str):
    return text.lower().strip()

def _regex_candidates(question: str) -> List[str]:
    tokens = re.findall(r"[A-Za-z]+", question.lower())
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]


def _filter_by_graph(driver: GraphDatabaseDriver, candidates: List[str]) -> List[str]:
    """
    Hanya terima yang benar-benar ada sebagai Person di Neo4j.
    """
    valid = []

    for name in candidates:
        cypher = f"""
        MATCH (p:Person {{name: "{name.capitalize()}"}})
        RETURN p LIMIT 1
        """
        result = driver.execute_query(cypher)
        if len(result) > 0:
            valid.append(name.capitalize())

    return valid


def extract_one_name(driver: GraphDatabaseDriver, question: str) -> str | None:
    candidates = _regex_candidates(question)
    valid_names = _filter_by_graph(driver, candidates)

    if len(valid_names) >= 1:
        return valid_names[0]

    return None


def extract_two_names(driver: GraphDatabaseDriver, question: str) -> Tuple[str | None, str | None]:
    candidates = _regex_candidates(question)
    valid_names = _filter_by_graph(driver, candidates)

    if len(valid_names) >= 2:
        return valid_names[0], valid_names[1]

    return None, None

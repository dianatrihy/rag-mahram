def build_check_marriage_query(name1, name2):
    query = f"""
    MATCH p = shortestPath(
      (a:Person {{name: "{name1}"}})-
      [:PARENT_OF|NURSED|MARRIED_TO*1..6]-
      (b:Person {{name: "{name2}"}})
    )
    WITH p,
         [r IN relationships(p) 
          WHERE type(r) = "MARRIED_TO" AND r.consummated = true] AS valid_marriage,
         [r IN relationships(p) 
          WHERE type(r) IN ["PARENT_OF", "NURSED"]] AS blood_or_milk
    RETURN 
    CASE 
      WHEN size(blood_or_milk) > 0 THEN true
      WHEN size(valid_marriage) > 0 THEN true
      ELSE false
    END AS is_mahram,
    p
    """
    return query

def build_list_mahram_query(name):
    query = f"""
    MATCH (a:Person {{name: "{name}"}})-
          [:PARENT_OF|NURSED|MARRIED_TO*1..6]-
          (m:Person)
    WHERE 
        a <> m
        AND a.gender <> m.gender
    RETURN DISTINCT 
        m.name AS mahram_name, 
        m.gender AS mahram_gender
    """
    return query

def build_explain_mahram_path_query(name1, name2):
    query = f"""
    MATCH p = (
      (a:Person {{name: "{name1}"}})-
      [:PARENT_OF|NURSED|MARRIED_TO*1..6]-
      (b:Person {{name: "{name2}"}})
    )
    RETURN p
    LIMIT 1
    """
    return query

def build_list_milk_mahram_query(name):
    query = f"""
    MATCH (a:Person {{name: "{name}"}})-[:NURSED]-(m:Person)
    WHERE 
        a <> m
    RETURN DISTINCT 
        m.name   AS milk_mahram_name,
        m.gender AS milk_mahram_gender
    ORDER BY m.name
    """
    return query


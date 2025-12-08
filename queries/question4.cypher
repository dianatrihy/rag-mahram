MATCH (a:Person {name: $name})-[:NURSED]-(m:Person)
WHERE 
    a <> m
RETURN DISTINCT 
    m.name AS milk_mahram_name,
    m.gender AS milk_mahram_gender
ORDER BY m.name
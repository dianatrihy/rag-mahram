MATCH (a:Person {name: $name})-
      [:PARENT_OF|NURSED|MARRIED_TO*1..6]-
      (m:Person)
WHERE 
    a <> m
    AND a.gender <> m.gender
RETURN DISTINCT 
    m.name   AS mahram_name,
    m.gender AS mahram_gender
ORDER BY m.name
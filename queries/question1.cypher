MATCH p = shortestPath(
  (a:Person {name: $name1})-
  [:PARENT_OF|NURSED|MARRIED_TO*1..6]-
  (b:Person {name: $name2})
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

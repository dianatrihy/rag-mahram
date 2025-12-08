// Tipe 3 - Penjelasan Jalur Kemahraman
MATCH p = (
  (a:Person {name: $name1})-
  [:PARENT_OF|NURSED|MARRIED_TO*1..6]-
  (b:Person {name: $name2})
)
RETURN p
LIMIT 1

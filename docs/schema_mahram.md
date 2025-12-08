# Skema Graf Pengetahuan Hukum Mahram (Neo4j)

## 1. Ringkasan Umum

Graf pengetahuan ini merepresentasikan hubungan kekerabatan, pernikahan, persusuan,
dan kemahraman antar individu berdasarkan prinsip hukum Islam.
Seluruh simpul dalam graf direpresentasikan oleh label `Person`, sedangkan hubungan
antar individu dinyatakan dalam bentuk relasi Neo4j.

Graf ini merupakan implementasi konkret dari ontologi hukum mahram yang sebelumnya
dirancang menggunakan Protégé.

---

## 2. Node Label

### 2.1. Person

- **Label**: `Person`
- **Deskripsi**: Merepresentasikan individu yang terlibat dalam hubungan keluarga,
  pernikahan, persusuan, dan kemahraman.
- **Properti**:
  - `id` (String / Integer): Identitas unik individu.
  - `name` (String): Nama individu.
  - `gender` (String): Jenis kelamin (misal: "L", "P").
  - `religion` (String): Agama individu.
  - `notes` (String, opsional): Keterangan tambahan.
- **Padanan Ontologi Protégé**: Class `Orang`.

---

## 3. Relationship Types

### 3.1. (:Person)-[:PARENT_OF]->(:Person)

- **Makna**: Individu pada sisi kiri adalah orang tua dari individu pada sisi kanan.
- **Arah relasi**: orang tua → anak.
- **Makna fiqih**:
  - Orang tua dan anak adalah mahram mu’abbad (mahram selamanya).
  - Relasi ini juga menjadi dasar penentuan mahram untuk kakek-nenek dan cucu.
- **Padanan Ontologi**: ObjectProperty `orangTuaDari`.

---

### 3.2. (:Person)-[:MARRIED_TO]->(:Person)

- **Makna**: Kedua individu terikat dalam hubungan pernikahan.
- **Sifat relasi**: Simetris.
- **Makna fiqih**:
  - Melahirkan hubungan mahram karena pernikahan (contoh: mertua, menantu).
  - Menjadi dasar penentuan hubungan kemahraman turunan.
- **Padanan Ontologi**: ObjectProperty `menikahDengan`.

---

### 3.3. (:Person)-[:NURSED]->(:Person)

- **Makna**: Individu pada sisi kiri adalah anak susuan dari individu di sisi kanan.
- **Makna fiqih**:
  - Menimbulkan hubungan mahram karena persusuan.
  - Anak susuan haram menikah dengan ibu susuan dan saudara sesusuan.
- **Padanan Ontologi**: ObjectProperty `anakSusuanDari`.

---

### 3.4. (:Person)-[:MAHRAM]->(:Person)

- **Makna**: Kedua individu memiliki hubungan mahram langsung.
- **Makna fiqih**:
  - Menandakan bahwa pernikahan antara kedua individu tersebut adalah **haram**.
  - Relasi ini merupakan hasil inferensi dari relasi keturunan, pernikahan, atau persusuan.
- **Padanan Ontologi**: Class atau hasil inferensi `HubunganMahram`.

---

## 4. Keterkaitan dengan Ontologi Sebelumnya (Protégé)

| Ontologi Protégé          | Neo4j                          | Keterangan                          |
|---------------------------|---------------------------------|-------------------------------------|
| Class `Orang`             | `:Person`                       | Representasi individu               |
| ObjectProperty `orangTuaDari` | `[:PARENT_OF]`             | Hubungan orang tua - anak           |
| ObjectProperty `menikahDengan` | `[:MARRIED_TO]`         | Hubungan pernikahan                 |
| ObjectProperty `anakSusuanDari` | `[:NURSED]`             | Hubungan persusuan                  |
| Class `HubunganMahram`    | `[:MAHRAM]`                     | Relasi mahram hasil inferensi       |

---

## 5. Peran Skema dalam Sistem RAG

Skema graf ini digunakan sebagai acuan utama oleh sistem RAG dalam:
- Menyusun kueri Cypher berdasarkan pertanyaan pengguna.
- Mengambil konteks berbasis hubungan keluarga, pernikahan, dan persusuan.
- Menentukan status boleh atau tidaknya pernikahan berdasarkan relasi mahram.
- Menghasilkan penjelasan berbasis jalur relasi dalam graf.

Skema ini juga digunakan dalam proses text-to-Cypher untuk memastikan bahwa model
bahasa hanya menggunakan label dan relasi yang valid sesuai dengan struktur graf.

from database import GraphDatabaseDriver
from text_to_cypher import TextToCypher
from response_generator import ResponseGenerator

from detectors import (
    detect_type_1,
    detect_type_2,
    detect_type_3,
    detect_type_4
)
from extractors import extract_one_name, extract_two_names

from handlers.type1_handler import handle_type_1
from handlers.type2_handler import handle_type_2
from handlers.type3_handler import handle_type_3
from handlers.type4_handler import handle_type_4

# LOAD SCHEMA & INIT RAG
with open("schema_mahram.txt") as fp:
    schema = fp.read().strip()

print("Preparing text-to-Cypher pipeline ....")
ttc = TextToCypher(schema)

print("Preparing response generator pipeline ....")
generator = ResponseGenerator(schema)


# MAIN APPLICATION LOOP
with GraphDatabaseDriver() as driver:
    print("(Interrupt to stop.)")

    interrupt = False
    while not interrupt:
        try:
            question = input("\nQuestion: ")
        except KeyboardInterrupt:
            interrupt = True
            break

        # TIPE 1 - CEK BOLEH MENIKAH
        if detect_type_1(question):
            name1, name2 = extract_two_names(question)
            answer = handle_type_1(driver, name1, name2)
            print(answer)
            continue

        # TIPE 4 - MAHRAM PERSUSUAN (DI ATAS TIPE 2 KARENA LEBIH SPESIFIK)
        if detect_type_4(question):
            name = extract_one_name(question)
            answer = handle_type_4(driver, name)
            print(answer)
            continue

        # TIPE 2 - DAFTAR MAHRAM UMUM
        if detect_type_2(question):
            name = extract_one_name(question)
            answer = handle_type_2(driver, name)
            print(answer)
            continue

        # TIPE 3 - PENJELASAN HUBUNGAN MAHRAM
        if detect_type_3(question):
            name1, name2 = extract_two_names(question)
            answer = handle_type_3(driver, name1, name2)
            print(answer)
            continue

        # FALLBACK: RAG MURNI (TextToCypher + LLM Response)
        print("\n[Fallback RAG Mode - LLM Based]")
        print("Generating Cypher query ....")
        query = ttc(question)
        print(query)

        print("Executing Cypher query ....")
        results = driver.execute_query(query)

        if len(results) > 0:
            query_result_str = "\n".join([str(x) for x in results])
        else:
            query_result_str = "(no result)"

        print(query_result_str)

        print("Generating response ....")
        response = generator(question, query, query_result_str)
        print(response)

    print("\n(Stopped.)")

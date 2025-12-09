from config import load_config
from neo4j import GraphDatabase as Neo4jDatabase
import streamlit as st

class GraphDatabaseDriver:
    def __init__(self, toml_config_path: str = "config.toml"):
        self._config = load_config(toml_config_path)
        self._driver = None
        self._last_result_details = None
        
        try:
            kwargs = self._config.get_neo4j_driver_kwargs()
            self._driver = Neo4jDatabase.driver(**kwargs)
            self._driver.verify_connectivity()
            print("Database Connected Successfully!")
        except Exception as e:
            print(f"Connection Failed in __init__: {e}")
            raise e

    def close(self):
        if self._driver:
            self._driver.close()

    def execute_query(self, query: str, parameters=None):
        if self._driver is None:
            raise Exception("Driver Neo4j belum terhubung! Cek config dan password.")

        database_name = self._config.get_neo4j_database_name()
        
        if parameters is None:
            parameters = {}

        with self._driver.session(database=database_name) as session:
            self._last_result_details = session.run(query, parameters)
            return self._last_result_details.data()
        
    def get_last_result_details(self):
        return self._last_result_details.to_eager_result()

if __name__ == "__main__":
    try:
        driver = GraphDatabaseDriver()
        results = driver.execute_query("MATCH (n) RETURN count(n) AS jumlah")
        print(f"Test Query Result: {results}")
        driver.close()
    except Exception as e:
        print(f"Test Error: {e}")
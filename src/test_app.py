import logging

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable

log = logging.getLogger(__name__)


class TestApp:
    """Test App for Neo4j"""

    def __init__(self, uri, user, password):
        self._driver = None
        self._driver_conf = {
            'uri': uri,
            'auth': (user, password),
        }

    @property
    def driver(self):
        if self._driver is None:
            self._driver = GraphDatabase.driver(**self._driver_conf)
        return self._driver

    def close(self):
        # Always close the driver connection when done
        if self._driver is not None:
            self._driver.close()

    def create_friendship(self, person1_name, person2_name):
        with self.driver.session() as session:
            # Check api for write transactions
            result = session.write_transaction(
                self._create_and_return_friendship,
                person1_name, person2_name
            )
            for row in result:
                log.info(
                    f"Created friendship: ({row['p1']})-[:KNOWS]->("
                    f"{row['p2']})")

    @staticmethod
    def _create_and_return_friendship(tx, person1_name, person2_name):
        # Query is a single long string, directly in Cypher syntax
        query = (
            "CREATE (p1: Person {name: $person1_name })"
            "CREATE (p2: Person {name: $person2_name })"
            "CREATE (p1)-[:KNOWS]->(p2)"
            "RETURN p1, p2"
        )
        # kwargs on run seem to allow mapping 'person1_name' to a value in
        # the query
        result = tx.run(query, person1_name=person1_name,
                        person2_name=person2_name)
        try:
            return [{
                        "p1": row["p1"]["name"],
                        "p2": row["p2"]["name"]
                    }
                    for row in result]
        except ServiceUnavailable as exception:
            log.error(f"{query} raised error:\n {exception}")
            raise

    def find_person(self, name):
        with self.driver.session() as session:
            result = session.read_transaction(self._find_and_return_person,
                                              name)
            for row in result:
                log.info(f"Found person: {row}")

    @staticmethod
    def _find_and_return_person(tx, name):
        query = (
            "MATCH (p: Person)"
            "WHERE p.name = $name"
            "RETURN p AS name"
        )
        result = tx.run(query, name=name)
        return [row["name"] for row in result]

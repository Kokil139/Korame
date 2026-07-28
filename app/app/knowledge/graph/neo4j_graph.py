"""
Graph storage using Neo4j.

For production deployments requiring distributed graph storage.
This is an interface/stub - implementation depends on neo4j driver being installed.
"""

from typing import Optional, Any, List, Dict
from abc import ABC, abstractmethod


class Neo4jGraph(ABC):
    """
    Neo4j graph interface for production use.

    Requires: pip install neo4j

    Usage:
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
        graph = Neo4jGraph(driver)
    """

    def __init__(self, driver):
        """
        Initialize Neo4j graph.

        Args:
            driver: Neo4j driver instance
        """
        self.driver = driver

    def add_node(
        self,
        node_id: str,
        label: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a node to the graph.

        Args:
            node_id: Unique node ID
            label: Node label (type)
            properties: Optional properties

        Returns:
            True if added
        """
        with self.driver.session() as session:
            query = f"""
            CREATE (n:{label} {{id: $id}})
            SET n += $properties
            RETURN n
            """
            result = session.run(query, id=node_id, properties=properties or {})
            return result.peek() is not None

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a node by ID.

        Args:
            node_id: Node ID

        Returns:
            Node data or None
        """
        with self.driver.session() as session:
            query = "MATCH (n {id: $id}) RETURN n"
            result = session.run(query, id=node_id)
            record = result.single()
            return dict(record['n']) if record else None

    def add_edge(
        self,
        source: str,
        target: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add an edge between two nodes.

        Args:
            source: Source node ID
            target: Target node ID
            relationship_type: Type of relationship
            properties: Optional properties

        Returns:
            True if added
        """
        with self.driver.session() as session:
            query = f"""
            MATCH (a {{id: $source}})
            MATCH (b {{id: $target}})
            CREATE (a)-[r:{relationship_type}]->(b)
            SET r += $properties
            RETURN r
            """
            result = session.run(
                query,
                source=source,
                target=target,
                properties=properties or {}
            )
            return result.peek() is not None

    def get_related_nodes(
        self,
        node_id: str,
        relationship_type: Optional[str] = None,
        max_depth: int = 1
    ) -> List[Dict[str, Any]]:
        """
        Get related nodes.

        Args:
            node_id: Starting node ID
            relationship_type: Filter by relationship type
            max_depth: Maximum traversal depth

        Returns:
            List of related nodes
        """
        with self.driver.session() as session:
            rel_filter = f":{relationship_type}" if relationship_type else ""
            query = f"""
            MATCH (start {{id: $id}})-[{rel_filter}*1..{max_depth}]-(related)
            RETURN related
            """
            result = session.run(query, id=node_id)
            return [dict(record['related']) for record in result]

    def find_path(self, source: str, target: str) -> Optional[List[str]]:
        """
        Find shortest path between two nodes.

        Args:
            source: Source node ID
            target: Target node ID

        Returns:
            List of node IDs or None
        """
        with self.driver.session() as session:
            query = """
            MATCH path = shortestPath((a {id: $source})-[*]-(b {id: $target}))
            RETURN [n in nodes(path) | n.id] as path
            """
            result = session.run(query, source=source, target=target)
            record = result.single()
            return record['path'] if record else None

    def close(self):
        """Close the driver connection."""
        self.driver.close()


# Neo4j Setup Guide
NEO4J_SETUP = """
# Neo4j Setup Guide

## Installation

```bash
pip install neo4j
```

## Docker Setup

```bash
docker run -d \\
  --name neo4j \\
  -p 7474:7474 -p 7687:7687 \\
  -e NEO4J_AUTH=neo4j/password \\
  neo4j:latest
```

## Usage

```python
from neo4j import GraphDatabase
from app.knowledge.graph.neo4j_graph import Neo4jGraph

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "password")
)
graph = Neo4jGraph(driver)

# Add nodes
graph.add_node("user-1", "User", {"name": "Alice"})
graph.add_node("artifact-1", "Artifact", {"type": "UserStory"})

# Add edges
graph.add_edge("user-1", "artifact-1", "CREATED", {"timestamp": "2026-07-27"})

# Query
related = graph.get_related_nodes("user-1", max_depth=2)
path = graph.find_path("user-1", "artifact-1")

# Close
graph.close()
```

## Cypher Query Examples

```cypher
# Create nodes
CREATE (a:User {id: "user-1", name: "Alice"})
CREATE (b:Artifact {id: "artifact-1", type: "UserStory"})

# Create relationship
CREATE (a)-[:CREATED]->(b)

# Query relationships
MATCH (n:User)-[:CREATED]->(artifacts)
RETURN n, artifacts

# Find paths
MATCH path = shortestPath((a:User)-[*]-(b:Artifact))
RETURN path
```
"""


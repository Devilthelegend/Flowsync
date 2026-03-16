"""DAG validation logic - ported from TypeScript."""

from typing import Set, Dict, List
from collections import deque

from app.schemas import WorkflowDefinition, ValidationResult


def validate_dag(definition: WorkflowDefinition) -> ValidationResult:
    """
    Validates a workflow definition is a valid DAG.
    
    Checks:
    1. Exactly one "start" node exists
    2. At least one "end" node exists
    3. All edge references point to existing nodes
    4. No duplicate node IDs
    5. No duplicate edge IDs
    6. No cycles (using Kahn's topological sort)
    7. All non-start nodes are reachable from the start node
    8. Fork nodes have at least 2 outgoing edges
    9. Join nodes have at least 2 incoming edges
    """
    errors: List[str] = []
    nodes = definition.nodes
    edges = definition.edges
    
    # ─── Basic structural checks ─────────────────────────────────────────
    
    if not nodes or len(nodes) == 0:
        return ValidationResult(valid=False, errors=["Workflow must have at least one node"])
    
    if edges is None:
        return ValidationResult(valid=False, errors=["Workflow must have an edges array"])
    
    # ─── Check for duplicate node IDs ────────────────────────────────────
    
    node_ids: Set[str] = set()
    for node in nodes:
        if node.id in node_ids:
            errors.append(f'Duplicate node ID: "{node.id}"')
        node_ids.add(node.id)
    
    # ─── Check for duplicate edge IDs ────────────────────────────────────
    
    edge_ids: Set[str] = set()
    for edge in edges:
        if edge.id in edge_ids:
            errors.append(f'Duplicate edge ID: "{edge.id}"')
        edge_ids.add(edge.id)
    
    # ─── Check start/end node counts ─────────────────────────────────────
    
    start_nodes = [n for n in nodes if n.type == "start"]
    end_nodes = [n for n in nodes if n.type == "end"]
    
    if len(start_nodes) == 0:
        errors.append('Workflow must have exactly one "start" node')
    elif len(start_nodes) > 1:
        errors.append(f'Workflow must have exactly one "start" node, found {len(start_nodes)}')
    
    if len(end_nodes) == 0:
        errors.append('Workflow must have at least one "end" node')
    
    # ─── Validate edge references ────────────────────────────────────────
    
    for edge in edges:
        if edge.source not in node_ids:
            errors.append(f'Edge "{edge.id}" references non-existent source node: "{edge.source}"')
        if edge.target not in node_ids:
            errors.append(f'Edge "{edge.id}" references non-existent target node: "{edge.target}"')
    
    # If structural errors exist, return early before cycle detection
    if errors:
        return ValidationResult(valid=False, errors=errors)
    
    # ─── Cycle detection via Kahn's algorithm (topological sort) ─────────
    
    # Build adjacency list and in-degree map
    adjacency: Dict[str, List[str]] = {node.id: [] for node in nodes}
    in_degree: Dict[str, int] = {node.id: 0 for node in nodes}
    
    for edge in edges:
        adjacency[edge.source].append(edge.target)
        in_degree[edge.target] += 1
    
    # Start with nodes that have no incoming edges
    queue: deque = deque([node_id for node_id, degree in in_degree.items() if degree == 0])
    
    processed_count = 0
    while queue:
        current = queue.popleft()
        processed_count += 1
        
        for neighbor in adjacency[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    if processed_count != len(nodes):
        errors.append("Workflow contains a cycle — workflows must be directed acyclic graphs (DAGs)")
    
    # ─── Reachability check ──────────────────────────────────────────────
    
    if len(start_nodes) == 1 and not errors:
        reachable: Set[str] = set()
        bfs_queue: deque = deque([start_nodes[0].id])
        reachable.add(start_nodes[0].id)
        
        while bfs_queue:
            current = bfs_queue.popleft()
            for neighbor in adjacency.get(current, []):
                if neighbor not in reachable:
                    reachable.add(neighbor)
                    bfs_queue.append(neighbor)
        
        for node in nodes:
            if node.id not in reachable:
                errors.append(f'Node "{node.id}" ({node.label}) is not reachable from the start node')
    
    # ─── Fork / Join / Condition structural checks ───────────────────────
    
    for node in nodes:
        if node.type == "fork":
            outgoing = [e for e in edges if e.source == node.id]
            if len(outgoing) < 2:
                errors.append(
                    f'Fork node "{node.id}" ({node.label}) must have at least 2 outgoing edges, '
                    f'found {len(outgoing)}'
                )
        
        if node.type == "join":
            incoming = [e for e in edges if e.target == node.id]
            if len(incoming) < 2:
                errors.append(
                    f'Join node "{node.id}" ({node.label}) must have at least 2 incoming edges, '
                    f'found {len(incoming)}'
                )
        
        if node.type == "condition":
            outgoing = [e for e in edges if e.source == node.id]
            labeled = [e for e in outgoing if e.condition_branch is not None]
            # Warning: condition has branches but no labels (still valid, backward compat)
    
    return ValidationResult(valid=len(errors) == 0, errors=errors)


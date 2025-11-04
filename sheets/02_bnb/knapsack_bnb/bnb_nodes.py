"""
BnB Node and Factory Module

This module defines the core data structures for nodes in your branch-and-bound tree,
and a factory to create new nodes. A node encapsulates:
  - a relaxed solution (upper-bound) under current fixations,
  - branching decisions (which items are fixed to 0 or 1),
  - metadata (depth, unique IDs, status).

You will not modify this file directly; instead, focus on supplying your own
`BranchingDecisions` and `RelaxationSolver` implementations.
"""

from __future__ import annotations

from enum import Enum
from typing import Callable, Optional

from .branching_decisions import BranchingDecisions
from .heuristics import Heuristics, HeuristicSolution
from .instance import Instance
from .relaxation import RelaxationSolver, RelaxedSolution


class NodeStatus(Enum):
    """
    Enumeration of possible states for a BnB node.
    """

    FEASIBLE = "Feasible"
    INFEASIBLE = "Infeasible"
    ENQUEUED = "Enqueued"
    PRUNED = "Pruned"
    BRANCHED = "Branched"
    UNKNOWN = "Unknown"


class BnBNode:
    """
    Represents a node in the branch-and-bound tree.

    Attributes:
        relaxed_solution: a copy of the bounding solution under current decisions.
        branching_decisions: a copy of fixed/undef decisions for each item.
        depth: tree depth (root = 0).
        node_id: unique identifier for tie-breaking and tracking.
        parent_id: optional ID of the parent node.
        status: current NodeStatus (initialized to UNKNOWN).

    You should not modify `relaxed_solution` or `branching_decisions` in place.
    Use `copy()` methods if you need to inspect and adjust.
    """

    __slots__ = (
        "_heuristic_solution",
        "_relaxed_solution",
        "_branching_decisions",
        "depth",
        "node_id",
        "parent_id",
        "status",
    )

    def __init__(
        self,
        relaxed_solution: RelaxedSolution,
        branching_decisions: BranchingDecisions,
        depth: int,
        node_id: int,
        parent_id: Optional[int] = None,
    ) -> None:
        # Store private copies to prevent external mutation
        self._heuristic_solution: HeuristicSolution | None = None
        self._relaxed_solution = relaxed_solution.copy()
        self._branching_decisions = branching_decisions.copy()
        self.depth = depth
        self.node_id = node_id
        self.parent_id = parent_id
        self.status = NodeStatus.UNKNOWN

    def __lt__(self, other: BnBNode) -> bool:
        # nodes compare by ID for deterministic ordering in priority queues
        return self.node_id < other.node_id

    def __eq__(self, other: object) -> bool:
        return isinstance(other, BnBNode) and self.node_id == other.node_id

    @property
    def heuristic_solution(self) -> HeuristicSolution | None:
        """
        Return a copy of the heuristic solution to avoid in-place edits.
        """
        if self._heuristic_solution is None:
            return None
        return self._heuristic_solution.copy()

    @heuristic_solution.setter
    def heuristic_solution(self, heuristic_solution: HeuristicSolution | None) -> None:
        self._heuristic_solution = heuristic_solution

    @property
    def relaxed_solution(self) -> RelaxedSolution:
        """
        Return a copy of the relaxed solution to avoid in-place edits.
        """
        return self._relaxed_solution.copy()

    @property
    def branching_decisions(self) -> BranchingDecisions:
        """
        Return a copy of the branching decisions to avoid in-place edits.
        """
        return self._branching_decisions.copy()


class NodeFactory:
    """
    Factory for creating root and child nodes in BnB search.

    Args:
        instance: your Knapsack problem instance.
        relaxation: a RelaxationSolver to compute upper bounds.
        heuristics: a Heuristics instance to generate feasible solutions.
        on_new_node: callback invoked after each node creation (e.g. for logging).
    """

    def __init__(
        self,
        instance: Instance,
        relaxation: RelaxationSolver,
        heuristics: Heuristics,
        on_new_node: Callable[[BnBNode], None],
    ) -> None:
        self._instance = instance
        self._relaxation = relaxation
        self._heuristics = heuristics
        self._on_new_node = on_new_node
        self._node_counter = 0

    def create_root(self) -> BnBNode:
        """
        Create the root node with no fixations (all decisions None).
        """
        initial_decisions = BranchingDecisions(len(self._instance.items))
        relaxed_solution = self._relaxation.solve(self._instance, initial_decisions)
        root = BnBNode(
            relaxed_solution=relaxed_solution,
            branching_decisions=initial_decisions,
            depth=0,
            node_id=self._node_counter,
            parent_id=None,
        )
        heuristic_solutions = self._heuristics.search(self._instance, relaxed_solution)
        root.heuristic_solution = (
            heuristic_solutions[0] if heuristic_solutions else None
        )

        self._node_counter += 1
        self._on_new_node(root)
        return root

    def create_child(self, parent: BnBNode, decisions: BranchingDecisions) -> BnBNode:
        """
        Create a child of `parent` by applying new `decisions`.

        Depth is parent.depth+1; `parent_id` is parent.node_id.
        """
        relaxed_solution = self._relaxation.solve(self._instance, decisions)
        child = BnBNode(
            relaxed_solution=relaxed_solution,
            branching_decisions=decisions,
            depth=parent.depth + 1,
            node_id=self._node_counter,
            parent_id=parent.node_id,
        )
        heuristic_solutions = self._heuristics.search(self._instance, relaxed_solution)
        child.heuristic_solution = (
            heuristic_solutions[0] if heuristic_solutions else None
        )

        self._node_counter += 1
        self._on_new_node(child)
        return child

    def num_nodes(self) -> int:
        """
        Return the total number of nodes created so far.
        """
        return self._node_counter

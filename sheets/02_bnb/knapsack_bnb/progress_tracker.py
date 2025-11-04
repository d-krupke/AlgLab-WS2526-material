"""
ProgressTracker Module

Track and display detailed statistics of your branch-and-bound search.
You will see iteration counts, node creation/exploration, depth, status, and bounds.

You can customize the printed table or integrate further visualization callbacks.
"""

from datetime import datetime
from typing import Optional

from .bnb_nodes import BnBNode, NodeStatus
from .heuristics import HeuristicSolution
from .instance import Instance
from .search_strategy import SearchStrategy
from .solutions import SolutionPool
from .visualization import BnBVisualization


class ProgressTracker:
    """
    Monitors and reports BnB search progress:
      - iteration count
      - nodes created vs. explored
      - current node depth and status
      - current node value, global UB and LB
      - visualization callbacks
    """

    def __init__(
        self,
        instance: Instance,
        search_strategy: SearchStrategy,
        solutions: SolutionPool,
    ) -> None:
        self._instance = instance
        self._search = search_strategy
        self._solutions = solutions
        self._vis = BnBVisualization(instance)

        self._start_time: Optional[datetime] = None
        self.num_iterations = 0
        self._nodes_created = 0
        self._current_node: Optional[BnBNode] = None

    def upper_bound(self) -> float:
        """Global upper bound = max(queue UB, best known feasible LB)."""
        q_ub = self._search.upper_bound()
        lb = self._solutions.best_solution_value()
        return max(q_ub, lb)

    def lower_bound(self) -> float:
        """Current best feasible solution value."""
        return self._solutions.best_solution_value()

    def on_new_node_in_tree(self, node: BnBNode) -> None:
        """Called whenever a new node is generated."""
        self._nodes_created += 1
        self._vis.on_new_node_in_tree(node)

    def on_heuristic_solution(self, node: BnBNode, sol: HeuristicSolution) -> None:
        """Called when a heuristic finds a new feasible solution."""
        if not sol.is_integral() or not sol.does_obey_capacity_constraint():
            raise ValueError(f"Invalid heuristic solution: {sol}")
        # if sol.value() >= self._solutions.best_solution_value():
        node.heuristic_solution = sol
        print(
            f"[Heuristic] node {node.node_id} -> new feasible solution {sol} (value={sol.value():.3f})"
        )

    def on_node_pruned(
        self, node: BnBNode, best_solution: HeuristicSolution | None
    ) -> None:
        """Called whenever a node is pruned."""
        self._vis.on_node_pruned(node, best_solution)

    def start_search(self) -> None:
        """Initialize search reporting and print header."""
        self._start_time = datetime.now()
        header = (
            f"{'Iter':>5} {'Explored/Total':>15} {'Depth':>5} "
            f"{'Status':>10} {'Val':>7} {'UB':>7} {'LB':>7}"
        )
        print("BnB search started:")
        print(header)
        print("=" * len(header))

    def start_iteration(self, node: BnBNode) -> None:
        """Begin processing a node."""
        self.num_iterations += 1
        self._current_node = node

    def end_iteration(self, status: NodeStatus) -> None:
        """Finish processing a node and report its stats."""
        if self._current_node is None:
            return
        explored = self.num_iterations
        total = self._nodes_created
        depth = self._current_node.depth
        val = self._current_node.relaxed_solution.value()
        ub = self.upper_bound()
        lb = self.lower_bound()
        print(
            f"{self.num_iterations:5d} {explored:7d}/{total:<6d}{depth:6d} "
            f"{status.value:>13} {val:7.1f} {ub:7.1f} {lb:7.1f}"
        )
        # Visualization callback
        self._vis.on_node_processed(
            self._current_node,
            lb=lb,
            ub=ub,
            best_solution=self._solutions.best_solution(),
        )
        # reset per-iteration data
        self._current_node = None

    def end_search(self) -> None:
        """Finalize reporting and output summary and visualization."""
        duration = datetime.now() - self._start_time if self._start_time else None
        print("\nSearch finished.")
        print(
            f"Iterations: {self.num_iterations}, Nodes created: {self._nodes_created}."
        )
        best = self._solutions.best_solution()
        val = self._solutions.best_solution_value()
        print(f"Best solution: {best} with value {val:.3f}.")
        if duration:
            print(f"Elapsed time: {duration}.")
        # write visualization
        ts = datetime.now().strftime("%Y-%m-%d_%Hh-%Mm-%Ss")
        self._vis.visualize(
            self._solutions.best_solution(), f"bnb-{self._instance.id}_{ts}.html"
        )

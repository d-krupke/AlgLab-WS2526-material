"""
Branch-and-bound is a tree-based search for combinatorial optimization problems.
At each node, it:
 1. Computes an upper bound via a relaxation to estimate the best possible objective.
 2. Prunes subproblems whose bound cannot beat the current best feasible solution.
 3. Splits (branches) on decision variables to explore promising regions of the search space.
 4. Optionally applies heuristics to quickly find feasible solutions and improve pruning.

This module provides a clear, step-by-step BnB solver for the 0/1 knapsack problem, with four interchangeable components:
  - RelaxationSolver: compute upper bounds via a relaxation
  - SearchStrategy: manage the open node list (e.g., depth-first, best-first)
  - BranchingStrategy: decide which item to branch on
  - Heuristics: generate feasible integer solutions to improve pruning

You do not modify this file; instead, you will implement and supply custom strategies
for relaxation, branching, search ordering, and heuristics to observe performance differences.
"""

import logging
from typing import Optional

from .bnb_nodes import BnBNode, NodeFactory, NodeStatus
from .branching_strategy import BranchingStrategy
from .heuristics import Heuristics
from .instance import Instance
from .progress_tracker import ProgressTracker
from .relaxation import RelaxationSolver, RelaxedSolution
from .search_strategy import SearchStrategy
from .solutions import SolutionPool


class BnBSearch:
    """
    Branch-and-bound solver for the 0/1 knapsack problem.

    Usage:
        searcher = BnBSearch(
            instance,
            relaxation=my_relaxation,
            search_strategy=my_search_strategy,
            branching_strategy=my_branching,
            heuristics=my_heuristics,
        )
        best = searcher.search(iteration_limit=10000)
    """

    def __init__(
        self,
        instance: Instance,
        relaxation: RelaxationSolver,
        search_strategy: SearchStrategy,
        branching_strategy: BranchingStrategy,
        heuristics: Heuristics,
    ):
        # Core components
        self.instance = instance
        self.relaxation = relaxation
        self.search_strategy = search_strategy
        self.branching_strategy = branching_strategy
        self.heuristics = heuristics

        # Data structures for solutions and progress tracking
        self.solutions = SolutionPool()
        self.progress_tracker = ProgressTracker(
            instance, search_strategy, self.solutions
        )

        # Factory to create tree nodes, with callback on new node
        self.node_factory = NodeFactory(
            instance=instance,
            relaxation=relaxation,
            heuristics=heuristics,
            on_new_node=self.progress_tracker.on_new_node_in_tree,
        )

    def _process_node(self, node: BnBNode) -> NodeStatus:
        """
        Process a single node:
          1. Prune if infeasible or bound too low.
          2. Accept if solution is feasible (integral and within capacity).
          3. Apply heuristics to discover additional feasible solutions.
          4. Branch otherwise.
        Returns the node status after processing.
        """
        sol: RelaxedSolution = node.relaxed_solution

        # 1. Infeasibility prune
        if sol.is_infeasible():
            node.status = NodeStatus.INFEASIBLE
            return node.status

        # 2. Bound-based prune: no better solution possible
        if sol.upper_bound <= self.solutions.best_solution_value():
            node.status = NodeStatus.PRUNED
            return node.status

        # 3. Feasible solution found: integral and obeys capacity
        if sol.does_obey_capacity_constraint() and sol.is_integral():
            self.solutions.add(sol)
            node.status = NodeStatus.FEASIBLE
            return node.status

        # 4. Heuristic improvement: generate extra feasible solutions
        for heur_sol in self.heuristics.search(self.instance, node.relaxed_solution):
            # heur_sol must be feasible; pool enforces validity
            self.solutions.add(heur_sol)
            self.progress_tracker.on_heuristic_solution(node, heur_sol)

        # 5. Branch on a fractional decision variable
        branches = self.branching_strategy.make_branching_decisions(node)
        if not branches:
            logging.warning(
                "No branches created for node %s; check branching strategy.", node
            )

        for decision in branches:
            child = self.node_factory.create_child(node, decision)
            self.search_strategy.enqueue(child)
            child.status = NodeStatus.ENQUEUED

        node.status = NodeStatus.BRANCHED
        return node.status

    def search(self, iteration_limit: int = 10_000) -> Optional[RelaxedSolution]:
        """
        Run the branch-and-bound algorithm to optimum or until iteration_limit is reached.

        Args:
            iteration_limit: max number of nodes to process before aborting.

        Returns:
            The best feasible solution found (relaxed) or None if none found.

        Raises:
            ValueError: if the iteration_limit is reached without completion.
        """
        # Initialize root node and progress tracking
        root = self.node_factory.create_root()
        self.search_strategy.enqueue(root)
        self.progress_tracker.start_search()

        for iteration in range(1, iteration_limit + 1):
            if not self.search_strategy.has_next():
                break

            node = self.search_strategy.next()
            self.progress_tracker.start_iteration(node)
            status = self._process_node(node)
            self.progress_tracker.end_iteration(status)

            # Global prune: no better solution exists
            if (
                self.search_strategy.upper_bound()
                <= self.solutions.best_solution_value()
            ):
                logging.info("Global prune at iteration %d", iteration)
                for pruned_node in self.search_strategy.nodes_in_queue():
                    pruned_node.status = NodeStatus.PRUNED
                    self.progress_tracker.on_node_pruned(
                        pruned_node, self.solutions.best_solution()
                    )
                break

        else:
            # Iteration limit exhausted without finishing
            raise ValueError(f"Iteration limit of {iteration_limit} reached")

        self.progress_tracker.end_search()
        return self.solutions.best_solution()

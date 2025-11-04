"""
SolutionPool Module

Manage the set of feasible integer solutions found during the BnB search,
keeping track of the best one (highest value) for pruning and final output.

You do not need to modify this file; it validates and stores your solutions.
"""

from typing import Optional, List
from .relaxation import RelaxedSolution
from .heuristics import HeuristicSolution


class SolutionPool:
    """
    Stores feasible integral solutions and tracks the best one.

    Usage:
        pool = SolutionPool()
        pool.add(solution)
        best_val = pool.best_solution_value()
        best_sol = pool.best_solution()
    """

    def __init__(self) -> None:
        self._solutions: List[HeuristicSolution] = []
        self._best_solution: Optional[HeuristicSolution] = None

    def add(self, solution: HeuristicSolution) -> None:
        """
        Add a new feasible integral solution to the pool.

        Raises:
            AssertionError: if `solution` is infeasible or non-integral.
        """
        assert solution.does_obey_capacity_constraint(), (
            "Attempted to add a solution that violates capacity; "
            "ensure your heuristics generate only feasible solutions."
        )
        assert solution.is_integral(), (
            "Attempted to add a non-integral solution; "
            "ensure your heuristics produce integer selections."
        )
        # Add only unique solutions by value and selection
        if solution not in self._solutions:
            self._solutions.append(solution)
            # Update best if it's strictly better
            if (
                self._best_solution is None
                or solution.value() > self._best_solution.value()
            ):
                self._best_solution = solution

    def best_solution_value(self) -> float:
        """
        Return the value of the best solution, or -inf if none.
        """
        return (
            self._best_solution.value()
            if self._best_solution is not None
            else float("-inf")
        )

    def best_solution(self) -> Optional[HeuristicSolution]:
        """
        Return the best solution, or None if no solution was added.
        """
        return self._best_solution

    def all_solutions(self) -> List[RelaxedSolution]:
        """
        Return a list of all unique solutions found so far.
        """
        return list(self._solutions)

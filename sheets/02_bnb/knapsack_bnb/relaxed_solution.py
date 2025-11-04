"""
RelaxedSolution Module

This class represents a bounding solution for a knapsack branch.
A relaxed solution may relax capacity or integrality constraints to
compute an upper bound on the best feasible 0/1 solution under given fixations.

You should ensure your relaxation solver produces RelaxedSolution objects that:
  1. Keep fixed decisions unchanged.
  2. Have `upper_bound` >= the value of any feasible 0/1 solution under those decisions.
  3. Pass validation checks in this class.
"""

from typing import Sequence

from .instance import Instance


class RelaxedSolution:
    """
    Encapsulates a possibly-relaxed assignment (`selection`) and its bound.

    Args:
        instance: the knapsack Instance (with `items` and `capacity`).
        selection: a sequence of floats in [0,1], one per item;
                   fixed items must match your fixation (0 or 1).
        upper_bound: an upper bound on the value of any 0/1 solution
                     consistent with `selection` fixations.
    """

    def __init__(
        self,
        instance: Instance,
        selection: Sequence[float],
        upper_bound: float,
    ):
        if len(selection) != len(instance.items):
            raise ValueError("`selection` length must match number of items.")
        self.instance = instance
        self.selection = list(selection)
        self.upper_bound = upper_bound

        # Validate consistency: bound must exceed or equal actual value.
        actual = self.value()
        if self.upper_bound >= 0 and self.upper_bound < actual - 1e-8:
            raise ValueError(
                f"Actual value {actual} exceeds upper_bound {self.upper_bound}."
            )

    @staticmethod
    def create_infeasible(instance: Instance) -> "RelaxedSolution":
        """
        Return a RelaxedSolution marking an infeasible branch.
        Its `upper_bound` is -infinity and `selection` is all zeros.
        """
        return RelaxedSolution(
            instance,
            [0.0] * len(instance.items),
            upper_bound=float("-inf"),
        )

    def is_infeasible(self) -> bool:
        """
        Return True if this solution represents an infeasible branch.
        """
        return self.upper_bound == float("-inf")

    def value(self) -> float:
        """
        Compute total value = sum(item.value * fraction).
        """
        return sum(
            item.value * frac for item, frac in zip(self.instance.items, self.selection)
        )

    def weight(self) -> float:
        """
        Compute total weight = sum(item.weight * fraction).
        """
        return sum(
            item.weight * frac
            for item, frac in zip(self.instance.items, self.selection)
        )

    def does_obey_capacity_constraint(self) -> bool:
        """
        Return True if this relaxed solution is within capacity and selections
        are in [0,1]. Returns False for infeasible marker.
        """
        if self.is_infeasible():
            return False
        return (
            all(0.0 <= frac <= 1.0 for frac in self.selection)
            and self.weight() <= self.instance.capacity
        )

    def is_integral(self) -> bool:
        """
        Return True if all fractions are integers (0 or 1).
        """
        if self.is_infeasible():
            return False
        return all(frac == int(frac) for frac in self.selection)

    def __str__(self) -> str:
        """
        String representation like "[1|0.5|0|...]".
        Fractions are shown with one decimal if non-integer.
        """
        parts = []
        for frac in self.selection:
            if frac == int(frac):
                parts.append(str(int(frac)))
            else:
                parts.append(f"{frac:.1f}")
        return "[" + "|".join(parts) + "]"

    def copy(self) -> "RelaxedSolution":
        """
        Return a deep copy of this RelaxedSolution.
        """
        return RelaxedSolution(self.instance, self.selection.copy(), self.upper_bound)

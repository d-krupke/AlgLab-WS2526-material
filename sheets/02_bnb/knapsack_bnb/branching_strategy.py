"""
Branching Strategy Module

Defines how to split (branch) a BnB tree node when its current relaxed solution
is not yet a feasible integer solution. At each branching step:
 1. Select a decision variable that has not been fixed.
 2. Create two children by fixing that variable to 0 (exclude) and 1 (include).
 3. If all variables are fixed, no branches are returned (leaf node).

You should implement your own strategies by subclassing `BranchingStrategy`.
"""

from abc import ABC, abstractmethod
from typing import Iterable, Tuple

from .bnb_nodes import BnBNode, BranchingDecisions


class BranchingStrategy(ABC):
    """
    Abstract base for branching policies based on a node's relaxed solution.

    Subclasses must implement `make_branching_decisions` to return zero,
    two, or more `BranchingDecisions` objects describing child nodes.
    """

    @abstractmethod
    def make_branching_decisions(self, node: BnBNode) -> Iterable[BranchingDecisions]:
        """
        Return an iterable of `BranchingDecisions` to create child nodes.
        If no decisions can be made (all variables fixed), return an empty iterable.
        """
        ...


class FirstUndecidedBranchingStrategy(BranchingStrategy):
    """
    Branch on the first variable that has not yet been fixed.
    """

    def make_branching_decisions(self, node: BnBNode) -> Tuple[BranchingDecisions, ...]:
        # find the smallest index i where no decision has been made
        first_unfixed = min(
            (i for i, val in enumerate(node.branching_decisions) if val is None),
            default=-1,
        )
        if first_unfixed < 0:
            return ()  # leaf node, nothing to branch
        return node.branching_decisions.split_on(first_unfixed)


class MyBranchingStrategy(BranchingStrategy):
    """
    Your implementation of a branching strategy.

    Decide which variable(s) to branch on at each node using information
    from the node's relaxed solution (e.g., fractional values, scores, etc.).
    The simplest strategy is to pick an unfixed variable and split on 0/1.
    """

    def make_branching_decisions(self, node: BnBNode) -> Tuple[BranchingDecisions, ...]:
                

        if node.heuristic_solution:
            
            if node.heuristic_solution.upper_bound >= int(node.relaxed_solution.upper_bound):
                return ()
                        
            max_val = 0
            idx = 0
            enforced_weight = sum(item.weight for item, val in zip(node.heuristic_solution.instance.items, node.branching_decisions) if val == 1)
            
            for item_e, x in zip(enumerate(node.heuristic_solution.instance.items), node.heuristic_solution.selection):

                if (node.branching_decisions[item_e[0]] is None) and  (x == 0 or x == None) and (item_e[1].value / item_e[1].weight) > max_val and (item_e[1].weight + enforced_weight <= node.heuristic_solution.instance.capacity): 

                    max_val = item_e[1].value / item_e[1].weight
                    idx = item_e[0]

            if (idx != 0):
                return node.branching_decisions.split_on(idx)

        # placeholder: branch on the first unfixed variable
        first_unfixed = min(
            (i for i, val in enumerate(node.branching_decisions) if val is None),
            default=-1,
        )
        if first_unfixed < 0:
            return ()
        return node.branching_decisions.split_on(first_unfixed)



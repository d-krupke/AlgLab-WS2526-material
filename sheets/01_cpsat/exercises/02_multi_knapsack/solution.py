import math
from typing import List

from ortools.sat.python.cp_model import FEASIBLE, OPTIMAL, CpModel, CpSolver
from data_schema import Instance, Item, Solution


class MultiKnapsackSolver:
    """
    This class can be used to solve the Multi-Knapsack problem
    (also the standard knapsack problem, if only one capacity is used).

    Attributes:
    - instance (Instance): The multi-knapsack instance
        - items (List[Item]): a list of Item objects representing the items to be packed.
        - capacities (List[int]): a list of integers representing the capacities of the knapsacks.
    - model (CpModel): a CpModel object representing the constraint programming model.
    - solver (CpSolver): a CpSolver object representing the constraint programming solver.
    """


    def __init__(self, instance: Instance, activate_toxic: bool = False):
        """
        Initialize the solver with the given Multi-Knapsack instance.

        Args:
        - instance (Instance): an Instance object representing the Multi-Knapsack instance.
        """
        self.items = instance.items
        self.activate_toxic = activate_toxic
        self.capacities = instance.capacities
        self.model = CpModel()
        self.solver = CpSolver()
        self.solver.parameters.log_search_progress = True
        # TODO: Implement me!
        # make a matrix of decision variables
        self.x = [[self.model.new_bool_var(f"x_{j}_{i}") for i in range(len(self.items))] for j in range(len(self.capacities))]
        # j = trucks, i = items
        accumulated_value = sum(x_j_i * i.value for x_j in self.x for x_j_i, i in zip(x_j, self.items))
        accumulated_weights = [sum(x_j_i * i.weight for x_j_i, i in zip(x_j, self.items)) for x_j in self.x]
        accumulated_decisions = [sum(x_j_i for x_j_i in x_i) for x_i in zip(*self.x)] # iterate over columns

        for w in range(len(accumulated_weights)):
            self.model.add(accumulated_weights[w] <= self.capacities[w])
        
        for d in range(len(accumulated_decisions)):
            self.model.add(accumulated_decisions[d] <= 1)

        if activate_toxic:

            self.toxic_trucks = [self.model.new_bool_var(f"x{j}_toxtruck") for j in range(len(self.capacities))]

            for j, _ in enumerate(self.capacities, 0):
                for i, item in enumerate(self.items, 0):

                    self.model.add(self.x[j][i] * item.toxic <= self.toxic_trucks[j])
                    self.model.add(self.toxic_trucks[j] <= item.toxic + ~self.x[j][i])


        self.model.maximize(accumulated_value)



    def solve(self, timelimit: float = math.inf) -> Solution:
        """
        Solve the Multi-Knapsack instance with the given time limit.

        Args:
        - timelimit (float): time limit in seconds for the cp-sat solver.

        Returns:
        - Solution: a list of lists of Item objects representing the items packed in each knapsack
        """
        # handle given time limit
        if timelimit <= 0.0:
            return Solution(trucks=[])  # empty solution
        if timelimit < math.inf:
            self.solver.parameters.max_time_in_seconds = timelimit
        # TODO: Implement me!


        status = self.solver.solve(self.model)
        arrangement = [[self.items[i] for _, i in zip(truck, range(len(self.items))) if self.solver.Value(self.x[j][i])] for truck, j in zip(self.x, range(len(self.capacities)))]

        return Solution(trucks=arrangement)
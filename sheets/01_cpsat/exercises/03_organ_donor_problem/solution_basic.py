import math

import networkx as nx
from data_schema import Donation, Solution
from database import TransplantDatabase
from ortools.sat.python.cp_model import FEASIBLE, OPTIMAL, CpModel, CpSolver


class CrossoverTransplantSolver:
    def __init__(self, database: TransplantDatabase) -> None:
        """
        Constructs a new solver instance, using the instance data from the given database instance.
        :param Database database: The organ donor/recipients database.
        """
        self.database = database
        # TODO: Implement me!
        self.model = CpModel()
        self.solver = CpSolver()
        self.solver.parameters.log_search_progress = False

        self.graph = self._build_directed_graph(self.database)

        all_recipients = self.database.get_all_recipients()
        all_donors = self.database.get_all_donors()
        edges = self.graph.edges(data=True)

        self.x = {donor: self.model.new_bool_var(f"x{i}") for i, _, _, donor in enumerate(edges)}


        #constraints
        
        for donor in all_donors:
            self.model.add(sum(x_i for x_i, edge in zip(self.x, edges) if edge["donor"] == donor) <= 1)

        for recipient in all_recipients:
            self.model.add(sum(x_i for x_i, u, v in zip(self.x, edges) if v == recipient) <= 1)




        accumulated_donations = sum(x_i for x_i in self.x)
        self.model.maximize(accumulated_donations)



    def _build_directed_graph(self, database) -> nx.DiGraph:
        graph = nx.DiGraph()
        donors = database.get_all_donors()
        for donor in donors:
            partner = database.get_partner_recipient(donor)
            graph.add_node(partner)
            compatible_recipients = database.get_compatible_recipients(donor)

            graph.add_nodes_from([recipient for recipient in compatible_recipients])
            graph.add_edges_from([(partner, recipient, {"donor": donor}) for recipient in compatible_recipients])
        
        return graph
    
    def _extract_donations(self):

        donations = []
        for index, cycle in enumerate(self.cycles):
            if self.solver.value(self.x[index]) == 1:
                for i in range(len(cycle)):
                    j = i+1
                    if j > len(cycle)-1:
                        j = 0

                    donor = self.graph[cycle[i]][cycle[j]]["donor"]
                    donations += [Donation(donor=donor, recipient=cycle[j])]

        return donations
                        

    def optimize(self, timelimit: float = math.inf) -> Solution:
        """
        Solves the constraint programming model and returns the optimal solution (if found within time limit).
        :param timelimit: The maximum time limit for the solver.
        :return: A list of Donation objects representing the best solution, or None if no solution was found.
        """
        if timelimit <= 0.0:
            return Solution(donations=[])
        if timelimit < math.inf:
            self.solver.parameters.max_time_in_seconds = timelimit
        # TODO: Implement me!

        status = self.solver.solve(self.model)

        solution = self._extract_donations()

        return Solution(donations=solution)

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

        self.graph = self._build_directed_graph(self.database)

        self.cycles = list(nx.simple_cycles(self.graph, 3))

        #sorted(self.cycles)
        all_recipients = self.database.get_all_recipients()
        self.recipients_matrix = [[1 if (recipient in cycle) else 0 for recipient in all_recipients] for cycle in self.cycles]
        
        #decision variable which cycle should be taken
        self.x = [self.model.new_bool_var(f"x{i}") for i in range(len(self.cycles))]


        #constraints
        accumulated_overlap = [sum(x_i * r_ij for x_i, r_ij in zip(self.x, recipient_node)) for recipient_node in zip(*self.recipients_matrix)]
        
        for i in range(len(accumulated_overlap)):
            self.model.add(accumulated_overlap[i] <= 1)
        """ 
        for recipient_node in zip(*self.recipients_matrix):
            self.model.add(sum(x_i * r_ij for x_i, r_ij in zip(self.x, recipient_node)) <= 1)
        
        """
        
        accumulated_nodes = sum(x_i * r_ij for cycle, x_i in zip(self.recipients_matrix, self.x) for r_ij in cycle)
        self.model.maximize(accumulated_nodes)


        self.solver = CpSolver()
        self.solver.parameters.log_search_progress = True


    def _build_directed_graph(self, database) -> nx.MultiDiGraph:
        graph = nx.MultiDiGraph()
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
        for cycle in self.cycles:
            for i in range(len(cycle)):
                if self.solver.value(self.x[i]):
                    j = i+1
                    if j > len(cycle)-1:
                        #break ########################################
                        j = 0

                    donor = self.graph[cycle[i], cycle[j]].get("donor", None)
                    donations += [Donation(donor, cycle[j])]

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

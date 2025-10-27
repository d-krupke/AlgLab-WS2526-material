import math
from collections import defaultdict

import networkx as nx
from data_schema import Donation, Solution
from database import TransplantDatabase
from ortools.sat.python.cp_model import FEASIBLE, OPTIMAL, CpModel, CpSolver


class CycleLimitingCrossoverTransplantSolver:
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
        all_donors = self.database.get_all_donors()
        self.recipients_matrix = [[1 if recipient in cycle else 0 for recipient in all_recipients] for cycle in self.cycles]
        self.donors_matrix = [[1 if self._donor_in_cycle(donor, cycle) else 0 for donor in all_donors] for cycle in self.cycles]

        #decision variable which cycle should be taken
        self.x = [self.model.new_bool_var(f"x{i}") for i in range(len(self.cycles))]


        #constraints
        accumulated_overlap_r = [sum(x_i * r_ij for x_i, r_ij in zip(self.x, recipient_node)) for recipient_node in zip(*self.recipients_matrix)]
        accumulated_overlap_d = [sum(x_i * d_ij for x_i, d_ij in zip(self.x, donor_node)) for donor_node in zip(*self.donors_matrix)]

        for i in range(len(accumulated_overlap_r)):
            self.model.add(accumulated_overlap_r[i] <= 1)

        for i in range(len(accumulated_overlap_d)):
            self.model.add(accumulated_overlap_d[i] <= 1)
            
        # amount of recipients
        accumulated_nodes = sum(x_i * len(cycle) for cycle, x_i in zip(self.cycles, self.x))
        self.model.maximize(accumulated_nodes)

        self.solver = CpSolver()
        self.solver.parameters.log_search_progress = True

    def _donor_in_cycle(self, donor, cycle):

        for i in range(len(cycle)):
            j = i+1
            if j > len(cycle)-1:
                j = 0

            doner = self.graph[cycle[i]][cycle[j]]["donor"]
            if doner == donor:
                return True
        return False



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
        if timelimit <= 0.0:
            return Solution(donations=[])
        if timelimit < math.inf:
            self.solver.parameters.max_time_in_seconds = timelimit
        # TODO: Implement me!
        status = self.solver.solve(self.model)

        solution = self._extract_donations()

        return Solution(donations=solution)

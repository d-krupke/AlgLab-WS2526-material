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

        self.all_recipients = self.database.get_all_recipients()
        self.all_donors = self.database.get_all_donors()
        self.edges = self.graph.edges(data=True)

        self.x = {(edge[0], edge[1], edge[2]["donor"]): self.model.new_bool_var(f"x{i}") for i, edge in enumerate(self.edges, 0)}


        #constraints
        
        for donor in self.all_donors:
            self.model.add(sum(self.x[(edge[0], edge[1], edge[2]["donor"])] for edge in self.edges if edge[2]["donor"] == donor) <= 1)

        for recipient in self.all_recipients:
            self.model.add(sum(self.x[(edge[0], edge[1], edge[2]["donor"])] for edge in self.edges if edge[1] == recipient) <= 1)

         
        for edge in self.edges:

            donors_out = self.graph.out_edges(edge[1], data=True)
            succ_donations = [self.x[(succ_edge[0], succ_edge[1], succ_edge[2]["donor"])] for succ_edge in donors_out]                    
            self.model.add(sum(succ_donations) <= 1)


            donors_in = self.graph.in_edges(edge[0], data= True)
            pred_donations = [self.x[(pred_edge[0], pred_edge[1], pred_edge[2]["donor"])] for pred_edge in donors_in]
            self.model.add(self.x[(edge[0], edge[1], edge[2]["donor"])] <= sum(pred_donations))
            #self.model.add(sum(pred_donations) <= 1)
        



        accumulated_donations = sum(x_i for x_i in self.x.values())
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
        for edge in self.graph.edges(data=True):
            if self.solver.value(self.x[(edge[0], edge[1], edge[2]["donor"])]) == 1:
                donations.append(Donation(donor=edge[2]["donor"], recipient=edge[1]))

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

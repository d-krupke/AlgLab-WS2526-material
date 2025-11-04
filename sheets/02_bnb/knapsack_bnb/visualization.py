"""
This code creates an interactive visualization of a branch and bound tree.
You do not need to modify this code.
"""

import logging
from pathlib import Path
from typing import Literal

from jinja2 import Template
from pydantic import BaseModel, Field

from .bnb_nodes import BnBNode
from .heuristics import HeuristicSolution
from .instance import Instance
from .relaxation import RelaxedSolution

RELAXED_STATUS = Literal["integral", "infeasible", "feasible"]


class BnBTree(BaseModel):
    """
    Provides a structure for the branch-and-bound tree. Because of its recursive nature,
    every node is a BnBTree object, and the children of a node are stored in a list of BnBTree objects.
    """

    node_id: int = Field(..., description="The ID of the root node.")
    lb: float | None = Field(
        default=None,
        description="The lower bound of the node from the heuristic solution. May also be None if it got pruned.",
    )
    ub: float | None = Field(
        default=None,
        description="The upper bound from the relaxed solution. May also be None if it got pruned.",
    )
    created_at: int = Field(..., description="The time when the node was created.")
    processed_at: int | None = Field(
        default=None,
        description="The time when the node was processed. This may be later than its creation time. It may also be None if it got pruned.",
    )
    label: str = Field(..., description="Label of the node in the visualization.")
    status: RELAXED_STATUS = Field(
        ..., description="Status of the node in the visualization."
    )
    color: str = Field(..., description="Color of the node in the visualization.")
    children: list["BnBTree"] = Field(
        default_factory=list, description="Children of the node."
    )


class BnBVisualization:
    def __init__(self, instance: Instance):
        self.root: BnBTree | None = None
        self.node_links: dict[int, BnBTree] = {}
        self.instance: Instance = instance
        self.node_detail_texts: dict[int, str] = {}
        self.iteration_info_detail_texts: dict[int, str] = {}
        self.iteration_solution_details: dict[int, str] = {}
        self.node_tooltips: dict[int, str] = {}
        self.iterations: list[int] = []  # id of node processed in iteration

    def _get_node_color(self, node: BnBNode) -> str:
        if (
            node.relaxed_solution.does_obey_capacity_constraint()
            and node.relaxed_solution.is_integral()
            and not node.relaxed_solution.is_infeasible()
        ):
            return "#20c997"
        return "#adb5bd" if not node.relaxed_solution.is_infeasible() else "#dc3545"

    def _get_node_status(self, node: BnBNode) -> RELAXED_STATUS:
        if (
            node.relaxed_solution.does_obey_capacity_constraint()
            and node.relaxed_solution.is_integral()
            and not node.relaxed_solution.is_infeasible()
        ):
            return "integral"
        return "feasible" if not node.relaxed_solution.is_infeasible() else "infeasible"

    def on_new_node_in_tree(self, node: BnBNode):
        color = self._get_node_color(node)
        status = self._get_node_status(node)
        label = f"{node.relaxed_solution.upper_bound:.1f}"
        data = BnBTree(
            node_id=node.node_id,
            label=label,
            color=color,
            status=status,
            children=[],
            created_at=len(self.iterations),
        )
        if node.parent_id is None:
            assert self.root is None, "Root already exists."
            self.root = data
        else:
            self.node_links[node.parent_id].children.append(data)
        self.node_links[node.node_id] = data

    def on_node_processed(
        self,
        node: BnBNode,
        lb: float,
        ub: float,
        best_solution: HeuristicSolution | None,
    ):
        """
        Called when a node is processed. Updates the jinja templates with information about the node.
        Args:
            node (BnBNode): The node that was processed.
            lb (float): The lower bound of the node from the heuristic solution.
            ub (float): The upper bound from the relaxed solution.
            best_solution (RelaxedSolution | None): The best heuristic solution found so far.
        """
        self.iterations.append(node.node_id)
        # Update BnB data
        vis_node = self.node_links[node.node_id]
        vis_node.processed_at = len(self.iterations) - 1
        vis_node.lb = lb
        vis_node.ub = ub
        if node.parent_id is not None:
            parent_processed_at = self.node_links[node.parent_id].processed_at
            node_processed_at = self.node_links[node.node_id].processed_at
            assert parent_processed_at is not None
            assert node_processed_at is not None
            assert parent_processed_at < node_processed_at

        with (
            Path(__file__).parent / "./templates/node_details.j2.html"
        ).open() as file:
            # Render the node details
            template_node_info = Template(file.read())
            node_info = template_node_info.render(
                node=node,
                lb=lb,
                ub=ub,
                current_heuristic=node.heuristic_solution,
                best_solution=best_solution,
                weight=node.relaxed_solution.weight(),
            )
            self.node_detail_texts[node.node_id] = node_info

        with (
            Path(__file__).parent / "./templates/iteration_info.j2.html"
        ).open() as file:
            # Render iteration information
            iteration_info_template = Template(file.read())
            iteration_info = iteration_info_template.render(
                node=node,
                instance=self.instance,
                best_solution=best_solution,
                current_heuristic=node.heuristic_solution,
            )
            self.iteration_info_detail_texts[node.node_id] = iteration_info

        with (
            Path(__file__).parent / "./templates/iteration_solution_details.j2.html"
        ).open() as file:
            # Render iteration solutions
            iteration_solutions_template = Template(file.read())
            iteration_solutions = iteration_solutions_template.render(
                instance=self.instance,
                best_solution=best_solution,
                current_heuristic=node.heuristic_solution,
                current_relaxed=node.relaxed_solution,
            )
            self.iteration_solution_details[node.node_id] = iteration_solutions

        with (
            Path(__file__).parent / "./templates/node_tooltip.j2.html"
        ).open() as file:
            node_tooltip_template = Template(file.read())
            node_tooltip = node_tooltip_template.render(
                node=node,
                included_items=node.branching_decisions.included_items(),
                included_weight=sum(
                    self.instance.items[i].weight
                    for i in node.branching_decisions.included_items()
                ),
                excluded_items=node.branching_decisions.excluded_items(),
                iteration=len(self.iterations) - 1,
                iterations=self.iterations,
                lb=lb,
                current_heuristic=node.heuristic_solution,
            )
            self.node_tooltips[node.node_id] = node_tooltip

    def on_node_pruned(
        self,
        node: BnBNode,
        best_solution: HeuristicSolution | None,
    ):
        """
        Called when a node is globally pruned. Updates the jinja templates with information about the node.
        Args:
            node (BnBNode): The node that was processed.

        """
        with (
            Path(__file__).parent / "./templates/node_tooltip.j2.html"
        ).open() as file:
            node_tooltip_template = Template(file.read())
            node_tooltip = node_tooltip_template.render(
                node=node,
                lb=best_solution.value() if best_solution else None,
                included_items=node.branching_decisions.included_items(),
                included_weight=sum(
                    self.instance.items[i].weight
                    for i in node.branching_decisions.included_items()
                ),
                excluded_items=node.branching_decisions.excluded_items(),
                iteration=len(self.iterations) - 1,
                iterations=self.iterations,
            )
            self.node_tooltips[node.node_id] = node_tooltip

    def visualize(
        self, end_solution: RelaxedSolution | None, path: str = "output.html"
    ):
        """
        Visualizes the branch-and-bound tree and saves it to an HTML file.
        Opens the file in the default web browser.
        Args:
            end_solution (RelaxedSolution | None): The best heuristic solution found at the end of the algorithm.
            path (str): The path to save the HTML file.
        """
        if self.root is None:
            msg = "No nodes to visualize."
            raise ValueError(msg)
        if end_solution is None:
            msg = "No solution to visualize."
            raise ValueError(msg)
        with (
            Path(__file__).parent / "./templates/instance_info.j2.html"
        ).open() as file:
            # Render instance information
            instance_template = Template(file.read())
            instance_info = instance_template.render(
                instance=self.instance, best_solution=end_solution
            )
        with (
            Path(__file__).parent / "./templates/solution_details.j2.html"
        ).open() as file:
            solution_template = Template(file.read())
            solution_details = solution_template.render(
                instance=self.instance,
                num_iterations=len(self.iterations) - 1,
                best_solution=end_solution,
            )

        # Render main html
        with (Path(__file__).parent / "./templates/bnb.j2.html").open() as file:
            template: Template = Template(file.read())
            with Path(path).open("w") as file:
                data = str(self.root.model_dump_json())
                file.write(
                    template.render(
                        tree_data=data,
                        num_iterations=len(self.iterations) - 1,
                        iterations=self.iterations,
                        iteration_info=self.iteration_info_detail_texts,
                        iteration_solution_details=self.iteration_solution_details,
                        instance_info=instance_info,
                        instance=self.instance,
                        solution_details=solution_details,
                        node_details=self.node_detail_texts,
                        node_tooltips=self.node_tooltips,
                    )
                )
                logging.info("Visualization saved to %s", path)
                # open the file in the default web browser
                try:
                    import webbrowser

                    webbrowser.open_new_tab(path)
                except Exception as e:
                    logging.error(
                        "Error opening the file in the browser. Please open it manually."
                    )
                    logging.exception(e)

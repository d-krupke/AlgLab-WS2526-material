import logging

from knapsack_bnb import BnBSearch
from knapsack_bnb.branching_strategy import MyBranchingStrategy
from knapsack_bnb.heuristics import MyHeuristic
from knapsack_bnb.instance import Instance, Item
from knapsack_bnb.relaxation import MyRelaxationSolver
from knapsack_bnb.search_strategy import SearchStrategy, my_search_order

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


def run_trivial_instance():
    logging.info(
        "Running first instance. You should try to tune the BnBSearch to get below 10 iterations."
    )
    instance = Instance(
        items=[
            Item(weight=1, value=1),
            Item(weight=2, value=1),
            Item(weight=3, value=1),
            Item(weight=4, value=1),
            Item(weight=5, value=1),
        ],
        capacity=10,
    )

    # You can easily exchange the various components of the BnBSearch here:
    bnb = BnBSearch(
        instance,
        relaxation=MyRelaxationSolver(),
        search_strategy=SearchStrategy(priority=my_search_order),
        branching_strategy=MyBranchingStrategy(),
        heuristics=MyHeuristic(),
    )

    bnb.search()
    logging.info(
        "Finished search with %d iterations.", bnb.progress_tracker.num_iterations
    )
    assert bnb.progress_tracker.upper_bound() == 4, "The objective value should be 5."
    assert bnb.progress_tracker.lower_bound() == 4, "The bound should be 5."
    logging.info(
        "Optimal solution found, that's already good. Now checking number of iterations."
    )


if __name__ == "__main__":
    run_trivial_instance()

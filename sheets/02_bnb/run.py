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


def run_first_instance():
    logging.info(
        "Running first instance. You should try to tune the BnBSearch to get below 10 iterations."
    )
    instance = Instance(
        id=1,
        items=[
            Item(weight=1, value=1),
            Item(weight=2, value=1),
            Item(weight=3, value=1),
            Item(weight=4, value=1),
            Item(weight=5, value=1),
            Item(weight=6, value=1),
            Item(weight=7, value=1),
            Item(weight=8, value=1),
            Item(weight=9, value=1),
            Item(weight=10, value=1),
        ],
        capacity=20,
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
    assert bnb.progress_tracker.upper_bound() == 5, "The objective value should be 5."
    assert bnb.progress_tracker.lower_bound() == 5, "The bound should be 5."
    logging.info(
        "Optimal solution found, that's already good. Now checking number of iterations."
    )
    assert bnb.progress_tracker.num_iterations <= 200, (
        "You should not need more than 200 iterations."
    )
    assert bnb.progress_tracker.num_iterations <= 50, "Try to get below 50 iterations!"


def run_second_instance():
    logging.info(
        "Running second instance. You should try to tune the BnBSearch to get below 10 iterations."
    )
    instance = Instance(
        id=2,
        items=[
            Item(weight=1, value=10),
            Item(weight=2, value=10),
            Item(weight=3, value=10),
            Item(weight=4, value=10),
            Item(weight=5, value=10),
            Item(weight=6, value=10),
            Item(weight=7, value=10),
            Item(weight=8, value=10),
            Item(weight=9, value=10),
            Item(weight=10, value=10),
            Item(weight=11, value=20),
            Item(weight=12, value=30),
        ],
        capacity=20,
    )

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
    assert bnb.progress_tracker.upper_bound() == 60, "The objective value should be 60."
    assert bnb.progress_tracker.lower_bound() == 60, "The bound should be 60."
    logging.info(
        "Optimal solution found, that's already good. Now checking number of iterations."
    )
    assert bnb.progress_tracker.num_iterations <= 200, (
        "You should not need more than 200 iterations."
    )
    assert bnb.progress_tracker.num_iterations <= 10, "Try to get below 10 iterations!"


def run_third_instance():
    logging.info(
        "Running third instance. You should try to tune the BnBSearch to get below 30 iterations."
    )
    instance = Instance(
        id=3,
        items=[
            Item(weight=1, value=10),
            Item(weight=3, value=15),
            Item(weight=5, value=7),
            Item(weight=7, value=22),
            Item(weight=9, value=13),
            Item(weight=11, value=17),
            Item(weight=13, value=9),
            Item(weight=15, value=27),
            Item(weight=17, value=16),
            Item(weight=19, value=21),
            Item(weight=21, value=29),
            Item(weight=23, value=30),
            Item(weight=25, value=25),
            Item(weight=27, value=31),
            Item(weight=29, value=18),
            Item(weight=31, value=33),
            Item(weight=33, value=20),
            Item(weight=35, value=35),
            Item(weight=37, value=23),
            Item(weight=39, value=37),
        ],
        capacity=100,
    )

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
    assert bnb.progress_tracker.upper_bound() == 171, (
        "The objective value should be 171."
    )
    assert bnb.progress_tracker.lower_bound() == 171, "The bound should be 171."
    logging.info(
        "Optimal solution found, that's already good. Now checking number of iterations."
    )
    assert bnb.progress_tracker.num_iterations <= 200, (
        "You should not need more than 200 iterations."
    )
    assert bnb.progress_tracker.num_iterations <= 30, "Try to get below 30 iterations!"


if __name__ == "__main__":
    run_first_instance()
    run_second_instance()
    run_third_instance()

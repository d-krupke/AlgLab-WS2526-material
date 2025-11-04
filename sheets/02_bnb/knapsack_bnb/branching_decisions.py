class BranchingDecisions:
    """
    Represents the binary branching decisions made during the branch-and-bound algorithm.

    This class provides methods to initialize, access, fix, and split the branching decisions.

    Args:
        length (int): Number of variables.

    Methods:
        __getitem__(index) -> int 
            Get the decision at `index`.
        fix(index, value) -> None 
            Fix the decision at `index` to `value`
        length() -> int 
            Get the length of the branching decisions. Equals the number of variables and is constant.
        __iter__() -> Iterator[int | None]: 
            Iterate over the branching decisions.
        split_on(index) -> (BranchingDecisions, BranchingDecisions) 
            Split the branching decisions into two based on the specified index.
    """

    def __init__(self, length: int) -> None:
        self._assignments: list[int | None] = [None] * length

    def __getitem__(self, item_index: int) -> int | None:
        return self._assignments[item_index]

    def fix(self, item_index: int, value: int) -> None:
        """
        Fixes the usage of an item in the knapsack to the specified value.
        Only do this if you are sure that you do not prohibit the optimal solution.
        """
        assert value in {0, 1}, "Value must be 0 or 1."
        assert self._assignments[item_index] is None, "Item is already fixed."
        self._assignments[item_index] = value

    def copy(self) -> "BranchingDecisions":
        """Create a copy of the branching decisions.

        Returns:
            BranchingDecisions: A copy of the branching decisions.

        Examples:
            >>> decisions = BranchingDecisions(5)
            >>> copy = decisions.copy()
        """
        copy = BranchingDecisions(len(self))
        copy._assignments = self._assignments.copy()
        return copy
    
    def included_items(self) -> list[int]:
        """
        Returns a list of fixed included items
        """
        return [idx for idx,assigned in enumerate(self._assignments) if assigned == 1]

    def excluded_items(self) -> list[int]:
        """
        Returns a list of fixed excluded items
        """
        return [idx for idx,assigned in enumerate(self._assignments) if assigned == 0]

    def __len__(self) -> int:
        return len(self._assignments)

    def __iter__(self):
        return iter(self._assignments)

    def is_fixed(self) -> bool:
        """Check if all items are fixed.

        Returns:
            bool: True if all items are fixed, False otherwise.

        Examples:
            >>> decisions = BranchingDecisions(5)
            >>> decisions.fix(0, 1)
            >>> decisions.is_fixed()
            False
        """
        return all(x is not None for x in self._assignments)

    def split_on(
        self, item_index: int
    ) -> tuple["BranchingDecisions", "BranchingDecisions"]:
        """Split the branching decisions into two based on the specified item index.

        This method creates two new instances of BranchingDecisions, left and right,
        with the same assignments as the current instance, except for the specified item index.
        The left instance fixes the item to 0, while the right instance fixes it to 1.

        Args:
            item_index: The index of the item to split on.

        Returns:
            Tuple[BranchingDecisions, BranchingDecisions]: The left and right instances of BranchingDecisions. The left instance does not use the item, while the right instance uses it.

        Examples:
            >>> decisions = BranchingDecisions(5)
            >>> left, right = decisions.split_on(2)
        """

        left = BranchingDecisions(len(self))
        right = BranchingDecisions(len(self))
        left._assignments = self._assignments.copy()
        right._assignments = self._assignments.copy()
        left.fix(item_index, 0)
        right.fix(item_index, 1)
        return left, right

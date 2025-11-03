from pydantic import BaseModel, ConfigDict, Field


class Item(BaseModel):
    """
    Represents an item with a weight and a value for the knapsack problem.
    """

    weight: int = Field(..., ge=0, description="Weight of the item")
    value: int = Field(..., ge=0, description="Value of the item")

    # Prevent the model from being modified after creation
    model_config = ConfigDict(frozen=True)


class Instance(BaseModel):
    """
    Represents an instance with a list of items and capacity of the knapsack problem.
    """

    items: list[Item] = Field(
        default_factory=list,
        description="List of items in the knapsack problem instance",
    )
    capacity: int = Field(
        ..., ge=0, description="Capacity of the knapsack problem instance"
    )
    id: int = Field(default=1, ge=1, description="Id of the instance")

    # Prevent the model from being modified after creation
    model_config = ConfigDict(frozen=True)

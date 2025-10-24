from data_schema import Instance, Solution
from ortools.sat.python import cp_model


def solve(instance: Instance) -> Solution:
    """
    Implement your solver for the problem here!
    """
    numbers = instance.numbers
    model = cp_model.CpModel()

    domain = cp_model.Domain.from_values(numbers)
    max_num = model.new_int_var_from_domain(domain, "max_num")
    min_num = model.new_int_var_from_domain(domain, "min_num")

    model.maximize(max_num - min_num)

    solver = cp_model.CpSolver()
    solver.solve(model)

    numbers[0] = solver.value(max_num)
    numbers[-1] = solver.value(min_num)

    return Solution(
        number_a=numbers[0],
        number_b=numbers[-1],
        distance=abs(numbers[0] - numbers[-1]),
    )

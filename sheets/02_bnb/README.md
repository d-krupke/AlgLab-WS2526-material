# Your Own Branch-and-Bound Solver for Knapsack

![Image](./.assets/bnb_symbol.png)

After experimenting with CP-SAT as a black-box solver, this exercise takes you
"under the hood" of NP-hard optimization by building a tailor-made
Branch-and-Bound (BnB) algorithm for the 0/1 Knapsack Problem. The aim is to
keep your search tree as small (and your runtime as low) as possible by plugging
in better relaxations, branching rules, search orders, and heuristics.

## Learning Goals

- **Understand** the four core BnB components: relaxation (upper bounds),
  branching, node ordering, and heuristics (lower bounds).
- **Experiment** with different strategies and immediately see their impact via
  an interactive tree visualization.
- **Measure** performance in terms of nodes created, iterations, and ability to
  solve benchmark instances within a fixed iteration limit.

## Prerequisites

- A refresher on BnB (e.g.,
  [Pascal van Hentenryck’s 15 min video on Coursera](https://www.coursera.org/lecture/discrete-optimization/knapsack-5-relaxation-branch-and-bound-66OlO?utm_source=link&utm_medium=page_share&utm_content=vlp&utm_campaign=top_button), EDIT: This course unfortunately has been removed, but you can find a copy on youtube, e.g., [here](https://www.youtube.com/watch?v=Kw5DNm39bmA)).
- Optional: Algorithms & Data Structures 2, or any textbook covering BnB.

## Getting Started

1. **Inspect the code** in `knapsack_bnb/`. You won’t modify the solver core --
   only the strategy classes.
2. Run the trivial instance:
   ```bash
   python run_trivial.py
   ```
   An `bnb_tree_DATETIME.html` will pop up showing the tiny BnB tree.
3. Open the pre-generated reference trees in the root folder
   (`bnb_tree_trivial.html`, `bnb_tree_benchmark_1.html`, etc.) to compare and
   maybe identify the strategies we used to generate them.

## Your Tasks

1. **Relaxations**: Swap in a fractional-knapsack or other tighter bound in
   `relaxation.py`.
2. **Branching**: Implement smarter variable-selection in
   `branching_strategy.py`.
3. **Search Order**: Try best-first or hybrid depth-first in
   `search_strategy.py`.
4. **Heuristics**: Add greedy or rounding methods in `heuristics.py`.

Each time you tweak a strategy, re-run `run.py` and watch the tree and
performance metrics. You are allowed to swap the components directly in the
`run.py` such that you can easily compare different strategies. The only thing
you need to change for this is the `BnBSearch` instantiation.

```python
bnb = BnBSearch(
    instance,
    relaxation=MyRelaxationSolver(),  # specify your relaxation here
    search_strategy=SearchStrategy(priority=my_search_order),  # specify your search order here
    branching_strategy=MyBranchingStrategy(),  # specify your branching strategy here
    heuristics=MyHeuristic(),  # specify your heuristics here
)
```

Note that every run will create a new HTML file with the instance number, current date and time in the filename.
You may want to delete the old files to avoid clutter:

```sh
chmod +x clean.sh   # Make clean-script executable
./clean.sh
```

> [!TIP]
>
> The most complex part of this exercise is probably the relaxation. All other
> components just need the right insights but otherwise are trivial to
> implement. In case you are lucky on the first try, I recommend to still try to
> play around a little to get a better feeling of the impact of certain
> decisions.

## Submission & Evaluation

- You must solve **all three** benchmark instances under the iteration limit.
  The time is not limited, although it should be reasonable.
- Include a short report (Markdown or Jupyter) summarizing which combination of
  strategies gave you the smallest tree and fastest run time.
- You are not allowed to hard code the solution or branching decisions in any
  way.

Good luck, and may your search tree stay shallow!

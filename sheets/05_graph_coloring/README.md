# Benchmarking the Performance of Different Solvers and Formulations for the Graph Coloring Problem

For the remainder of the semester, we will focus on the **graph coloring
problem**, which arises as a subproblem in various applications, such as
register allocation in compilers, scheduling, and frequency assignment in
wireless networks.

Numerous formulations have been proposed for solving the graph coloring problem
using different solvers. Nevertheless, the problem remains computationally
challenging, making it a suitable candidate for comparing the performance of
various solvers and formulations—an endeavor that, as you will see, is far from
trivial.

In contrast to sorting algorithms, where performance comparisons are relatively
straightforward—for example, by measuring the average time to sort _n_ elements
for increasing values of _n_—graph coloring presents a more complex landscape.
Some small graphs may remain unsolved within a reasonable time limit, while some
large graphs can be solved within seconds. Moreover, solver performance may vary
significantly across different graph classes: a solver might perform well on one
class but poorly on another.

## The Graph Coloring Problem

Given an undirected graph $G = (V, E)$ , the goal is to assign colors to the
vertices such that:

- No two adjacent vertices share the same color.
- The total number of colors used is minimized.

Formally, we seek a function $c : V \rightarrow \{1, \dots, k\}$ such that
$c(u) \neq c(v)$ for all edges $(u, v) \in E$ , and $k$ is minimized. The
minimum such $k$ is called the _chromatic number_ of the graph, denoted
$\chi(G)$ .

This problem arises in a variety of contexts, including register allocation,
scheduling, and frequency assignment in wireless networks.

### Why Is Graph Coloring Interesting?

The graph coloring problem is NP-hard. Even for small graphs, determining the
chromatic number can be computationally demanding. Moreover, it is hard to
approximate: unless $\text{P} = \text{NP}$ , there exists no polynomial-time
algorithm that guarantees a good approximation factor in the general case.

This makes the problem an excellent benchmark for evaluating the performance of
exact algorithms, such as:

- Integer Linear Programming (ILP) formulations
- Constraint Programming (CP) models
- SAT-based encodings

Each of these approaches has distinct strengths depending on the structure of
the input graph.

### Different Formulations

The graph coloring problem admits several formulations, each with distinct
characteristics and implications for solving the problem.

#### Assignment-Based ILP Formulation (ASS)

In the assignment-based ILP formulation, we introduce for every vertex $v \in V$
a binary decision variable $x_{v,c} \in \mathbb{B}$ that indicates whether
vertex $v$ is assigned color $c \in \mathcal{C}$ from the set of colors
$\mathcal{C}$. Additionally, we introduce for every color $c$ a binary variable
$y_c \in \mathbb{B}$ that indicates whether color $c$ is used. Minimizing the
number of colors then corresponds to minimizing the sum
$\sum_{c \in \mathcal{C}} y_c$:

$$\min \sum_{c \in \mathcal{C}} y_c$$

To ensure that no two adjacent vertices share the same color, we add the
following constraints:

$$x_{u,c} + x_{v,c} \leq 1 \quad \forall (u,v) \in E, \ \forall c \in \mathcal{C}$$

Next, we connect the vertex-color assignment variables $x$ with the color usage
variables $y$ through the constraints:

$$x_{v,c} \leq y_c \quad \forall v \in V, \ \forall c \in \mathcal{C}$$

This formulation theoretically allows a color to be marked as used without being
assigned to any vertex, since the constraints only enforce that $y_c=1$ whenever
$x_{v,c}=1$ for some vertex $v$. However, because the objective minimizes
$\sum y_c$, the solver will not set $y_c=1$ unless the color is actually used.

One issue remains: the set $\mathcal{C}$ is not part of the input but has a
major impact on the model size. Nonetheless, it is relatively easy to construct
a feasible choice for $\mathcal{C}$:

- The most naive choice is $|V|$ colors, which trivially yields a feasible
  solution by assigning each vertex a distinct color. This eliminates conflicts
  but produces a very large model.
- A slightly better choice is $\Delta(G) + 1$ colors, where $\Delta(G)$ denotes
  the maximum degree of the graph (i.e., the maximum number of neighbors of any
  vertex). This also guarantees feasibility: suppose a vertex is assigned a
  color outside the $\Delta(G) + 1$ range. Since the vertex has at most
  $\Delta(G)$ neighbors, at most $\Delta(G)$ distinct colors are occupied,
  leaving at least one color available within the range. Reassigning in this
  manner ensures all vertices can be colored within $\Delta(G) + 1$ colors.
- An even better choice is to first run a heuristic coloring algorithm (the
  previous argument essentially describes a naive greedy heuristic) and then
  restrict $\mathcal{C}$ to the colors produced by the heuristic solution.

#### Assignment-based ILP Formulation with Symmetry Breaking (ASS-S)

A major drawback of the ASS model is its large number of symmetries, which often
cause inefficiencies during solving. For every feasible solution, one can
permute the colors assigned to the vertices, yielding a different representation
of the same solution. Consequently, each (partial) solution has up to
$|\mathcal{C}|!$ equivalent representations. Although this might seem
advantageous—since the optimal solution now has many representatives—it actually
inflates the number of partial solutions that must be explored. Each incorrect
assignment can reappear up to $|\mathcal{C}|!$ times under different
permutations, significantly slowing the search.

To mitigate this, we can _break the symmetry_ by imposing an order on the
colors. Specifically, color $c_i$ may only be used if color $c_{i-1}$ is already
in use. This enforces a sequential structure: we must begin with $c_0$, then
proceed to $c_1$, and so forth. While no inherent order exists on $\mathcal{C}$,
we can impose one, for instance, by indexing the colors. This yields the
constraints:

$$y_c \leq y_{c-1} \quad \forall c \in \mathcal{C}\setminus\{c_0\}$$

Recall, however, that $y_c$ merely indicates that color $c$ is available, not
necessarily that it is used. To ensure consistency with actual assignments, we
add:

$$y_c \leq \sum_{v \in V} x_{v,c} \quad \forall c \in \mathcal{C}$$

Thus, $y_c$ can take the value 1 only if some vertex $v$ is assigned color $c$.

> [!WARNING]
>
> Many solvers attempt to detect and break symmetries automatically. These
> built-in mechanisms are frequently more efficient than manually added
> constraints. In fact, manual symmetry breaking may interfere with the solver’s
> ability to recognize other, more subtle symmetries, and can even reduce
> overall efficiency. Since it is difficult to predict which method will be
> superior, it is usually best to try both approaches in practice.

#### Representative-based ILP Formulation (REP)

In the ASS formulations, we encountered the drawback of working with explicit
colors, which introduced symmetries. However, we are not truly interested in the
specific colors; we only need to know which vertices share the same color. This
idea forms the basis of the **Representative-based ILP Formulation**.

We introduce binary decision variables $x_{v,w}$ that indicate whether vertex
$v \in V$ takes the same color as vertex $w \in V \setminus N(v)$, thereby
making $w$ the representative of $v$. Since adjacent vertices cannot share a
color, all neighbors $N(v)$ of $v$ are excluded. The special case $x_{v,v}$
indicates that $v$ is a representative of itself. To minimize the number of
colors used, we minimize the number of representatives:

$$\min \sum_{v \in V} x_{v,v}$$

First, every vertex must choose exactly one representative (possibly itself).
This is enforced by:

$$\sum_{w \in V \setminus N(v)} x_{v,w} = 1 \quad \forall v \in V$$

Next, we ensure two properties:

1. No two adjacent vertices $u$ and $v$ may select the same representative $w$.
2. If $v$ selects $w$ as its representative, then $w$ must itself be marked as a
   representative.

Both conditions can be expressed in a single constraint:

$$x_{u,w} + x_{v,w} \leq x_{w,w} \quad \forall (u,v) \in E,\; u,v \in V \setminus \big(N(w) \cup \{w\}\big)$$

Alternatively, these can be split into two sets of constraints:

- $x_{v,w} \leq x_{w,w} \quad \forall v \in V,\; w \in V \setminus (N(v) \cup \{v\})$
- $x_{u,w} + x_{v,w} \leq 1 \quad \forall (u,v) \in E,\; u,v \in V \setminus \big(N(w) \cup \{w\}\big)$

As a rule of thumb, formulations should use as few coefficients as possible;
therefore, the single combined constraint is often more efficient.

At this point, one might observe that symmetries remain: any vertex can serve as
a representative. This becomes particularly problematic if there are few but
large color classes. Fortunately, there is a simple fix: enforce the vertex with
the lowest index in each class to be the representative. This can be achieved by
setting $x_{v_i,v_j} = 0$ for all $v_i,v_j \in V$ with $j > i$. Thus, the
smallest-index vertex in each class must serve as its representative, and no
vertex can select a higher-index vertex as its representative. Rather than
encoding these equalities as explicit constraints, it is more efficient to apply
them directly, which nearly halves the number of variables.

> [!WARNING]
>
> Be careful with the definition of sets in this formulation.

#### Constraint Programming: ≠-Formulation (CP≠)

When using a Constraint Programming solver such as CP-SAT that supports the `!=`
constraint, we can define a straightforward formulation with integer variables.
For each vertex $v \in V$, we introduce an integer variable
$z_v \in \{1, \dots, |\mathcal{C}|\}$ representing the color index of $v$. The
model is then:

$$ \min \max\_{v \in V} z_v $$

$$
\text{s.t.} \quad z_u \neq z_v \quad \forall
(u,v) \in E
$$

Since most solvers cannot directly represent the min–max objective, we introduce
an auxiliary variable $z_{\max}$ with the following constraints:

$$ z*v \leq z_{\max} \quad \forall v \in V $$

This allows us to reformulate the problem as:

$$ \min z_{\max} $$

$$
\text{s.t.} \quad z_u \neq z_v \quad \forall (u,v) \in
E
$$

$$ z_v \leq z_{\max} \quad \forall v \in V $$

#### Constraint Programming: AllDifferent Formulation (CP-AllDiff)

We can strengthen the CP≠ model by posting `AllDifferent` constraints on subsets
of vertices that form cliques. For any clique $Q \subseteq V$:

$$\text{s.t.}\quad \text{AllDifferent}(z_v \mid v \in Q)$$

This enforces that all vertices in $Q$ receive distinct colors. Since every edge
is itself a clique of size two, the standard edge constraints are just the
smallest special case. By adding larger cliques, we capture more structure and
prune the search space more effectively.

In practice, the number of cliques can be exponential, so only a selection
should be added. Common approaches include:

- greedily extending edges to larger cliques,
- or generating maximal cliques (e.g., with `networkx.find_cliques`) and adding
  only the first $n$ or those above a certain size.

This way, the formulation incorporates additional clique structure without
overwhelming the solver with constraints.

#### SAT Formulation (SAT)

Finally, we can also use a SAT solver to search for an optimal coloring. To test
whether a given set of colors $\mathcal{C}'$ admits a valid coloring, we encode
the problem as a SAT instance, in close analogy to the ASS formulation.

For every vertex $v \in V$ and color $c \in \mathcal{C}'$, we introduce a
Boolean variable $x_{v,c}$ that is true if and only if vertex $v$ is assigned
color $c$. The constraints are then expressed as:

1. **Every vertex receives at least one color:**

$$\bigvee_{c \in \mathcal{C}'} x_{v,c} \quad \forall v \in V$$

2. **No two adjacent vertices share the same color:**

$$\neg x_{v,c} \vee \neg x_{w,c} \quad \forall (v,w) \in E,\; \forall c \in \mathcal{C}'$$

This encoding may allow a vertex to be assigned more than one color if several
are feasible. Since this does not affect the validity of the solution,
additional _at-most-one_ constraints are not necessary and can even slow down
the solver.

To determine the chromatic number, we must probe different sizes of
$\mathcal{C}'$. That is, we iteratively test whether a coloring is feasible with
$k$ colors. Once we find the smallest $k$ for which the SAT instance is
satisfiable, and confirm that $k-1$ colors are not sufficient, we have
identified the optimal number of colors.

### Preprocessing

If we know a lower bound $l$ on the chromatic number, we can apply preprocessing
steps that may drastically reduce the size of the graph. Formally, any valid
coloring requires at least $l$ colors.

Consider a vertex $v$ with degree at most $l-1$. Since $v$ has at most $l-1$
neighbors but $l$ available colors, it is always possible to assign $v$ a color
different from all of its neighbors without increasing the total number of
colors. Thus, $v$ does not influence the chromatic number and can safely be
removed. After solving the reduced graph, we can reinsert $v$ and assign it a
valid color by selecting one not used in its neighborhood.

This reduction can be applied **iteratively**. When a vertex is removed, the
degrees of its neighbors decrease, which may render them removable in the next
round. Repeating this process can considerably shrink the graph. To reconstruct
the original solution, we store removed vertices on a stack and reinsert them in
reverse order, coloring them greedily at the end.

The remaining question is how to obtain the lower bound $l$. A simple and
effective method is to use the size of a clique. Since all vertices in a clique
must receive distinct colors, the maximum clique size provides a valid lower
bound on the chromatic number. In practice, functions such as
`networkx.large_clique_size` allow us to compute such a bound efficiently, which
is sufficient for this exercise.

Finally, note that this preprocessing can even disconnect the graph. In such
cases, each connected component can be solved independently, which is often
faster than solving the entire graph at once.

The structure for such a preprocessor could look as follows:

```python
class DegreeBasedPreprocessor:
    """
    A preprocessor that removes low-degree vertices from the graph.
    This needs to be a class as it maintains state between the preprocessing and postprocessing steps.
    """
    def __init__(self, graph: nx.Graph):
        self.graph = graph  # the original graph

    def preprocess(self) -> nx.Graph:
        """
        Return a preprocessed graph.
        """
        pass

    def postprocess(self, coloring: dict, lower_bound: int) -> tuple[dict, int]:
        """
        Convert a solution for the reduced graph back to the original graph.
        As we are also interested in the lower bound, also pass it through.
        """
        pass
```

### Heuristics

In addition to exact methods, it is often useful to consider heuristic
approaches to graph coloring. While libraries such as `networkx` provide
ready-made heuristics, in many contexts one must implement them manually.

#### Naive Greedy

The most basic approach is the **greedy algorithm**: iterate over the vertices
in some order and assign to each vertex the smallest color not already used by
its neighbors. This procedure always produces a feasible coloring, but not
necessarily a good one.

The quality of the solution depends strongly on the vertex order. Using the
input order often yields poor results, whereas prioritizing high-degree vertices
can already improve performance. If the order is chosen randomly, the number of
colors used may vary considerably across runs. A simple enhancement is the
**multi-start greedy** strategy: run the greedy algorithm multiple times with
different random orders and keep the best solution found.

#### DSATUR

A more advanced strategy is the **DSATUR heuristic**. Instead of fixing a static
order, DSATUR dynamically selects the next vertex to color. At each step, it
chooses the uncolored vertex with the **highest saturation degree**, defined as
the number of distinct colors already present in its neighborhood. If multiple
vertices share the same saturation degree, ties are usually broken by selecting
the vertex of highest degree in the graph. By focusing on the most constrained
vertices first, DSATUR often yields substantially better colorings than the
naive greedy approach.

## Benchmarking

This section is adapted from the chapter
[Benchmarking your Model](https://d-krupke.github.io/cpsat-primer/08_benchmarking.html)
of the CP-SAT Primer. You are encouraged to read the full chapter for the
complete discussion, but for self-containedness the most relevant parts are
summarized here in slightly adapted form.

### No-Free-Lunch Theorem and Timeouts

The **no‐free‐lunch theorem** and timeouts complicate benchmarking more than you
might have anticipated. The no‐free‐lunch theorem asserts that no single
algorithm outperforms all others across every instance, which is especially true
for NP‐hard problems. Consequently, improving performance on some instances
often coincides with degradations on others. It is essential to assess whether
the gains justify the losses.

Another challenge arises when imposing a time limit to prevent individual
instances from running indefinitely. Without such a limit, benchmark runs can
become prohibitively long. However, including aborted runs in the dataset
complicates performance evaluation, as it remains unclear whether a solver would
have found a solution shortly after the timeout or was trapped in an infinite
loop. Discarding all instances that timed out on a particular model restricts
the evaluation to simpler instances, even though the more complex ones are often
of greater interest. Conversely, discarding all models that timed out on any
instance may leave no viable candidates, as any solver is likely to fail on at
least one instance in a sufficiently large benchmark set. Whether the goal is to
find a provably optimal solution, the best solution within a fixed time limit,
or simply any feasible solution, it is essential to enable comparisons over data
sets that include unknown outcomes.

### Performance Plots for Solution Quality within a Time Limit

When dealing with instances that frequently cannot be solved to optimality,
**performance plots** can be an excellent choice to find out which model came
closest to the optimal solution. These plots illustrate the relative performance
of different models or solvers on a set of instances, usually under a fixed time
limit. At the leftmost point of the plot (where $x = 1$), each solver’s line
indicates the proportion of instances for which it achieved the best-known
solution (not necessarily exclusively). Then its $(x,y)$ coordinates indicate
the proportion $y$ of instances for which the solver achieved a solution that is
at most $x$ times worse than the best known solution. For example, if a solver
has a point at $(1.05, 0.8)$, it means that it found a solution within 5% of the
best-known solution for 80% of the instances. Often, a logarithmic scale is used
for the x-axis, especially when the performance ratios vary widely. However,
down below we use a linear scale because the values are close to 1.

In the example below, based on the **Capacitated Vehicle Routing Problem
(CVRP)**, the performance plots compare three different models across a
benchmark set. These plots offer a clear visual summary of how closely each
model approaches the best solution.

|                                                                                                                                 ![Performance Plot Objective](https://github.com/d-krupke/cpsat-primer/blob/main/images/performance_plot_objective.png?raw=true)                                                                                                                                  |
| :-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
| Performance plot comparing the objective values of different CVRP models on a benchmark set. The Miller–Tucker–Zemlin model performs best on most instances and remains close to the best on the rest. The other two models find the best solution in only about 10% of instances but solve roughly 70% within 2% of the best known solution, with `multiple_circuit` showing a slight advantage. |

This can of course also be done for the lower bounds produced by each model.

|                                                                               ![Performance Plot Lower Bound](https://github.com/d-krupke/cpsat-primer/blob/main/images/performance_plot_bound.png?raw=true)                                                                               |
| :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: |
| Performance plot comparing the lower bounds produced by each CVRP model. The `add_circuit` model consistently achieves the best bounds, while the other two models yield bounds that are up to 20% worse in the best case and up to 100% worse (i.e., half the quality) on some instances. |

<details>
<summary>Here is the code I used to generate the plots. You can freely copy and use it.</summary>

```python
# MIT License
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes


def plot_performance_profile(
    data: pd.DataFrame,
    instance_column: str,
    strategy_column: str,
    metric_column: str,
    direction: str,
    comparison: str = "relative",
    title: str | None = None,
    highlight_best: bool = False,
    ax: Axes | None = None,
    scale: str | None = None,
    log_base: int = 2,
    figsize: tuple = (9, 6),
) -> Axes:
    """
    Plot a performance profile, either on a relative-ratio basis or absolute-difference basis:
      - For comparison="relative":
          x-axis: performance ratio τ (log scale if τ_max > 10)
          τ = (value / best) if direction="min", or τ = (best / value) if direction="max".
      - For comparison="absolute":
          x-axis: absolute difference Δ = (value - best) if direction="min",
                                      or Δ = (best - value) if direction="max".
      - y-axis: proportion of problems with τ (or Δ) ≤ x for each solver.
      - If highlight_best=True, detect and bold the dominating solver curve (AUC in appropriate space).
      - Ensures a reasonable number of ticks on the x-axis.

    Args:
        data: DataFrame with columns [instance, strategy, metric].
        instance_column: column name identifying each problem instance.
        strategy_column: column name identifying each solver/strategy.
        metric_column: column name of the performance metric (e.g. runtime or cost).
        direction: "min" if lower metric → better, "max" if higher → better.
        comparison: "relative" or "absolute".
        title: Optional plot title.
        highlight_best: If True, find the solver with largest AUC and draw it in bold.
        ax: An existing matplotlib Axes to draw into. If None, a new Figure+Axes will be created using figsize.
        scale: x-axis scale override ("linear" or "log"); if None, chosen automatically.
        log_base: base for log scale if used (default 2).
        figsize: Tuple (width, height). Only used if ax is None.

    Returns:
        The matplotlib Axes containing the performance profile.
    """
    if direction not in ("min", "max"):
        raise ValueError("`direction` must be 'min' or 'max'.")
    if comparison not in ("relative", "absolute"):
        raise ValueError("`comparison` must be 'relative' or 'absolute'.")

    # 1) Compute best value per instance
    best_val = data.groupby(instance_column)[metric_column].agg(direction)

    # 2) Pivot to get per-instance × per-strategy medians
    pivot = (
        data.groupby([instance_column, strategy_column])[metric_column]
        .median()
        .unstack(fill_value=np.nan)
    )

    # 3) Build comparison matrix C[p, s]
    comp = pd.DataFrame(index=pivot.index, columns=pivot.columns, dtype=float)

    if comparison == "relative":
        for strat in pivot.columns:
            if direction == "min":
                comp[strat] = pivot[strat] / best_val
            else:  # direction == "max"
                comp[strat] = best_val / pivot[strat]
        comp = comp.replace([np.inf, -np.inf, 0.0], np.nan)

    else:  # comparison == "absolute"
        for strat in pivot.columns:
            if direction == "min":
                comp[strat] = pivot[strat] - best_val
            else:  # direction == "max"
                comp[strat] = best_val - pivot[strat]
        comp = comp.replace([np.inf, -np.inf], np.nan)

    # 4) Collect all distinct x-values (τ or Δ), including baseline
    all_vals = comp.values.flatten()
    finite_vals = all_vals[np.isfinite(all_vals)]
    baseline = 1.0 if comparison == "relative" else 0.0
    all_x = np.unique(np.sort(finite_vals))
    all_x = np.concatenate(([baseline], all_x))
    all_x = np.unique(np.sort(all_x))

    # 5) Build performance-profile DataFrame ρ(x)
    n_instances = comp.shape[0]
    profile = pd.DataFrame(index=all_x, columns=comp.columns, dtype=float)

    for x in all_x:
        leq = (comp <= x).sum(axis=0)
        profile.loc[x] = leq / n_instances

    # 6) Identify dominating solver if requested (max AUC)
    best_solver = None
    if highlight_best:
        if comparison == "relative":
            # integrate ρ(τ) w.r.t. log(τ)
            log_x = np.log(all_x)
            areas = {}
            for strat in profile.columns:
                y = profile[strat].astype(float).values
                areas[strat] = np.trapz(y, x=log_x)
            best_solver = max(areas, key=areas.get)
        else:
            # integrate ρ(Δ) w.r.t. Δ
            areas = {}
            for strat in profile.columns:
                y = profile[strat].astype(float).values
                areas[strat] = np.trapz(y, x=all_x)
            best_solver = max(areas, key=areas.get)

    # 7) Create or use existing Axes
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.figure

    # 8) Determine scale if not overridden
    if scale is None:
        if comparison == "relative" and all_x[-1] > 10:
            use_log = True
        else:
            use_log = False
    else:
        use_log = scale == "log"

    # 9) Plot each solver’s curve
    for strat in profile.columns:
        y = profile[strat].astype(float)
        if highlight_best and strat == best_solver:
            ax.step(all_x, y, where="post", label=strat, linewidth=3.0, alpha=1.0)
        else:
            ax.step(
                all_x,
                y,
                where="post",
                label=strat,
                linewidth=1.5,
                alpha=0.6 if highlight_best else 1.0,
            )

    # 10) Axis scaling and limits
    if comparison == "relative":
        if use_log:
            ax.set_xscale("log", base=log_base)
            ax.set_xlim(all_x[1], all_x[-1] * 1.1)
        else:
            ax.set_xscale("linear")
            ax.set_xlim(1.0, all_x[-1] * 1.1)
        xlabel = (
            f"Within this factor of the best (log{log_base} scale)"
            if use_log
            else "Within this factor of the best (linear scale)"
        )
    else:  # absolute
        ax.set_xscale("linear")
        ax.set_xlim(0.0, all_x[-1] * 1.1)
        xlabel = "Absolute difference from the best"

    ax.set_ylim(0.0, 1.02)
    ax.set_xlabel(xlabel, fontsize=12)
    ax.set_ylabel("Proportion of problems", fontsize=12)

    if title:
        ax.set_title(title, fontsize=14, pad=14)
    else:
        ax.set_title("Performance Profile", fontsize=14, pad=14)

    ax.axvline(x=baseline, color="gray", linestyle="--", alpha=0.7)
    ax.grid(True, which="both", linestyle=":", linewidth=0.5)

    # 11) Legend inside lower right
    ax.legend(loc="lower right", frameon=False)

    fig.tight_layout()
    return ax
```

</details>

> [!TIP]
>
> Tangi Migot has written an excellent article on
> [Performance Plots](https://tmigot.github.io/posts/2024/06/teaching/). Also
> take a look on the original paper
> [Benchmarking optimization software with performance profiles (Dolan & Moré 2002)](https://link.springer.com/article/10.1007/s101070100263)

### Instance Generators

Networkx provides a lot of different instance generators which you can use for
benchmarking. You can find a full list
[here](https://networkx.org/documentation/stable/reference/generators.html).
Generators you should definitely try out:

- `erdos_renyi_graph`
- `kneser_graph`
- `barabasi_albert_graph`

## Tasks

1. Explain how completing a Sudoku can be expressed as a graph coloring problem.
   In particular, describe how to convert a partially filled Sudoku grid into a
   graph such that an optimal coloring corresponds to a valid solution (if one
   exists), independent of the specific model used to solve it. A detailed
   implementation is not required; only a clear explanation of the idea.
2. Read the chapter
   [Benchmarking your Model](https://d-krupke.github.io/cpsat-primer/08_benchmarking.html)
   from the CP-SAT Primer. Ensure that you understand the challenges of
   benchmarking and are able to answer questions about them.
3. Implement the three heuristics discussed in this chapter and compare their
   solution quality. Investigate whether you can identify a class of graphs
   where DSATUR clearly outperforms the other methods. Present your findings
   using a **performance profile on the objective**.
4. Implement the different models for graph coloring. The ILP models should be
   implemented both for Gurobi and for CP-SAT (recall that CP-SAT can also solve
   ILPs).
5. Compute a performance profile for the different models with a 60-second time
   limit. Identify which models are strongest in terms of finding good solutions
   and which are most effective at proving lower bounds.
6. Implement the preprocessing technique and evaluate its impact on the
   performance of the models.
7. Carefully check the consistency and correctness of your results. Ensure that
   no obviously incorrect results appear, as such outcomes would suggest that
   you did not validate the raw data and simply trusted your code.
8. Reevaluate your instance set and see if you can find instance generators
   where the performances significantly differ.

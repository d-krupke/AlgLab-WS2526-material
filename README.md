# Algorithms Lab - Winter 2025/2026

_Instructor: [Dr. Dominik Krupke](https://www.ibr.cs.tu-bs.de/users/krupke/)
IBR, Algorithms Group_

Optimization problems are pervasive across numerous real-world applications
within computer science, ranging from
[route planning](https://en.wikipedia.org/wiki/Travelling_salesman_problem) to
[job scheduling](https://en.wikipedia.org/wiki/Job-shop_scheduling). Certain
problems, like the
[shortest path](https://en.wikipedia.org/wiki/Shortest_path_problem), can be
solved efficiently in theory and practice. However, a significant number of
these optimization problems are classified as
[NP-hard](https://en.wikipedia.org/wiki/NP-hardness), indicating that, for these
problems, there is no known algorithm capable of consistently solving every
instance efficiently to proven optimality. In such instances, heuristic
approaches, such as
[genetic algorithms](https://en.wikipedia.org/wiki/Genetic_algorithm), are
frequently employed as practical solutions. Yet, the question arises: Is it
possible to devise algorithms that yield optimal solutions within a feasible
timeframe for reasonably sized instances? This laboratory course is dedicated to
exploring three sophisticated techniques that hold the potential for computing
optimal solutions for a vast array of problems within practical limits. These
techniques include:

- **Constraint Programming** with
  [CP-SAT](https://developers.google.com/optimization/cp/cp_solver): This
  versatile methodology enables the definition of a problem’s constraints, upon
  which it employs a comprehensive suite of strategies, including the two
  techniques discussed below, to find optimal solutions.
- **SAT Solvers**: Renowned for their ability to resolve extensive logical
  formulas, these tools can be ingeniously adapted to address optimization
  challenges by transforming them into logical propositions.
- **Mixed Integer Programming (MIP)**: This approach is adept at solving
  optimization problems characterized by integer and continuous variables under
  linear constraints.

For algorithm engineers and operations researchers, mastering these techniques
opens the door to modeling and solving a wide spectrum of combinatorial
optimization problems. By the end of this course, you will have acquired the
skills to leverage these powerful methodologies, enabling you to approach
NP-hard problems not only with theoretical insight but with practical,
actionable solutions. This journey is not just about crafting elegant models but
also about utilizing robust solution engines to navigate the complexities of
NP-hard challenges effectively.

## Content

This class consists of a series of exercise sheets. These exercises are
carefully crafted to either introduce you to new techniques or enhance your
existing knowledge of them. Designed with a hands-on approach, these tasks aim
to provide you with practical exposure to relevant tools and methodologies.

Each exercise sheet is allocated a two-week completion window. However, with new
sheets released on a weekly basis, you effectively have one week to work on each
exercise, with an additional week serving as a buffer. While the exercises are
designed to be completed within a few hours, the learning curve associated with
mastering new techniques may necessitate additional time. The time required to
complete each sheet may vary; for example, you might spend more time on the
initial sheet and less on subsequent ones, or vice versa, depending on your
familiarity with the topics covered.

> [!NOTE]
>
> The schedule is subject to change. The dates are tentative and may be adjusted
> based on the progress of the course. If you struggle with a sheet, please
> reach out to us. We are happy to help you and can adjust the schedule if
> necessary.

|                      Sheet                      |          Time           |                                                                                                                                                       Content                                                                                                                                                       |     |
| :---------------------------------------------: | :---------------------: | :-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------: | --- |
|     [Exercise Sheet 1A](./sheets/01_cpsat/)     | 2025-10-22 - 2025-11-05 |                                                                                              Constraint Programming with CP-SAT - A Hello-World with CP-SAT, NetworkX, and Scalene. All nice and easy to get started.                                                                                               |     |
|     [Exercise Sheet 1B](./sheets/01_cpsat/)     | 2025-10-29 - 2025-11-12 |                                           Constraint Programming with CP-SAT - Here you will explore the use of CP-SAT, a declarative constraint programming solver. You will learn to define your problem mathematically, allowing CP-SAT to efficiently find solutions.                                           |     |
|       [Exercise Sheet 2](./sheets/02_bnb)       | 2025-11-05 - 2025-11-19 |                                DIY: Branch and Bound - This exercise delves into the foundational algorithm behind generic solvers like CP-SAT. Participants will gain insights into what these solvers require for optimal performance by exploring the Branch and Bound algorithm.                                |     |
|      [Exercise Sheet 3](./sheets/03_sat/)       | 2025-11-12 - 2025-12-26 |                                            SAT Solver - After the high-level interface provided by CP-SAT, this exercise demands a closer interaction with the core mechanics of a SAT solver. You will learn to translate complex problems into basic logical formulas.                                            |     |
|      [Exercise Sheet 4](./sheets/04_mip/)       | 2025-11-19 - 2025-12-03 |       Mixed Integer Programming - Learn about Mixed Integer Programming (MIP), a technique favored by many optimization experts. Although not as expressive as CP-SAT, MIP offers better scalability and the opportunity to apply various optimization tricks thanks to an extensive mathematical foundation.       |     |
| [Exercise Sheet 5](./sheets/05_graph_coloring/) | 2025-11-26 - 2025-12-10 | Benchmarking the Performance of Different Solvers and Formulations for the Graph Coloring Problem - This exercise focuses on comparing various formulations and solvers for the graph coloring problem, a common subproblem in many applications. It will help you understand how to benchmark solvers effectively. |     |

> [!WARNING]
>
> These exercises are not traditional homework; they are the core of this course
> and should be approached accordingly. Each exercise sheet will require a full
> day of focused work, as they introduce new concepts and techniques you may not
> have encountered before. You will need to carefully study both the course
> material and the provided references to fully understand these concepts. Given
> the complexity, I expect you to ask more questions and seek assistance
> frequently. Please do take the time to really engage with the material and do
> not just iterate with ChatGPT until the tests pass. First, we will notice in
> the code interviews if you really understood what you just did and second, you
> will not learn anything this way. Use ChatGPT as a personalized tutor to
> deepen your understanding but do not let it do the work for you.

## Prerequisites

For a successful experience in this course and to effectively work on the
projects, students are expected to meet the following prerequisites:

1. **Proficiency in Python**: The course's programming components will be
   exclusively conducted in Python. It is essential that you have a solid grasp
   of Python, as there will not be sufficient time to learn the language during
   the course.
2. **Algorithmic Foundations**:
   - Completion of _Algorithms and Data Structures 1_ is compulsory for
     foundational knowledge.
   - It is advisable to have also completed (or complete in parallel)
     _Algorithms and Data Structures 2_ and _Network Algorithms_ to be better
     prepared for the more complex topics.
   - Additionally, it is beneficial to have attended _Logic for Computer
     Scientist_ and _Theoretical Computer Science I+II_ to be familiar with
     NP-hardness and propositional logic.
3. **Unix-Based Operating System**:
   - Access to a Unix system, which could be in the form of a virtual machine,
     is required for the course. Students should possess a fundamental
     understanding of Unix command-line operations.
   - While most of the tools and software used in this course are compatible
     with Windows, support for Windows-specific issues cannot be guaranteed.
4. **Version Control with Git**:
   - A basic familiarity with Git is needed for version control purposes. While
     Git skills can be acquired swiftly, students are expected to learn them
     independently prior to or during the initial phase of the course.

Please ensure you meet these requirements to engage fully in the course
activities. If you have any questions or need clarification on the
prerequisites, feel free to reach out to us.

## Lectures to go next

This class is just a quick peek into solving NP-hard problems in practice, there
is more!

- _Algorithm Engineering (Master, infrequently)_ will teach you a superset of
  this class, with more details.
- _Mathematische Methoden der Algorithmik (Master)_ will teach you the
  theoretical background of Linear Programming and Mixed Integer Programming.
- _Approximation Algorithms (Master)_ will teach you theoretical aspects of how
  to approximate NP-hard problems with guarantees. While this takes a
  theoretical point of view, the theoretical understanding can improve your
  practical skills on understanding and solving such problems.

## References

## References

- [In Pursuit of the Traveling Salesman](https://press.princeton.edu/books/paperback/9780691163529/in-pursuit-of-the-traveling-salesman):
  This excellent book is not only a surprisingly enjoyable read but also a
  remarkable introduction to the field of optimization. It presents many of the
  ideas that enable us to solve NP-hard problems in practice, while gently
  introducing the reader to the mindset of an optimization expert.
- [Hands-On Mathematical Optimization with Python](https://www.cambridge.org/us/universitypress/subjects/mathematics/optimization-or-and-risk-analysis/hands-mathematical-optimization-python?format=AR#):
  A great introduction to mathematical optimization. Its focus differs from that
  of this class, but it serves as a valuable complementary resource for
  deepening your understanding of the topic.
- [Primal Heuristics in Integer Programming](https://www.cambridge.org/core/books/primal-heuristics-in-integer-programming/FF179F5A69E7794BF0B737BEE0F92159):
  This book provides an excellent overview of the generic techniques used to
  find good primal solutions in mixed-integer programming (and also in
  constraint programming). Since we are mainly interested in primal solutions in
  this class—and do not focus much on duality—this book is a natural next step.
  It should not be your first book, but you can start exploring it fairly early
  to gain a deeper understanding of the tricks solvers use to identify good
  solutions.
- [The Series by Adam DeJans Jr.](https://www.bitbrosdata.com/resources/optimization-books):
  A very concise set of books that can be read over a weekend. They stick to the
  essentials without spending many words on unnecessary details. While these
  books are not sufficient on their own to master optimization, their clarity
  and brevity make them highly enjoyable. If I were starting again from scratch,
  I would read these books in parallel with
  [Hands-On Mathematical Optimization with Python](https://www.cambridge.org/us/universitypress/subjects/mathematics/optimization-or-and-risk-analysis/hands-mathematical-optimization-python?format=AR#)
  (and, of course, the
  [CP-SAT Primer](https://d-krupke.github.io/cpsat-primer/)!).
- [Integrated Methods for Optimization](https://link.springer.com/book/10.1007/978-1-4614-1900-6):
  I really appreciate this book, though it can be somewhat intimidating for
  beginners due to its breadth and depth. Read it once you have realized that
  many of the seemingly complicated concepts are, in fact, quite natural.

## Found an error?

Please let us know by opening an issue! You can also create a pull request on a
separate branch, but as we have to do the changes in our internal repository
(which also contains solutions), from which the public repository is
automatically updated, it is easier for us if you open an issue and let us do
the changes.

## Are you an instructor?

If you are an instructor and want to use this material in your course, feel free
to do so! We are happy to share our material with you. If you have any
questions, feel free to reach out to us. To get the solutions, please contact us
directly from your official university email address, so we can verify that you
are an instructor and not a student.

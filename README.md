# Optimization Techniques — Python Implementations

<p align="center">
  <strong>Big-M Simplex Method & Transportation Problem (VAM + MODI)</strong><br>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3">
  <img src="https://img.shields.io/badge/Optimization-Techniques-6C5CE7?style=for-the-badge" alt="Optimization Techniques">
  <img src="https://img.shields.io/badge/Algorithms-Simplex%20%7C%20VAM%20%7C%20MODI-00A86B?style=for-the-badge" alt="Algorithms">
</p>

## 📌 Overview

This repository contains two standalone Python programs implementing classical Operations Research / Optimization Techniques algorithms:

1. **Big-M Simplex Method** for solving Linear Programming Problems (LPPs).
2. **Transportation Problem Solver** using **Vogel's Approximation Method (VAM)** to obtain an initial feasible solution and **Modified Distribution Method (MODI)** to optimize it.

Both programs are **interactive**: the problem data is entered at runtime, so the solvers are designed to work with different problem sizes rather than relying on one hard-coded example.

The repository also contains the corresponding assignment report with the theory, source-code documentation, sample runs, and observed results.

---

## 📂 Repository Structure

```text
.
├── OT_ASSIGNMENT1.py
├── OT_ASSIGNMENT2.py
├── OT_Assignment_Report.pdf
└── README.md
```

### File Description

| File | Description |
|---|---|
| `OT_ASSIGNMENT1.py` | Big-M Simplex solver for maximization/minimization LPPs |
| `OT_ASSIGNMENT2.py` | Transportation Problem solver using VAM + MODI |
| `OT_Assignment_Report.pdf` | Detailed assignment report containing objectives, theory, program design, sample runs, and results |
| `README.md` | Project documentation and usage guide |

---

# 1. Big-M Simplex Method

## 🎯 Objective

`OT_ASSIGNMENT1.py` implements the **Big-M Simplex Method** for Linear Programming Problems with:

- Maximization and minimization objectives
- Any number of decision variables
- Multiple constraints
- `<=`, `>=`, and `=` constraint types
- Non-negative decision variables

The implementation uses **symbolic Big-M arithmetic** instead of choosing an arbitrary numerical value for `M`.

### Core idea

Artificial variables introduced for `>=` and `=` constraints are penalized using `M`. The implementation represents values involving `M` as:

```text
(constant, coefficient_of_M)
```

This allows the program to compare expressions symbolically by considering the coefficient of `M` first and the constant part second.

---

## ⚙️ Main Components

### `get_problem_from_user()`

Collects:

- Number of decision variables
- Number of constraints
- Optimization direction
- Objective-function coefficients
- Constraint coefficients
- Constraint relations
- RHS values

### `build_standard_form()`

Converts the original LPP into a simplex-ready representation.

It:

- Handles negative RHS values by multiplying the constraint by `-1`
- Converts minimization into an internally handled maximization form
- Adds slack variables for `<=`
- Adds surplus and artificial variables for `>=`
- Adds artificial variables for `=`

### `solve_big_m()`

Performs the simplex iterations:

1. Builds and displays the current tableau
2. Computes the Dev.Row / net-evaluation row
3. Selects the entering variable
4. Applies the minimum-ratio test
5. Selects the leaving variable
6. Performs the pivot operation
7. Repeats until optimality, unboundedness, or the iteration safety limit is reached

### `report_solution()`

Checks for a remaining positive artificial variable and reports:

- Decision-variable values
- Optimal objective value
- Infeasibility when an artificial variable remains positive

---

## 🧮 Big-M Workflow

```text
                 Original LPP
                      │
                      ▼
              Read problem input
                      │
                      ▼
             Convert to standard form
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       Slack       Surplus     Artificial
      (<=)          (>=)        (>=, =)
          └───────────┼───────────┘
                      ▼
             Build simplex tableau
                      │
                      ▼
               Big-M iterations
                      │
          ┌───────────┼───────────┐
          │           │           │
          ▼           ▼           ▼
       Optimal     Unbounded   Infeasible
          │
          ▼
       Final LPP solution
```

---

## 📝 Example

The report tests the program using:

```text
Minimize
    Z = 4x1 + x2

Subject to
    3x1 + x2 = 3
    4x1 + 3x2 >= 6
    x1 + 2x2 <= 4
    x1, x2 >= 0
```

### Reported result

```text
x1 = 0.4
x2 = 1.8
Minimum Z = 3.4
```

The sample run converges in four tableaus, with the artificial variables leaving the basis and no positive Dev.Row entry remaining at the final tableau.

---

# 2. Transportation Problem — VAM + MODI

## 🎯 Objective

`OT_ASSIGNMENT2.py` solves a general **Transportation Problem** in two stages:

### Phase 1 — Vogel's Approximation Method (VAM)

VAM constructs an initial basic feasible solution by calculating row and column penalties and assigning as much as possible to the cheapest cell of the row/column with the largest penalty.

### Phase 2 — Modified Distribution Method (MODI)

MODI checks whether the initial solution is optimal and, when necessary, improves it using:

- Dual variables `uᵢ` and `vⱼ`
- Opportunity / net-evaluation values `Δᵢⱼ`
- Closed-loop adjustments
- Iterative reallocation

---

## ⚙️ Main Components

### `get_problem_size_and_cost()`

Reads:

- Number of sources
- Number of destinations
- Supply values
- Demand values
- Transportation-cost matrix

If total supply and total demand are unequal, the program automatically adds a **dummy source or destination with zero transportation cost** to balance the problem.

### `vogel_approximation()`

Calculates row and column penalties and repeatedly:

1. Finds the largest penalty
2. Selects the cheapest cell in that row/column
3. Allocates the maximum feasible quantity
4. Updates supply and demand
5. Continues until the initial plan is complete

### `fix_degeneracy()`

Checks whether the number of basic cells is sufficient for MODI:

```text
m + n - 1
```

When necessary, it adds a very small near-zero allocation to a suitable empty cell without creating a closed loop.

### `find_uv()`

Calculates MODI dual values:

```text
uᵢ + vⱼ = cᵢⱼ
```

for every basic cell.

### `modi_optimize()`

For every iteration:

1. Computes `u` and `v`
2. Calculates `Δᵢⱼ`
3. Checks optimality
4. Selects the most negative `Δᵢⱼ` when improvement is possible
5. Builds a closed loop
6. Applies alternating `+ / -` adjustments
7. Repeats until all relevant `Δᵢⱼ >= 0`

---

## 🚚 Transportation Workflow

```text
              Transportation Data
                      │
                      ▼
          Balance supply and demand
                      │
                      ▼
        Vogel's Approximation Method
                      │
                      ▼
           Initial feasible solution
                      │
                      ▼
              Compute uᵢ and vⱼ
                      │
                      ▼
             Compute Δᵢⱼ values
                      │
             ┌────────┴────────┐
             │                 │
     All Δᵢⱼ >= 0       Some Δᵢⱼ < 0
             │                 │
             ▼                 ▼
          Optimal        Find entering cell
                               │
                               ▼
                         Closed-loop shift
                               │
                               └──────► Repeat
```

---

## 📝 Example

The report tests the transportation solver on the following balanced problem:

| Source | D1 | D2 | D3 | D4 | Supply |
|---|---:|---:|---:|---:|---:|
| S1 | 3 | 1 | 7 | 4 | 300 |
| S2 | 2 | 6 | 5 | 9 | 400 |
| S3 | 8 | 3 | 3 | 2 | 500 |
| **Demand** | **250** | **350** | **400** | **200** | **1200** |

### Reported optimal allocation

```text
S1 → D2 = 300
S2 → D1 = 250
S2 → D3 = 150
S3 → D2 = 50
S3 → D3 = 250
S3 → D4 = 200
```

### Minimum transportation cost

```text
2850
```

For this test case, the VAM solution is already optimal: the MODI evaluation values for the empty cells are strictly positive in the first MODI iteration.

---

# 🛠️ Requirements

## Software

- Python **3.x**
- NumPy

`OT_ASSIGNMENT1.py` uses NumPy for matrix operations.  
`OT_ASSIGNMENT2.py` uses Python's standard library and does not require an external numerical package.

---

# 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/<YOUR-USERNAME>/<YOUR-REPOSITORY>.git
cd <YOUR-REPOSITORY>
```

Optional: create and activate a virtual environment:

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install the dependency:

```bash
pip install numpy
```

---

# ▶️ Running the Programs

## Assignment 1 — Big-M Simplex

```bash
python OT_ASSIGNMENT1.py
```

The program will interactively ask for:

```text
Number of decision variables
Number of constraints
Minimize / Maximize
Objective coefficients
Constraint coefficients
Constraint relation
RHS value
```

Example objective input:

```text
4 1
```

for:

```text
Z = 4x1 + x2
```

Example constraint relation:

```text
<=
>=
=
```

---

## Assignment 2 — Transportation Problem

```bash
python OT_ASSIGNMENT2.py
```

The program asks for:

```text
Number of sources
Number of destinations
Supply values
Demand values
Cost matrix
```

It then prints:

1. VAM allocation rounds
2. Initial feasible allocation
3. Initial transportation cost
4. MODI iterations
5. `u` and `v` values
6. `Δᵢⱼ` values
7. Final optimal allocation
8. Minimum transportation cost

---

# 📖 Documentation

For complete theory, program design, source-code snapshots, sample runs, and results, see:

```text
OT_Assignment_Report.pdf
```

The report documents both assignments and includes the sample problems and results summarized above.

---

<p align="center">
  <i>Implemented in Python • Big-M Simplex • Vogel's Approximation Method • MODI</i>
</p># optimization-techniques-python

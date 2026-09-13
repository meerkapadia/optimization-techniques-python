import numpy as np

TOL = 1e-9

def madd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def msub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def mscale(a, k):
    return (a[0] * k, a[1] * k)


def m_is_positive(a):
    if abs(a[1]) > TOL:
        return a[1] > 0
    return a[0] > TOL


def format_m(a):
    const, coeff = a
    const = round(const, 4)
    coeff = round(coeff, 4)

    if abs(coeff) < TOL:
        return f"{const:g}"

    coeff_str = "" if abs(coeff - 1) < TOL else ("-" if abs(coeff + 1) < TOL else f"{coeff:g}")
    m_part = f"{coeff_str}M" if coeff_str != "-" else "-M"

    if abs(const) < TOL:
        return m_part

    if const > 0:
        return f"{m_part}+{const:g}" if not m_part.startswith("-") else f"{const:g}{m_part}"
    else:
        return f"{m_part}{const:g}" if not m_part.startswith("-") else f"{const:g}{m_part}"


def get_problem_from_user():
    print("=== Big-M Simplex Solver (symbolic M) ===\n")
    n = int(input("How many decision variables (x1, x2, ...)? "))
    m = int(input("How many constraints? "))
    sense = input("Minimize or Maximize? (type min/max): ").strip().lower()

    print(f"\nEnter the {n} objective function coefficients, space separated")
    print("(example: for  Z = 4x1 + x2  just type: 4 1)")
    obj = list(map(float, input("Objective coefficients: ").split()))

    constraints = []
    print("\nNow enter each constraint one by one.")
    print("(Don't type the plain x_i >= 0 lines - those are assumed automatically.)")
    for i in range(m):
        print(f"\n-- Constraint {i + 1} --")
        coeffs = list(map(float, input(f"Coefficients of x1..x{n}: ").split()))
        relation = input("Relation (type <=, >=, or =): ").strip()
        rhs = float(input("RHS value: "))
        constraints.append((coeffs, relation, rhs))

    return n, m, sense, obj, constraints


def build_standard_form(n, m, sense, obj, constraints):

    col_names = [f"x{i+1}" for i in range(n)]
    rows = [list(c[0]) for c in constraints]
    rhs = [c[2] for c in constraints]
    relations = [c[1] for c in constraints]

    for i in range(m):
        if rhs[i] < 0:
            rows[i] = [-v for v in rows[i]]
            rhs[i] = -rhs[i]
            if relations[i] == "<=":
                relations[i] = ">="
            elif relations[i] == ">=":
                relations[i] = "<="

    if sense.startswith("min"):
        internal_obj = [-c for c in obj]
    else:
        internal_obj = list(obj)

    cost = [(c, 0.0) for c in internal_obj]
    basis = [None] * m

    for i in range(m):
        if relations[i] == "<=":
            col_names.append(f"s{i+1}")
            col = [0.0] * m
            col[i] = 1.0
            cost.append((0.0, 0.0))
            for r in range(m):
                rows[r].append(col[r])
            basis[i] = len(col_names) - 1

        elif relations[i] == ">=":
            col_names.append(f"s{i+1}")
            col = [0.0] * m
            col[i] = -1.0
            cost.append((0.0, 0.0))
            for r in range(m):
                rows[r].append(col[r])

            col_names.append(f"a{i+1}")
            col2 = [0.0] * m
            col2[i] = 1.0
            cost.append((0.0, -1.0))
            for r in range(m):
                rows[r].append(col2[r])
            basis[i] = len(col_names) - 1

        elif relations[i] == "=":
            col_names.append(f"a{i+1}")
            col = [0.0] * m
            col[i] = 1.0
            cost.append((0.0, -1.0))
            for r in range(m):
                rows[r].append(col[r])
            basis[i] = len(col_names) - 1

        else:
            raise ValueError(f"Relation '{relations[i]}' not recognized, use <=, >= or =")

    A = np.array(rows, dtype=float)
    b = np.array(rhs, dtype=float)

    return A, b, cost, basis, col_names, sense


COL_W = 11
LABEL_W = 8


def _border(num_cols):
    return "+" + "-" * (LABEL_W + 2) + ("+" + "-" * (COL_W + 2)) * num_cols + "+"


def _row(label, values):
    cells = "".join(f" {v.center(COL_W)} |" for v in values)
    return "|" + f" {label.center(LABEL_W)} |" + cells


def print_table(A, b, cost, basis, col_names, iteration):
    print(f"\n--- Table {iteration} ---")
    num_cols = len(col_names) + 1  # +1 for the RHS column

    border = _border(num_cols)
    print(border)
    print(_row("Basis", col_names + ["RHS"]))
    print(border)

    for i, var in enumerate(basis):
        values = [f"{A[i, j]:.3f}" for j in range(len(col_names))] + [f"{b[i]:.3f}"]
        print(_row(col_names[var], values))

    print(border)

    cb = [cost[v] for v in basis]

    dev_row = []
    for j in range(len(col_names)):
        zj = (0.0, 0.0)
        for i in range(len(basis)):
            zj = madd(zj, mscale(cb[i], A[i, j]))
        dev_row.append(msub(cost[j], zj))

    z_val = (0.0, 0.0)
    for i in range(len(basis)):
        z_val = madd(z_val, mscale(cb[i], b[i]))

    dev_values = [format_m(d) for d in dev_row] + [f"z={format_m(z_val)}"]
    print(_row("Dev.Row", dev_values))
    print(border)

    return dev_row


def solve_big_m(A, b, cost, basis, col_names):
    iteration = 0
    while True:
        iteration += 1
        dev_row = print_table(A, b, cost, basis, col_names, iteration)

        if not any(m_is_positive(d) for d in dev_row):
            print("\nNo positive entries left in the Dev.Row -> optimal solution reached.")
            break

        # entering column = the one with the largest Dev.Row value
        entering = max(range(len(dev_row)), key=lambda j: (dev_row[j][1], dev_row[j][0]))

        ratios = []
        for i in range(len(b)):
            if A[i, entering] > TOL:
                ratios.append(b[i] / A[i, entering])
            else:
                ratios.append(np.inf)

        if all(r == np.inf for r in ratios):
            print("\nAll entries in the pivot column are <= 0 -> problem is UNBOUNDED.")
            return None, None, basis

        leaving_row = int(np.argmin(ratios))
        print(f"Entering variable: {col_names[entering]}   Leaving variable: {col_names[basis[leaving_row]]}")

        pivot_val = A[leaving_row, entering]
        A[leaving_row, :] /= pivot_val
        b[leaving_row] /= pivot_val
        for i in range(len(b)):
            if i != leaving_row and abs(A[i, entering]) > 1e-12:
                factor = A[i, entering]
                A[i, :] -= factor * A[leaving_row, :]
                b[i] -= factor * b[leaving_row]

        basis[leaving_row] = entering

        if iteration > 50:
            print("Stopped after 50 iterations (something is probably cycling).")
            break

    return A, b, basis


def report_solution(n, sense, obj, col_names, basis, b):
    for i, var in enumerate(basis):
        if col_names[var].startswith("a") and b[i] > 1e-6:
            print("\nThe original problem is INFEASIBLE "
                  "(an artificial variable could not be driven to zero).")
            return

    values = {name: 0.0 for name in col_names}
    for i, var in enumerate(basis):
        values[col_names[var]] = round(b[i], 4)

    print("\n----- Final Answer -----")
    x_values = []
    for i in range(n):
        xi = values[f"x{i+1}"]
        x_values.append(xi)
        print(f"x{i+1} = {xi}")

    original_Z = sum(obj[i] * x_values[i] for i in range(n))

    label = "minimum" if sense.startswith("min") else "maximum"
    print(f"Optimal Z ({label}) = {round(original_Z, 4)}")


if __name__ == "__main__":
    n, m, sense, obj, constraints = get_problem_from_user()
    A, b, cost, basis, col_names, sense = build_standard_form(n, m, sense, obj, constraints)
    A, b, basis = solve_big_m(A, b, cost, basis, col_names)
    if A is not None:
        report_solution(n, sense, obj, col_names, basis, b)

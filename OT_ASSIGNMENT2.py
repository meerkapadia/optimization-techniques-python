import copy

TOL = 1e-6
EPS = 1e-3

def print_bordered(headers, rows, label_w=10, col_w=10):
    def border():
        return "+" + "-" * (label_w + 2) + ("+" + "-" * (col_w + 2)) * (len(headers) - 1) + "+"

    def row_line(cells):
        first = f" {str(cells[0]).center(label_w)} |"
        rest = "".join(f" {str(c).center(col_w)} |" for c in cells[1:])
        return "|" + first + rest

    print(border())
    print(row_line(headers))
    print(border())
    for r in rows:
        print(row_line(r))
    print(border())


def get_problem_size_and_cost():
    m = int(input("How many sources (supply points)? "))
    n = int(input("How many destinations (demand points)? "))

    print(f"\nEnter the {m} supply values, space separated:")
    supply = list(map(float, input("Supply: ").split()))

    print(f"\nEnter the {n} demand values, space separated:")
    demand = list(map(float, input("Demand: ").split()))

    print("\nNow enter the cost matrix, one row at a time")
    cost = []
    for i in range(m):
        row = list(map(float, input(f"Costs for source {i+1} ({n} values): ").split()))
        cost.append(row)

    total_supply = sum(supply)
    total_demand = sum(demand)
    if abs(total_supply - total_demand) > TOL:
        print(f"\nSupply ({total_supply}) and demand ({total_demand}) don't match, "
              f"adding a dummy {'destination' if total_supply > total_demand else 'source'} "
              f"with cost 0 to balance it.")
        if total_supply > total_demand:
            demand.append(total_supply - total_demand)
            for row in cost:
                row.append(0.0)
        else:
            supply.append(total_demand - total_supply)
            cost.append([0.0] * n)

    return supply, demand, cost

def vogel_approximation(cost, supply, demand):
    rows, cols = len(supply), len(demand)
    supply = supply[:]
    demand = demand[:]
    allocation = [[0.0] * cols for _ in range(rows)]
    done_rows = set()
    done_cols = set()
    round_no = 0

    while len(done_rows) < rows and len(done_cols) < cols:
        round_no += 1

        row_penalty = {}
        for r in range(rows):
            if r in done_rows:
                continue
            vals = sorted(cost[r][c] for c in range(cols) if c not in done_cols)
            row_penalty[r] = vals[1] - vals[0] if len(vals) > 1 else vals[0]

        col_penalty = {}
        for c in range(cols):
            if c in done_cols:
                continue
            vals = sorted(cost[r][c] for r in range(rows) if r not in done_rows)
            col_penalty[c] = vals[1] - vals[0] if len(vals) > 1 else vals[0]

        best_row = max(row_penalty, key=row_penalty.get) if row_penalty else None
        best_col = max(col_penalty, key=col_penalty.get) if col_penalty else None

        if best_row is not None and (best_col is None or row_penalty[best_row] >= col_penalty[best_col]):
            r = best_row
            c = min((c for c in range(cols) if c not in done_cols), key=lambda c: cost[r][c])
            chosen = f"row S{r+1} (penalty {row_penalty[best_row]:g})"
        else:
            c = best_col
            r = min((r for r in range(rows) if r not in done_rows), key=lambda r: cost[r][c])
            chosen = f"column D{c+1} (penalty {col_penalty[best_col]:g})"

        qty = min(supply[r], demand[c])
        allocation[r][c] = qty
        supply[r] -= qty
        demand[c] -= qty

        print(f"VAM round {round_no}: biggest penalty is {chosen} -> "
              f"cheapest cell there is (S{r+1}, D{c+1}), allocate {qty:g}")

        if supply[r] <= TOL:
            done_rows.add(r)
        if demand[c] <= TOL:
            done_cols.add(c)

    return allocation


def print_allocation(allocation, cost, supply_labels, demand_labels, title):
    rows, cols = len(allocation), len(allocation[0])
    print(f"\n{title}")
    headers = [""] + [f"D{c+1}" for c in range(cols)]
    table_rows = []
    for r in range(rows):
        cells = []
        for c in range(cols):
            if allocation[r][c] > TOL:
                cells.append(f"{allocation[r][c]:g} (c={cost[r][c]:g})")
            else:
                cells.append(f"- (c={cost[r][c]:g})")
        table_rows.append([f"S{r+1}"] + cells)
    print_bordered(headers, table_rows, label_w=8, col_w=16)

def get_basic_cells(allocation):
    rows, cols = len(allocation), len(allocation[0])
    return [(r, c) for r in range(rows) for c in range(cols) if allocation[r][c] > TOL]


def fix_degeneracy(allocation, cost):
    rows, cols = len(allocation), len(allocation[0])
    needed = rows + cols - 1

    while len(get_basic_cells(allocation)) < needed:
        basic = set(get_basic_cells(allocation))
        placed = False
        for r in range(rows):
            for c in range(cols):
                if (r, c) in basic:
                    continue
                trial = set(basic)
                trial.add((r, c))
                if find_closed_loop(list(trial), (r, c)) is None:
                    allocation[r][c] = EPS
                    placed = True
                    break
            if placed:
                break
        if not placed:
            break
    return allocation


def find_uv(basic_cells, cost, rows, cols):
    u = [None] * rows
    v = [None] * cols

    row_counts = [sum(1 for (r, c) in basic_cells if r == i) for i in range(rows)]
    col_counts = [sum(1 for (r, c) in basic_cells if c == j) for j in range(cols)]
    if max(row_counts) >= max(col_counts):
        u[row_counts.index(max(row_counts))] = 0
    else:
        v[col_counts.index(max(col_counts))] = 0

    changed = True
    while changed:
        changed = False
        for (r, c) in basic_cells:
            if u[r] is not None and v[c] is None:
                v[c] = cost[r][c] - u[r]
                changed = True
            elif v[c] is not None and u[r] is None:
                u[r] = cost[r][c] - v[c]
                changed = True

    u = [x if x is not None else 0 for x in u]
    v = [x if x is not None else 0 for x in v]
    return u, v


def next_loop_nodes(loop, candidates):
    last = loop[-1]
    if len(loop) < 2:
        return [n for n in candidates if n[0] == last[0] or n[1] == last[1]]
    prev = loop[-2]
    if prev[0] == last[0]:
        return [n for n in candidates if n[1] == last[1]]
    else:
        return [n for n in candidates if n[0] == last[0]]


def find_closed_loop(basic_cells, start):
    def search(loop):
        if len(loop) >= 4 and start in next_loop_nodes(loop, [start]):
            return loop
        remaining = [cell for cell in basic_cells if cell not in loop]
        for nxt in next_loop_nodes(loop, remaining):
            result = search(loop + [nxt])
            if result:
                return result
        return None

    return search([start])


def modi_optimize(allocation, cost):
    allocation = copy.deepcopy(allocation)
    rows, cols = len(allocation), len(allocation[0])
    allocation = fix_degeneracy(allocation, cost)

    iteration = 0
    while True:
        iteration += 1
        basic_cells = get_basic_cells(allocation)
        u, v = find_uv(basic_cells, cost, rows, cols)

        print(f"\n--- MODI iteration {iteration} ---")
        print("u values:", [round(x, 3) for x in u])
        print("v values:", [round(x, 3) for x in v])

        deltas = {}
        for r in range(rows):
            for c in range(cols):
                if allocation[r][c] <= TOL:
                    deltas[(r, c)] = cost[r][c] - (u[r] + v[c])

        headers = [""] + [f"D{c+1}" for c in range(cols)]
        table_rows = []
        for r in range(rows):
            cells = []
            for c in range(cols):
                if allocation[r][c] > TOL:
                    cells.append(f"{allocation[r][c]:g}")
                else:
                    cells.append(f"D={deltas[(r, c)]:.2f}")
            table_rows.append([f"S{r+1}"] + cells)
        print_bordered(headers, table_rows, label_w=8, col_w=12)

        if not deltas or all(d >= -TOL for d in deltas.values()):
            if all(d > TOL for d in deltas.values()):
                print("All Δij > 0 -> optimal, and this is the unique optimum.")
            else:
                print("All Δij >= 0 -> optimal, but an alternate optimal solution also exists.")
            break

        entering_cell = min(deltas, key=deltas.get)
        print(f"Most negative Δij is at {('S'+str(entering_cell[0]+1), 'D'+str(entering_cell[1]+1))} "
              f"-> not optimal yet, bringing this cell in.")

        loop = find_closed_loop(basic_cells, entering_cell)
        minus_cells = loop[1::2]
        theta = min(allocation[r][c] for (r, c) in minus_cells)

        for i, (r, c) in enumerate(loop):
            if i % 2 == 0:
                allocation[r][c] += theta
            else:
                allocation[r][c] -= theta

    for r in range(rows):
        for c in range(cols):
            if allocation[r][c] < 1e-2:
                allocation[r][c] = 0.0

    return allocation


if __name__ == "__main__":
    print("=== Transportation Problem Solver (VAM + MODI) ===")

    print("\n--- Input Data ---")
    supply, demand, cost = get_problem_size_and_cost()

    print("\n--- Phase 1: Vogel's Approximation Method (VAM) ---")
    print("Distributing units row by row / column by column until every")
    print("supply and demand value is used up, to build the baseline plan.\n")
    allocation = vogel_approximation(cost, supply, demand)
    print_allocation(allocation, cost, supply, demand, "\nBaseline plan from VAM:")
    vam_cost = sum(allocation[r][c] * cost[r][c]
                   for r in range(len(cost)) for c in range(len(cost[0])))
    print(f"\nCost of the VAM baseline plan: {vam_cost:g}")

    print("\n--- Phase 2: MODI (Modified Distribution) Method ---")
    print("Computing u_i and v_j for every occupied cell, checking each empty")
    print("cell's Delta_ij, and looping the allocation around whenever a cell")
    print("shows the cost can still be reduced.\n")
    final_allocation = modi_optimize(allocation, cost)
    print_allocation(final_allocation, cost, supply, demand, "\nFinal (optimal) allocation after MODI:")
    final_cost = sum(final_allocation[r][c] * cost[r][c]
                      for r in range(len(cost)) for c in range(len(cost[0])))
    print(f"\nMinimum total transportation cost: {final_cost:g}")

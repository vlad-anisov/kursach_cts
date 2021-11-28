import time

INF = 100000000

best_cost = 0

def reduce(size, w, row, col, rowred, colred):
    rvalue = 0
    for i in range(size):
        temp = INF
        for j in range(size):
            temp = min(temp, w[row[i]][col[j]])
        if temp > 0:
            for j in range(size):
                if w[row[i]][col[j]] < INF:
                    w[row[i]][col[j]] -= temp
            rvalue += temp
        rowred[i] = temp
    for j in range(size):
        temp = INF
        for i in range(size):
            temp = min(temp, w[row[i]][col[j]])
        if temp > 0:
            for i in range(size):
                if w[row[i]][col[j]] < INF:
                    w[row[i]][col[j]] -= temp
            rvalue += temp
        colred[j] = temp
    return rvalue


def bestEdge(size, w, row, col):
    mosti = -INF
    ri = 0
    ci = 0
    for i in range(size):
        for j in range(size):
            if not w[row[i]][col[j]]:
                minrowwelt = INF
                zeroes = 0
                for k in range(size):
                    if not w[row[i]][col[k]]:
                        zeroes += 1
                    else:
                        minrowwelt = min(minrowwelt, w[row[i]][col[k]])
                if zeroes > 1: minrowwelt = 0
                mincolwelt = INF
                zeroes = 0
                for k in range(size):
                    if not w[row[k]][col[j]]:
                        zeroes += 1
                    else:
                        mincolwelt = min(mincolwelt, w[row[k]][col[j]])
                if zeroes > 1: mincolwelt = 0
                if minrowwelt + mincolwelt > mosti:
                    mosti = minrowwelt + mincolwelt
                    ri = i
                    ci = j
    return mosti, ri, ci


def explore(n, w, edges, cost, row, col, best, fwdptr, backptr):
    global best_cost

    colred = [0 for _ in range(n)]
    rowred = [0 for _ in range(n)]
    size = n - edges
    cost += reduce(size, w, row, col, rowred, colred)
    if cost < best_cost:
        if edges == n - 2:
            for i in range(n): best[i] = fwdptr[i]
            if w[row[0]][col[0]] >= INF:
                avoid = 0
            else:
                avoid = 1
            best[row[0]] = col[1 - avoid]
            best[row[1]] = col[avoid]
            best_cost = cost
        else:
            mostv, rv, cv = bestEdge(size, w, row, col)
            lowerbound = cost + mostv
            fwdptr[row[rv]] = col[cv]
            backptr[col[cv]] = row[rv]
            last = col[cv]
            while fwdptr[last] != INF: last = fwdptr[last]
            first = row[rv]
            while backptr[first] != INF: first = backptr[first]
            colrowval = w[last][first]
            w[last][first] = INF
            newcol = [INF for _ in range(size)]
            newrow = [INF for _ in range(size)]
            for i in range(rv): newrow[i] = row[i]
            for i in range(rv, size - 1): newrow[i] = row[i + 1]
            for i in range(cv): newcol[i] = col[i]
            for i in range(cv, size - 1): newcol[i] = col[i + 1]
            explore(n, w, edges + 1, cost, newrow, newcol, best, fwdptr, backptr)
            w[last][first] = colrowval
            backptr[col[cv]] = INF
            fwdptr[row[rv]] = INF
            if lowerbound < best_cost:
                w[row[rv]][col[cv]] = INF
                explore(n, w, edges, cost, row, col, best, fwdptr, backptr)
                w[row[rv]][col[cv]] = 0

    for i in range(size):
        for j in range(size):
            w[row[i]][col[j]] = w[row[i]][col[j]] + rowred[i] + colred[j]


def atsp(w):
    global best_cost
    size = len(w)
    col = [i for i in range(size)]
    row = [i for i in range(size)]
    best = [0 for _ in range(size)]
    route = [0 for _ in range(size)]
    fwdptr = [INF for _ in range(size)]
    backptr = [INF for _ in range(size)]
    best_cost = INF

    explore(size, w, 0, 0, row, col, best, fwdptr, backptr)

    index = 0
    for i in range(size):
        route[i] = index
        index = best[index]
    index = []
    cost = 0

    for i in range(size):
        if i != size - 1:
            src = route[i]
            dst = route[i + 1]
        else:
            src = route[i]
            dst = 0
        cost += w[src][dst]
        index.append([src, dst])
    route.append(route[0])
    return route

if __name__ == "__main__":
    matrix = [
        [float("inf"),20,18,12,8],
        [5,float("inf"),14,7,11],
        [12,18,float("inf"),6,11],
        [11,17,11,float("inf"),12],
        [5,5,5,5,float("inf")]
    ]

    start_time = time.time()
    cost, path = atsp(matrix)
    print("Cost = ", cost)
    print("Path = ", path)
    print("Time (s)", time.time() - start_time)
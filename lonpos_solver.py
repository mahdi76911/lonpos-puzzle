import time, sys

PIECES = [
    [(0,1),(0,2),(1,0),(2,0)],              # 0: L-pentomino
    [(0,1),(1,1),(1,0)],                    # 1: O-tetromino
    [(0,1),(1,0)],                          # 2: V-triomino
    [(0,1),(0,2),(1,0),(1,2)],              # 3: N-pentomino
    [(0,1),(1,0),(-1,0),(0,-1)],            # 4: X-pentomino (cross)
    [(0,1),(0,2),(0,3),(1,0)],              # 5: P-pentomino
    [(0,1),(0,2),(0,3)],                    # 6: I-tetromino
    [(0,1),(0,2),(0,3),(1,1)],              # 7: T-pentomino
    [(0,1),(1,1),(1,2),(1,3)],              # 8: P-pentomino (mirrored)
    [(0,1),(1,1),(1,2),(2,2)],              # 9: W-pentomino
    [(0,1),(1,1),(1,0),(0,2)],              # 10: U-pentomino
    [(0,1),(0,2),(1,0)],                    # 11: L-tetromino
]
COLORS = ["midnightblue","yellow","darkorchid","lime","saddlebrown","pink",
          "deepskyblue","olivedrab","seagreen","red","indigo","orangered"]
N = 10

# exact transforms from the notebook:
# rotate_R: (x,y) -> (y,-x)      rotate_L: (x,y) -> (-y,x)
# vertical_flip: (x,y) -> (-x,y) horizental_flip: (x,y) -> (x,-y)
def rot_cw(cs):  return [( y, -x) for (x, y) in cs]
def rot_ccw(cs): return [(-y,  x) for (x, y) in cs]
def vflip(cs):   return [(-x,  y) for (x, y) in cs]
def hflip(cs):   return [( x, -y) for (x, y) in cs]

def orientations(piece):
    """All distinct shapes (origin + offsets), deduped."""
    base = [(0, 0)] + list(piece)
    seen, cur = {}, base
    for _ in range(4):
        for s in (cur, vflip(cur)):
            k = frozenset(s)
            if k not in seen:
                seen[k] = tuple(sorted(s))
        cur = rot_cw(cur)
    return list(seen.values())

PLAYABLE = [(i, j) for i in range(N) for j in range(N) if j <= i]

def solve(placed=None, t0=None):
    """Backtracking exact-cover. placed: {piece_id: (origin, shape)} for pre-placed pieces."""
    placed = placed or {}
    occupied = {}
    for pid, (o, shape) in placed.items():
        for (a, b) in shape:
            occupied[(o[0]+a, o[1]+b)] = pid
    unused = set(range(12)) - set(placed)
    orients = [orientations(p) for p in PIECES]
    solution = dict(placed)
    cells_order = PLAYABLE

    def first_empty():
        for c in cells_order:
            if c not in occupied:
                return c
        return None

    def fits(shape, ox, oy):
        for (dx, dy) in shape:
            x, y = ox+dx, oy+dy
            if not (0 <= x < N) or not (0 <= y < N) or y > x or (x, y) in occupied:
                return False
        return True

    def bt(depth=0):
        f = first_empty()
        if f is None:
            return True
        for pid in sorted(unused):
            for shape in orients[pid]:
                for (dx, dy) in shape:      # anchor: this cell of the piece covers f
                    ox, oy = f[0]-dx, f[1]-dy
                    if fits(shape, ox, oy):
                        for (a, b) in shape:
                            occupied[(ox+a, oy+b)] = pid
                        solution[pid] = ((ox, oy), shape)
                        unused.discard(pid)
                        if bt(depth+1):
                            return True
                        unused.add(pid)
                        del solution[pid]
                        for (a, b) in shape:
                            del occupied[(ox+a, oy+b)]
        return False

    t0 = time.time()
    ok = bt()
    return (ok, solution, time.time()-t0)

if __name__ == "__main__":
    ok, sol, dt = solve()
    print(f"solved={ok} in {dt:.3f}s")
    if ok:
        grid = [[-2]*N for _ in range(N)]
        for i in range(N):
            for j in range(i+1, N):
                grid[i][j] = -2
        for pid, ((ox, oy), shape) in sorted(sol.items()):
            for (a, b) in shape:
                grid[ox+a][oy+b] = pid
        print("\nboard (-2=blocked, number=piece id):")
        for row in grid:
            print(" ".join(f"{v:2d}" for v in row))
        # validate
        covered = sum(1 for i in range(N) for j in range(N) if j <= i and grid[i][j] != -2)
        assert covered == 55, covered
        per = {}
        for i in range(N):
            for j in range(N):
                if j <= i and grid[i][j] != -2:
                    per[grid[i][j]] = per.get(grid[i][j], 0) + 1
        assert sorted(per) == list(range(12))
        print(f"\nvalid tiling: all 55 cells covered, all 12 pieces used once")
        print("\nplacements (piece_id, origin (row,col), shape cells):")
        for pid in sorted(sol):
            (ox, oy), shape = sol[pid]
            print(f"  {pid:2d} at ({ox},{oy}): {sorted(shape)}")
        with open(r"C:\Users\mahdi\AppData\Local\Temp\lonpos_solution.json", "w") as f:
            import json
            json.dump({str(k): [list(v[0]), [list(c) for c in v[1]]] for k, v in sol.items()}, f, indent=1)
        print("solution saved to lonpos_solution.json")

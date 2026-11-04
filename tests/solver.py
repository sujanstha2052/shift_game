"""
Comprehensive Level Solver for Shift/Return.
Supports:
- Walking / Collisions
- Dimension Shifting (with wall / laser / block check)
- RAM Block pushes (with Sokoban physics & dimension checks)
- Pressure Plates & Laser Barriers (circuits)
- Hostile Daemon Sentinels (patrol steps when in Corrupted dimension)
- Terminals & Win Condition (all terminals rebooted + step into exit)
"""
from collections import deque


def solve_full_level(lvl):
    start_x, start_y = lvl["player_start"]
    exit_x, exit_y = lvl["exit_pos"]
    normal_map = lvl["normal_map"]
    corrupt_map = lvl["corrupt_map"]
    terminals = lvl.get("terminals", [])
    blocks = lvl.get("blocks", [])
    plates = lvl.get("plates", [])
    lasers = lvl.get("lasers", [])
    daemons_cfg = lvl.get("daemons", [])

    initial_blocks = tuple((b["x"], b["y"]) for b in blocks)
    # daemons state: tuple of (point_index, direction)
    initial_daemons = tuple((0, 1) for _ in daemons_cfg)

    initial_rebooted = 0
    for i, t in enumerate(terminals):
        if t["x"] == start_x and t["y"] == start_y and t["corrupted"] == False:
            initial_rebooted |= (1 << i)

    initial_state = (start_x, start_y, False, initial_blocks, initial_daemons, initial_rebooted)
    queue = deque([(initial_state, [])])
    visited = {initial_state}
    target_rebooted = (1 << len(terminals)) - 1

    def is_block_active(b_idx, is_corr):
        dim = blocks[b_idx].get("dimension", "both")
        if dim == "both":
            return True
        if dim == "corrupt":
            return is_corr
        return not is_corr

    def get_active_channels(cur_px, cur_py, cur_blocks, is_corr):
        active = set()
        for p in plates:
            p_dim = p.get("dimension", "both")
            p_active = (p_dim == "both") or (p_dim == "corrupt" and is_corr) or (p_dim == "normal" and not is_corr)
            if not p_active:
                continue
            if cur_px == p["x"] and cur_py == p["y"]:
                active.add(p.get("channel", "A"))
                continue
            for b_idx, (bx, by) in enumerate(cur_blocks):
                if is_block_active(b_idx, is_corr) and bx == p["x"] and by == p["y"]:
                    active.add(p.get("channel", "A"))
                    break
        return active

    def is_laser_blocking(lx, ly, cur_blocks, is_corr, active_channels):
        for l in lasers:
            if l["x"] == lx and l["y"] == ly:
                l_dim = l.get("dimension", "corrupt")
                l_active = (l_dim == "both") or (l_dim == "corrupt" and is_corr) or (l_dim == "normal" and not is_corr)
                if l_active and l.get("channel", "A") not in active_channels:
                    shielded = False
                    for b_idx, (bx, by) in enumerate(cur_blocks):
                        if is_block_active(b_idx, is_corr) and bx == lx and by == ly:
                            shielded = True
                            break
                    if not shielded:
                        return True
        return False

    def step_daemons(d_state):
        new_d = []
        for i, (idx, direct) in enumerate(d_state):
            cfg = daemons_cfg[i]
            points = cfg["patrol_points"]
            loop = cfg.get("loop", False)
            if len(points) <= 1:
                new_d.append((idx, direct))
                continue
            if loop:
                new_idx = (idx + 1) % len(points)
                new_d.append((new_idx, direct))
            else:
                next_i = idx + direct
                if next_i >= len(points) or next_i < 0:
                    direct *= -1
                    next_i = idx + direct
                new_d.append((next_i, direct))
        return tuple(new_d)

    def is_caught(px, py, is_corr, d_state):
        if not is_corr:
            return False
        for i, (idx, _) in enumerate(d_state):
            pt = daemons_cfg[i]["patrol_points"][idx]
            if pt[0] == px and pt[1] == py:
                return True
        return False

    while queue:
        (px, py, is_corr, cur_blocks, cur_daemons, rebooted), path = queue.popleft()

        if rebooted == target_rebooted and px == exit_x and py == exit_y:
            return path

        cur_map = corrupt_map if is_corr else normal_map
        active_channels = get_active_channels(px, py, cur_blocks, is_corr)

        # 1. MOVEMENT
        for dx, dy, act_name in [(0, -1, "UP"), (0, 1, "DOWN"), (-1, 0, "LEFT"), (1, 0, "RIGHT")]:
            nx, ny = px + dx, py + dy

            if not (0 <= nx < 16 and 0 <= ny < 12) or cur_map[ny][nx] == 1:
                continue

            if is_laser_blocking(nx, ny, cur_blocks, is_corr, active_channels):
                continue

            colliding_block_idx = None
            for b_idx, (bx, by) in enumerate(cur_blocks):
                if is_block_active(b_idx, is_corr) and bx == nx and by == ny:
                    colliding_block_idx = b_idx
                    break

            new_blocks = cur_blocks
            if colliding_block_idx is not None:
                dest_bx, dest_by = nx + dx, ny + dy
                if not (0 <= dest_bx < 16 and 0 <= dest_by < 12) or cur_map[dest_by][dest_bx] == 1:
                    continue
                other_block = False
                for ob_idx, (obx, oby) in enumerate(cur_blocks):
                    if ob_idx != colliding_block_idx and is_block_active(ob_idx, is_corr):
                        if obx == dest_bx and oby == dest_by:
                            other_block = True
                            break
                if other_block:
                    continue

                temp_blocks = list(cur_blocks)
                temp_blocks[colliding_block_idx] = (dest_bx, dest_by)
                new_blocks = tuple(temp_blocks)

            # Step daemons if in Corrupted dimension
            new_daemons = cur_daemons
            if is_corr and daemons_cfg:
                new_daemons = step_daemons(cur_daemons)

            # If caught by a daemon, illegal move
            if is_caught(nx, ny, is_corr, new_daemons):
                continue

            new_rebooted = rebooted
            for i, t in enumerate(terminals):
                if t["x"] == nx and t["y"] == ny and t["corrupted"] == is_corr:
                    new_rebooted |= (1 << i)

            new_state = (nx, ny, is_corr, new_blocks, new_daemons, new_rebooted)
            if new_state not in visited:
                visited.add(new_state)
                queue.append((new_state, path + [act_name]))

        # 2. DIMENSION SHIFT
        target_corr = not is_corr
        target_map = corrupt_map if target_corr else normal_map

        if target_map[py][px] == 1:
            continue

        blocked_by_block = False
        for b_idx, (bx, by) in enumerate(cur_blocks):
            if is_block_active(b_idx, target_corr) and bx == px and by == py:
                blocked_by_block = True
                break
        if blocked_by_block:
            continue

        target_channels = get_active_channels(px, py, cur_blocks, target_corr)
        if is_laser_blocking(px, py, cur_blocks, target_corr, target_channels):
            continue

        # Step daemons if entering Corrupted dimension
        new_daemons = cur_daemons
        if target_corr and daemons_cfg:
            new_daemons = step_daemons(cur_daemons)

        # Check daemon collision on shift
        if is_caught(px, py, target_corr, new_daemons):
            continue

        new_rebooted = rebooted
        for i, t in enumerate(terminals):
            if t["x"] == px and t["y"] == py and t["corrupted"] == target_corr:
                new_rebooted |= (1 << i)

        new_state = (px, py, target_corr, cur_blocks, new_daemons, new_rebooted)
        if new_state not in visited:
            visited.add(new_state)
            queue.append((new_state, path + ["SHIFT"]))

    return None

import csv, glob, os, re

def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None

def natural(path):
    return int(re.findall(r'\d+', os.path.basename(path))[0])

rows_out = []
for path in sorted(glob.glob('src/collector/dataset_obd/live*.csv'), key=natural):
    with open(path, newline='') as f:
        r = csv.DictReader(f)
        cols = r.fieldnames
        t_col = next((c for c in cols if 'ENGINE_RUN' in c.upper()), None)
        v_col = next((c for c in cols if 'SPEED' in c.upper()), None)
        p_col = next((c for c in cols if 'RPM' in c.upper()), None)
        n = active = moving = 0
        vmax = vsum = 0.0
        t_last = 0.0
        resets = 0
        prev_t = None
        for row in r:
            n += 1
            t = num(row.get(t_col)); v = num(row.get(v_col)); p = num(row.get(p_col))
            if t is not None:
                if prev_t is not None and t < prev_t:
                    resets += 1
                prev_t = t
                t_last = max(t_last, t)
            if (v or 0) > 0 or (p or 0) > 0:
                active += 1
            if (v or 0) > 0:
                moving += 1
                vsum += v
                vmax = max(vmax, v)
        rows_out.append((os.path.basename(path), n, active, t_last, moving,
                         vmax, (vsum/moving if moving else 0), len(cols), resets))

print(f"{'fisier':12} {'randuri':>7} {'active':>7} {'durata_s':>8} {'in_miscare':>10} {'v_max':>6} {'v_med':>6} {'cols':>4} {'reset':>5}")
for r in rows_out:
    print(f"{r[0]:12} {r[1]:7d} {r[2]:7d} {r[3]:8.0f} {r[4]:10d} {r[5]:6.0f} {r[6]:6.1f} {r[7]:4d} {r[8]:5d}")

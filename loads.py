"""Redistribuicao de cargas nas secoes da fuselagem"""

LOADS_PATH = 'data/forcas.csv'
SECTIONS_PATH = 'data/secoes.csv'
OUTPUT_PATH = 'results.csv'


# leitura das cargas
loads = []
with open(LOADS_PATH) as f:
    next(f)
    for line in f:
        parts = line.strip().split(',')
        x, fx, fy, fz = map(float, parts)
        loads.append((x, fx, fy, fz))

# leitura das secoes
with open(SECTIONS_PATH) as f:
    next(f)
    sections = [float(l.strip()) for l in f]
sections = list(sorted(sections))


def sections_around(x):
    """Calculo das secoes a esquerda e a direita de um ponto"""
    for x_l, x_r in zip([None] + sections, sections):
        if x <= x_r:
            return x_l, x_r
    return sections[-1], None


def main():
    forces, moments = {}, {}

    x_pivot = sections[0]
    for x, fx, fy, fz in loads:
        x_left, x_right = sections_around(x)

        if x_left is None:  # antes da primeira secao
            continue

        if x_right is None:  # ultima secao
            fx_old, fy_old, fz_old = forces.setdefault(x_left, (0, 0, 0))
            forces[x_left] = fx_old + fx, fy_old + fy, fz_old + fz

            mx = 0.0
            my = - fz * (x - x_left)
            mz = fy * (x - x_left)

            mx_old, my_old, mz_old = forces.setdefault(x_left, (0, 0, 0))
            moments[x_left] = mx_old + mx, my_old + my, mz_old + mz

            continue

        coef_left = (x_right - x) / (x_right - x_left)
        fx_left = fx * 0.5
        fy_left = fy * coef_left
        fz_left = fz * coef_left

        coef_right = (x - x_left) / (x_right - x_left)
        fx_right = fx * 0.5
        fy_right = fy * coef_right
        fz_right = fz * coef_right

        # verificacoes
        assert fy_left + fy_right == fy
        assert fz_left + fz_right == fz
        assert fy_left * (x_left - x_pivot) + fy_right * (x_right - x_pivot) == fy * (x - x_pivot)
        assert fz_left * (x_left - x_pivot) + fz_right * (x_right - x_pivot) == fz * (x - x_pivot)

        fx_old, fy_old, fz_old = forces.setdefault(x_left, (0, 0, 0))
        forces[x_left] = fx_old + fx_left, fy_old + fy_left, fz_old + fz_left

        fx_old, fy_old, fz_old = forces.setdefault(x_right, (0, 0, 0))
        forces[x_right] = fx_old + fx_right, fy_old + fy_right, fz_old + fz_right


    with open(OUTPUT_PATH, 'w') as out:
        out.write('{},{},{}\n'.format(
            'x', ','.join(['fx', 'fy', 'fz']), ','.join(['mx', 'my', 'mz'])))

        for x in sections:
            f = forces.setdefault(x, (0, 0, 0))
            m = moments.setdefault(x, (0, 0, 0))

            out.write('{},{},{}\n'.format(
                x, ','.join(map(str, f)), ','.join(map(str, m))))


if __name__ == '__main__':
    main()

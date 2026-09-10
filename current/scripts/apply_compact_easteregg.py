"""Place an original pixel-cane island in the compact board's front free space.

Only appends board-level F.Silkscreen rectangles and their locked group. The
rest of the native file is retained byte for byte; rerunning is idempotent.
"""
from pathlib import Path
from uuid import UUID, uuid5

ROOT = Path(__file__).resolve().parents[1]
NAMESPACE = UUID('455f03c3-7c5b-4d0e-9ca5-bf4e74e62037')
PIXEL = .25
ORIGIN = (1.1, 7.65)
WORD_PIXEL = .16
WORD_ORIGIN = (.65, 19.90)
# A separate small-size pixel alphabet keeps every stroke/gap at least 0.16 mm.
# Lowercase bodies start two rows below the capitals; g has a real descender.
WORD_GLYPHS = {
    's': (2, ['01111', '10000', '01110', '00001', '11110']),
    'u': (2, ['10001', '10001', '10001', '10011', '01101']),
    'g': (2, ['01111', '10001', '10001', '01111', '00001', '10001', '01110']),
    'a': (2, ['01110', '00001', '01111', '10001', '01111']),
    'r': (2, ['1011', '1100', '1000', '1000', '1000']),
    'C': (0, ['01111', '10000', '10000', '10000', '10000', '10000', '01111']),
    'A': (0, ['01110', '10001', '10001', '11111', '10001', '10001', '10001']),
    'N': (0, ['10001', '11001', '11001', '10101', '10011', '10011', '10001']),
    'e': (2, ['01110', '10001', '11111', '10000', '01111']),
}
# Three jointed stalks, stepped leaves and a raised, ragged floating island.
# Each # is one printable square. No fonts or externally copied artwork.
PIXELS = (
    '          ##         ',
    '       #  ##         ',
    '    ##  ####         ',
    '    ##   ####   ##   ',
    ' #  ##    ##    ## # ',
    '  ####   ####   ###  ',
    '   ####   ##   ###   ',
    '    ##    ##    ##   ',
    '   ####  ####  ####  ',
    '    ##    ##    ##   ',
    '    ##############   ',
    '  ################## ',
    '    ##### ########   ',
    '      ##   ####      ',
)


def rectangles():
    result = []
    for y, row in enumerate(PIXELS):
        x = 0
        while x < len(row):
            if row[x] != '#':
                x += 1
                continue
            start = x
            while x < len(row) and row[x] == '#':
                x += 1
            result.append((ORIGIN[0] + start * PIXEL, ORIGIN[1] + y * PIXEL,
                           ORIGIN[0] + x * PIXEL, ORIGIN[1] + (y + 1) * PIXEL))
    return result


def illustration_payload():
    items, identifiers = [], []
    for i, (x0, y0, x1, y1) in enumerate(rectangles()):
        uid = str(uuid5(NAMESPACE, f'row-run-{i}'))
        identifiers.append(uid)
        items.append(f'\t(gr_rect (start {x0:.4f} {y0:.4f}) (end {x1:.4f} {y1:.4f})\n'
                     f'\t\t(stroke (width 0) (type default)) (fill yes)\n'
                     f'\t\t(layer "F.SilkS") (uuid "{uid}"))\n')
    members = ' '.join(f'"{uid}"' for uid in identifiers)
    items.append(f'\t(group "compact-pixel-cane" (locked yes)\n'
                 f'\t\t(uuid "{uuid5(NAMESPACE, "group")}") (members {members}))\n')
    return ''.join(items)


def wordmark_rectangles():
    result, cursor = [], 0
    for letter in 'sugarCANe':
        top, rows = WORD_GLYPHS[letter]
        for y, row in enumerate(rows, top):
            for x, bit in enumerate(row, cursor):
                if bit == '1':
                    # 90 degrees counterclockwise: read from bottom to top.
                    result.append((WORD_ORIGIN[0] + y * WORD_PIXEL,
                                   WORD_ORIGIN[1] - (x+1) * WORD_PIXEL,
                                   WORD_ORIGIN[0] + (y+1) * WORD_PIXEL,
                                   WORD_ORIGIN[1] - x * WORD_PIXEL))
        cursor += len(rows[0]) + 1
    return result


def wordmark_payload():
    items, identifiers = [], []
    for i, (x0, y0, x1, y1) in enumerate(wordmark_rectangles()):
        uid = str(uuid5(NAMESPACE, f'wordmark-pixel-{i}'))
        identifiers.append(uid)
        items.append(f'\t(gr_rect (start {x0:.4f} {y0:.4f}) (end {x1:.4f} {y1:.4f})\n'
                     f'\t\t(stroke (width 0) (type default)) (fill yes)\n'
                     f'\t\t(layer "F.SilkS") (uuid "{uid}"))\n')
    members = ' '.join(f'"{uid}"' for uid in identifiers)
    items.append(f'\t(group "compact-wordmark-90deg" (locked yes)\n'
                 f'\t\t(uuid "{uuid5(NAMESPACE, "wordmark-group")}") (members {members}))\n')
    return ''.join(items)


def payload():
    return illustration_payload() + wordmark_payload()


def main():
    board = ROOT / 'hardware/FRC_Sensor_CAN.kicad_pcb'
    text = board.read_text()
    art = payload()
    if '"compact-pixel-cane"' in text and '"compact-wordmark-90deg"' not in text:
        original = illustration_payload()
        assert text.count(original) == 1, 'Existing illustration differs'
        text = text.replace(original, art)
        board.write_text(text)
        print('Added 90-degree pixel wordmark beside C1')
    if '"compact-pixel-cane"' in text:
        assert art in text, 'Existing artwork differs; review it before replacing it'
        print('Pixel-cane artwork already current')
    else:
        tail = text.rfind(')')
        board.write_text(text[:tail] + art + text[tail:])
        print(f'Added {len(rectangles())} front-silkscreen rectangles')
    # Reviewable vector source at actual physical size, also useful for a case.
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="5.25mm" height="3.5mm" '
           'viewBox="0 0 21 14" shape-rendering="crispEdges">',
           '<title>Original sugarCANe pixel-cane island</title>', '<g fill="#fff">']
    for x0, y0, x1, y1 in rectangles():
        svg.append(f'<rect x="{(x0-ORIGIN[0])/PIXEL:.0f}" y="{(y0-ORIGIN[1])/PIXEL:.0f}" '
                   f'width="{(x1-x0)/PIXEL:.0f}" height="1"/>')
    svg += ['</g>', '</svg>']
    (ROOT / 'hardware/artwork/compact-pixel-cane.svg').write_text('\n'.join(svg) + '\n')


if __name__ == '__main__':
    main()

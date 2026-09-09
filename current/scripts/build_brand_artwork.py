"""Build the original sugarCANe pixel wordmark and cane illustration."""
from pathlib import Path
from shapely.geometry import box
from shapely import affinity, union_all

R = Path(__file__).resolve().parents[1]
OUT = R / 'hardware/artwork'

# Original grid-drawn letters: two-cell stems, seven-row lowercase bodies,
# nine-row capitals and an explicit g descender. The final e has a full crossbar
# and a five-cell opening on the right. No installed or downloaded font needed.
GLYPHS = {
    's': (2, [
        '0111110',
        '1111111',
        '1100000',
        '0111110',
        '0000011',
        '1111111',
        '0111110',
    ]),
    'u': (2, [
        '1100011',
        '1100011',
        '1100011',
        '1100011',
        '1100011',
        '0111111',
        '0011011',
    ]),
    'g': (2, [
        '0011111',
        '0111111',
        '1100011',
        '1100011',
        '0111111',
        '0011111',
        '0000011',
        '0111110',
        '0111100',
    ]),
    'a': (2, [
        '0111100',
        '0111110',
        '0000011',
        '0111111',
        '1100011',
        '1100011',
        '0111111',
    ]),
    'r': (2, [
        '110110',
        '111111',
        '111000',
        '110000',
        '110000',
        '110000',
        '110000',
    ]),
    'C': (0, [
        '0011110',
        '0111111',
        '1100011',
        '1100000',
        '1100000',
        '1100000',
        '1100011',
        '0111111',
        '0011110',
    ]),
    'A': (0, [
        '0011100',
        '0111110',
        '1100011',
        '1100011',
        '1100011',
        '1111111',
        '1111111',
        '1100011',
        '1100011',
    ]),
    'N': (0, [
        '1100011',
        '1110011',
        '1110011',
        '1111011',
        '1101111',
        '1100111',
        '1100111',
        '1100011',
        '1100011',
    ]),
    'e': (2, [
        '0011100',
        '0111110',
        '1100011',
        '1111111',
        '1100000',
        '0111110',
        '0011110',
    ]),
}
word = []
cursor = 0
for letter in 'sugarCANe':
    top, rows = GLYPHS[letter]
    assert len(set(map(len, rows))) == 1
    word.extend(box(cursor+x, top+y, cursor+x+1, top+y+1)
                for y, row in enumerate(rows) for x, bit in enumerate(row) if bit == '1')
    cursor += len(rows[0]) + 1.5
word = union_all(word)
x0, y0, x1, y1 = word.bounds
pixel_mm = 45.6/(x1-x0)
word = affinity.translate(affinity.scale(word, pixel_mm, pixel_mm, origin=(0, 0)), 3.2, 49.3)

# Original pixel stalks and stair-step leaves stand on a raised mound with a
# stepped, tapering underside, matching the original floating-island treatment.
cane = []
def rect(x, y, width, height):
    cane.append(box(x, y, x+width, y+height))

def leaf(x, y, dx, dy, count):
    for i in range(count):
        size = 2 if i < count-1 else 1
        rect(x+dx*i, y+dy*i, size, size)

for x, top in [(7, 11), (17, 1), (28, 7)]:
    rect(x, top, 3, 39-top)
    for y in range(top+7, 35, 9):
        rect(x-1, y, 5, 1)
leaf(6, 15, -1, -1, 7)
leaf(9, 21, 1, -1, 5)
leaf(16, 8, -1, -1, 7)
leaf(19, 13, 1, -1, 8)
leaf(30, 16, 1, -1, 7)
leaf(27, 25, -1, -1, 6)
plant = union_all(cane)
slots = [box(x+1, y, x+2, min(y+4, 35))
         for x, top in [(7, 11), (17, 1), (28, 7)]
         for y in range(top+2, 34, 9)]
plant = plant.difference(union_all(slots))
soil = union_all([box(15, 35, 23, 36), box(11, 36, 27, 37),
                  box(7, 37, 31, 38), box(4, 38, 34, 39),
                  box(6, 39, 32, 40), box(9, 40, 29, 41)])
soil = soil.difference(union_all([
    box(x, y, x+1, y+1) for x, y in [(8, 38), (14, 37), (21, 38), (29, 38)]]))
plant = union_all([plant, soil])
plant = affinity.translate(affinity.scale(plant, .8, .8, origin=(0, 0)), 10.4, 12.1)
art = union_all([word, plant])
assert art.is_valid


def pieces(geometry):
    if geometry.is_empty:
        return []
    if geometry.geom_type == 'Polygon':
        return [geometry]
    return [p for g in getattr(geometry, 'geoms', []) for p in pieces(g)]


svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="52mm" height="74mm" viewBox="0 0 52 74">',
       '<title>sugarCANe — readable pixel lettering and cane</title>',
       '<desc>Underside reading orientation. Original pixel cane on a raised floating island with a stepped underside; original bold pixel lettering with open counters and a distinct lowercase e. Only the product name is text. No border.</desc>',
       '<g fill="#ffffff" fill-rule="evenodd">']
for poly in pieces(art):
    contours = []
    for ring in [poly.exterior, *poly.interiors]:
        coords = list(ring.coords)[:-1]
        contours.append('M '+' L '.join(f'{x:.6f},{y:.6f}' for x,y in coords)+' Z')
    svg.append('<path d="'+' '.join(contours)+'"/>')
svg += ['</g>', '</svg>']
OUT.mkdir(exist_ok=True)
(OUT/'sugarCANe.svg').write_text('\n'.join(svg)+'\n')
print('Wrote sugarCANe artwork:', len(pieces(art)), 'filled paths; ink bounds', art.bounds)

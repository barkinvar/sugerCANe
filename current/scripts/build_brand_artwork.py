"""Build the original pixel cane with a clear, non-pixel sugarCANe wordmark."""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.basePen import BasePen
from shapely.geometry import LineString, box
from shapely import affinity, union_all
from shapely.ops import polygonize

R = Path(__file__).resolve().parents[1]
OUT = R / 'hardware/artwork'


class OutlinePen(BasePen):
    """Flatten Bezier outlines adaptively, retaining closed counter contours."""
    def __init__(self, glyphs=None, tolerance=.004):
        super().__init__(glyphs)
        self.tolerance = tolerance
        self.rings = []
        self.points = []

    def _moveTo(self, pt):
        self.points = [pt]

    def _lineTo(self, pt):
        self.points.append(pt)

    def curve(self, points):
        a, b = points[0], points[-1]
        dx, dy = b[0]-a[0], b[1]-a[1]
        length = (dx*dx+dy*dy)**.5
        errors = [abs(dx*(p[1]-a[1])-dy*(p[0]-a[0])) / length
                  if length else ((p[0]-a[0])**2+(p[1]-a[1])**2)**.5
                  for p in points[1:-1]]
        if max(errors, default=0) <= self.tolerance:
            self.points.append(b)
            return
        levels = [points]
        while len(levels[-1]) > 1:
            levels.append([((p[0]+q[0])/2, (p[1]+q[1])/2)
                           for p, q in zip(levels[-1], levels[-1][1:])])
        self.curve([level[0] for level in levels])
        self.curve([level[-1] for level in reversed(levels)])

    def _curveToOne(self, p1, p2, p3):
        self.curve([self.points[-1], p1, p2, p3])

    def _qCurveToOne(self, p1, p2):
        self.curve([self.points[-1], p1, p2])

    def _closePath(self):
        self.rings.append(self.points)
        self.points = []

    def _endPath(self):
        self._closePath()

    def geometry(self):
        # Fonts may contain overlapping strokes. Resolve their nonzero winding
        # before generating the simple polygon/holes used by SVG and KiCad.
        rings = [ring+[ring[0]] for ring in self.rings if len(ring) > 2]
        faces = polygonize(union_all([LineString(ring) for ring in rings]))
        filled = []
        for face in faces:
            sample = face.representative_point()
            x, y = sample.x, sample.y
            winding = 0
            for ring in rings:
                for a,b in zip(ring, ring[1:]):
                    cross = (b[0]-a[0])*(y-a[1])-(x-a[0])*(b[1]-a[1])
                    if a[1] <= y < b[1] and cross > 0:
                        winding += 1
                    elif b[1] <= y < a[1] and cross < 0:
                        winding -= 1
            if winding:
                filled.append(face)
        return union_all(filled)


# Clear, open letterforms keep the word readable beside the pixel illustration.
fonts = {w: instantiateVariableFont(TTFont(R/'sources/fonts/IBMPlexSans.ttf'),
         {'wght': w, 'wdth': 100}) for w in (600, 700)}
word = []
cursor = 0
for letter in 'sugarCANe':
    font = fonts[700 if letter.isupper() else 600]
    glyphs = font.getGlyphSet()
    glyph = glyphs[font.getBestCmap()[ord(letter)]]
    pen = OutlinePen(glyphs, tolerance=.35)
    glyph.draw(pen)
    word.append(affinity.translate(pen.geometry(), cursor, 0))
    cursor += glyph.width + 14
word = union_all(word)
x0, y0, x1, y1 = word.bounds
scale = min(45.6/(x1-x0), 8.4/(y1-y0))
word = affinity.scale(word, scale, -scale, origin=(0, 0))
x0, y0, x1, _ = word.bounds
word = affinity.translate(word, (52-(x1-x0))/2-x0, 49.3-y0)

# Restore the original three pixel stalks and stair-step leaves. A stepped
# convex mound retains the raised-ground silhouette without corner ornaments.
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
soil = union_all([box(4, 38, 34, 40), box(7, 37, 31, 38),
                  box(11, 36, 27, 37), box(15, 35, 23, 36)])
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
       '<title>sugarCANe — pixel cane with clear lettering</title>',
       '<desc>Underside reading orientation. Original three-stalk pixel cane on a stepped convex mound; clear IBM Plex Sans outlined lettering, weights 600 and 700. Only the product name is text. No border.</desc>',
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

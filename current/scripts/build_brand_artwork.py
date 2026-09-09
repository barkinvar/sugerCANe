"""Build the original sugarCANe wordmark and flowing cane illustration."""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.basePen import BasePen
from shapely.geometry import LineString
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


def curve(start, commands):
    """An original closed path in millimetres, using cubic Bezier handles."""
    pen = OutlinePen()
    pen.moveTo(start)
    for cmd in commands:
        if len(cmd) == 2:
            pen.lineTo(cmd)
        else:
            pen.curveTo(*zip(cmd[::2], cmd[1::2]))
    pen.closePath()
    return pen.geometry()


# Smooth geometric letterforms; the weight change makes CAN read within the name.
fonts = {w: instantiateVariableFont(TTFont(R/'sources/fonts/Outfit.ttf'), {'wght': w})
         for w in (550, 800)}
word = []
cursor = 0
for letter in 'sugarCANe':
    font = fonts[800 if letter.isupper() else 550]
    glyphs = font.getGlyphSet()
    glyph = glyphs[font.getBestCmap()[ord(letter)]]
    pen = OutlinePen(glyphs, tolerance=.35)
    glyph.draw(pen)
    word.append(affinity.translate(pen.geometry(), cursor, 0))
    cursor += glyph.width + 5
word = union_all(word)
x0, y0, x1, y1 = word.bounds
scale = 45.6/(x1-x0)
word = affinity.scale(word, scale, -scale, origin=(0, 0))
x0, y0, _, _ = word.bounds
word = affinity.translate(word, 3.2-x0, 49.6-y0)

# Three jointed stalks fan from a common root. Curved edges and broad blades
# make this an original botanical mark, independent of game graphics.
stems = [
    curve((22.6, 44.5), [(24.8, 35.3, 25.3, 25.3, 31.4, 13.1),
          (31.8, 12.4, 32.4, 12.4, 32.6, 13.1),
          (28.8, 27.1, 28.4, 37.5, 26.3, 44.7)]),
    curve((18.8, 43.6), [(19.9, 33.6, 17.4, 26.7, 14.6, 22.3),
          (14.1, 21.6, 14.7, 21.1, 15.4, 21.8),
          (20.8, 27.9, 23.5, 35.2, 22.1, 44.4)]),
    curve((28.3, 44.1), [(30.2, 36.6, 34.2, 30.7, 39.2, 27.1),
          (39.9, 26.5, 40.4, 26.9, 39.8, 27.6),
          (35.8, 33.4, 34.1, 38.4, 32.2, 44.4)]),
]
# Open .5 mm node cuts distinguish the cane segments at actual print scale.
nodes = [((24.5, 36.8), (28.9, 37.5)), ((26.3, 28.1), (30.4, 29.1)),
         ((28.6, 20.2), (33, 21.6)), ((18.4, 36.5), (23.2, 36.1)),
         ((16.7, 29.4), (20.5, 27.9)), ((30, 37.2), (35.1, 39.5))]
stalks = union_all(stems).difference(union_all([
    LineString([a,b]).buffer(.25, cap_style='round') for a,b in nodes]))
leaves = [
    curve((29.2, 25.3), [(21, 24.2, 21.1, 14.8, 8.2, 12.3),
          (18.4, 11.2, 28.9, 16.1, 29.2, 25.3)]),
    curve((28.5, 28.1), [(31.5, 17.6, 42.1, 13.5, 47.7, 18.1),
          (40.1, 16.6, 38.9, 24.3, 28.5, 28.1)]),
    curve((20.4, 33.8), [(10.5, 31.7, 10.6, 25, 4.8, 22.8),
          (13.3, 21.8, 20.3, 27.4, 20.4, 33.8)]),
    curve((34, 36.8), [(35.1, 29.4, 41.6, 26.2, 48, 26.8),
          (42.4, 29.1, 42.2, 35.1, 34, 36.8)]),
]
# Sweeping negative-space veins reinforce the gesture of each blade.
veins = [
    curve((26.8, 22.6), [(24.1, 18.4, 18.7, 15.4, 14.5, 14.1),
          (19.6, 16.9, 24.2, 19.7, 26.8, 22.6)]),
    curve((31.6, 25.1), [(35.7, 20.3, 41, 17.4, 45.4, 17.8),
          (40.4, 18.4, 37.3, 21.5, 31.6, 25.1)]),
    curve((18.1, 30.9), [(15.7, 27.2, 11.1, 25, 7.3, 23.6),
          (10.4, 25.7, 14.5, 28.7, 18.1, 30.9)]),
    curve((36.9, 33.9), [(38.6, 30.4, 42.2, 28.2, 45.3, 27.5),
          (42.2, 29, 40.8, 31.5, 36.9, 33.9)]),
]
# One brush-like sweep gathers the stems, with open ends rather than a frame.
root = curve((10.6, 42.6), [(20.5, 45.2, 35.8, 44.7, 45.8, 38.8),
             (39, 46.7, 21, 49.3, 10.6, 42.6)])
art = union_all([word, stalks, union_all(leaves).difference(union_all(veins)), root])
assert art.is_valid


def pieces(geometry):
    if geometry.is_empty:
        return []
    if geometry.geom_type == 'Polygon':
        return [geometry]
    return [p for g in getattr(geometry, 'geoms', []) for p in pieces(g)]


svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="52mm" height="74mm" viewBox="0 0 52 74">',
       '<title>sugarCANe — flowing cane and smooth wordmark</title>',
       '<desc>Underside reading orientation. Original sweeping three-stalk cane illustration; Outfit weight 550 and ExtraBold outlined lettering. Only the product name is text. No border.</desc>',
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

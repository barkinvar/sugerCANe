"""Build the original sugarCANe pixel poster as font-independent SVG geometry."""
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.recordingPen import RecordingPen
from shapely.geometry import Polygon, box, GeometryCollection
from shapely import affinity, union_all

R=Path(__file__).resolve().parents[1]
OUT=R/'hardware/artwork';OUT.mkdir(exist_ok=True)
font_path=R/'sources/fonts/PixelifySans.ttf'
font=instantiateVariableFont(TTFont(font_path),{'wght':700})
glyphs=font.getGlyphSet();cmap=font.getBestCmap()
word=[];cursor=0
for letter in 'sugarCANe':
    glyph=glyphs[cmap[ord(letter)]];pen=RecordingPen();glyph.draw(pen)
    shape=GeometryCollection();contour=[]
    for op,args in pen.value:
        if op in ('moveTo','lineTo'):
            # Pixel-font outlines contain tiny interpolation offsets. Snap to
            # whole font units, far below a printable feature at this scale.
            contour.append((round(args[0][0])+cursor,-round(args[0][1])))
        elif op=='closePath':
            shape=shape.symmetric_difference(Polygon(contour));contour=[]
        else:raise ValueError(('Unexpected curved glyph',op))
    word.append(shape);cursor+=glyph.width+12
word=union_all(word);x0,y0,x1,y1=word.bounds
scale=45.2/(x1-x0)
word=affinity.translate(affinity.scale(word,scale,scale,origin=(x0,y0)),2.9-x0,49.3-y0)

# Three jointed stalks: the three sensor inputs, with stair-step leaves and
# a floating block of soil. All original artwork, on a 0.8 mm pixel grid.
cane=[]
def rect(x,y,w,h):cane.append(box(x,y,x+w,y+h))
def leaf(x,y,dx,dy,count):
    for i in range(count):rect(x+dx*i,y+dy*i,2 if i<count-1 else 1,2 if i<count-1 else 1)
for x,top in [(7,11),(17,1),(28,7)]:
    rect(x,top,3,36-top)
    for y in range(top+7,35,9):rect(x-1,y,5,1)
leaf(6,15,-1,-1,7);leaf(9,21,1,-1,5)
leaf(16,8,-1,-1,7);leaf(19,13,1,-1,8)
leaf(30,16,1,-1,7);leaf(27,25,-1,-1,6)
plant=union_all(cane)
slots=[]
for x,top in [(7,11),(17,1),(28,7)]:
    for y in range(top+2,34,9):slots.append(box(x+1,y,x+2,min(y+4,35)))
plant=plant.difference(union_all(slots))
soil=union_all([box(4,36,34,38),box(6,38,32,39),box(9,39,29,40)])
soil=soil.difference(union_all([box(x,y,x+1,y+1) for x,y in [(7,37),(12,36),(18,38),(23,36),(29,37)]]))
plant=union_all([plant,soil])
plant=affinity.translate(affinity.scale(plant,.8,.8,origin=(0,0)),10.4,12.1)

# Sparse pixels and open corners make a poster composition without enclosing
# the circuitry in a heavy white border. No secondary lettering is present.
accents=[]
for x,y,s in [(6.2,19.3,.8),(43.2,16.1,.8),(44.8,18.5,.8),(5.4,32.1,.8),(44,36.1,1.6),(7.8,39.3,.8),(39.2,11.3,.8)]:
    accents.append(box(x,y,x+s,y+s))
for x,dx in [(3.2,1),(48.8,-1)]:
    for y,dy in [(12.1,1),(58.5,-1)]:
        accents.extend([box(min(x,x+dx*4),min(y,y+dy*.6),max(x,x+dx*4),max(y,y+dy*.6)),
                        box(min(x,x+dx*.6),min(y,y+dy*4),max(x,x+dx*.6),max(y,y+dy*4))])
art=union_all([word,plant,*accents])

def pieces(g):
    if g.is_empty:return []
    if g.geom_type=='Polygon':return [g]
    return [p for q in getattr(g,'geoms',[]) for p in pieces(q)]

svg=['<svg xmlns="http://www.w3.org/2000/svg" width="52mm" height="74mm" viewBox="0 0 52 74">',
     '<title>sugarCANe — original pixel cane poster</title>',
     '<desc>Bottom-side reading orientation. Pixelify Sans Bold outlined lettering; original three-stalk pixel illustration. Only the product name is text.</desc>',
     '<g fill="#ffffff" fill-rule="evenodd">']
for poly in pieces(art):
    contours=[]
    for ring in [poly.exterior,*poly.interiors]:
        coords=list(ring.coords)[:-1]
        contours.append('M '+' L '.join(f'{x:.6f},{y:.6f}' for x,y in coords)+' Z')
    svg.append('<path d="'+' '.join(contours)+'"/>')
svg+=['</g>','</svg>']
(OUT/'sugarCANe.svg').write_text('\n'.join(svg)+'\n')
print('Wrote sugarCANe poster:',len(pieces(art)),'filled paths; ink bounds',art.bounds)

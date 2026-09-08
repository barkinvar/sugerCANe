#!/usr/bin/env python3
"""Strict Specctra SES geometry reader for the local two-layer routing workflow.
KiCad's Python importer returns False on this SES; keep placement fixed and read
only explicitly supported paths/vias. DRC and netlist parity are separate checks.
"""
from pathlib import Path
import json,re,sys
import sexpdata
ROOT=Path(__file__).resolve().parents[1]
src=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'hardware/design/routed.ses'
out=src.with_suffix('.routes.json')
r=sexpdata.loads(src.read_text())
def tag(v):return str(v[0]) if isinstance(v,list) and v else ''
def children(v,k):return [a for a in v[1:] if tag(a)==k]
def child(v,k):
 a=children(v,k);assert len(a)==1,(k,len(a));return a[0]
assert tag(r)=='session'
routes=child(r,'routes');res=child(routes,'resolution');assert str(res[1])=='um'
scale=float(res[2])*1000
positions=[]
placement=child(r,'placement')
assert float(child(placement,'resolution')[2])==float(res[2])
for comp in children(placement,'component'):
 for place in children(comp,'place'):
  assert str(place[4])=='front',place
  positions.append({'ref':str(place[1]),'xy':[float(place[2])/scale,-float(place[3])/scale],'angle':float(place[5])})
via_types={}
for pad in children(child(routes,'library_out'),'padstack'):
 name=str(pad[1]);m=re.fullmatch(r'Via\[0-1\]_(\d+):(\d+)_um',name);assert m,name
 shapes=children(pad,'shape');assert len(shapes)==2
 diams=[]
 for shape in shapes:
  circ=child(shape,'circle');assert str(circ[1]) in ['F.Cu','B.Cu'];assert float(circ[3])==float(circ[4])==0
  diams.append(float(circ[2])/scale)
 assert abs(diams[0]-diams[1])<1e-8
 assert abs(diams[0]-float(m[1])/1000)<1e-8
 via_types[name]={'diameter':diams[0],'drill':float(m[2])/1000}
tracks=[];vias=[];netnames=[]
for net in children(child(routes,'network_out'),'net'):
 name=str(net[1]);netnames.append(name)
 for item in net[2:]:
  if tag(item)=='wire':
   path=child(item,'path');layer=str(path[1]);assert layer in ['F.Cu','B.Cu']
   coords=list(map(float,path[3:]));assert len(coords)%2==0 and len(coords)>=4
   pts=[[coords[i]/scale,-coords[i+1]/scale] for i in range(0,len(coords),2)]
   tracks.append({'net':name,'width':float(path[2])/scale,'layer':layer,'points':pts})
  elif tag(item)=='via':
   namevia=str(item[1]);assert namevia in via_types
   vias.append({'net':name,'xy':[float(item[2])/scale,-float(item[3])/scale],**via_types[namevia]})
  else:raise ValueError(f'Unsupported SES network item {tag(item)}')
report={'source':str(src),'coordinate_resolution':str(res),'placement':positions,'nets':netnames,'tracks':tracks,'vias':vias}
out.write_text(json.dumps(report,indent=2)+'\n')
print(f'{len(tracks)} polylines, {len(vias)} vias, {len(positions)} unchanged placement records -> {out}')

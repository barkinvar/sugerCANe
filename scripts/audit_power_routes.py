#!/usr/bin/env python3
"""Conservative single-path trace resistance from actual PCB geometry, no plane solver.
Run with kicad-python. SMD/PTH pad copper is lumped, via barrels use20um plating.
"""
from pathlib import Path
import pcbnew as p
import json,math,heapq
ROOT=Path(__file__).resolve().parents[1];b=p.LoadBoard(str(ROOT/'hardware/FRC_Sensor_CAN.kicad_pcb'))
fs={f.GetReference():f for f in b.GetFootprints()}
COPPER_RHO=1.724e-5*(1+.00393*(85-20)) # ohm.mm at85C
THICKNESS=.035
REPORT={'scope':'Single conducting route, 35um copper at85C, 20um via plating; pad copper lumped. Parallel paths can reduce resistance. This is not IPC thermal qualification or a ground-plane field solution.','routes':[]}
def xy(v):return tuple(p.ToMM(v))
def key(point,layer):return (round(point[0],6),round(point[1],6),layer)
def measure(net,source,destination):
 tracks=[t for t in b.GetTracks() if t.GetNetname()==net]
 pads=[(f.GetReference(),z) for f in b.GetFootprints() for z in f.Pads() if z.GetNetname()==net]
 nodes={};graph={};padnodes={}
 def node(pos,layer):
  k=key(pos,layer)
  if k not in nodes:nodes[k]=len(nodes);graph[nodes[k]]=[]
  return nodes[k]
 def edge(a,c,r,length=0,width=None):graph[a].append((c,r,length,width));graph[c].append((a,r,length,width))
 for t in tracks:
  if isinstance(t,p.PCB_VIA):
   pos=xy(t.GetPosition());a=node(pos,p.F_Cu);c=node(pos,p.B_Cu)
   edge(a,c,COPPER_RHO*1.6/(math.pi*p.ToMM(t.GetDrillValue())*.020))
  else:node(xy(t.GetStart()),t.GetLayer());node(xy(t.GetEnd()),t.GetLayer())
 for ref,pad in pads:
  pos=xy(pad.GetPosition());ids=[]
  for layer in [p.F_Cu,p.B_Cu]:
   if pad.IsOnLayer(layer):ids.append(node(pos,layer))
  padnodes[(ref,pad.GetNumber())]=ids[0]
  for other in ids[1:]:edge(ids[0],other,0)
 for t in tracks:
  if isinstance(t,p.PCB_VIA):continue
  a=xy(t.GetStart());z=xy(t.GetEnd());dx=z[0]-a[0];dy=z[1]-a[1];length=math.hypot(dx,dy);width=p.ToMM(t.GetWidth())
  points=[]
  for (x,y,layer),idx in nodes.items():
   if layer!=t.GetLayer():continue
   u=((x-a[0])*dx+(y-a[1])*dy)/(length*length)
   if -.000001<=u<=1.000001 and abs((x-a[0])*dy-(y-a[1])*dx)/length<=width/2+1e-6:points.append((max(0,min(1,u)),idx))
  points.sort()
  for (ua,ia),(uc,ic) in zip(points,points[1:]):
   segment=(uc-ua)*length;edge(ia,ic,COPPER_RHO*segment/(width*THICKNESS),segment,width)
 for ref,pad in pads:
  center=padnodes[(ref,pad.GetNumber())]
  for (x,y,layer),idx in nodes.items():
   if pad.IsOnLayer(layer) and pad.HitTest(p.VECTOR2I(p.FromMM(x),p.FromMM(y))):edge(center,idx,0)
 start=padnodes[source];end=padnodes[destination];queue=[(0,start)];dist={start:0};previous={}
 while queue:
  resistance,n=heapq.heappop(queue)
  if resistance!=dist[n]:continue
  if n==end:break
  for dest,r,l,w in graph[n]:
   new=resistance+r
   if new<dist.get(dest,float('inf')):dist[dest]=new;previous[dest]=(n,l,w);heapq.heappush(queue,(new,dest))
 assert end in dist,(net,source,destination,'No route found in approximate graph')
 n=end;length=0;widths=[]
 while n!=start:
  n,l,w=previous[n];length+=l
  if w is not None:widths.append(w)
 result={'net':net,'source':'.'.join(source),'destination':'.'.join(destination),'trace_length_mm':length,'minimum_trace_width_mm':min(widths),'single_path_resistance_at85C_ohm':dist[end]}
 REPORT['routes'].append(result);return dist[end]
upstream=measure('V5_INTERNAL',('L1','2'),('U4','1'))
ports=[]
for ch in range(1,5):
 z=ch*100
 v5=measure('SENSOR_5V',('U4','6'),(f'JP{z+1}','1'))
 bat=measure('SENSOR_VBAT',('U3','7'),(f'JP{z+1}','3'))
 port=measure(f'VPORT{ch}',(f'JP{z+1}','2'),(f'J{ch+3}','1'))
 low=json.loads((ROOT/'reports/electrical/calculations.json').read_text())['buck']['dc_reference_and_divider_only_V'][0]
 vmin=low-.46*upstream-.31*(.135+v5+port+.060)
 assert vmin>4.8,(ch,vmin)
 ports.append({'channel':ch,'full_300mA_at_this_port_minimum_5V_budget_V':vmin,
 'voltage_budget_assumptions':'135mohm TPS2553 hot maximum;60mohm additional allowance for connector, shunt and ground return;0.46A upstream5V load;all0.3A sensor current plus0.01A bias/bleed allowance conservatively placed at this one port.'})
REPORT['5V_port_budgets']=ports
(ROOT/'reports/electrical/power_routes.json').write_text(json.dumps(REPORT,indent=2)+'\n')
print(json.dumps(REPORT,indent=2))

"""Estimate DC ground return resistance from the exported copper geometry.

This is a square-grid resistor-sheet approximation, not a certified PCB field
solver. Copper is35um at85C. Pad contacts are equipotential, plated barrels20um.
Run two mesh sizes and inspect convergence; no AC/thermal/EMC claim is made.
"""
from pathlib import Path
import sys, json, time, math, hashlib
import numpy as np
from scipy import sparse
from scipy.sparse.csgraph import connected_components
from scipy.sparse.linalg import spsolve
from shapely import union_all, contains_xy
import pyamg
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import verify_gerber_connectivity as geom
from gerbonara.graphic_objects import Flash
OUT=ROOT/'reports/electrical';OUT.mkdir(exist_ok=True)
RHO=1.724e-5*(1+.00393*(85-20)) # ohm.mm
SHEET_R=RHO/.035
GROUND={side:union_all([poly for i,poly in enumerate(polys)
                        if geom.root_nets[geom.root(geom.offset[side]+i)]=={'GND'}])
        for side,polys in geom.islands.items()}
PADS={}
for side,layer in geom.layers.items():
    for obj in layer.objects:
        if isinstance(obj,Flash) and '.P' in obj.attrs and obj.attrs.get('.N')==('GND',):
            ref,pin,*_=obj.attrs['.P']
            PADS[(side,ref+'.'+pin)]=union_all([geom.shape(p) for p in obj.to_primitives()])
CONTACTS=['J1.2','J4.2','J5.2','J6.2','J7.2','C4.2']
SAMPLES=['U7.12','U5.16','U5.32','R24.2','R26.2','R107.2','R207.2','R307.2','R407.2']

def laplacian(n,a,b,g):
    good=a!=b;a,b,g=a[good],b[good],g[good]
    return sparse.coo_matrix((np.concatenate([g,g,-g,-g]),
                              (np.concatenate([a,b,a,b]),np.concatenate([a,b,b,a]))),
                             shape=(n,n)).tocsr()

# Analytic calibration: rectangular sheet, full-width electrodes at each end.
nx,ny=20,10
grid=np.arange(nx*ny).reshape(ny,nx)
a=np.concatenate([grid[:,:-1].ravel(),grid[:-1,:].ravel()])
b=np.concatenate([grid[:,1:].ravel(),grid[1:,:].ravel()])
A=laplacian(nx*ny,a,b,np.ones(len(a)))
fixed=np.concatenate([grid[:,0],grid[:,-1]])
free=np.setdiff1d(np.arange(nx*ny),fixed)
v=np.zeros(nx*ny);v[grid[:,0]]=1
v[free]=spsolve(A[free,:][:,free],-(A[free,:]@v))
current=(A@v)[grid[:,0]].sum();calibration=1/current
assert abs(calibration-(nx-1)/ny)<1e-10
print('Analytic rectangular-sheet calibration PASS:',calibration,'squares',flush=True)

def run(pitch):
    start=time.monotonic();n=round(96/pitch);axis=(np.arange(n)+.5)*pitch
    X,Y=np.meshgrid(axis,-axis)
    ids={};count=0
    for side in ('top','bottom'):
        mask=contains_xy(GROUND[side],X,Y)
        idx=np.full((n,n),-1,dtype=np.int32);idx[mask]=np.arange(count,count+mask.sum())
        ids[side]=idx;count+=int(mask.sum())
    parent=np.arange(count,dtype=np.int32)
    def root(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return int(i)
    def pool(indices):
        values=np.unique(indices[indices>=0]);assert len(values)
        base=root(values[0])
        for i in values[1:]:parent[root(i)]=base
        return base
    def in_shape(side,poly):
        xmin,ymin,xmax,ymax=poly.bounds
        x0=max(0,int(xmin/pitch)-1);x1=min(n,int(xmax/pitch)+2)
        y0=max(0,int(-ymax/pitch)-1);y1=min(n,int(-ymin/pitch)+2)
        mask=contains_xy(poly,X[y0:y1,x0:x1],Y[y0:y1,x0:x1])
        return ids[side][y0:y1,x0:x1][mask]
    contact={name:pool(in_shape('top',PADS[('top',name)])) for name in CONTACTS}
    # Collect pad copper close to each ground barrel into a local contact.
    vias=[]
    for drill in geom.drills:
        if geom.root_nets[geom.root(geom.at('top',drill.x,drill.y))]!={'GND'}:continue
        from shapely.geometry import Point
        diameter=drill.aperture.diameter
        disk=Point(drill.x,drill.y).buffer(diameter/2+.075)
        top=pool(in_shape('top',disk));bottom=pool(in_shape('bottom',disk))
        resistance=RHO*1.6/(math.pi*diameter*.020)
        vias.append((top,bottom,1/resistance))
    while not np.array_equal(parent,parent[parent]):parent=parent[parent]
    _,remap=np.unique(parent,return_inverse=True);nodes=int(remap.max()+1)
    edges_a=[];edges_b=[];conduct=[]
    for side,idx in ids.items():
        for u,v in [(idx[:,:-1],idx[:,1:]),(idx[:-1,:],idx[1:,:])]:
            valid=(u>=0)&(v>=0)
            edges_a.append(remap[u[valid]]);edges_b.append(remap[v[valid]])
            conduct.append(np.full(valid.sum(),1/SHEET_R))
    edges_a.append(np.array([remap[a] for a,b,g in vias]))
    edges_b.append(np.array([remap[b] for a,b,g in vias]))
    conduct.append(np.array([g for a,b,g in vias]))
    A=laplacian(nodes,np.concatenate(edges_a),np.concatenate(edges_b),np.concatenate(conduct))
    contacts={name:int(remap[idx]) for name,idx in contact.items()}
    components,labels=connected_components(A,directed=False)
    selected=labels==labels[contacts['J1.2']]
    assert all(selected[i] for i in contacts.values()),'Grid missed a required copper path'
    omitted=int((~selected).sum())
    selected[contacts['J1.2']]=False # ground reference
    active=np.flatnonzero(selected)
    reduce_map=np.full(nodes,-1,dtype=np.int32);reduce_map[active]=np.arange(len(active))
    reduced=A[active,:][:,active]
    print(f'{pitch}mm grid: {count} cells, {len(active)} unknowns, {len(vias)} ground barrels; building AMG',flush=True)
    solver=pyamg.ruge_stuben_solver(reduced)
    solutions={};residuals={}
    for name in CONTACTS[1:]:
        rhs=np.zeros(len(active));rhs[reduce_map[contacts[name]]]=1
        history=[];voltage=solver.solve(rhs,tol=1e-10,maxiter=200,accel='cg',residuals=history)
        residual=float(np.linalg.norm(reduced@voltage-rhs));assert residual<1e-7,(name,residual)
        full=np.zeros(nodes);full[active]=voltage;solutions[name]=full;residuals[name]=residual
        print(f'  {name} to J1.2: {full[contacts[name]]*1000:.5f}mohm, residual {residual:.2g}',flush=True)
    cap='C4.2';routes=[]
    for port in CONTACTS[1:5]:
        self_r=solutions[port][contacts[port]]
        mutual=solutions[port][contacts[cap]]
        assert abs(mutual-solutions[cap][contacts[port]])<1e-7,'Reciprocity failed'
        to_cap=self_r+solutions[cap][contacts[cap]]-2*mutual
        routes.append(dict(port=port,to_input_ground_ohm=float(self_r),to_buck_cap_ground_ohm=float(to_cap)))
    worst=max(routes,key=lambda r:r['to_buck_cap_ground_ohm'])['port']
    field=.31*(solutions[worst]-solutions[cap])
    contact_ref=field[contacts[cap]]
    fig,axes=plt.subplots(1,2,figsize=(11,5),constrained_layout=True)
    lo,hi=np.inf,-np.inf;images=[]
    for ax,side in zip(axes,['top','bottom']):
        idx=ids[side];mask=idx>=0;view=np.full((n,n),np.nan)
        view[mask]=(field[remap[idx[mask]]]-contact_ref)*1000
        im=ax.imshow(view,extent=(0,96,96,0),cmap='viridis',interpolation='nearest')
        ax.set(title=side+' copper',xlabel='Board X (mm)',ylabel='Board Y (mm)')
        images.append(im);lo=min(lo,np.nanmin(view));hi=max(hi,np.nanmax(view))
    for im in images:im.set_clim(lo,hi)
    fig.colorbar(images[0],ax=axes,label='Estimated ground voltage relative to C4.2 (mV)')
    fig.suptitle(f'DC ground sheet estimate: 310mA at {worst}, return at C4.2; mesh {pitch}mm')
    fig.savefig(OUT/f'ground_return_{pitch:g}mm.png',dpi=180);plt.close(fig)
    samples={}
    for name in SAMPLES:
        indices=in_shape('top',PADS[('top',name)]);indices=indices[indices>=0]
        samples[name]=float(np.mean(field[remap[indices]])-contact_ref)*1000
    return dict(mesh_mm=pitch,grid_cells=count,solved_nodes=len(active),omitted_disconnected_grid_nodes=omitted,
                ground_barrels=len(vias),routes=routes,residual_norms=residuals,
                worst_5v_return_port=worst,estimated_ground_samples_mV_at_310mA=samples,
                elapsed_seconds=time.monotonic()-start)

meshes=[float(v) for v in sys.argv[1:]] or [.15,.10]
results=[run(pitch) for pitch in meshes]
report=dict(method='Gerber copper polygons, center-sampled square-grid resistor sheets; PyAMG5.3.0',
            assumptions=dict(copper_thickness_mm=.035,copper_temperature_C=85,copper_resistivity_ohm_mm=RHO,
                             board_thickness_mm=1.6,barrel_plating_mm=.020,equipotential_top_pad_contacts=True),
            analytic_sheet_calibration_squares=calibration,results=results,
            limitations='Grid boundaries and equipotential contacts approximate actual geometry. Filled pad interiors omit hole voids. DC only: no inductance, ground bounce, contact resistance, thermal rise, manufacturing tolerance or EMI model. Mesh convergence is a numerical sensitivity check, not hardware validation.')
if len(results)>1:
    report['maximum_route_change_fraction']=max(abs(a[key]-b[key])/b[key]
        for a,b in zip(results[-2]['routes'],results[-1]['routes'])
        for key in ['to_input_ground_ohm','to_buck_cap_ground_ohm'])
report['sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'output/fabrication').glob('*')) if p.suffix in ('.gbr','.gtl','.gbl','.gts','.gbs','.gtp','.gbp','.gto','.gbo','.gm1','.drl')}
(OUT/'ground_return_model.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))

"""Create a shareable original block diagram of the implemented revision."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/documentation'
fig,ax=plt.subplots(figsize=(12,8));fig.patch.set_facecolor('white');ax.set(xlim=(0,12),ylim=(0,8));ax.axis('off')
ink='#173348';power='#ad5426';signal='#126a83';muted='#536b79'
def box(x,y,w,h,title,detail,kind='signal'):
    color=power if kind=='power' else signal
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.02,rounding_size=0.09',linewidth=1.4,edgecolor=color,facecolor='#fff7f0' if kind=='power' else '#f0f7f9'))
    ax.text(x+w/2,y+h*.70,title,ha='center',va='center',fontsize=10.5,fontweight='bold',color=ink)
    ax.text(x+w/2,y+h*.31,detail,ha='center',va='center',fontsize=8.3,color=muted,linespacing=1.4)
def route(points,color=signal,label=None,at=None):
    for a,b in zip(points[:-2],points[1:-1]):ax.plot([a[0],b[0]],[a[1],b[1]],color=color,lw=1.5)
    ax.add_patch(FancyArrowPatch(points[-2],points[-1],arrowstyle='-|>',mutation_scale=11,lw=1.5,color=color))
    if label:ax.text(*at,label,ha='center',va='center',fontsize=8,color=color,bbox=dict(facecolor='white',edgecolor='none',pad=2))
ax.text(.15,7.7,'FRC SENSOR CAN',fontsize=23,fontweight='bold',color=ink)
ax.text(.15,7.32,'Revision A prototype  •  Original four-channel sensor interface',fontsize=11,color=muted)
box(.15,5.95,2.15,1,'FRC battery input','J1 · 6–18 V target\nProtected distribution branch','power')
box(2.85,5.95,2.55,1,'Input protection','F1 · Q1 · D2\nFuse / reverse polarity / TVS','power')
box(6.0,5.95,2.4,1,'Battery sensor switch','U3 TPS1H200A\nCurrent limit + hardware latch','power')
route([(2.3,6.45),(2.85,6.45)],power)
route([(5.4,6.45),(6,6.45)],power)
box(2.85,4.3,2.55,1,'5 V buck supply','U1 LMR51420X\n5.023 V nominal internally','power')
box(6,4.3,2.4,1,'5 V sensor switch','U4 TPS2553-1\nCurrent limit + hardware latch','power')
route([(4.125,5.95),(4.125,5.3)],power)
route([(5.4,4.8),(6,4.8)],power)
box(9.15,4.3,2.55,1,'Power selectors','Battery OR 5 V per port\n300 mA per rail, shared total','power')
route([(8.4,6.45),(10.425,6.45),(10.425,5.3)],power,'Follows battery',(10.425,5.85))
route([(8.4,4.8),(9.15,4.8)],power)
box(2.85,2.65,2.55,1,'3.3 V logic supply','U2 AP2112\nMCU / CAN / input pull-ups','power')
route([(4.125,4.3),(4.125,3.65)],power)
box(9.15,2.65,2.55,1,'J4–J7 sensor ports','POWER · GND · SIGNAL\nThree-wire DC sensors','power')
route([(10.425,4.3),(10.425,3.65)],power)
box(8.1,.9,3.6,1.1,'Four digital front ends','30 V TVS · divider · LM2901B\nIndustrial / 3.3–5 V thresholds')
route([(10.425,2.65),(10.425,2)],signal)
box(4.0,.9,3.35,1.1,'STM32F042K6 controller','1 kHz sampling · debounce · counts\nWatchdog · rail control / monitoring')
route([(8.1,1.45),(7.35,1.45)],signal)
route([(4.125,2.65),(4.125,2.32),(5.675,2.32),(5.675,2)],power)
box(.15,.9,3.05,1.1,'TCAN3413 transceiver','1 Mbit/s Classical CAN\nJ2 / J3 H–L daisy chain')
route([(4,1.45),(3.2,1.45)],signal,'CAN',(3.6,1.67))
ax.text(.15,4.45,'Both rail switches:\nMCU enable control\nSwitched-voltage sensing\nManual fault recovery',fontsize=9,color=ink,linespacing=1.6)
ax.text(.15,3.0,'All blocks share ground.\nControl wires omitted\nfor clarity.',fontsize=8.5,color=muted,linespacing=1.5)
ax.text(.15,.53,'Unconfigured: rails OFF / CAN standby. UART + SWD service access. Terminate CAN only at a trunk end.',fontsize=9.1,color=ink)
ax.text(.15,.14,'No voltage boost • No 1.8 V guarantee • Custom protocol; no Phoenix emulation • Physical qualification pending',fontsize=9,color=muted)
fig.subplots_adjust(left=.025,right=.985,bottom=.025,top=.98)
for ext in ['svg','pdf','png']:fig.savefig(OUT/f'architecture.{ext}',dpi=180,facecolor='white')
print('Architecture diagram written in SVG, PDF and PNG.')

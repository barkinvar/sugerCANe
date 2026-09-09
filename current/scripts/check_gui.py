import sys,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0,str(ROOT/'host'))
import tkinter as tk
from service_gui import App
from input_settings import pack_settings,unpack_settings
from PIL import ImageGrab
root=tk.Tk();app=App(root);root.update()
uid='000000000000000000000001'
info=dict(uid=uid,mode='application',version='0.8.0',configured=True,device_id=17,invert=0,debounce=2,**unpack_settings(pack_settings(['npn','pnp','push-pull'])))
app.nodes[uid]=info;app.table.insert('','end',iid=uid,text=uid,values=(17,'application','0.8.0'));app.table.selection_set(uid);app.selected();root.update()
assert [v.get() for v in app.input_modes]==['npn','pnp','push-pull']
assert [v.get() for v in app.input_active]==['low','high','high']
class Fake:
 def power_reset(self,uid):self.reset_uid=uid;return info
 def configure(self,*args):self.args=args;return info
fake=Fake();app.work=lambda fn:fn(fake);app.configure();assert fake.args[4:]==(['npn','pnp','push-pull'],['low','high','high'])
app.power_reset();assert fake.reset_uid==uid
app.status.set('Setup preview with simulated device data. No physical device connected.');root.update()
x,y=root.winfo_rootx(),root.winfo_rooty();ImageGrab.grab().crop((x,y,x+root.winfo_width(),y+root.winfo_height())).save('output/review/service_gui.png')
root.destroy();print('PASS GUI: per-channel selection, polarity defaults, configure argument capture; simulated screenshot')

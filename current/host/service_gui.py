"""SC12 desktop commissioning. Python with Tk; no browser or USB connector required."""
import json
import queue
import threading
import tkinter as tk
from pathlib import Path
from tkinter import ttk, filedialog, messagebox
from input_settings import MODES, ACTIVE, DEFAULT_ACTIVE
from can_service import Client, TcpBridge, SocketCan, BLINK

class App:
    def __init__(self, root):
        self.root=root;root.title('SC12 setup and firmware');root.geometry('820x720')
        self.events=queue.Queue();self.busy=False;self.nodes={}
        area=ttk.Frame(root,padding=16);area.pack(fill='both',expand=True)
        ttk.Label(area,text='SC12 setup and firmware',font=('',18,'bold')).pack(anchor='w')
        ttk.Label(area,text='Keep the robot disabled and maintenance mode enabled. Measurements pause during service.').pack(anchor='w',pady=(6,14))
        row=ttk.Frame(area);row.pack(fill='x');self.kind=tk.StringVar(value='Robot tunnel');self.address=tk.StringVar(value='localhost:5810')
        ttk.Combobox(row,textvariable=self.kind,values=('Robot tunnel','SocketCAN'),state='readonly',width=15).pack(side='left')
        ttk.Entry(row,textvariable=self.address,width=30).pack(side='left',padx=8)
        self.buttons=[];self.button(row,'Discover',self.discover).pack(side='left')
        self.table=ttk.Treeview(area,columns=('id','mode','version'),height=8)
        self.table.heading('#0',text='Permanent serial');self.table.column('#0',width=290)
        for col,title in [('id','CAN ID'),('mode','Mode'),('version','Version')]:self.table.heading(col,text=title);self.table.column(col,width=110)
        self.table.pack(fill='both',expand=True,pady=14);self.table.bind('<<TreeviewSelect>>',self.selected)
        row=ttk.Frame(area);row.pack(fill='x');self.fields={}
        for name,default in [('CAN ID','0'),('Invert mask','0'),('Debounce ms','2')]:
            ttk.Label(row,text=name).pack(side='left');v=tk.StringVar(value=default);self.fields[name]=v;ttk.Entry(row,textvariable=v,width=5).pack(side='left',padx=(4,12))
        self.input_modes=[];self.input_active=[]
        for i in range(3):
            row=ttk.Frame(area);row.pack(fill='x',pady=3)
            ttk.Label(row,text=f'Input {i+1}',width=10).pack(side='left')
            m=tk.StringVar(value=MODES[0]);a=tk.StringVar(value=ACTIVE[0])
            self.input_modes.append(m);self.input_active.append(a)
            box=ttk.Combobox(row,textvariable=m,values=MODES,state='readonly',width=14)
            box.pack(side='left',padx=6)
            box.bind('<<ComboboxSelected>>',lambda _,m=m,a=a:a.set(DEFAULT_ACTIVE[MODES.index(m.get())]))
            ttk.Label(row,text='Active when').pack(side='left',padx=6)
            ttk.Combobox(row,textvariable=a,values=ACTIVE,state='readonly',width=14).pack(side='left')
        row=ttk.Frame(area);row.pack(fill='x',pady=12)
        for label,callback in [('Blink',self.blink),('Save and verify',self.configure),('Update firmware…',self.update)]:self.button(row,label,callback).pack(side='left',padx=(0,8))
        self.progress=ttk.Progressbar(area,maximum=100);self.progress.pack(fill='x')
        self.status=tk.StringVar(value='Open an SSH tunnel for the robot connection, then discover devices.')
        ttk.Label(area,textvariable=self.status,wraplength=760).pack(anchor='w',pady=8)
        root.after(50,self.poll);root.protocol('WM_DELETE_WINDOW',self.close)
    def button(self,parent,label,callback):
        b=ttk.Button(parent,text=label,command=callback);self.buttons.append(b);return b
    def uid(self):
        selection=self.table.selection()
        if not selection:raise ValueError('Select a device first')
        return selection[0]
    def selected(self,_=None):
        if not self.table.selection():return
        info=self.nodes[self.uid()]
        for field,key in [('CAN ID','device_id'),('Invert mask','invert'),('Debounce ms','debounce')]:self.fields[field].set(str(info[key] if info[key]!=255 else 0))
        for i in range(3):
            self.input_modes[i].set(info['modes'][i]);self.input_active[i].set(info['active'][i])
    def work(self, operation):
        if self.busy:return
        self.busy=True;self.status.set('Working…');self.progress['value']=0
        for b in self.buttons:b.state(['disabled'])
        kind,address=self.kind.get(),self.address.get()
        def worker():
            client=None
            try:
                transport=TcpBridge(address) if kind=='Robot tunnel' else SocketCan('socketcan',address)
                client=Client(transport);client.open();result=operation(client);self.events.put(('done',result))
            except Exception as error:self.events.put(('error',str(error)))
            finally:
                if client:client.close()
        threading.Thread(target=worker,daemon=True).start()
    def discover(self):self.work(lambda c:c.discover())
    def blink(self):
        try:uid=self.uid()
        except ValueError as e:messagebox.showerror('Select device',str(e));return
        def operation(c):c.select(uid);c.request(BLINK);return c.info()
        self.work(operation)
    def configure(self):
        try:uid=self.uid();values=[int(v.get()) for v in self.fields.values()]
        except ValueError as e:messagebox.showerror('Check settings',str(e));return
        modes=[v.get() for v in self.input_modes];active=[v.get() for v in self.input_active]
        self.work(lambda c:c.configure(uid,*values,modes,active))
    def update(self):
        try:uid=self.uid()
        except ValueError as e:messagebox.showerror('Select device',str(e));return
        path=filedialog.askopenfilename(title='Select SC12 application',filetypes=[('SC12 firmware','*.sc12')])
        if not path:return
        try:raw=Path(path).read_bytes()
        except OSError as e:messagebox.showerror('Cannot read firmware',str(e));return
        self.work(lambda c:c.update(uid,raw,lambda p:self.events.put(('progress',p))))
    def poll(self):
        try:
            while True:
                kind,data=self.events.get_nowait()
                if kind=='progress':self.progress['value']=data*100;continue
                self.busy=False
                for b in self.buttons:b.state(['!disabled'])
                if kind=='error':self.status.set('Failed: '+data);continue
                if isinstance(data,list):
                    self.table.delete(*self.table.get_children());self.nodes={}
                    rows=data
                else:rows=[data]
                for info in rows:
                    uid=info['uid'];self.nodes[uid]=info
                    if self.table.exists(uid):self.table.delete(uid)
                    self.table.insert('', 'end', iid=uid,text=uid,values=('Unconfigured' if not info['configured'] else info['device_id'],info['mode'],info['version']))
                self.status.set('Verified. '+str(len(rows))+' device(s) read back. Firmware updates are complete only after application/version verification.')
        except queue.Empty:pass
        self.root.after(50,self.poll)
    def close(self):
        if self.busy:
            messagebox.showinfo('Operation in progress','Wait for this operation to finish. An interrupted upload requires a fresh retry.');return
        self.root.destroy()

def main():
    root=tk.Tk();App(root);root.mainloop()
if __name__=='__main__':main()

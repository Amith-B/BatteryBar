from tkinter.ttk import Progressbar, Style, Button
import tkinter as tk
import time  
import threading
import os
import psutil as ps
import sys
import pygame
from mutagen import mp3

xpos=0
ypos=0
windowx=0
windowy=0
mn=None
run=True
s=None
enablemovement=True


previousStatus='charging'
status='charging'


def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


switcher={
    'connected': resource_path('charging.mp3'),
    'disconnected': resource_path('disconnected.mp3'),
    'full': resource_path('full.mp3'),
    'low': resource_path('low.mp3')
}

try:
    if(os.path.exists('C:\\ProgramData\\BatteryBar\\batterybardata.log')):
        with open('C:\\ProgramData\\BatteryBar\\batterybardata.log','r') as f:
            line=str(f.readline()).strip()
            windowx,windowy,em=(int(i) for i in line.split(','))
            if(em==1):
                enablemovement=True
            else:
                enablemovement=False
except:
    windowx=0
    windowy=0
    enablemovement=True
    pass





# creating tkinter window 
root = tk.Tk()


s = Style(root)
#'side': 'top',left of stickey
s.layout("LabeledProgressbar",
         [('LabeledProgressbar.trough',
           {'children': [('LabeledProgressbar.pbar',
                          {'sticky': 'ns'}),
                         ("LabeledProgressbar.label",
                          {"sticky": ""})],
           'sticky': 'nswe'})])

#l1 = tk.Label(root, borderwidth=3, relief="ridge")
#l1.pack()
# Progress bar widget
fr=tk.Frame(root,highlightbackground="white", highlightthickness=3, bd=0)
fr.pack()
progress = Progressbar(fr, orient = 'horizontal',length = 60, mode = 'determinate',style="LabeledProgressbar")
progress.pack()


s.configure("LabeledProgressbar", thickness=16,text=" 0%",foreground='white',background='#009800',font='Helvetica 12 bold',troughcolor='black')
  
# Function responsible for the updation 
# of the progress bar value 
def bar():
    global run,s,mn,connected,status,previousStatus
    while(run):
        root.attributes('-topmost',1)
        if(mn!=None):
            mn.attributes('-topmost', 1)
        try:
            bp=ps.sensors_battery().percent
            progress['value'] = bp
            s.configure("LabeledProgressbar",text=" {0}%".format(bp))
            if(ps.sensors_battery().power_plugged):
                s.configure("LabeledProgressbar",background='#0000c8')
                status='connected'
                if(bp == 100):
                    status='full'
            else:
                status='disconnected'
                if(bp<20):
                    s.configure("LabeledProgressbar",background='#ff0000')
                    status='low'
                elif(bp<30):
                    s.configure("LabeledProgressbar",background='#ff962a')
                elif(bp<50):
                    s.configure("LabeledProgressbar",background='#ff8600')
                elif(bp<60):
                    s.configure("LabeledProgressbar",background='#a3d900')
                elif(bp<80):
                    s.configure("LabeledProgressbar",background='#00d900')
                elif(bp<101):
                    s.configure("LabeledProgressbar",background='#009800')
                
            if(previousStatus != status):
                play(switcher.get(status))
                previousStatus = status
            
        except:
            pass
        
        root.update() 
        time.sleep(1)

def getorigin(eventorigin):
    global xpos,ypos,mn
    xpos = eventorigin.x
    ypos = eventorigin.y
    if(mn!=None):
        mn.destroy()
        mn=None
        
def move_window(event):
    global windowx,windowy,enablemovement
    if(enablemovement):
        windowx=event.x_root-xpos-3
        windowy=event.y_root-ypos-3
        root.geometry(f'+{windowx}+{windowy}')

def on_closing():
    global run
    run=False
    os._exit(0)

def disable_or_enable():
    global enablemovement,mn
    if(enablemovement):
        enablemovement=False
    else:
        enablemovement=True
    mn.destroy()
    mn=None
    getCoordinates()

def getmenu(event):
    global mn,enablemovement
    if(mn==None):
        mn=tk.Tk()
        Button(mn,text='{0} movement'.format('Disable' if enablemovement else 'Enable'),command=disable_or_enable).pack()
        Button(mn,text='close',command=on_closing,width=17).pack()
        mn.attributes('-topmost', 1)
        mn.resizable(0, 0)
        mn.overrideredirect(1)
        mn.geometry('%dx%d+%d+%d' % (120,50,event.x_root, event.y_root-50))
        mn.configure(background='blue')
        mn.wm_attributes("-transparentcolor", "blue")
        mn.mainloop()
    else:
        mn.destroy()
        mn=None
    print('Menu')

def getCoordinates(event=None):
    global windowx,windowy,enablemovement
    try:
        if(os.path.exists('C:\\ProgramData\\BatteryBar')):
            with open('C:\\ProgramData\\BatteryBar\\batterybardata.log','w+') as f:
                if(enablemovement):
                    em=1
                else:
                    em=0
                f.write(str(windowx)+','+str(windowy)+','+str(em))
        else:
            os.mkdir('C:\\ProgramData\\BatteryBar')
            with open('C:\\ProgramData\\BatteryBar\\batterybardata.log','w+') as f:
                if(enablemovement):
                    em=1
                else:
                    em=0
                f.write(str(windowx)+','+str(windowy)+','+str(em))
    except:
        pass


def play(music):
    try:
        pygame.mixer.quit()
        mp = mp3.MP3(music)
        pygame.mixer.init(frequency=mp.info.sample_rate)
        clock = pygame.time.Clock()
        pygame.mixer.music.set_volume(10)
        pygame.mixer.music.load(music)
        pygame.mixer.music.play()
    except Exception as e:
        pass

def initMixer():
    BUFFER = 3072
    FREQ, SIZE, CHAN = getmixerargs()
    pygame.mixer.init(FREQ, SIZE, CHAN, BUFFER)

def getmixerargs():
    pygame.mixer.init()
    freq, size, chan = pygame.mixer.get_init()
    return freq, size, chan

try:
    initMixer()
except:
    pygame.mixer.music.stop()
  
# This button will initialize 
# the progress bar

#Button(root, text = 'Start', command = bar).pack()
#root.configure(background='black')
root.attributes('-topmost',1)
root.resizable(0, 0)
root.overrideredirect(1)
#root.wm_attributes("-transparentcolor", 'black')

t = threading.Thread(target=bar, args=())
t.daemon = True
t.start()

root.bind("<Button 1>",getorigin)
root.bind("<Button 3>",getmenu)

root.bind("<B1-Motion>", move_window)
root.bind("<ButtonRelease-1>",getCoordinates)
root.geometry('%dx%d+%d+%d' % (66,28,windowx, windowy))

root.mainloop()

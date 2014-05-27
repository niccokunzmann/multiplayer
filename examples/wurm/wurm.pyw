# -*- coding: cp1252 -*-
#      up down right left
keys= (('Up', 'w', 'W'),('Down', 's', 'S'),('Right', 'd', 'D'),('Left', 'a', 'A'))
try:
    from tkinter import *
    import tkinter
except ImportError:
    print('Python 3!!!')
    raise
import time

Up= 0
Down= 1
Right= 2
Left= 3

minimize= 'End'

import sys
sch= 0
schreibe= lambda *txt: sch and sys.stdout.write(*txt)

WURM_WIDTH= 20  #int min 20
ESSEN_WIDTH= 30 #min 20 , int
BG= '#0a4469'

STARTLENGTH= 10
FIRST= 0
TIMEOUT= 0.045 #0.053

BEWERTUNG= True
BEENDEN= '<Double-Escape>'

foo = lambda *x: None

# groesse fuer pizza
rangeroot= Tk()
rangeroot.update()
try:
    rangeroot.attributes("-alpha", 00)
    rangeroot.state('zoomed')
except:
    print('feldmasze konnten nicht ermittelt werden.')
    screenheight= height= rangeroot.winfo_screenheight()
    screenwidth= width= rangeroot.winfo_screenwidth()
    height-= 60
else:
    print('richtige hoehe ermittelt')
    height= rangeroot.winfo_height()
    width= rangeroot.winfo_width()
    screenheight= rangeroot.winfo_screenheight()
    screenwidth= rangeroot.winfo_screenwidth()

if __name__ != '__main__':
    rangeroot.destroy()
    tkinter._default_root= None
elif tkinter._default_root == rangeroot:
    tkinter._default_root= None

def geometry(t):
    g= t.geometry()
    x= g.index('x')
    p1=  g.index('+')
    p2= g[p1 +1:].index('+')
    return int(g[p1 + 1: p2]), int(g[p2 + 1:]), int(g[:x]), int(g[x + 1: p1])

def t_overlapping(t1, t2):
    x1, y1, w1, h1= geometry(t1)
    x2, y2, w2, h2= geometry(t2)
    return overlapping( x1, y1, w1, h1, x2, y2, w2, h2)

def overlapping( x1, y1, w1, h1, x2, y2, w2, h2):
    return (x1 - w2 < x2 < x1 + w1) and (y1 - h2 < y2 < y1 + h1)
    

class Wurm(object):
    def __init__(self, master= None, length= STARTLENGTH, width= WURM_WIDTH, start= [10,10], auge= 'auge.gif', feld= None):
        self.auge= PhotoImage(master= master, file = auge)
        self.master= master
        self.width= width
        self.direction= ''
        self.pos= [] #[[x, y, toplevel], ...]
        self.add= 0 # 0 !
        self.lastmove= (0,0)
        self.lasttestmove= (1, 0)
        self.lastpos= None
        self.lastdir= None
        self.feld= feld

        self.lastkopf= []
        self.new(length, start)

    def kopf(self, t):
        [l.destroy() for l in self.lastkopf]
        l1= Label(t, bg= BG)
        l1.place(y= 0, x= 0, anchor= NW)                        # < /\
        l2= Label(t, bg= BG)
        l2.place(y= self.width / 2, x= 0, anchor= NW)           # > /\
        l3= Label(t, bg= BG)
        l3.place(y= 0, x= self.width / 2, anchor= NW)           # < \/
        l4= Label(t, bg= BG)
        l4.place(y= self.width / 2, x= self.width / 2, anchor= NW)# > \/
        self.lastkopf= [l1, l3, l2, l4]

    def schauen(self):
        a= ()
        l= self.lastmove
        if l[0] < 0:
            a= (1, 3, 2, 4)
        elif l[0] > 0:
            a= (2, 4, 1, 3)
        elif l[1] < 0:
            a= (1, 2, 3, 4)
        elif l[1] > 0:
            a= (3, 4, 1, 2)
        for i in a[:2]:
            self.lastkopf[i - 1].config(image= self.auge)
        for i in a[2:]:
            self.lastkopf[i - 1].config(image= None)

    def add_t(self, n):
        self.add+= n

    def _add_toplevel(self, pos):
        t= Toplevel(self.master)
        pos.append(t)
        t.overrideredirect(1)
        t.config(borderwidth= 0, width= self.width, height= self.width, bg= BG)
        t.protocol('WM_DELETE_WINDOW', foo)
        if self.feld:
            t.bind('<Any-KeyPress>', lambda e: (self.feld.root.focus(), self.feld.start()))
        t.wm_focusmodel("active")
##        t.bind('<Any-ButtonPress>', lambda e:self.master.focus_set())
        self.pos.insert(FIRST, pos)
        t.geometry('+%i+0' % self.width)
        self.actpos(pos)

    def actpos(self, pos):
        schreibe(pos)
        if type(pos[0]) != int or type(pos[1]) != int:
            return
        pos[2].geometry('+%i+%i' % tuple(pos)[:2])

    def next(self):
        if not self._stop:
            if self.add > 0:
                self._add_toplevel([None, None])
                self.add-= 1
            self.nextpos()
            

    def nextpos(self):
        if not self.direction:
            self.move(*self.lastmove)
        elif self.direction in keys[Left]:
            self.move(-1, 0)
        elif self.direction in keys[Right]:
            self.move(1, 0)
        elif self.direction in keys[Up]:
            self.move(0, -1)
        elif self.direction in keys[Down]:
            self.move(0, 1)

    def move(self, x, y):
        if not (x or y):
            return
        elif ((x * self.lasttestmove[0] < 0) or (y * self.lasttestmove[1] < 0)):
            # entgegengesetzte richtung
            self.direction= self.lastdir
            self.nextpos()
            return
        p= self.pos.pop(FIRST)#p: kopf
        self.pos.append(p)
        lp= self.pos[-2]
        if x > 0:
            p[0]= lp[0] + self.width
            p[1]= lp[1]
        elif x < 0:
            p[0]= lp[0] - self.width
            p[1]= lp[1]
        elif y > 0:
            p[1]= lp[1] + self.width
            p[0]= lp[0]
        elif y < 0:
            p[1]= lp[1] - self.width
            p[0]= lp[0]


        self.kopf(p[2])
        self.schauen()

        self.actpos(p)
        self.lastmove= (x, y)
        self.lasttestmove= (x, y)
        self.lastdir= self.direction
        self.lastpos= p


    def destroy(self):
        self._funkall(Toplevel.destroy, )
        self.pos= []

    def new(self, length= STARTLENGTH, start= [10,10]):
        self.destroy()
        self.lasttestmove= (1, 0)
        width= self.width
        for i in range(length):
            self._add_toplevel([start[0] * width - i * width, \
                                start[1] * width ])

    def stop(self):
        self._stop= True
        self.direction= ''
        self.lastmove= (0, 0)
        self.lastpos= None                  
        self.lastdir= None
    def start(self):
        self._stop= False

    def expose(self):
        self._funkall(Toplevel.focus_set, )

    def iconify(self):
        self._funkall(Toplevel.wm_withdraw, )
    def deiconify(self):
        self._funkall(Toplevel.deiconify, )
        
    def _funkall(self, funk, *arg, **kw):
        [funk(p[2], *arg, **kw) for p in self.pos]
        
class Essen(object):
    def __init__(self, root, pos= None, width= ESSEN_WIDTH, add= 3):
        self.root= root
        self.root.overrideredirect(1)
        self.image= PhotoImage(master= self.root, file= 'pizza.gif')
        self.label= Label(self.root, image= self.image, \
                          borderwidth= 0, width= width, height= width, bg= 'white')
        self.label.pack()
        self.root.config(borderwidth= 0, width= width, height= width, bg= 'white')
        self.width= width
        self.add= add

        if pos:
            self.setpos(pos)
        else:
            self.replace()

    def kollisionstest(self, wurm):
        if wurm.lastpos and overlapping(self.pos[0], self.pos[1], self.width, self.width,\
                       wurm.lastpos[0], wurm.lastpos[1], wurm.width,\
                       wurm.width):
            wurm.add_t(self.add)
            self.replace(wurm)
            return True
        return False
    
    def setpos(self, pos= None):
        if pos:
            self.pos= pos
        self.root.geometry('%ix%i+%i+%i' % ((self.width,) * 2 + tuple(self.pos)))
        
    def replace(self, wurm = []):
        import random
        if type(wurm) != list:
            wurm= [wurm]
        while 1:
            b= False
            r1= random.random()
            r2= random.random()
            x= int((width - self.width) * r1)
            y= int((height- self.width) * r2)
            sw= self.width
            for w in wurm:
                ww= w.width
                for p in w.pos:
                    if overlapping(p[0], p[1], ww, ww, x, y, sw, sw, ):
                        b= True
                        break
                if b:
                    break
            if b:
                schreibe('auf wurm')
                continue
            break
        self.setpos([x, y])

#--------------Spieler-----------

class Spieler(object):
    def __init__(self, wurm, feld= None):
        self.reset()

        self.wurm= wurm

        self.feld= feld
        self.t= []
        if BEWERTUNG:
            self.bewertungsroot= Toplevel(self.feld.root)
            self.bewertungsroot.geometry('%ix0+0+350'%width)
            self.bewertungsroot.protocol('WM_DELETE_WINDOW', self.bewertungsroot.iconify)
            self.bewertungsroot.bind(BEENDEN, self.feld.destroy)
            self.bewertungsroot.bind('<KeyPress-'+minimize+'>', self.feld.minimize)
            self.bewertungsroot.wm_resizable(True, False)

##        self.root= root= Toplevel(master, bg= BG)

    def info(self):
        t= Toplevel(self.feld.root)
        self.t.append(t)
        def destroy():
            self.feld.start()
            self.t.remove(t)
            t.destroy()
        def focus_out(e):
            self.feld.start()
        
        t.protocol('WM_DELETE_WINDOW', destroy)
        t.bind(BEENDEN, lambda e: destroy())
        t.bind('<KeyPress-%s>'%minimize, lambda e: self.feld.minimize())
        t.focus()
        
        b= None

        if BEWERTUNG:
            l= len(self.wurm.pos)
            ba= float(self.wurm.width) * self.wurm.width / screenwidth / screenheight# h
            v= TIMEOUT # n
            gg= self.gegessen # h
            ww= self.wurm.width # h, h
            ew= self.feld.essen.width # n
            self.r # n
            self.sl# h
            # durchschittsl + flaeche + gg + 
            b= int((self.sl / self.r  + gg * ww / ew + (self.maxlen + l) / 2) * ba / v**1.3 / self.r ** 0.25 * 100)
        
        t.title('Auswertung')
        Label(t, text= 'Maximale Laenge: ' + str(self.maxlen) + ' ( '+ \
              str(100 * ba * self.maxlen)\
              + '% vom Bildschirm )').grid(row= 0, column= 0, sticky= NW)
        Label(t, text= 'Letzte Laenge: ' + self.wurm.pos.__len__().__str__()).grid(row= 1, column= 0, sticky= NW)
        Label(t, text= 'Verspeiste Pizzen: ' + str(gg)).grid(row= 2, column= 0, sticky= NW)
        Label(t, text= 'Bewertung: %i' % (b,)).grid(row= 3, column= 0, sticky= NW)
##        Label(t, text= 'Kollision ' + koll).grid(row= 3, column= 0, sticky= NW)

    def reset(self):
        self.maxlen= STARTLENGTH
        self.gegessen= 0
        self.sl= 0
        self.r= 0
        
    def act(self):
        if self.wurm.lastpos:
            l= len(self.wurm.pos)
            self.sl+= l
            self.r+= 1
            if l > self.maxlen:
                self.maxlen= l

            if BEWERTUNG:
                #bewertung
                ba= float(self.wurm.width) * float(self.wurm.width) / screenwidth / screenheight# h
                v= TIMEOUT # n
                gg= self.gegessen # h
                ww= self.wurm.width # h, h
                ew= self.feld.essen.width # n
                self.r # n
                self.sl# h
                # durchschittsl + flaeche + gg + 
                b= int((self.sl / self.r  + gg * ww / ew + (self.maxlen + l) / 2) * ba / v**1.3 / self.r ** 0.25 * 100)
                self.bewertungsroot.title('|' * b + ' - ' + str(b) + '    Laenge: ' + str(l))

        

    def iconify(self):
        for t in self.t:
            t.wm_withdraw()
        if BEWERTUNG:
            self.bewertungsroot.wm_withdraw()
    def deiconify(self):
        for t in self.t:
            t.iconify()
        if BEWERTUNG:
            self.bewertungsroot.deiconify()


#--------------Feld--------------

class Feld(object):
    def __init__(self):
        self.root= Tk()
        self.root.focus()
        self.root.tk_setPalette(background= BG)
        self.pxlheight= height
        self.pxlwidth= width
        self.wurm= [Wurm(master= self.root, length= STARTLENGTH, feld= self)]
        self.root.protocol('WM_DELETE_WINDOW', self.destroy)

        self.essen= Essen(self.root)

        self.timeout= TIMEOUT

        self.root.bind('<Any-KeyPress>', self.keypress)
        self.root.bind('<Any-KeyRelease>', self.keyrelease)
        self.root.bind('<FocusOut>', lambda e: (self.pause()))
        self.root.bind('<Any-ButtonPress>', lambda e: self.start())
        self.root.bind('<Double-Key-Escape>', lambda e: self.destroy())

        self.mainid= None
        self._pause= False

        self.spieler= [Spieler(self.wurm[i], feld= self) for i in range(len(self.wurm))]

    def kollisionstest(self):
        #rand
        for nr, wurm in enumerate(self.wurm):
            p= wurm.lastpos #kopf
            if not p:
                return
            if ( p[0] < 0 or p[0] > screenwidth - wurm.width or \
                      p[1] < 0 or p[1] > screenheight - wurm.width):
                self.kollision(nr)
            #wurm selbst
            x,y, t= p
            width= wurm.width
            kollision= 0
            for i, p2 in enumerate(wurm.pos[:]):
                if p == p2:
                    continue
                if (p2[0] <= x < p2[0] + width) and \
                   (p2[1] <= y < p2[1] + width):
                    kollision= i
            if kollision:
                [(wurm.pos.pop(FIRST)[2].destroy()  ) for i in range(kollision)]
            #                                       /\  time.sleep(DELETE_TIMEOUT); self.root.update()
            elif self.essen.kollisionstest(wurm):
                self.spieler[nr].gegessen+= 1

    def kollision(self, nr):
        self.spieler[nr].info()
        self.spieler[nr].reset()
        self.wurm[nr].new(STARTLENGTH)
#        self.essen.replace(self.wurm)
        self.pause()

    def keypress(self, event):
        #fuer multiplayer ueberarbeiten
        key= event.keysym
        if True in [key in k for k in keys]:
            for wurm in self.wurm:
                wurm.direction= key
        elif key == minimize:
            self.minimize()
            
    def minimize(self, e= None):
        self.pause()
        [wurm.iconify() for wurm in self.wurm]
        [spieler.iconify() for spieler in self.spieler]
        self.root.geometry('1x1+0+0')
    def normal(self, e= None):
        [spieler.deiconify() for spieler in self.spieler]
        [wurm.deiconify() for wurm in self.wurm]
        self.essen.setpos()
            
    def keyrelease(self, event):
        for wurm in self.wurm:
            if wurm.direction == event.keysym:
                wurm.direction= ''
        
    def mainloop(self):
        self.root.mainloop()

    def wurmstop(self):
        [wurm.stop() for wurm in self.wurm]
    def wurmstart(self):
        [wurm.start() for wurm in self.wurm]    

    def _mainloop(self):
        t= time.time()

        self.wurmstart()
        [wurm.next() for wurm in self.wurm]
        self.kollisionstest()
        [spieler.act() for spieler in self.spieler]
        
        if not self._pause:
            t= int(1000 * (self.timeout - time.time() + t))
            if t < 0:
                t= 0
            self.mainid= self.root.after(t, self._mainloop)

    def destroy(self, event= None):
        self.pause()
        self.root.quit()
        self.root.destroy()

    def pause(self):
        self.wurmstop()
        if self.mainid != None:
            self._pause= True
            self.root.after_cancel(self.mainid)
            self.mainid= None

    def start(self):
        self.pause()
        [wurm.expose() for wurm in self.wurm]
        self.normal()
        self.root.update()

        self.root.focus_set()
        self.mainid= self.root.after(0, self._mainloop)
        self._pause= False
        

if __name__=='__main__':
    feld= Feld()
    rangeroot.destroy()
    feld.start()
    import sys
    if len(sys.argv) >= 2 and sys.argv[1] == 'minimized':
        feld.minimize()
    if not 'idlelib' in dir():
        feld.mainloop()

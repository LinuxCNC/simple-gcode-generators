#!/usr/bin/python

"""
    Grill.py G-Code Generator
    Version 1.3
    Copyright (C) <2012> <Alex Bobotek> <alex at bobotek dot net>
  
    based on work by <Lawrence Glaister> and <John Thornton>  -- thanks Lawrence and John!

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    To make it a menu item in Ubuntu use the Alacarte Menu Editor and add
    the command python YourPathToThisFile/grill.py
    make sure you have made the file executable by right
    clicking and selecting properties then Permissions and Execute

    To use with EMC2 see the instructions at:
    http://wiki.linuxcnc.org/cgi-bin/emcinfo.pl?Simple_EMC_G-Code_Generators

    Version 1.0 intial round pattern
    Version 1.1 added rectangular and oval shapes
    Version 1.2 offset alternate lines by 1/2 the spacing
    Version 1.3 fixed "Y clipping" bug from V1.2, added true oval and renamed old "oval" to "ellipse"

"""

from Tkinter import *
from math import *
import os
import math


IN_AXIS = os.environ.has_key("AXIS_PROGRESS_BAR")

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
        self.DoIt()


    def createWidgets(self):
        self.HoleID = []
        self.gcode = []
        self.CanvasSize = IntVar()
        self.CanvasSize.set(300)
        self.PreviewFrame = Frame(self,bd=5)
        self.PreviewFrame.grid(row=0, column=0)
        self.PreviewCanvas = Canvas(self.PreviewFrame,width=500, height=500, bg='white', bd='3', relief = 'raised')
        self.PreviewCanvas.grid(sticky=N+S+E+W)
        self.XLine = self.PreviewCanvas.create_line(15,500/2,500 - 15,500/2, fill = 'green')
        self.YLine = self.PreviewCanvas.create_line(250,15,250,485, fill = 'green')

        self.EntryFrame = Frame(self,bd=5)
        self.EntryFrame.grid(row=0, column=1)

        self.st00 = Label(self.EntryFrame, text='      Peck Drill an Array of Holes\n\n\n\n\n\n\n\n\n')
        self.st00.grid(row=0, column=0, columnspan=2)

        self.st000 = Label(self.EntryFrame, text='Shape')
        self.st000.grid(row=1, column=0)
        self.ShapeVar = IntVar()
        self.ShapeVar.set(1)
        Radiobutton(self.EntryFrame, text='Circle', variable=self.ShapeVar, value = 0, command=self.DoIt).grid(row=1, column=1, sticky=W)
        Radiobutton(self.EntryFrame, text='Ellipse', variable=self.ShapeVar, value = 1, command=self.DoIt).grid(row=1, column=1)
        Radiobutton(self.EntryFrame, text='Rectangle',   variable=self.ShapeVar, value = 2, command=self.DoIt).grid(row=1, column=1, sticky=E)
        Radiobutton(self.EntryFrame, text='Oval',   variable=self.ShapeVar, value = 3, command=self.DoIt).grid(row=1, column=2)



        self.st01 = Label(self.EntryFrame, text='Preamble')
        self.st01.grid(row=2, column=0)
        self.PreambleVar = StringVar()
        self.PreambleVar.set('G17 G21 G90 G64 P0.05 M3 S2000 M7')
        self.Preamble = Entry(self.EntryFrame, textvariable=self.PreambleVar ,width=35)
        self.Preamble.grid(row=2, column=1)

        self.NormalColor =  self.Preamble.cget('bg')

        self.st02 = Label(self.EntryFrame, text='X Center of Grill')
        self.st02.grid(row=3, column=0)
        self.XGrillCenterVar = StringVar()
        self.XGrillCenterVar.set('3.0')
        self.XGrillCenter = Entry(self.EntryFrame, textvariable=self.XGrillCenterVar ,width=15)
        self.XGrillCenter.grid(row=3, column=1)

        self.st03 = Label(self.EntryFrame, text='Y Center of Grill')
        self.st03.grid(row=4, column=0)
        self.YGrillCenterVar = StringVar()
        self.YGrillCenterVar.set('4.0')
        self.YGrillCenter = Entry(self.EntryFrame, textvariable=self.YGrillCenterVar ,width=15)
        self.YGrillCenter.grid(row=4, column=1)

        self.st04 = Label(self.EntryFrame, text='Dimension of Grill(X,Y)')
        self.st04.grid(row=5, column=0)
        self.GrillXVar = StringVar()
        self.GrillXVar.set('40')
        self.GrillX = Entry(self.EntryFrame, textvariable=self.GrillXVar ,width=15)
        self.GrillX.grid(row=5, column=1, sticky = W)

        self.GrillYVar = StringVar()
        self.GrillYVar.set('80')
        self.GrillY = Entry(self.EntryFrame, textvariable=self.GrillYVar ,width=15)
        self.GrillY.grid(row=5, column=1, sticky = E)

        self.st05 = Label(self.EntryFrame, text='Hole Spacing')
        self.st05.grid(row=6, column=0)
        self.HoleSpaceVar = StringVar()
        self.HoleSpaceVar.set('2.5')
        self.HoleSpace = Entry(self.EntryFrame, textvariable=self.HoleSpaceVar ,width=15)
        self.HoleSpace.grid(row=6, column=1)

        self.st06 = Label(self.EntryFrame, text='Final Hole Depth')
        self.st06.grid(row=7, column=0)
        self.HoleDepthVar = StringVar()
        self.HoleDepthVar.set('-4')
        self.HoleDepth = Entry(self.EntryFrame, textvariable=self.HoleDepthVar ,width=15)
        self.HoleDepth.grid(row=7, column=1)

        self.st07 = Label(self.EntryFrame, text='Q - peck incr')
        self.st07.grid(row=8, column=0)
        self.PeckVar = StringVar()
        self.PeckVar.set('10')
        self.Peck = Entry(self.EntryFrame, width=15, textvariable = self.PeckVar)
        self.Peck.grid(row=8, column=1)

        self.st08 = Label(self.EntryFrame, text='R - Safe Z')
        self.st08.grid(row=9, column=0)
        self.SafeZVar = StringVar()
        self.SafeZVar.set('4')
        self.SafeZ = Entry(self.EntryFrame, width=15, textvariable = self.SafeZVar)
        self.SafeZ.grid(row=9, column=1)

        self.st09 = Label(self.EntryFrame, text='Feedspeed')
        self.st09.grid(row=10, column=0)
        self.FeedspeedVar = StringVar()
        self.FeedspeedVar.set('500')
        self.Feedspeed = Entry(self.EntryFrame, textvariable=self.FeedspeedVar ,width=15)
        self.Feedspeed.grid(row=10, column=1)

        self.st10 = Label(self.EntryFrame, text='Drill Size')
        self.st10.grid(row=11, column=0)
        self.DrillVar = StringVar()
        self.DrillVar.set('1.8')
        self.Drill = Entry(self.EntryFrame, textvariable=self.DrillVar ,width=15)
        self.Drill.grid(row=11, column=1)

        self.st11 = Label(self.EntryFrame, text='Postamble')
        self.st11.grid(row=12, column=0)
        self.PostambleVar = StringVar()
        self.PostambleVar.set('M5 M9 M2')
        self.Postamble = Entry(self.EntryFrame, textvariable=self.PostambleVar ,width=15)
        self.Postamble.grid(row=12, column=1)

        self.DoItButton = Button(self.EntryFrame, text='Recalculate', command=self.DoIt)
        self.DoItButton.grid(row=13, column=0)

        self.ToClipboard = Button(self.EntryFrame, text='To Clipboard', command=self.CopyClipboard)
        self.ToClipboard.grid(row=13, column=1)

        if IN_AXIS:
            self.quitButton = Button(self, text='Write to AXIS and Quit',command=self.WriteToAxis)
        else:
            self.quitButton = Button(self, text='Quit', command=self.quit)
        self.quitButton.grid(row=13, column=0, sticky=S)

    def DoIt(self):
        # range check inputs for gross errors
        self.GrillX.configure( bg = self.NormalColor )
        if (float(self.GrillX.get()) <= 0.0 ):
            self.GrillX.configure( bg = 'red')
            return

        self.GrillY.configure( bg = self.NormalColor )
        if (float(self.GrillY.get()) <= 0.0 ):
            self.GrillY.configure( bg = 'red')
            return

        self.HoleSpace.configure( bg = self.NormalColor )
        if (float(self.HoleSpace.get()) <= 0.0 ):
            self.HoleSpace.configure( bg = 'red')
            return

        self.HoleDepth.configure( bg = self.NormalColor )
        self.Peck.configure( bg = self.NormalColor )
        self.SafeZ.configure( bg = self.NormalColor )
# at this point, I have not figured out all the reasonable combinations for peck drilling
#       if float(self.HoleDepth.get()) >= float(self.SafeZ.get()) or float(self.Peck.get()) <= 0.0:
#            self.HoleDepth.configure( bg = 'red' )
#            self.Peck.configure( bg = 'red' )
#            self.SafeZ.configure( bg = 'red' )
#            return

        self.Feedspeed.configure( bg = self.NormalColor )
        if float(self.Feedspeed.get()) <= 0.0:
            self.Feedspeed.configure( bg = 'red' )
            return

        self.Drill.configure( bg = self.NormalColor )
        if float(self.Drill.get()) <= 0.0:
            self.Drill.configure( bg = 'red' )
            return

        # rough guess at number of holes each direction from centerpoint
        xholes = int(((float(self.GrillX.get())/float(self.HoleSpaceVar.get()))+3.0)/2.0)
        if self.ShapeVar.get() == 0:    # circular grid
            yholes = int(((float(self.GrillX.get())/float(self.HoleSpaceVar.get()))+3.0)/cos(math.pi/6))
        else:
            yholes = int(((float(self.GrillY.get())/float(self.HoleSpaceVar.get()))+3.0)/cos(math.pi/6))

        # erase old holes/display objects as needed
        for hole in self.HoleID:
            self.PreviewCanvas.delete(hole)
        self.HoleID = []

        # erase old gcode as needed
        self.gcode = []
        self.gcode.append('( Code generated by grill.py widget )')
        self.gcode.append('( by Alex Bobotek - 2012 )')
        self.gcode.append(self.PreambleVar.get())
        self.gcode.append( 'G0 Z%.4f F%s' %(float(self.SafeZVar.get()), self.FeedspeedVar.get()))

        DrillRad = float(self.DrillVar.get()) / 2.0
        Spacing  = float(self.HoleSpaceVar.get())

        if self.ShapeVar.get() == 0:
            # temps used for circular grills
            self.gcode.append('( %.4f dia circular grill at %.4f,%.4f )'
                %(float(self.GrillXVar.get()),
                  float(self.XGrillCenterVar.get()),
                  float(self.YGrillCenterVar.get()) ))
            self.GrillY.configure(state=DISABLED)
            GrillRadius = float(self.GrillXVar.get())/2.0
            RadSQ = GrillRadius * GrillRadius
            Scale = float(self.GrillXVar.get()) * 1.2 / 500.0
            self.HoleID.append(self.PreviewCanvas.create_oval(
                250-GrillRadius/Scale,
                250-GrillRadius/Scale,
                250+GrillRadius/Scale,
                250+GrillRadius/Scale, outline='green'))

        if self.ShapeVar.get() == 1:      # ellipse
            # temps used for elliptical grills
            self.gcode.append('( %.4fx%.4f elliptical grill at %.4f,%.4f )'
                %(float(self.GrillXVar.get()),
                  float(self.GrillYVar.get()),
                  float(self.XGrillCenterVar.get()),
                  float(self.YGrillCenterVar.get()) ))

            self.GrillY.configure(state=NORMAL)
            a = float(self.GrillXVar.get())/2.0
            b = float(self.GrillYVar.get())/2.0
            aSQ = a * a
            bSQ = b * b
            if a > b:
                Scale = float(self.GrillXVar.get()) * 1.2 / 500.0
            else:
                Scale = float(self.GrillYVar.get()) * 1.2 / 500.0
            self.HoleID.append(self.PreviewCanvas.create_oval(
                250-a/Scale,
                250-b/Scale,
                250+a/Scale,
                250+b/Scale, outline='green'))

        if self.ShapeVar.get() == 2:      # rectangle
            # temps used for rectangular grills
            self.gcode.append('( %.4fx%.4f rectangular grill at %.4f,%.4f )'
                %(float(self.GrillXVar.get()),
                  float(self.GrillYVar.get()),
                  float(self.XGrillCenterVar.get()),
                  float(self.YGrillCenterVar.get()) ))

            self.GrillY.configure(state=NORMAL)
            a = float(self.GrillXVar.get())/2.0
            b = float(self.GrillYVar.get())/2.0
            if a > b:
                Scale = float(self.GrillXVar.get()) * 1.2 / 500.0
            else:
                Scale = float(self.GrillYVar.get()) * 1.2 / 500.0
            self.HoleID.append(self.PreviewCanvas.create_rectangle(
                250-a/Scale,
                250-b/Scale,
                250+a/Scale,
                250+b/Scale, outline='green'))

        if self.ShapeVar.get() == 3:      # oval
            # temps used for oval grills
            self.gcode.append('( %.4fx%.4f oval grill at %.4f,%.4f )'
                %(float(self.GrillXVar.get()),
                  float(self.GrillYVar.get()),
                  float(self.XGrillCenterVar.get()),
                  float(self.YGrillCenterVar.get()) ))

            self.GrillY.configure(state=NORMAL)
            a = float(self.GrillXVar.get())/2.0
            b = float(self.GrillYVar.get())/2.0
            aSQ = a * a
            bSQ = b * b
            if a > b:
                Scale = float(self.GrillXVar.get()) * 1.2 / 500.0
            else:
                Scale = float(self.GrillYVar.get()) * 1.2 / 500.0
            self.HoleID.append(self.PreviewCanvas.create_oval(
                250-a/Scale,
                250-b/Scale,
                250+a/Scale,
                250+b/Scale, outline='green'))


        first = 1;
        numholes = 0;
        YSpacing = sqrt((Spacing * Spacing) - ((Spacing/2.0) * (Spacing/2.0)))

        # grid computed so it is always symmetrical about center point
        for x in range(-xholes,xholes):
            for y in range(-yholes-1,yholes+1):
                CurY = y * YSpacing
                if (y % 2)==0:
                    CurX = x * Spacing
                else:
                    CurX = x * Spacing + Spacing/2.0

                # the selection criterion for holes is that the center has to be inside
                # the requested grill perimeter
                inside = 0
                if self.ShapeVar.get() == 0:      # circle
                    if (( CurY * CurY + CurX * CurX ) < RadSQ):
                        inside = 1
                if self.ShapeVar.get() == 1:      # ellipse
                    if ((CurX * CurX / aSQ) + ( CurY * CurY /bSQ )) < 1:
                        inside = 1
                if self.ShapeVar.get() == 2:      # rectangle
                    if (CurX > -a  and CurX < a and CurY > -b and CurY < b):
                        inside = 1
                if self.ShapeVar.get() == 3:      # oval
                    if (b >= a):
                        if (abs(CurX) < a) and (abs(CurY) < (b - a)):
                            inside = 1
                        if (CurX * CurX) + (abs(CurY)-(b-a))*(abs(CurY)-(b-a)) < aSQ:
                            inside = 1
                    if (a > b):
                        if (abs(CurX) < (a - b)) and (abs(CurY) < b):
                            inside = 1
                        if (abs(CurX)-(a-b))*(abs(CurX)-(a-b)) + (CurY * CurY)  < bSQ:
                            inside = 1

                if inside:
                    numholes += 1
                    # plot the hole position on the canvas
                    self.HoleID.append( self.PreviewCanvas.create_oval(
                        250+(CurX-DrillRad)/Scale,
                        250+(CurY-DrillRad)/Scale,
                        250+(CurX+DrillRad)/Scale,
                        250+(CurY+DrillRad)/Scale, fill='grey'))

                    # generate the G code
                    if first:
                        self.gcode.append( 'G83 X%.4f Y%.4f Z%.4f Q%.4f R%.4f'
                            %( CurX + float(self.XGrillCenterVar.get()),
                            CurY + float(self.YGrillCenterVar.get()),
                            float(self.HoleDepthVar.get()),
                            float(self.PeckVar.get()),
                            float(self.SafeZVar.get())))
                        first = 0
                    else:
                        self.gcode.append( 'G83 X%.4f Y%.4f'
                            %( CurX + float(self.XGrillCenterVar.get()),
                               CurY + float(self.YGrillCenterVar.get())))

        self.HoleID.append(self.PreviewCanvas.create_text(250, 495, text='%d holes with %2.2f%% open area'%(numholes, 
		100*math.pi*float(self.DrillVar.get())*float(self.DrillVar.get())/6/float(self.HoleSpaceVar.get())/float(self.HoleSpaceVar.get())/tan(math.pi/6)  )))
        self.gcode.append(self.PostambleVar.get())

    def CopyClipboard(self):
        self.clipboard_clear()
        for line in self.gcode:
            self.clipboard_append(line+'\n')

    def WriteToAxis(self):
        for line in self.gcode:
            sys.stdout.write(line+'\n')
        self.quit()

app = Application()
app.master.title("Grill.py 1.3 by Alex Bobotek and Lawrence Glaister")
app.mainloop()

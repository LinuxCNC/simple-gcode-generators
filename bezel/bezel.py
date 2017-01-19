#!/usr/bin/python
"""
    bezel-11.py G-Code Generator
    Version 1.1
    Copyright (C) <2008>  <Lawrence Glaister> <ve7it at shaw dot ca>
    based on work by <John Thornton>  -- thanks John!

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

    Version 1.0 intial port from cp1 code
    Version 1.1 used vars to hold center offsets and Z depths for 
        easy reuse of bezel code. Moved feedspeed to preamble

"""

from Tkinter import *
from math import *
import os

IN_AXIS = os.environ.has_key("AXIS_PROGRESS_BAR")

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
        self.DoIt()


    def createWidgets(self):
        self.segID = []
        self.gcode = []
        self.PreviewFrame = Frame(self,bd=5)
        self.PreviewFrame.grid(row=0, column=0)
        self.PreviewCanvas = Canvas(self.PreviewFrame,width=300, height=300, bg='white', bd='3', relief = 'raised')
        self.PreviewCanvas.grid(sticky=N+S+E+W)
        self.XLine = self.PreviewCanvas.create_line(15,150,285,150, fill = 'green')
        self.YLine = self.PreviewCanvas.create_line(150,15,150,285, fill = 'green')

        self.EntryFrame = Frame(self,bd=5)
        self.EntryFrame.grid(row=0, column=1)

        self.st00 = Label(self.EntryFrame, text='Engrave a Control Bezel\n')
        self.st00.grid(row=0, column=0, columnspan=2)

        self.st01 = Label(self.EntryFrame, text='Preamble')
        self.st01.grid(row=1, column=0)
        self.PreambleVar = StringVar()
        self.PreambleVar.set('G17 G20 G90 G64 P0.003 M3 S3000 M7 F5')
        self.Preamble = Entry(self.EntryFrame, textvariable=self.PreambleVar ,width=40)
        self.Preamble.grid(row=1, column=1)

        self.NormalColor =  self.Preamble.cget('bg')

        self.st02 = Label(self.EntryFrame, text='X Center of Bezel')
        self.st02.grid(row=2, column=0)
        self.XBezelCenterVar = StringVar()
        self.XBezelCenterVar.set('1.0')
        self.XBezelCenter = Entry(self.EntryFrame, textvariable=self.XBezelCenterVar ,width=15)
        self.XBezelCenter.grid(row=2, column=1)

        self.st03 = Label(self.EntryFrame, text='Y Center of Bezel')
        self.st03.grid(row=3, column=0)
        self.YBezelCenterVar = StringVar()
        self.YBezelCenterVar.set('2.0')
        self.YBezelCenter = Entry(self.EntryFrame, textvariable=self.YBezelCenterVar ,width=15)
        self.YBezelCenter.grid(row=3, column=1)

        self.st04 = Label(self.EntryFrame, text='Inner Radius of Bezel')
        self.st04.grid(row=4, column=0)
        self.BezelInnerRVar = StringVar()
        self.BezelInnerRVar.set('0.6')
        self.BezelInnerR = Entry(self.EntryFrame, textvariable=self.BezelInnerRVar ,width=15)
        self.BezelInnerR.grid(row=4, column=1)

        self.st05 = Label(self.EntryFrame, text='Minor Tick Radius of Bezel')
        self.st05.grid(row=5, column=0)
        self.BezelMinorRVar = StringVar()
        self.BezelMinorRVar.set('0.75')
        self.BezelMinorR = Entry(self.EntryFrame, textvariable=self.BezelMinorRVar ,width=15)
        self.BezelMinorR.grid(row=5, column=1)

        self.st06 = Label(self.EntryFrame, text='Major Tick Radius of Bezel')
        self.st06.grid(row=6, column=0)
        self.BezelMajorRVar = StringVar()
        self.BezelMajorRVar.set('0.85')
        self.BezelMajorR = Entry(self.EntryFrame, textvariable=self.BezelMajorRVar ,width=15)
        self.BezelMajorR.grid(row=6, column=1)

        self.st07 = Label(self.EntryFrame, text='Start Angle of Bezel')
        self.st07.grid(row=7, column=0)
        self.BezelStartAVar = StringVar()
        self.BezelStartAVar.set('-60.0')
        self.BezelStartA = Entry(self.EntryFrame, textvariable=self.BezelStartAVar ,width=15)
        self.BezelStartA.grid(row=7, column=1)

        self.st08 = Label(self.EntryFrame, text='End Angle of Bezel')
        self.st08.grid(row=8, column=0)
        self.BezelEndAVar = StringVar()
        self.BezelEndAVar.set('240.0')
        self.BezelEndA = Entry(self.EntryFrame, textvariable=self.BezelEndAVar ,width=15)
        self.BezelEndA.grid(row=8, column=1)

        self.st09 = Label(self.EntryFrame, text='Number of Ticks')
        self.st09.grid(row=9, column=0)
        self.BezelNumTicksVar = StringVar()
        self.BezelNumTicksVar.set('37')
        self.BezelNumTicks = Entry(self.EntryFrame, textvariable=self.BezelNumTicksVar ,width=15)
        self.BezelNumTicks.grid(row=9, column=1)

        self.st10 = Label(self.EntryFrame, text='Major Ticks Every')
        self.st10.grid(row=10, column=0)
        self.BezelTicksEveryVar = StringVar()
        self.BezelTicksEveryVar.set('4')
        self.BezelTicksEvery = Entry(self.EntryFrame, textvariable=self.BezelTicksEveryVar ,width=15)
        self.BezelTicksEvery.grid(row=10, column=1)


        self.st11 = Label(self.EntryFrame, text='Engraving Depth')
        self.st11.grid(row=11, column=0)
        self.DepthVar = StringVar()
        self.DepthVar.set('-0.010')
        self.Depth = Entry(self.EntryFrame, textvariable=self.DepthVar ,width=15)
        self.Depth.grid(row=11, column=1)

        self.st12 = Label(self.EntryFrame, text='Safe Z')
        self.st12.grid(row=12, column=0)
        self.SafeZVar = StringVar()
        self.SafeZVar.set('+0.100')
        self.SafeZ = Entry(self.EntryFrame, width=15, textvariable = self.SafeZVar)
        self.SafeZ.grid(row=12, column=1)

        self.st13 = Label(self.EntryFrame, text='Postamble')
        self.st13.grid(row=13, column=0)
        self.PostambleVar = StringVar()
        self.PostambleVar.set('M5 M9 M2')
        self.Postamble = Entry(self.EntryFrame, textvariable=self.PostambleVar ,width=15)
        self.Postamble.grid(row=13, column=1)

        self.DoItButton = Button(self.EntryFrame, text='Recalculate', command=self.DoIt)
        self.DoItButton.grid(row=16, column=0)

        self.ToClipboard = Button(self.EntryFrame, text='To Clipboard', command=self.CopyClipboard)
        self.ToClipboard.grid(row=16, column=1)

        if IN_AXIS:
            self.quitButton = Button(self, text='Write to AXIS and Quit',command=self.WriteToAxis)
        else:
            self.quitButton = Button(self, text='Quit', command=self.quit)
        self.quitButton.grid(row=13, column=0, sticky=S)

    def DoIt(self):
        # range check inputs for gross errors
        self.BezelInnerR.configure( bg = self.NormalColor )
        if float(self.BezelInnerR.get()) < 0.0:
            self.BezelInnerR.configure( bg = 'red' )
            return

        self.BezelMinorR.configure( bg = self.NormalColor )
        if float(self.BezelMinorR.get()) < 0.0:
            self.BezelMinorR.configure( bg = 'red' )
            return

        self.BezelMajorR.configure( bg = self.NormalColor )
        if float(self.BezelMajorR.get()) < 0.0:
            self.BezelMajorR.configure( bg = 'red' )
            return

        self.BezelNumTicks.configure( bg = self.NormalColor )
        if int(self.BezelNumTicks.get()) < 2:
            self.BezelNumTicks.configure( bg = 'red' )
            return

        # erase old segs/display objects as needed
        for seg in self.segID:
            self.PreviewCanvas.delete(seg)
        self.segID = []

        # erase old gcode as needed
        self.gcode = []

        # temps used for bezel calcs
        SafeZ =    float(self.SafeZVar.get())
        NumTicks = int(self.BezelNumTicksVar.get())
        StartA =   float(self.BezelStartAVar.get())
        EndA =     float(self.BezelEndAVar.get())
        DeltaA =   (EndA - StartA) / (float(NumTicks) - 1.0)
        XCenter =  float(self.XBezelCenterVar.get())
        YCenter =  float(self.YBezelCenterVar.get())
        InnerR =   float(self.BezelInnerRVar.get())
        MinorR =   float(self.BezelMinorRVar.get())
        MajorR =   float(self.BezelMajorRVar.get())
        Depth =    float(self.DepthVar.get())
        Every =    int(self.BezelTicksEveryVar.get())
        Scale =    MajorR * 2.0 * 1.2 / 300.0          # nominal inches(mm) / pixel for plotting
        TwoPi =    6.283185307
        DegToRad = TwoPi/360.0

        self.gcode.append('( Code generated by bezel-11.py widget )')
        self.gcode.append('( by Lawrence Glaister VE7IT - 2008 )')
        self.gcode.append('( Engraving a %d tick, %.1f degree, %.3f dia bezel )' %(NumTicks, EndA-StartA, MajorR*2.0))
        self.gcode.append('#1 = %.4f  ( Safe Z )' %(SafeZ))
        self.gcode.append('#2 = %.4f  ( Engraving Depth Z )' %(Depth))
        self.gcode.append('#3 = %.4f  ( X Center )' %(XCenter))
        self.gcode.append('#4 = %.4f  ( Y Center )' %(YCenter))
        self.gcode.append(self.PreambleVar.get())
        self.gcode.append( 'G0 Z#1')

        for tick in range(0,NumTicks):
            angle = StartA + tick * DeltaA
            # calculate co-ordinates of inner point on tick mark
            x1 = InnerR * cos( angle * DegToRad )
            y1 = InnerR * sin( angle * DegToRad )

            # move to inner radius of tick mark
            self.gcode.append( 'G0 X[%.4f+#3]  Y[%.4f+#4]' %(x1, y1))

            # set to cutting height
            self.gcode.append( 'G1 Z#2')
    
            if ( (tick %  Every) == 0 ):
                rad = MajorR
            else:
                rad = MinorR

            # compute outer point of tick mark
            x2 = rad * cos( angle * DegToRad )
            y2 = rad * sin( angle * DegToRad ) 

            # cut to outer radius of tick mark
            self.gcode.append( 'G1 X[%.4f+#3]  Y[%.4f+#4]' %(x2, y2))

            # raise engraver
            self.gcode.append( 'G0 Z#1')
            
            self.segID.append( self.PreviewCanvas.create_line(
                150+x1/Scale, 150-y1/Scale,150+x2/Scale, 150-y2/Scale, fill = 'black', width = 2))

        # spot drill the center point of the bezel
        self.gcode.append( 'G0 X#3  Y#4')
        self.gcode.append( 'G1 Z#2 G4 P0.5')
        self.gcode.append( 'G0 Z#1')

        # finish up with icing
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
app.master.title("bezel-11.py by Lawrence Glaister ")
app.mainloop()






#!/usr/bin/python

"""
    pocket.py G-Code Generator
    Version 1.0
    Copyright (C) <2010>  <Sammel Lothar > <Lothar at Sammellothar dot de>
    based on work by 
    <Lawrence Glaister> <ve7it at shaw dot ca>
    <John Thornton>  -- thanks John!

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
    the command python YourPathToThisFile/pocketing.py
    make sure you have made the file executable by right
    clicking and selecting properties then Permissions and Execute

    To use with LinuxCNC see the instructions at: 
    https://github.com/linuxcnc/simple-gcode-generators

    Version 1.0 

"""

from Tkinter import *
from math import *
import os
import tkMessageBox


IN_AXIS = os.environ.has_key("AXIS_PROGRESS_BAR")

toolChange = ''

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
        self.DoIt()


    def createWidgets(self):
        self.CanvasDrawings = []
        self.gcode = []
        self.PreviewFrame = Frame(self,bd=3)
        self.PreviewFrame.grid(row=0, column=0)
        self.PreviewCanvas = Canvas(self.PreviewFrame,width=300, height=300, bg='white', bd='3', relief = 'raised')
        self.PreviewCanvas.grid(sticky=N+S+E+W)
        self.XLine = self.PreviewCanvas.create_line(15,150,285,150, fill = 'green')
        self.YLine = self.PreviewCanvas.create_line(150,15,150,285, fill = 'green')

        self.EntryFrame = Frame(self,bd=5)
        self.EntryFrame.grid(row=0, column=1)

        self.rownumber = 0
        self.st00 = Label(self.EntryFrame, text='Pocketing an Array')
        self.st00.grid(row=self.rownumber, column=0, columnspan=2)
 
        self.rownumber += 1
        self.st000 = Label(self.EntryFrame, text='Shape')
        self.st000.grid(row=self.rownumber,column=0,sticky=W)
        self.ShapeVar = IntVar()
        self.ShapeVar.set(0)
        Radiobutton(self.EntryFrame, text='Circle', variable=self.ShapeVar, value = 0, command=self.DoIt,indicatoron=0,width=5,).grid(row=self.rownumber+1, column=0, sticky = W)
        Radiobutton(self.EntryFrame, text=' Rect ',   variable=self.ShapeVar, value = 2, command=self.DoIt,indicatoron=0,width=5,).grid(row=self.rownumber+2, column=0,sticky=W)

        self.stPS = Label(self.EntryFrame, text='Path',width=7)
        self.stPS.grid(row=self.rownumber, column=0,sticky=E)
        self.PathVar = IntVar()
        self.PathVar.set(0)
        Radiobutton(self.EntryFrame, text='Paralell', variable=self.PathVar, value = 0, command=self.DoIt ,indicatoron=0,width=7,).grid(row=self.rownumber+1, column=0, sticky = E)
        Radiobutton(self.EntryFrame, text=' Spiral ', variable=self.PathVar, value = 1, command=self.DoIt ,indicatoron=0,width=7,).grid(row=self.rownumber+2, column=0, sticky = E)

        self.stMove = Label(self.EntryFrame, text='Movement',width=7)
        self.stMove.grid(row=self.rownumber, column=1,sticky=W,padx=10)
        self.MovmentVar = IntVar()
        self.MovmentVar.set(0)
        Radiobutton(self.EntryFrame, text='Zero', variable=self.MovmentVar, value = 0, command=self.DoIt ,indicatoron=0,width=7,).grid(row=self.rownumber+1, column=1, sticky = W,padx=10)
        Radiobutton(self.EntryFrame, text='G41/G42', variable=self.MovmentVar, value = 1, command=self.DoIt ,indicatoron=0,width=7,).grid(row=self.rownumber+2, column=1, sticky = W,padx=10)

        self.stDir = Label(self.EntryFrame, text='Direction',width=7)
        self.stDir.grid(row=self.rownumber, column=1,sticky=N)
        self.DirVar = StringVar()
        self.DirVar.set('CCW')
        Radiobutton(self.EntryFrame, text='CCW', variable=self.DirVar, value = 'CCW', command=self.DoIt ,indicatoron=0,width=7,).grid(row=self.rownumber+1, column=1, sticky = N)
        Radiobutton(self.EntryFrame, text='CW', variable=self.DirVar, value = 'CW', command=self.DoIt ,indicatoron=0,width=7,).grid(row=self.rownumber+2, column=1, sticky = N)
              
        self.st13 = Label(self.EntryFrame, text='Units',width=5)
        self.st13.grid(row=self.rownumber, column=1,sticky=E)
        self.UnitVar = IntVar()
        self.UnitVar.set(1)
        Radiobutton(self.EntryFrame, text='Inch', variable=self.UnitVar, value = 0, command=self.Change_Units ,indicatoron=0,width=5,).grid(row=self.rownumber+1, column=1,sticky=E)
        Radiobutton(self.EntryFrame, text=' MM ', variable=self.UnitVar, value = 1, command=self.Change_Units ,indicatoron=0,width=5,).grid(row=self.rownumber+2, column=1,sticky=E)

        self.rownumber += 3

        self.st01 = Label(self.EntryFrame, text='Preamble')
        self.st01.grid(row=self.rownumber, column=0)
        self.PreambleVar = StringVar()
        self.PreambleVar.set('G17 G21 G90 G64 P0.01%s M3 S3000 M7' %(toolChange))
        self.Preamble = Entry(self.EntryFrame, textvariable=self.PreambleVar ,width=35)
        self.Preamble.grid(row=self.rownumber, column=1)
        self.NormalColor =  self.Preamble.cget('bg')

        #Tool
        self.rownumber += 1
        self.st10 = Label(self.EntryFrame, text='Tool Diameter')
        self.st10.grid(row=self.rownumber, column=0)
        self.ToolDiameterVar = StringVar()
        self.ToolDiameterVar.set('5.0')
        self.ToolDiameter = Entry(self.EntryFrame, textvariable=self.ToolDiameterVar ,width=8)
        self.ToolDiameter.grid(row=self.rownumber, column=1,sticky=W)

        self.rownumber += 1
        self.st10a = Label(self.EntryFrame, text='ToolNumber (T)')
        self.st10a.grid(row=self.rownumber, column=0)
        self.ToolNumberVar = IntVar()
        self.ToolNumberVar.set('0')
        self.ToolNumber = Spinbox(self.EntryFrame, textvariable=self.ToolNumberVar,from_=0,to=99 ,width=4, command=self.ChangeTool)
        self.ToolNumber.grid(row=self.rownumber, column=1,sticky=W)

        self.st10ab = Label(self.EntryFrame, text='             ToolOffsetNumber (D)')
        self.st10ab.grid(row=self.rownumber, column=1,sticky=N)
        self.ToolOffsetNumberVar = IntVar()
        self.ToolOffsetNumberVar.set('1')
        self.ToolOffsetNumber = Entry(self.EntryFrame, textvariable=self.ToolOffsetNumberVar ,width=3)
        self.ToolOffsetNumber.grid(row=self.rownumber, column=1,sticky=E)
        self.rownumber += 1
        self.st02 = Label(self.EntryFrame, text='X Center ')
        self.st02.grid(row=self.rownumber, column=0)
        self.XPocketCenterVar = StringVar()
        self.XPocketCenterVar.set('30.0')
        self.XPocketCenter = Entry(self.EntryFrame, textvariable=self.XPocketCenterVar ,width=10)
        self.XPocketCenter.grid(row=self.rownumber, column=1,sticky=W)
        self.rownumber += 1
        self.st03 = Label(self.EntryFrame, text='Y Center ')
        self.st03.grid(row=self.rownumber, column=0)
        self.YPocketCenterVar = StringVar()
        self.YPocketCenterVar.set('30.0')
        self.YPocketCenter = Entry(self.EntryFrame, textvariable=self.YPocketCenterVar ,width=10)
        self.YPocketCenter.grid(row=self.rownumber, column=1,sticky=W)

        self.rownumber += 1
        self.st04 = Label(self.EntryFrame, text='Dimension (X/D,Y)')
        self.st04.grid(row=self.rownumber, column=0)
        self.PocketXVar = StringVar()
        self.PocketXVar.set('40.0')
        self.PocketX = Entry(self.EntryFrame, textvariable=self.PocketXVar ,width=15)
        self.PocketX.grid(row=self.rownumber, column=1, sticky = W)
        self.PocketYVar = StringVar()
        self.PocketYVar.set('40.0')
        self.PocketY = Entry(self.EntryFrame, textvariable=self.PocketYVar ,width=15)
        self.PocketY.grid(row=self.rownumber, column=1, sticky = E)

        self.rownumber +=1
        self.st05 = Label(self.EntryFrame, text='StepoverXY ')
        self.st05.grid(row=self.rownumber, column=0)
        self.StepoverVar = StringVar()
        self.StepoverVar.set('2.0')
        self.Stepover = Entry(self.EntryFrame, textvariable=self.StepoverVar ,width=5)
        self.Stepover.grid(row=self.rownumber, column=1,sticky=W)
        self.Finish = IntVar()
        self.Finish.set(0)
        Checkbutton(self.EntryFrame, text='Finish Contour', variable=self.Finish, onvalue = 1,offvalue=0, command=self.DoIt ).grid(row=self.rownumber, column=1,sticky=E)

        self.rownumber +=1
        self.stOffsetXY = Label(self.EntryFrame, text='OffsetXY ')
        self.stOffsetXY.grid(row=self.rownumber, column=0)
        self.OffsetXYVar = StringVar()
        self.OffsetXYVar.set('2.0')
        self.OffsetXY = Entry(self.EntryFrame, textvariable=self.OffsetXYVar ,width=5)
        self.OffsetXY.grid(row=self.rownumber, column=1,sticky=W)
        self.stOffsetZ = Label(self.EntryFrame, text='OffsetZ ')
        self.stOffsetZ.grid(row=self.rownumber, column=1,sticky=N )
        self.OffsetZVar = StringVar()
        self.OffsetZVar.set('0.0')
        self.OffsetZ = Entry(self.EntryFrame, textvariable=self.OffsetZVar ,width=5)
        self.OffsetZ.grid(row=self.rownumber, column=1,sticky=E)
        self.rownumber +=1
        self.st06 = Label(self.EntryFrame, text='Final Depth')
        self.st06.grid(row=self.rownumber, column=0)
        self.FinalDepth = StringVar()
        self.FinalDepth.set('1.0')
        self.HoleDepth = Entry(self.EntryFrame, textvariable=self.FinalDepth ,width=8)
        self.HoleDepth.grid(row=self.rownumber, column=1,sticky=W)

        self.st06a = Label(self.EntryFrame, text='Z Stepover')
        self.st06a.grid(row=self.rownumber, column=1,sticky=N)
        self.ZStepoverVar = StringVar()
        self.ZStepoverVar.set('1.0')
        self.ZStepover = Entry(self.EntryFrame, textvariable=self.ZStepoverVar ,width=8)
        self.ZStepover.grid(row=self.rownumber, column=1,sticky=E)

        self.rownumber +=1
        self.st08 = Label(self.EntryFrame, text='Safe Z')
        self.st08.grid(row=self.rownumber, column=0)
        self.SafeZVar = StringVar()
        self.SafeZVar.set('5')
        self.SafeZ = Entry(self.EntryFrame, width=8, textvariable = self.SafeZVar)
        self.SafeZ.grid(row=self.rownumber, column=1,sticky=W)

        self.st08a = Label(self.EntryFrame, text='Rapid Z down')
        self.st08a.grid(row=self.rownumber, column=1,sticky=N)
        self.RapidZVar = StringVar()
        self.RapidZVar.set('2')
        self.RapidZ = Entry(self.EntryFrame, width=8, textvariable = self.RapidZVar)
        self.RapidZ.grid(row=self.rownumber, column=1,sticky=E)

        self.rownumber +=1 
        self.st09 = Label(self.EntryFrame, text='Feedspeed XY')
        self.st09.grid(row=self.rownumber, column=0)
        self.FeedspeedVar = StringVar()
        self.FeedspeedVar.set('250.0')
        self.Feedspeed = Entry(self.EntryFrame, textvariable=self.FeedspeedVar ,width=8)
        self.Feedspeed.grid(row=self.rownumber, column=1,sticky=W)

        self.st09a = Label(self.EntryFrame, text='Feedspeed Z')
        self.st09a.grid(row=self.rownumber, column=1,sticky=N)
        self.FeedspeedZVar = StringVar()
        self.FeedspeedZVar.set('100.0')
        self.FeedspeedZ = Entry(self.EntryFrame, textvariable=self.FeedspeedZVar ,width=8)
        self.FeedspeedZ.grid(row=self.rownumber, column=1,sticky=E)


        self.rownumber += 1
        self.st11 = Label(self.EntryFrame, text='Postamble')
        self.st11.grid(row=self.rownumber, column=0)
        self.PostambleVar = StringVar()
        self.PostambleVar.set('M5 M9 M2')
        self.Postamble = Entry(self.EntryFrame, textvariable=self.PostambleVar ,width=35)
        self.Postamble.grid(row=self.rownumber, column=1,sticky=W)

        self.rownumber += 1

        self.DoItButton = Button(self.EntryFrame, text='Recalculate', command=self.DoIt)
        self.DoItButton.grid(row=self.rownumber, column=0)

        self.ToClipboard = Button(self.EntryFrame, text='To Clipboard', command=self.CopyClipboard)
        self.ToClipboard.grid(row=self.rownumber, column=1)

        if IN_AXIS:
            self.quitButton = Button(self, text='Write to AXIS and Quit',command=self.WriteToAxis)
        else:
            self.quitButton = Button(self, text='Quit', command=self.quit)
        self.quitButton.grid(row=13, column=0, sticky=S)

    def Change_Units(self):
        if (self.UnitVar.get() == 0) :
            #Inch 
            self.PreambleVar.set('G17 G20 G90 G64 P0.001%s M3 S3000 M7' %(toolChange))
        else :
            #MM
            self.PreambleVar.set('G17 G21 G90 G64 P0.01%s M3 S3000 M7' %(toolChange))
        
    def ChangeTool(self):
        global toolChange
        print 'Inside ChangeTool T:'+str(self.ToolNumberVar.get())
        if (self.ToolNumberVar.get() > 0):
            toolChange = (" M6 T%d" %(int(self.ToolNumberVar.get())))
        else:
            toolChange = ''
        self.Change_Units()

    def DoIt(self):
        # if g41/42 enable tooloffsetnumber entry
        if self.MovmentVar.get() == 0:
            self.ToolOffsetNumber.configure(state=DISABLED)
        else :
            self.ToolOffsetNumber.configure(state=NORMAL)

        if self.Finish.get() == 1:
            self.OffsetXY.configure(state=DISABLED)
            self.OffsetZ.configure(state=DISABLED)
        else:
            self.OffsetXY.configure(state=NORMAL)
            self.OffsetZ.configure(state=NORMAL)

        # range check inputs for gross errors
        self.PocketX.configure( bg = self.NormalColor )
        if (float(self.PocketX.get()) <= 0.0 ):
            self.PocketX.configure( bg = 'red')
            return

        self.PocketY.configure( bg = self.NormalColor )
        if (float(self.PocketY.get()) <= 0.0 ):
            self.PocketY.configure( bg = 'red')
            return

        self.Stepover.configure( bg = self.NormalColor )
        if (float(self.Stepover.get()) <= 0.0 ):
            self.Stepover.configure( bg = 'red')
            return

        self.HoleDepth.configure( bg = self.NormalColor )
        #self.Peck.configure( bg = self.NormalColor )
        self.SafeZ.configure( bg = self.NormalColor )

        self.Feedspeed.configure( bg = self.NormalColor )
        if float(self.Feedspeed.get()) <= 0.0:
            self.Feedspeed.configure( bg = 'red' )
            return

        self.ToolDiameter.configure( bg = self.NormalColor )
        if float(self.ToolDiameter.get()) <= 0.0:
            self.ToolDiameter.configure( bg = 'red' )
            return
        # erase old holes/display objects as needed
        for draw in self.CanvasDrawings:
            self.PreviewCanvas.delete(draw)
        self.CanvasDrawings = []

        # erase old gcode as needed
        self.gcode = []
        self.gcode.append('( Code generated by pocket.py widget )')
        self.gcode.append('( by Sammel Lothar - 2010 )')
        self.gcode.append(self.PreambleVar.get()) # lead in
        #move to Pocket Start
        self.gcode.append( 'G0 Z%.4f ' %(float(self.SafeZVar.get()))) #G0 Zsafe
        self.gcode.append( 'G0 X%.4f Y%.4f ' %(float(self.XPocketCenterVar.get()),float(self.YPocketCenterVar.get())))#G0 CenterZsafe
        #get the inputs
        speedZ=float(self.FeedspeedZVar.get())
        speedXY=float(self.FeedspeedVar.get())
        ToolDiameterRad = float(self.ToolDiameter.get()) / 2.0
        ToolDiameter = float(self.ToolDiameter.get())

        Spacing  = float(self.StepoverVar.get()) #spacing 
        MaterialallowanceXY=float(self.OffsetXY.get())
        MaterialallowanceZ=float(self.OffsetZ.get())
        tempz=float(self.FinalDepth.get())-MaterialallowanceZ
        # Z depth calculation
        if tempz > 0:
            tempz = tempz * (-1)
        stepoverz=float(self.ZStepover.get())
        if stepoverz > 0:
            stepoverz = stepoverz * (-1)
        firstRun = True
        #----------------------
        #circulare pocketing
        #---------------------
        if self.ShapeVar.get() == 0: #circel
            pocket_length_x=float(self.PocketXVar.get())
            centerx = float(self.XPocketCenter.get())
            centery = float(self.YPocketCenter.get())

            Scale = float(self.PocketXVar.get()) * 1.2 / 300.0
            # temps used for circular Pockets
            self.gcode.append('( %.4f Diameter Circular Pocket at %.4f,%.4f )'
                %(float(self.PocketXVar.get()),
                  float(self.XPocketCenterVar.get()),
                  float(self.YPocketCenterVar.get()) ))
            self.PocketY.configure(state=DISABLED)
            PocketRadius = float(self.PocketXVar.get())/2.0
            
            self.CanvasDrawings.append(self.PreviewCanvas.create_oval(
                150-PocketRadius/Scale,
                150-PocketRadius/Scale,
                150+PocketRadius/Scale,
                150+PocketRadius/Scale,outline='Black' ))
            if self.PathVar.get() == 0: #cricel parallell path 
                if self.Finish.get() == 1:
                    numberofcircels= int((PocketRadius-ToolDiameterRad)/Spacing)
                else:
                    numberofcircels= int((PocketRadius-ToolDiameterRad-MaterialallowanceXY)/Spacing)
                canvasoldX=150 
                canvasoldY=150 
                for cir in range(numberofcircels,1,-1):
                    canvasnewY= 150+(Spacing*(cir))/Scale
                    
                    PocketRadius= canvasnewY
                    self.CanvasDrawings.append(self.PreviewCanvas.create_line(150,150,canvasnewY,150,fill='red'))
                    self.CanvasDrawings.append(self.PreviewCanvas.create_oval(
                        PocketRadius,
                        PocketRadius,
                        300-PocketRadius,
                        300-PocketRadius, outline='Red'))
                    canvasoldY=canvasnewY
                #G-code parallel zero line Circel
                PocketRadius = float(self.PocketXVar.get())/2.0 #variable neww loadet after change from canvas
                self.gcode.append('(Parallel ZeroPath Circular Pocket )')
                self.gcode.append('G1 Z0.00 F%.2f (Move to Z Zero for incremental Z pathes )' %speedZ)
                centerx = float(self.XPocketCenter.get())
                # keep here in while till final depth is reatched
                while tempz < 0 :
                    gword = 91
                    if firstRun:
                        firstRun = False
                        gword = 90
                    if tempz < stepoverz:
                        self.gcode.append('G1 G%d Z%.3f F%.2f ' %(gword,stepoverz,speedZ))
                    else:
                        self.gcode.append('G1 G%d Z%.3f F%.2f ' %(gword,tempz,speedZ))
                    tempz=tempz-stepoverz
                    for cir in xrange(1,numberofcircels):
                        self.gcode.append('G1 G90 X%.3f F%.2f ' %((centerx+(cir*Spacing)),speedXY))
                        if self.DirVar.get() == 'CCW':
                            self.gcode.append('G3 I-%.3f' %(cir*Spacing))
                        else:
                            self.gcode.append('G2 I-%.3f' %(cir*Spacing))
                    if self.Finish.get() == 1:
                        #canval finish circel
                        corner=((PocketRadius-ToolDiameterRad))/Scale
                        self.CanvasDrawings.append(self.PreviewCanvas.create_line(150,150,150+corner,150,fill='red'))
                        self.CanvasDrawings.append(self.PreviewCanvas.create_oval(150-corner,150-corner,150+corner,150+corner, outline='Red'))
                        #Gcode finish
                        self.gcode.append('G1 G90 X%.3f' %((centerx+PocketRadius-ToolDiameterRad)))
                        if self.DirVar.get() == 'CCW':
                            self.gcode.append('G3 I-%.3f' %(PocketRadius-ToolDiameterRad))
                        else:
                            self.gcode.append('G2 I-%.3f' %(PocketRadius-ToolDiameterRad))
                            
                    #go to Zsafe before moving to center
                    if(tempz >= 0):
                        self.gcode.append( 'G0 Z%.4f ' %(float(self.SafeZVar.get()))) #G0 Zsafe
                    self.gcode.append( 'G1 X%.4f Y%.4f ' %(float(self.XPocketCenterVar.get()),float(self.YPocketCenterVar.get())))# Center
                self.gcode.append( 'G0 Z%.4f ' %(float(self.SafeZVar.get()))) #G0 Zsafe
            else:#cirel_spiral
                #Canvas Circel Spiral
                numberofcircels= int((PocketRadius-ToolDiameterRad)/Spacing)*2
                vsh=(Spacing/Scale)/2.0
                self.CanvasDrawings.append(self.PreviewCanvas.create_line(150,150,150+(Spacing/Scale),150, fill = 'red'))
                for arc_curve in xrange(1,numberofcircels+1):
                    if arc_curve %2 == 0:#geradezahl
                        if arc_curve==2:
                            #canvas_new_Y =150-((arc_curve*(versatz/2.0))/scale)
                            self.CanvasDrawings.append(self.PreviewCanvas.create_arc(canvas_new_Y,canvas_new_Y,300-canvas_new_Y+vsh,300-canvas_new_Y,start=180,extent=180,outline='red',style=ARC))
                        else:
                            canvas_new_Y =150-((arc_curve*(Spacing/2.0))/Scale)
                            self.CanvasDrawings.append(self.PreviewCanvas.create_arc(canvas_new_Y+vsh,canvas_new_Y,300-canvas_new_Y+vsh,300-canvas_new_Y,start=180,extent=180,outline='red',style=ARC))
                    else:
                        if arc_curve ==1 :
                            canvas_new_Y =150-((arc_curve*Spacing)/Scale)
                            self.CanvasDrawings.append(self.PreviewCanvas.create_arc(canvas_new_Y,canvas_new_Y,300-canvas_new_Y,300-canvas_new_Y,start=0,extent=180,outline='red',style=ARC))
                        else:
                            canvas_new_Y =150-((arc_curve*(Spacing/2.0))/Scale)
                            self.CanvasDrawings.append(self.PreviewCanvas.create_arc(canvas_new_Y,canvas_new_Y,300-canvas_new_Y,300-canvas_new_Y,start=0,extent=180,outline='red',style=ARC))
                    Radius=(PocketRadius-ToolDiameterRad)/Scale
                    self.CanvasDrawings.append(self.PreviewCanvas.create_oval(        
                        150-Radius+(vsh/2),
                        150-Radius+(vsh/2),
                        150+Radius-(vsh/2),
                        150+Radius-(vsh/2), outline='Red'))
                    self.CanvasDrawings.append(self.PreviewCanvas.create_line(150,150,150+Radius-(vsh/2),150, fill = 'red'))        
                self.CanvasDrawings.append(self.PreviewCanvas.create_text((150,280),text="Grafic may differ to G_code on some Enterys" ))        
                if self.Finish.get()==1:
                    Radius=(PocketRadius-ToolDiameterRad)/Scale
                    self.CanvasDrawings.append(self.PreviewCanvas.create_oval(        
                        150-Radius+(vsh/2),
                        150-Radius+(vsh/2),
                        150+Radius-(vsh/2),
                        150+Radius-(vsh/2), outline='Red'))
                #Gcode circel Spiral
                # keep here in while till final depth is reatched
                self.gcode.append('( Spiral Zero Path )')
                self.gcode.append('G1 Z0.00 F%.2f (Move to Z Zero for incremental Z pathes )' %speedZ)
                while tempz < 0 :
                    gword = 91
                    if firstRun:
                        firstRun = False
                        gword = 90
                    if tempz < stepoverz:
                        self.gcode.append('G1 G%d Z%.3f F%.2f ' %(gword,stepoverz,speedZ))
                    else:
                        self.gcode.append('G1 G%d Z%.3f F%.2f ' %(gword,tempz,speedZ))
                    tempz=tempz-stepoverz
                    cycels=int((pocket_length_x-ToolDiameter)/Spacing/2.0) 
                    tempr=Spacing
                    tempI=1
                    cycle=1
                    self.gcode.append('G1 G90 X%.3f F%.2f ' %((centerx+tempr),speedXY))
                    while cycle < cycels:
                        self.gcode.append('G3 X%.3f I-%.3f ' %(centerx-(cycle*Spacing),(tempI*Spacing)))
                        cycle=cycle+1
                        tempI=tempI+0.5
                        self.gcode.append('G3 X%.3f I%.3f ' %(centerx+(cycle*Spacing),(tempI*Spacing)))
                        tempI=tempI+0.5
                    PocketRadius = float(self.PocketXVar.get())/2.0
                    newI= ((centerx+(cycle*Spacing))-(centerx-PocketRadius+ToolDiameterRad))/2.0
                    self.gcode.append('G3 X%.3f Y%.3f I-%.3f ' %(centerx-PocketRadius+ToolDiameterRad,centery,newI))
                    self.gcode.append('G3 I%.3f ' %(PocketRadius-ToolDiameterRad))
                    #go to Zsafe before moving to center
                    if(tempz >= 0):
                        self.gcode.append( 'G0 Z%.4f ' %(float(self.SafeZVar.get()))) #G0 Zsafe
                    self.gcode.append( 'G1 X%.4f Y%.4f ' %(centerx,centery))# Center
                self.gcode.append( 'G0 Z%.4f ' %(float(self.SafeZVar.get()))) #G0 Zsafe
        #---------------
        # rectancular pocketing
        #----------------
        if self.ShapeVar.get() == 2:      # rectangle
            self.PocketY.configure(state=NORMAL)
            pocket_length_x=float(self.PocketXVar.get())
            pocket_length_y=float(self.PocketYVar.get())
            centerx = float(self.XPocketCenter.get())
            centery = float(self.YPocketCenter.get())

            self.gcode.append('( %.4fx%.4f rectangular Pocket at %.4f,%.4f )'
                  %(pocket_length_x,pocket_length_y,centerx,centery))

            if pocket_length_x > pocket_length_y:
                Scale = pocket_length_x * 1.2 / 300.0
            else:
                Scale = pocket_length_y * 1.2 / 300.0
            #draw outer rect on canvas 
            self.CanvasDrawings.append(self.PreviewCanvas.create_rectangle(
                150-(pocket_length_x/2.0/Scale),
                150-(pocket_length_y/2.0/Scale),
                150+(pocket_length_x/2.0/Scale),
                150+(pocket_length_y/2.0/Scale),outline='Black'))
  
            if self.PathVar.get() == 0: #Parallel
                self.gcode.append('( Parallel Zero Path )')
                #calculate How many times into while
                offsetxy=float(self.OffsetXYVar.get())
                if self.Finish.get() ==1: #fiinish path
                    offsetxy=0.0
                if pocket_length_x > pocket_length_y:
                    rec_cycels=int((pocket_length_y-ToolDiameter-offsetxy)/Spacing/2.0)
                else:
                    rec_cycels=int((pocket_length_x-ToolDiameter-offsetxy)/Spacing/2.0)
                first_length_x=((pocket_length_x-ToolDiameter)/2.0)-(rec_cycels*Spacing)
                first_length_y=((pocket_length_y-ToolDiameter)/2.0)-(rec_cycels*Spacing)
                self.gcode.append('G1 G90 Z0.00 F%.2f (Move to Z Zero for incremental Z pathes )' %speedZ)
                while tempz < 0 :
                    gword = 91
                    if firstRun:
                        firstRun = False
                        gword = 90
                    if tempz < stepoverz:
                        self.gcode.append('G1 G%d Z%.3f F%.2f ' %(gword,stepoverz,speedZ))
                    else:
                        self.gcode.append('G1 G%d Z%.3f F%.2f ' %(gword,tempz,speedZ))
                    tempz=tempz-stepoverz
                    while_value=0
                    canvasoldX=150
                    canvasoldY=150
                    while while_value < rec_cycels:
                        canvas_new_X=(first_length_x+(while_value*Spacing))/Scale
                        canvas_new_Y=(first_length_y+(while_value*Spacing))/Scale
                        self.CanvasDrawings.append(self.PreviewCanvas.create_rectangle(
                                        150-canvas_new_X,150-canvas_new_Y,150+canvas_new_X,150+canvas_new_Y, outline='red'))
                        self.gcode.append('G1 G90 X%.3f Y%.3f F%.2f ' %(centerx+first_length_x+(while_value*Spacing)
                            ,centery+first_length_y+(while_value*Spacing),speedXY))
                        self.CanvasDrawings.append(self.PreviewCanvas.create_line(canvasoldX,canvasoldY,150+canvas_new_X,150-canvas_new_Y, fill='red'))
                        canvasoldX=150+canvas_new_X                        
                        canvasoldY=150-canvas_new_Y                        
                        self.gcode.append('G1 X%.3f ' %(centerx-first_length_x-(while_value*Spacing)))
                        self.gcode.append('G1 Y%.3f ' %(centery-first_length_y-(while_value*Spacing)))
                        self.gcode.append('G1 X%.3f ' %(centerx+first_length_x+(while_value*Spacing)))
                        self.gcode.append('G1 Y%.3f ' %(centery+first_length_y+(while_value*Spacing)))
                        while_value=while_value+1
                    if self.Finish.get() == 1:
                        self.gcode.append('G1 G90 X%.3f Y%.3f ' %((centerx+(pocket_length_x/2.0)-ToolDiameterRad),(centery+(pocket_length_y/2.0)-ToolDiameterRad)))
                        self.CanvasDrawings.append(self.PreviewCanvas.create_line(canvasoldX,canvasoldY,
                            150+((pocket_length_x-ToolDiameter)/2.0/Scale),
                            150-((pocket_length_y-ToolDiameter)/2.0/Scale), fill='red'))
                        self.gcode.append('G1 X%.3f ' %(centerx-(pocket_length_x/2.0)+ToolDiameterRad))
                        self.gcode.append('G1 Y%.3f ' %(centery-(pocket_length_y/2.0)+ToolDiameterRad))
                        self.gcode.append('G1 X%.3f ' %(centerx+(pocket_length_x/2.0)-ToolDiameterRad))
                        self.gcode.append('G1 Y%.3f ' %(centery+(pocket_length_y/2.0)-ToolDiameterRad))
                        self.CanvasDrawings.append(self.PreviewCanvas.create_rectangle(
                                        150-((pocket_length_x-ToolDiameter)/2.0/Scale),
                                        150-((pocket_length_y-ToolDiameter)/2.0/Scale),
                                        150+((pocket_length_x-ToolDiameter)/2.0/Scale),
                                        150+((pocket_length_y-ToolDiameter)/2.0/Scale), outline='red'))
                    #go to Zsafe before moving to center
                    if(tempz >= 0):
                        self.gcode.append( 'G0 Z%.4f ' %(float(self.SafeZVar.get()))) #G0 Zsafe
                    self.gcode.append( 'G1 G90 X%.4f Y%.4f ' %(centerx,centery))# Center
                self.gcode.append( 'G0 Z%.4f ' %(float(self.SafeZVar.get()))) #G0 Zsafe
            
            
            #----------
            #spiral rectangular
            #----------
            else :#Spiral Rectangular 
                #calculate How many times into while
                self.gcode.append('( Spiral Zero Path )')
                if pocket_length_x > pocket_length_y:
                    rec_cycels=int((pocket_length_x-ToolDiameter)/Spacing/2.0)
                else:
                    rec_cycels=int((pocket_length_y-ToolDiameter)/Spacing/2.0)
                new_x_stepover=(pocket_length_x-ToolDiameter)/(rec_cycels*2)
                new_y_stepover=(pocket_length_y-ToolDiameter)/(rec_cycels*2)
                while tempz < 0 :
                    gword = 91
                    if firstRun:
                        firstRun = False
                        gword = 90
                    if tempz < stepoverz:
                        self.gcode.append('G1 G%d Z%.3f F%.2f ' %(gword,stepoverz,speedZ))
                    else:
                        self.gcode.append('G1 G%d Z%.3f F%.2f ' %(gword,tempz,speedZ))
                    tempz=tempz-stepoverz
                    cycle=1
                    tempx=new_x_stepover
                    tempy=new_y_stepover
                    canvasoldX=150
                    canvasoldY=150
                    while cycle < rec_cycels:
                        self.gcode.append('G1 G91 X%.3f F%.2f ' %(tempx,speedXY))
                        canvas_new_X=canvasoldX+(tempx/Scale)
                        self.CanvasDrawings.append(self.PreviewCanvas.create_line(canvasoldX,canvasoldY,canvas_new_X,canvasoldY, fill='red'))
                        canvasoldX=canvas_new_X
                        self.gcode.append('G1 Y%.3f ' %(tempy))
                        canvas_new_Y=canvasoldY-(tempy/Scale)
                        self.CanvasDrawings.append(self.PreviewCanvas.create_line(canvasoldX,canvasoldY,canvasoldX,canvas_new_Y, fill='red'))
                        canvasoldY=canvas_new_Y
                        tempx=tempx+new_x_stepover
                        tempy=tempy+new_y_stepover
                        self.gcode.append('G1 X-%.3f ' %(tempx))
                        canvas_new_X=canvasoldX-(tempx/Scale)
                        self.CanvasDrawings.append(self.PreviewCanvas.create_line(canvasoldX,canvasoldY,canvas_new_X,canvasoldY, fill='red'))
                        canvasoldX=canvas_new_X
                        self.gcode.append('G1 Y-%.3f ' %(tempy))
                        canvas_new_Y=canvasoldY+(tempy/Scale)
                        self.CanvasDrawings.append(self.PreviewCanvas.create_line(canvasoldX,canvasoldY,canvasoldX,canvas_new_Y, fill='red'))
                        canvasoldY=canvas_new_Y
                        tempx=tempx+new_x_stepover
                        tempy=tempy+new_y_stepover
                        cycle=cycle+1
                    self.gcode.append('G1 X%.3f ' %(tempx-new_x_stepover))
                    canvas_new_X=canvasoldX+((tempx-new_x_stepover)/Scale)
                    self.CanvasDrawings.append(self.PreviewCanvas.create_line(canvasoldX,canvasoldY,canvas_new_X,canvasoldY, fill='red'))
                    canvasoldX=canvas_new_X
                    if self.Finish.get() == 1:
                        self.gcode.append('G1 G90 X%.3f Y%.3f ' %((centerx+(pocket_length_x/2.0)-ToolDiameterRad),(centery+(pocket_length_y/2.0)-ToolDiameterRad)))
                        self.CanvasDrawings.append(self.PreviewCanvas.create_line(canvasoldX,canvasoldY,
                            150+((pocket_length_x-ToolDiameter)/2.0/Scale),
                            150-((pocket_length_y-ToolDiameter)/2.0/Scale), fill='red'))
                        self.gcode.append('G1 X%.3f ' %(centerx-(pocket_length_x/2.0)+ToolDiameterRad))
                        self.gcode.append('G1 Y%.3f ' %(centery-(pocket_length_y/2.0)+ToolDiameterRad))
                        self.gcode.append('G1 X%.3f ' %(centerx+(pocket_length_x/2.0)-ToolDiameterRad))
                        self.gcode.append('G1 Y%.3f ' %(centery+(pocket_length_y/2.0)-ToolDiameterRad))
                        self.CanvasDrawings.append(self.PreviewCanvas.create_rectangle(
                                        150-((pocket_length_x-ToolDiameter)/2.0/Scale),
                                        150-((pocket_length_y-ToolDiameter)/2.0/Scale),
                                        150+((pocket_length_x-ToolDiameter)/2.0/Scale),
                                        150+((pocket_length_y-ToolDiameter)/2.0/Scale), outline='red'))
                      
                    #go to Zsafe before moving to center
                    if(tempz >= 0):
                        self.gcode.append( 'G0 Z%.4f ' %(float(self.SafeZVar.get()))) #G0 Zsafe
                    self.gcode.append( 'G1 G90 X%.4f Y%.4f ' %(centerx,centery))
                self.gcode.append( 'G0 Z%.4f ' %(float(self.SafeZVar.get()))) #G0 Zsafe
                        
                
        #G-code
        self.gcode.append(self.PostambleVar.get())
        if self.MovmentVar.get() == 1:
            tkMessageBox.showinfo("Pocket V1"," G41/42 Not implemented ")
            self.MovmentVar.set(0)   
        #Tool on canvas
        self.CanvasDrawings.append(self.PreviewCanvas.create_oval(
            150-ToolDiameterRad/Scale,
            150-ToolDiameterRad/Scale,
            150+ToolDiameterRad/Scale,
            150+ToolDiameterRad/Scale,fill='Blue' ))
        self.CanvasDrawings.append(self.PreviewCanvas.create_oval(10,275,25,290,fill='Blue' ))
        self.CanvasDrawings.append(self.PreviewCanvas.create_text((20,270),text="Tool" ))        
 
    def CopyClipboard(self):
        self.clipboard_clear()
        for line in self.gcode:
            self.clipboard_append(line+'\n')

    def WriteToAxis(self):
        for line in self.gcode:
            sys.stdout.write(line+'\n')
        self.quit()

app = Application()
app.master.title("Pocket.py 1.0 by Sammel Lothar")
app.mainloop()

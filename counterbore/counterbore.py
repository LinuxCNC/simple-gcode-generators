#!/usr/local/bin/python

"""
    Counterbore G-Code Generator
    Version 1.3.1
    Copyright (C) <2008>  <John Thornton>

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

    e-mail me any suggestions to "bjt 128 at gmail dot com"
    If you make money using this software
    you must donate $20 USD to a local food bank
    or the food police will get you! Think of others from time to time...
    
    To make it a menu item in Ubuntu use the Alacarte Menu Editor and add 
    the command python YourPathToThisFile/face.py
    make sure you have made the file execuatble by right
    clicking and selecting properties then Permissions and Execute
    
    To use with EMC2 see the instructions at: 
    http://wiki.linuxcnc.org/cgi-bin/emcinfo.pl?Simple_EMC_G-Code_Generators
    
    1.2 Fix bug that incorrectly calculated the number of circles when the tool
    	was less than 1/2 the diameter of the hole
    1.3 Fix bug that did not calculate the depth of the hole if it was a single cut	

"""
from Tkinter import *
from math import *
import tkMessageBox
import os

IN_AXIS = os.environ.has_key("AXIS_PROGRESS_BAR")

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid()
        self.createMenu()
        self.createWidgets()

    def createMenu(self):
        #Create the Menu base
        self.menu = Menu(self)
        #Add the Menu
        self.master.config(menu=self.menu)
        #Create our File menu
        self.FileMenu = Menu(self.menu)
        #Add our Menu to the Base Menu
        self.menu.add_cascade(label='File', menu=self.FileMenu)
        #Add items to the menu
        #self.FileMenu.add_command(label='New')#, command=self.Simple)
        #self.FileMenu.add_command(label='Open')#, command=self.Simple)
        #self.FileMenu.add_separator()
        self.FileMenu.add_command(label='Cancel', command=self.quit)
        
        self.EditMenu = Menu(self.menu)
        self.menu.add_cascade(label='Edit', menu=self.EditMenu)
        #self.EditMenu.add_command(label='Copy')#, command=self.CopyClpBd)
        #self.EditMenu.add_command(label='Select All')#, command=self.SelectAllText)
        #self.EditMenu.add_command(label='Delete All')#, command=self.ClearTextBox)
        #self.EditMenu.add_separator()
        #self.EditMenu.add_command(label='Preferences')#, command=self.Simple)
        #self.EditMenu.add_command(label='NC Directory')#, command=self.NcFileDirectory)
        
        self.HelpMenu = Menu(self.menu)
        self.menu.add_cascade(label='Help', menu=self.HelpMenu)
        self.HelpMenu.add_command(label='Help Info', command=self.HelpInfo)
        self.HelpMenu.add_command(label='About', command=self.HelpAbout)


    def createWidgets(self):
        self.title = Label(self, text='Socket Head Cap Screw Counterbore G-Code Generator')
        self.title.grid(row=0, column=0, columnspan=10)

        self.cl1 = Label(self, text=' Number SHCS ')
        self.cl1.grid(row=1, column=0)
        self.SHCS1=[(' 0',1),(' 1',2),(' 2',3),(' 3',4),(' 4',5),
        (' 5',6),(' 6',7),(' 8',8),('10',9),('12',10)]
        self.var1 = IntVar()
        for text, value in self.SHCS1:
            self.rb1 = Radiobutton(self, text=text, value=value, variable=self.var1,
            font="monospace 10")
            self.rb1.grid(column=0,row=value+1)
            self.rb1.bind("<ButtonRelease-1>", self.rb1event)
        self.var1.set(0)
        
        self.cl2 = Label(self, text=' Fraction SHCS ')
        self.cl2.grid(row=1, column=1)
        self.SHCS2=[('  1/4',1),(' 5/16',2),('  3/8',3),(' 7/16',4),('  1/2',5),
        (' 9/16',6),('  5/8',7),('  3/4',8),('  7/8',9),('1    ',10),
        ('1-1/8',11),('1-1/4',12),('1-1/2',13),('1-3/4',14),('2    ',15)]
        self.var2 = IntVar()
        for text, value in self.SHCS2:
            self.rb2=Radiobutton(self, text=text, value=value, variable=self.var2,
            font="monospace 10")
            self.rb2.grid(column=1,row=value+1)
            self.rb2.bind("<ButtonRelease-1>", self.rb2event)

        self.cl3 = Label(self, text=' Metric SHCS ')
        self.cl3.grid(row=1, column=2)
        self.SHCS3=[('M1.6',1),('M2  ',2),('M2.5',3),('M3  ',4),('M4  ',5),
        ('M5  ',6),('M6  ',7),('M8  ',8),('M10 ',9),('M12 ',10),
        ('M14 ',11),('M16 ',12),('M18 ',13),('M20 ',14),('M24 ',15),
        ('M30 ',16),('M36 ',17),('M42 ',18),('M48 ',19)]
        self.var3 = IntVar()
        for text, value in self.SHCS3:
            self.rb3=Radiobutton(self, text=text, value=value, variable=self.var3,
            font="monospace 10")
            self.rb3.grid(column=2,row=value+1)
            self.rb3.bind("<ButtonRelease-1>", self.rb3event)

        self.st1 = Label(self, text='Hole Diameter')
        self.st1.grid(row=13, column=0)
        self.HoleDiameterVar = StringVar()
        self.HoleDiameterE = Entry(self, width=10, textvariable=self.HoleDiameterVar)
        self.HoleDiameterE.grid(row=14, column=0)
        self.HoleDiameterE.bind("<Return>", self.TabToNext)
        self.HoleDiameterE.bind("<KP_Enter>", self.TabToNext)

        self.st2 = Label(self, text='Hole Depth')
        self.st2.grid(row=15, column=0)
        self.HoleDepthVar = StringVar()
        self.HoleDepthE = Entry(self, width=10, textvariable=self.HoleDepthVar)
        self.HoleDepthE.grid(row=16, column=0)
        self.HoleDepthE.bind("<Return>", self.TabToNext)
        self.HoleDepthE.bind("<KP_Enter>", self.TabToNext)

        self.st3 = Label(self, text='Clearance Height Z  ')
        self.st3.grid(row=1, column=3)
        self.ClearanceHeightVar = StringVar()
        self.ClearanceHeightE = Entry(self, width=10, textvariable=self.ClearanceHeightVar)
        self.ClearanceHeightE.grid(row=2, column=3)
        self.ClearanceHeightVar.set('0.2500')
        self.ClearanceHeightE.bind("<Return>", self.TabToNext)
        self.ClearanceHeightE.bind("<KP_Enter>", self.TabToNext)

        self.st4 = Label(self, text='Material Top Z')
        self.st4.grid(row=3, column=3)
        self.MaterialTopVar = StringVar()
        self.MaterialTopE = Entry(self, width=10, textvariable=self.MaterialTopVar)
        self.MaterialTopE.grid(row=4, column=3)
        self.MaterialTopVar.set('0.000')
        self.MaterialTopE.bind("<Return>", self.TabToNext)
        self.MaterialTopE.bind("<KP_Enter>", self.TabToNext)

        self.st5 = Label(self, text='Start Height Z')
        self.st5.grid(row=5, column=3)
        self.StartHeightVar = StringVar()
        self.StartHeightE = Entry(self, width=10, textvariable=self.StartHeightVar)
        self.StartHeightE.grid(row=6, column=3)
        self.StartHeightVar.set('0.1000')
        self.StartHeightE.bind("<Return>", self.TabToNext)
        self.StartHeightE.bind("<KP_Enter>", self.TabToNext)
        
        self.st6 = Label(self, text='Tool Diameter')
        self.st6.grid(row=7, column=3)
        self.ToolDiameterVar = StringVar()
        self.ToolDiameterE = Entry(self, width=10, textvariable=self.ToolDiameterVar)
        self.ToolDiameterE.grid(row=8, column=3)
        self.ToolDiameterE.focus_set()
        self.ToolDiameterE.bind("<Return>", self.TabToNext)
        self.ToolDiameterE.bind("<KP_Enter>", self.TabToNext)
        
        self.st7 = Label(self, text='Spindle RPM')
        self.st7.grid(row=9, column=3)
        self.SpindleRPMVar = StringVar()
        self.SpindleRPME = Entry(self, width=10, textvariable=self.SpindleRPMVar)
        self.SpindleRPME.grid(row=10, column=3)
        self.SpindleRPME.bind("<Return>", self.TabToNext)
        self.SpindleRPME.bind("<KP_Enter>", self.TabToNext)

        self.st8 = Label(self, text='Feed Rate')
        self.st8.grid(row=11, column=3)
        self.FeedRateVar = StringVar()
        self.FeedRateE = Entry(self, width=10, textvariable=self.FeedRateVar)
        self.FeedRateE.grid(row=12, column=3)
        self.FeedRateVar.set('10.0')
        self.FeedRateE.bind("<Return>", self.TabToNext)
        self.FeedRateE.bind("<KP_Enter>", self.TabToNext)

        self.st9 = Label(self, text='Depth each Pass')
        self.st9.grid(row=13, column=3)
        self.DepthOfCutVar = StringVar()
        self.DepthOfCutE = Entry(self, width=10, textvariable=self.DepthOfCutVar)
        self.DepthOfCutE.grid(row=14, column=3)
        self.DepthOfCutE.bind("<Return>", self.TabToNext)
        self.DepthOfCutE.bind("<KP_Enter>", self.TabToNext)

        self.st10 = Label(self, text='Stepover %')
        self.st10.grid(row=15, column=3)
        self.StepOverVar = StringVar()
        self.StepOverE = Entry(self, width=10, textvariable=self.StepOverVar)
        self.StepOverE.grid(row=16, column=3)
        self.StepOverE.bind("<Return>", self.TabToNext)
        self.StepOverE.bind("<KP_Enter>", self.TabToNext)

        self.st11 = Label(self, text='Spiral Depth')
        self.st11.grid(row=17, column=3)
        self.SpiralDepthVar = StringVar()
        self.SpiralDepthE = Entry(self, width=10, textvariable=self.SpiralDepthVar)
        self.SpiralDepthE.grid(row=18, column=3)
        self.SpiralDepthE.bind("<Return>", self.TabToNext)
        self.SpiralDepthE.bind("<KP_Enter>", self.TabToNext)

        self.InsertEOFVar = IntVar()
        self.InsertEOF = Checkbutton(self, text='Insert EOF', 
            variable=self.InsertEOFVar, width=10)
        self.InsertEOF.grid(row=19, column=3, rowspan=2)
        self.InsertEOF.bind("<Return>", self.TabToNext)
        self.InsertEOF.bind("<KP_Enter>", self.TabToNext)

        self.st12 = Label(self, text='X Center')
        self.st12.grid(row=1, column=4, sticky=W)
        self.XCenterVar = StringVar()
        self.XCenterE = Entry(self, width=10, textvariable=self.XCenterVar)
        self.XCenterE.grid(row=2, column=4, sticky=W)
        self.XCenterE.bind("<Return>", self.MoveToY)
        self.XCenterE.bind("<KP_Enter>", self.MoveToY)

        self.st13 = Label(self, text='Y Center')
        self.st13.grid(row=1, column=4, sticky=E)
        self.YCenterVar = StringVar()
        self.YCenterE = Entry(self, width=10, textvariable=self.YCenterVar)
        self.YCenterE.grid(row=2, column=4, sticky=E)
        self.YCenterE.bind("<Return>", self.AddToList)
        self.YCenterE.bind("<KP_Enter>", self.AddToList)

        self.st14 = Label(self, text='Cut Direction')
        self.st14.grid(row=18, column=0)
        self.CutDirection=[('Climb',1),('Conventional', 2)]
        self.CutDirectionVar = IntVar()
        for text, value in self.CutDirection:
            self.rb4=Radiobutton(self, text=text, value=value, variable=self.CutDirectionVar)
            self.rb4.grid(column=0,row=value+18, sticky=W)
        self.CutDirectionVar.set(1)
        
        self.st15 = Label(self, text='X & Y List')
        self.st15.grid(row=3, column=4)
        self.CordList = Listbox(self, height=20)
        self.CordList.grid(row=4, column=4, rowspan=17, sticky=E+W+N+S)
        self.CordList.bind("<Double-Button-1>", self.EditListItem)
        self.CordList.bind("<ButtonRelease-1>", self.MouseSelect)
        self.CordList.bind("<Delete>", self.RemoveFromList)
        self.ListIndex = ''
        self.CLScroll = Scrollbar(self,command = self.CordList.yview)
        self.CLScroll.grid(row=4, column=5, rowspan=17, sticky=N+S+W)
        self.CordList.configure(yscrollcommand = self.CLScroll.set) 

        self.st16 = Label(self, text='G-Code')
        self.st16.grid(row=1, column=6)
        self.g_code = Text(self,width=50,height=25,bd=2)
        self.g_code.grid(row=2, column=6, rowspan=20, sticky=E+W+N+S)
        self.Gscroll = Scrollbar(self,command = self.g_code.yview)
        self.Gscroll.grid(row=2, column=7, rowspan=20, sticky=N+S+W)
        self.g_code.configure(yscrollcommand = self.Gscroll.set) 

        self.GenerateBtn = Button(self, text="Generate", command=self.GeneratePath, width=7)
        self.GenerateBtn.grid(row=22, column=3)

        if IN_AXIS:
            self.WriteButton = Button(self, text='To AXIS',\
                command=self.WriteToAxis)
        else:
            self.WriteButton = Button(self, text='To Clipboard',
                command=self.CopyClipboard, width=7)
        self.WriteButton.grid(row=22, column=4)

        self.ClearGCode = Button(self, text='Clear G Code Window', command=self.ClearGCode)
        self.ClearGCode.grid(row=22,column=6, sticky=W)
        
        self.quitButton = Button(self, text="Cancel", command=self.quit, width=7)
        self.quitButton.grid(row=22, column=6, sticky=E)

        self.nSHCS = {1:'No.0,0.125,0.060',
                      2:'No.1,0.15625,0.073',
                      3:'No.2,0.1875,0.086',
                      4:'No.3,0.21875,0.099',
                      5:'No.4,0.21875,0.112',
                      6:'No.5,0.250,0.125',
                      7:'No.6,0.28125,0.138',
                      8:'No.8,0.3125,0.164',
                      9:'No.10,0.375,0.190',
                     10:'No.12,0.40625,0.216'}
        self.fSHCS = {1:'1/4",0.4375,0.250',
                      2:'5/16",0.53125,0.313',
                      3:'3/8",0.625,0.375',
                      4:'7/16",0.7185,0.438',
                      5:'1/2",0.8125,0.500',
                      6:'9/16",0.90625,0.563',
                      7:'5/8",1.0,0.625',
                      8:'3/4",1.1875,0.750',
                      9:'7/8",1.375,0.875',
                     10:'1",1.625,1.000',
                     11:'1-1/8",1.8125,1.125',
                     12:'1-1/4",2.000,1.250',
                     13:'1-1/2",2.375,1.500',
                     14:'1-3/4",2.750,1.750',
                     15:'2",3.125,2.000'}
        self.mSHCS = {1:'M1.6,3.50,1.6',
                      2:'M2,4.40,2.0',
                      3:'M2.5,5.40,2.5',
                      4:'M3,6.00,3.0',
                      5:'M4,8.25,4.0',
                      6:'M5,9.75,5.0',
                      7:'M6,11.20,6.0',
                      8:'M8,14.50,8.0',
                      9:'M10,17.50,10.0',
                     10:'M12,19.50,12.0',
                     11:'M14,22.50,14.0',
                     12:'M16,25.50,16.0',
                     13:'M18,28.50,18.0',
                     14:'M20,31.50,20.0',
                     15:'M24,37.50,24.0',
                     16:'M30,47.50,30.0',
                     17:'M36,56.50,36.0',
                     18:'M42,66.00,42.0',
                     19:'M48,75.00,48.0',}

    def GeneratePath(self):
    	# If ToolDiameter > HoleDiameter then Complain
    	# If ToolDiameter == HoleDiameter then Plunge to HoleDepth
    	# If (ToolDiameter*1.25) <= HoleDiameter then Plunge to each Level and Spiral out to HoleDiameter
    	# If (ToolDiameter*1.25) > HoleDiameter then Spiral to each Level and Spiral out to HoleDiameter
    	
    	# Chicken Checking
        if len(self.ToolDiameterVar.get()) == 0:
            tkMessageBox.showwarning('Entry Missing', 'Please Enter a Tool Diameter!')
            return
        self.ToolDiameter = float(self.ToolDiameterVar.get())
        if len(self.HoleDiameterVar.get()) == 0:
            tkMessageBox.showwarning('Entry Missing',\
                'Please Enter a Hole Diameter!\nOr select one from the list.')
            return
        self.HoleDiameter = float(self.HoleDiameterVar.get())
        if self.ToolDiameter > self.HoleDiameter:
            tkMessageBox.showwarning('Entry Error', \
            'Tool Diameter Larger than Hole Diameter\nPlease use a smaller tool.')
            self.ToolDiameterE.focus_set()
            self.ToolDiameterE.select_range(0, END)
            return
        if self.CordList.size() == 0:
            tkMessageBox.showwarning('Entry Missing',\
                'Please Press Enter from the Y Center\nto add an entry to the list.')
            return
        
        # Gather the information from the form            
        self.ClearanceHeight = float(self.ClearanceHeightVar.get())
        self.StartHeight = float(self.StartHeightVar.get())
        self.MaterialTop = float(self.MaterialTopVar.get())
        self.FeedRate = float(self.FeedRateVar.get())
        if len(self.SpindleRPMVar.get()) > 0:
            self.SpindleRPM = int(self.SpindleRPMVar.get())
        self.HoleRadius = self.HoleDiameter/2
        self.HoleDepth = float(self.HoleDepthVar.get())
        self.FinishPathDiameter = self.HoleDiameter - self.ToolDiameter
        self.FinishPathRadius = self.FinishPathDiameter/2
        
        # Figure out what kind of entry into the hole
        if (self.ToolDiameter * 1.25 <= self.HoleDiameter):
        	self.CutType = 'Spiral Down to Depth of each Pass and Spiral Out'
        else:
        	if (self.ToolDiameter < self.HoleDiameter):
        		self.CutType = 'Plunge Down to Depth of each Pass and Spiral Out' 	
	        else:
        		self.CutType = 'Plunge Down to Hole Depth'

        # Max Depth of each pass
        if len(self.DepthOfCutVar.get()) == 0:
            self.MaxCutDepth = self.ToolDiameter/4
        else:
            self.MaxCutDepth = float(self.DepthOfCutVar.get())

        # Calculate depth of each pass not to exceed Max Depth of each pass
        if self.HoleDepth > self.MaxCutDepth:
            self.NumberOfCuts = int(ceil(self.HoleDepth/self.MaxCutDepth))
            self.CutDepth = self.HoleDepth / self.NumberOfCuts
        else:
            self.CutDepth = self.HoleDepth
            self.NumberOfCuts = 1

        # Number of Spirals Out
        if len(self.SpiralDepthVar.get()) == 0:
            self.SpiralDepth = self.CutDepth / 4
            self.NumberOfSpirals = 4
        else:
            self.NumberOfSpirals = int(ceil(self.CutDepth/float(self.SpiralDepthE.get())))
            self.SpiralDepth = self.CutDepth / self.NumberOfSpirals
            
        # Stepover %
        if len(self.StepOverVar.get()) == 0:
            self.StepOver = .25
        else:
            self.StepOver = float(self.StepOverVar.get()) * .01
            
        self.StepOver = self.FinishPathDiameter / \
            int(ceil(self.FinishPathDiameter / self.StepOver))
        self.ArcCenterOffset = self.StepOver / 8

        # Number of Circles
        self.NumberOfCircles = int(self.FinishPathDiameter/self.StepOver)-1
        
    
        # generate tool paths
        self.g_code.insert(END, '(SHCS Counterbore, Diameter = %.4f, Depth = %.4f )\n'\
            %(self.HoleDiameter, self.HoleDepth))
        self.g_code.insert(END, '(Number of Cuts %d, Depth of Cut %.4f)\n' \
            %(self.NumberOfCuts, self.CutDepth))
        self.g_code.insert(END, '(Tool Diameter = %.4f)\n' %self.ToolDiameter)
        self.g_code.insert(END, '(' + self.CutType + ')\n')
        if len(self.SpindleRPMVar.get()) > 0:
            self.g_code.insert(END, 'F%.1f S%d\n' %(self.FeedRate, self.SpindleRPM))
        else:
            self.g_code.insert(END, 'F%.1f\n' %(self.FeedRate))
        for n in range(0,int(self.CordList.size())):
            self.Items = self.CordList.get(0,END)
            self.SplitUp = self.Items[n].split()
            self.XCenter = float(self.SplitUp[0].lstrip('XY'))
            self.YCenter = float(self.SplitUp[1].lstrip('XY'))
            self.g_code.insert(END, '(Hole Center X%.4f Y%.4f)\n' \
                %(self.XCenter, self.YCenter))
                        
            # raise to clearance height
            self.g_code.insert(END, 'G0 Z%.4f\n' %(self.ClearanceHeight))

            if self.ToolDiameter <= self.HoleRadius:
                
                # go to start position at 12 o'clock
                if len(self.SpindleRPMVar.get()) > 0:
                    self.g_code.insert(END, 'G0 X%.4f Y%.4f M3\n'\
                        %(self.XCenter, self.YCenter+self.StepOver))
                else:
                   self.g_code.insert(END, 'G0 X%.4f Y%.4f\n'\
                        %(self.XCenter, self.YCenter+self.StepOver))
                
                # go to start height
                self.g_code.insert(END, 'G1 Z%.4f\n' %(self.StartHeight))

                # spiral down to material top
                self.g_code.insert(END, 'G3 X%.4f Y%.4f Z%.4f J%.4f\n' \
                        %(self.XCenter, self.YCenter+self.StepOver,\
                        self.MaterialTop, -self.StepOver))
                self.CurrentZ = self.MaterialTop
                        
                for n in range(0,self.NumberOfCuts):
                    # spiral down to cut depth
                    self.g_code.insert(END, '(spiral down)\n')
                    for n in range(0,self.NumberOfSpirals):
                        self.g_code.insert(END, 'G3 X%.4f Y%.4f Z%.4f J%.4f\n' \
                            %(self.XCenter, self.YCenter+self.StepOver,\
                            self.CurrentZ-self.SpiralDepth, -self.StepOver))
                        self.CurrentZ = self.CurrentZ - self.SpiralDepth

                    # spiral out to max cut diameter
                    self.g_code.insert(END, '(spiral out)\n')
                    # cypher destination of each arc end point
                    self.XMinus = self.XCenter - (self.StepOver + (self.ArcCenterOffset*2))
                    self.YMinus = self.YCenter - (self.StepOver + (self.ArcCenterOffset*4))
                    self.XPlus = self.XCenter + (self.StepOver + (self.ArcCenterOffset*6))
                    self.YPlus = self.YCenter + (self.StepOver*2)
                    for n in range(1,(self.NumberOfCircles-1)):
                        # 1st arc
                        self.g_code.insert(END, 'G3 X%.4f Y%.4f I%.4f J%.4f\n' \
                            %(self.XMinus, (self.YCenter),
                            -self.ArcCenterOffset, \
                            -(self.ArcCenterOffset+(self.StepOver*n))))
                        self.XMinus = self.XMinus - self.StepOver
                        # 2nd arc
                        self.g_code.insert(END, 'G3 X%.4f Y%.4f I%.4f J%.4f\n' \
                            %(self.XCenter, (self.YMinus),
                            (self.ArcCenterOffset*3)+(self.StepOver*n), \
                            -self.ArcCenterOffset))
                        self.YMinus = self.YMinus - self.StepOver
                        # 3rd arc
                        self.g_code.insert(END, 'G3 X%.4f Y%.4f I%.4f J%.4f\n' \
                            %(self.XPlus, (self.YCenter),
                            self.ArcCenterOffset, \
                            (self.ArcCenterOffset*5)+(self.StepOver*n)))
                        self.XPlus = self.XPlus + self.StepOver
                        # 4th arc
                        self.g_code.insert(END, 'G3 X%.4f Y%.4f I%.4f J%.4f\n' \
                            %(self.XCenter, (self.YPlus),
                            -((self.ArcCenterOffset*7)+(self.StepOver*n)),\
                                self.ArcCenterOffset))
                        self.YPlus = self.YPlus + self.StepOver

                    # clean up circle
                    self.g_code.insert(END, '(finish OD)\n')
                    self.g_code.insert(END, 'G3 X%.4f Y%.4f J%.4f\n' \
                        %(self.XCenter, (self.YPlus-self.StepOver), \
                            -(self.StepOver+(self.StepOver*n))))
                    self.g_code.insert(END, 'G1 X%.4f Y%.4f\n' \
                        %(self.XCenter, self.YCenter+self.StepOver))
            elif self.ToolDiameter > self.HoleRadius:
                # start at 12 o'clock and spiral down to final depth
                self.Offset = self.HoleDiameter - self.ToolDiameter
                self.ArcRadius = self.Offset/2
                self.StartPositionY = self.YCenter - (self.Offset/2)
                self.ArcRadius = self.Offset/2
                # go to start position
                self.g_code.insert(END, 'G0 X%.4f Y%.4f\n' \
                %(self.XCenter,self.StartPositionY))
                # go to start height
                self.g_code.insert(END, 'G1 Z%.4f\n' %(self.StartHeight))
                # spiral down
                self.g_code.insert(END, '(spiral down)\n')
                self.NextZPosition = self.CutDepth
                for n in range(0,self.NumberOfCuts):
                    self.g_code.insert(END, 'G3 X%.4f Y%.4f Z%.4f J%.4f\n' \
                        %(self.XCenter,self.StartPositionY \
                        ,-(self.NextZPosition), self.ArcRadius))
                    self.NextZPosition = self.NextZPosition + self.CutDepth

                # clean up circle
                self.g_code.insert(END, '(clean up hole)\n')
                self.g_code.insert(END, 'G3 X%.4f Y%.4f J%.4f\n' \
                    %(self.XCenter, self.StartPositionY, \
                    self.FinishPathRadius))
    
            # return to center
            self.g_code.insert(END, 'G1 X%.4f Y%.4f\n' %(self.XCenter, self.YCenter))
            # return to safe Z height
            if len(self.SpindleRPMVar.get()) > 0:
                self.g_code.insert(END, 'G0 Z%.4f M5\n' %(self.ClearanceHeight))
            else:
                self.g_code.insert(END, 'G0 Z%.4f M5\n' %(self.ClearanceHeight))
                self.g_code.insert(END, '(end of SHCS Counterbore)\n')
        if self.InsertEOFVar.get() == 1:
            self.g_code.insert(END, 'M2\n')

    def WriteToAxis(self):
        sys.stdout.write(self.g_code.get(0.0, END))
        self.quit()

    def CopyClipboard(self):
        self.g_code.clipboard_clear()
        self.g_code.clipboard_append(self.g_code.get(0.0, END))

    def ClearGCode(self):
        self.g_code.delete(1.0,END)

    def TabToNext(self,event):
        #def return_pressed(event):
        event.widget.event_generate('<Tab>')
        return 'break'     
       
    def rb1event(self,var):
        self.ns = self.nSHCS[self.var1.get()]
        self.nssp = self.ns.split(',')
        self.HoleDiameterVar.set(self.nssp[1])
        self.HoleDepthVar.set(self.nssp[2])
        self.var2.set(0)
        self.var3.set(0)

    def rb2event(self,var):
        self.fs = self.fSHCS[self.var2.get()]
        self.fssp = self.fs.split(',')
        self.HoleDiameterVar.set(self.fssp[1])
        self.HoleDepthVar.set(self.fssp[2])     
        self.var1.set(0)
        self.var3.set(0)
 
    def rb3event(self,var):
        self.ms = self.mSHCS[self.var3.get()]
        self.mssp = self.ms.split(',')
        self.InchHoleDia = str(.03937*float(self.mssp[1]))
        self.InchHoleDepth = str(.03937*float(self.mssp[2]))
        self.HoleDiameterVar.set(self.InchHoleDia)
        self.HoleDepthVar.set(self.InchHoleDepth)
        self.var1.set(0)
        self.var2.set(0)

    def MoveToY(self,var):
        self.YCenterE.focus_set()

    def AddToList(self,var):
        if len(self.XCenterE.get()) > 0 and len(self.YCenterE.get()) > 0:
            self.InsertString = 'X%.4f Y%.4f' \
                %(float(self.XCenterE.get()), float(self.YCenterE.get()))
            if len(self.ListIndex) > 0:
                self.CordList.delete(int(self.ListIndex))
                self.CordList.insert(int(self.ListIndex), self.InsertString)
                self.ListIndex = ''
            else:
                self.CordList.insert(END, self.InsertString)
            self.XCenterVar.set('')
            self.YCenterVar.set('')
        self.XCenterE.focus_set()

    def EditListItem(self,var):
        self.ListIndex = self.CordList.curselection()[0]
        self.seltext = []
        self.seltext = self.CordList.get(self.ListIndex).split()
        self.Xtext = self.seltext[0]
        self.Ytext = self.seltext[1]
        self.XCenterVar.set(self.Xtext[1:])
        self.YCenterVar.set(self.Ytext[1:])
        self.XCenter.focus_set()         

    def RemoveFromList(self,var):
        self.ListIndex = self.CordList.curselection()[0]
        self.CordList.delete(int(self.ListIndex))
        self.ListIndex = ''

    def MouseSelect(self, var):
        self.CordList.focus_set()
    def HelpInfo(self):
        c1 = Toplevel(app)
        c1.transient(app)
        canvas = Canvas(c1, width = 600,  height = 375)
        canvas.create_text( 150, 80, text="This Program cuts a counterbore in steps\n"
            "until full depth is reached.\n"
            "Followed by one finish cut at each depth\n\n"
            "To Edit an item in the X & Y List double click on it.\n"
            "Then edit it and press Enter to put it back in the list\n"
            "To Delete an item in the X & Y List click on it and\n"
            "press the delete key.\n\n"
            "The Enter key will advance you to the next field.")
        """ 
        #canvas.create_text( 140, 330, text="the dashed red line shows the lead-in\
         #\nto the final cut.  Slightly exagerated here :^)")
        #canvas.create_oval( 45, 75, 255, 285, dash=(4, 4), fill='white')
        #canvas.create_oval( 70, 100, 230, 260, fill='cyan', outline='cyan')
        #canvas.create_oval( 220, 180, 230, 190, fill='black')
        #canvas.create_arc( 60, 75, 230, 280, style=ARC, dash=(4, 4), outline='red')
        #canvas.create_oval( 80, 110, 220, 250, fill='white')
        #canvas.create_text( 180, 185, text='cyan area is cut \nfirst until full\
         \ndepth is reached', fill='purple', font=("Helvectica", "12"))
        #canvas.create_text(180,185, text="cyan area is cut \nfirst until full\
         \ndepth is reached", fill="purple",font=("Helvectica", "12"))
        """
        canvas.create_text( 450, 90, text="Minimum entry's are Tool Diameter\n\
Hole Diameter, Hole Depth\n\
X Center and Y Center.\n\
Some effort has been made \n\
to reject senseless input.\n\n\
Please check the output with a backplotter\n\
such as Axis\n\n\
To use this software in Axis, save the g-code \n\
in the nc directory.\n\
Make sure Axis is setup for .py extensions")
        canvas.grid()
    def HelpAbout(self):
        tkMessageBox.showinfo('Help About', 'Programmed by\n'
            'Big John T\n'
            'Version 0.5\n'
            'Use at your own risk!')

app = Application()
app.master.title("Counterbore 1.3")
app.mainloop()        

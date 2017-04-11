#!/usr/local/bin/python
from Tkinter import *

"""
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
    the command python YourPathToThisFile/drill.py
    make sure you have made the file execuatble by right
    clicking and selecting properties then Permissions and Execute

    To use with LinuxCNC see the instructions at: 
    https://github.com/linuxcnc/simple-gcode-generators

    Once you find the SFM that suits your machine just change the DrillList to suit.
    
    Enjoy and use safely
    BigJohnT
"""

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid()
        self.createFrames()
        self.createWidgets()

    def createFrames(self):
    	self.f1 = Frame(self, width=150, height=225, bd=5, relief=RIDGE)
    	self.f1.grid(row=0, column=0)
    	self.f1.grid_propagate(0)
    	self.f2 = Frame(self, width=150, height=225, bd=5, relief=RIDGE)
    	self.f2.grid(row=0, column=1)
    	self.f2.grid_propagate(0)
    	self.f3 = Frame(self, width=150, height=225, bd=5, relief=RIDGE)
    	self.f3.grid(row=0, column=2)
    	self.f3.grid_propagate(0)
    	self.f4 = Frame(self, width=450, height=100, bd=5, relief=RIDGE)
    	self.f4.grid(row=1, column=0, columnspan=3)
    	self.f4.grid_propagate(0)
    	
    def createWidgets(self):
        # Frame 1 Widgets
        self.f1st01 = Label(self.f1, text='Material', bd=5)
        self.f1st01.grid(row=0, column=0)
        self.Material=[('Tool Steel',1),('Cast Iron',2),('Bronzes',3),
        ('Mild Steel',4),('Brass',5),('Aluminum',6)]
        self.f1rb1Var = IntVar()
        for text, value in self.Material:
            self.f1rb1 = Radiobutton(self.f1, text=text, value=value, variable=self.f1rb1Var)
            self.f1rb1.grid(column=0,row=value+1, sticky=W)
            self.f1rb1.bind("<ButtonRelease-1>", self.f1rb1Event)
        self.f1rb1Var.set(0)

        self.f1st02 = Label(self.f1, text='SFM Range', bd=5)
        self.f1st02.grid(row=8, column=0)
        self.f1st03Var = StringVar()
        self.f1st03 = Label(self.f1, textvariable=self.f1st03Var)
        self.f1st03.grid(row=9, column=0)
        
        # Frame 2 Widgets
        self.f2st01 = Label(self.f2, text='Drill Diameter')
        self.f2st01.grid(row=0, column=0)
        self.DiameterVar = StringVar()
        self.Diameter=Entry(self.f2, width=10, textvariable=self.DiameterVar)
        self.Diameter.grid(row=1, column=0)

        self.f2st02 = Label(self.f2, text='RPM')
        self.f2st02.grid(row=2, column=0)
        self.RPMVar = StringVar()
        self.RPM=Entry(self.f2, width=10, textvariable=self.RPMVar)
        self.RPM.grid(row=3, column=0)

        self.f2st03 = Label(self.f2, text='Chip Load per Inch')
        self.f2st03.grid(row=4, column=0)
        self.ChipLoadVar = StringVar()
        self.ChipLoad = Entry(self.f2, width=10, textvariable=self.ChipLoadVar)
        self.ChipLoad.grid(row=5, column=0)
        self.ChipLoadVar.set('0.012')

        self.f2st04 = Label(self.f2, text='Number of Flutes')
        self.f2st04.grid(row=6, column=0)
        self.FlutesVar = StringVar()
        self.Flutes = Entry(self.f2, width=10, textvariable=self.FlutesVar)
        self.Flutes.grid(row=7, column=0)
        self.FlutesVar.set('2')
        
        # Frame 3 Widgets
        self.f3st01 = Label(self.f3, text='Feed IPM')
        self.f3st01.grid(row=0, column=0)
        self.f3st02Var = StringVar()
        self.f3st02 = Label(self.f3, textvariable=self.f3st02Var)
        self.f3st02.grid(row=1, column=0)

        self.f3st03 = Label(self.f3, text='SFM')
        self.f3st03.grid(row=2, column=0)
        self.f3st04Var = StringVar()
        self.f3st04 = Label(self.f3, textvariable=self.f3st04Var)
        self.f3st04.grid(row=3, column=0)

        self.f3st05 = Label(self.f3, text='Chip Load')
        self.f3st05.grid(row=4, column=0)
        self.f3st06Var = StringVar()
        self.f3st06 = Label(self.f3, textvariable=self.f3st06Var)
        self.f3st06.grid(row=5, column=0)
        
        # Frame 4 Widgets
        self.Instructions = 'Select a material to get the SFM Range' + \
                            '(Surface Feet per Minute)\n'+ \
                            'Enter the Drill Diameter and RPM\n'+ \
                            'Press Calculate to see the results\n'+ \
                            'Start with speeds that are in the low end of the SFM range\n'+ \
                            'Using Chip Load per Inch of Diameter of the drill bit\n' + \
                            'keeps the load even as you change diameters. Default is 0.012"'
        self.f4st01 = Label(self.f4, text=self.Instructions)
        self.f4st01.grid(row=0, column=0)

        self.CalcButton = Button(self, text="Calculate", command=self.CalcFeed)
        self.CalcButton.grid(row=2, column=1)

        self.quitButton = Button(self, text="Quit", command=self.quit)
        self.quitButton.grid(row=2, column=2)

        self.DrillList = {1:'50,60',
                      2:'80,100',
                      3:'80,100',
                      4:'60,80',
                      5:'150,200',
                      6:'120,350'}

    def f1rb1Event(self,var):
        self.ms = self.DrillList[self.f1rb1Var.get()]
        self.mssp = self.ms.split(',')
        self.MinSFM = self.mssp[0]
        self.MaxSFM = self.mssp[1]
        self.f1st03Var.set(self.MinSFM + '-' + self.MaxSFM)

    def CalcFeed(self):
        # Calculate Chip Load
        self.ChipLoadInch = float(self.ChipLoadVar.get())
        self.DrillDiameter = float(self.DiameterVar.get())
        self.CalcChipLoad = self.ChipLoadInch * self.DrillDiameter
        self.f3st06Var.set(self.CalcChipLoad)
        
        # Calculate Feed
        self.NumberOfFlutes = int(self.FlutesVar.get())
        self.DrillRPM = int(self.RPMVar.get())
        self.FeedRate = (self.CalcChipLoad*self.NumberOfFlutes)*self.DrillRPM
        self.f3st02Var.set(self.FeedRate)
        
        # Calculate SFM
        self.CalcSFM = int((0.262*self.DrillDiameter)*self.DrillRPM)
        self.f3st04Var.set(self.CalcSFM)
        
app = Application()
app.master.title("Drilling Speeds & Feeds 0.1")
app.mainloop()        

#!/usr/bin/python
"""
    ruler-xx.py G-Code Generator
 
	Copyright (C) <2018> <Andrew Williams> <linuxras at gmail dot com>
	based on bazel-11.py and engrave.py -- Thanks for a great example Lawrence!
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
    the command python YourPathToThisFile/ruler.py
    make sure you have made the file executable by right
    clicking and selecting properties then Permissions and Execute

    To use with LinuxCNC see the instructions at:
    https://github.com/linuxcnc/simple-gcode-generators

    Version 1.0 intial port from bazel and engrave code

"""

from Tkinter import *
from math import *
import tkFileDialog
import os
import re
import glob

version = '1.0'
fontPath = os.path.dirname(os.path.realpath(__file__))+'/cxf-fonts/'
fontList = [os.path.basename(x) for x in glob.glob(fontPath + '*.cxf')]
fontList = sorted(fontList)
fontfile = ''

IN_AXIS = os.environ.has_key("AXIS_PROGRESS_BAR")

#=======================================================================
# parse function borrowed from engrave.py
# This routine parses the .cxf font file and builds a font dictionary of
# line segment strokes required to cut each character.
# Arcs (only used in some fonts) are converted to a number of line
# segemnts based on the angular length of the arc. Since the idea of
# this font description is to make it support independant x and y scaling,
# we can not use native arcs in the gcode.
#=======================================================================
def parse(file):
    font = {}
    key = None
    num_cmds = 0
    line_num = 0
    for text in file:
        #format for a typical letter (lowercase r):
        ##comment, with a blank line after it
        #
        #[r] 3
        #L 0,0,0,6
        #L 0,6,2,6
        #A 2,5,1,0,90
        #
        line_num += 1
        end_char = re.match('^$', text) #blank line
        if end_char and key: #save the character to our dictionary
            font[key] = Character(key)
            font[key].stroke_list = stroke_list
            font[key].xmax = xmax
            if (num_cmds != cmds_read):
                print "(warning: discrepancy in number of commands %s, line %s, %s != %s )" % (fontfile, line_num, num_cmds, cmds_read)

        new_cmd = re.match('^\[(.*)\]\s(\d+)', text)
        if new_cmd: #new character
            key = new_cmd.group(1)
            num_cmds = int(new_cmd.group(2)) #for debug
            cmds_read = 0
            stroke_list = []
            xmax, ymax = 0, 0

        line_cmd = re.match('^L (.*)', text)
        if line_cmd:
            cmds_read += 1
            coords = line_cmd.group(1)
            coords = [float(n) for n in coords.split(',')]
            stroke_list += [Line(coords)]
            xmax = max(xmax, coords[0], coords[2])

        arc_cmd = re.match('^A (.*)', text)
        if arc_cmd:
            cmds_read += 1
            coords = arc_cmd.group(1)
            coords = [float(n) for n in coords.split(',')]
            xcenter, ycenter, radius, start_angle, end_angle = coords
            # since font defn has arcs as ccw, we need some font foo
            if ( end_angle < start_angle ):
                start_angle -= 360.0
            # approximate arc with line seg every 20 degrees
            segs = int((end_angle - start_angle) / 20) + 1
            angleincr = (end_angle - start_angle)/segs
            xstart = cos(start_angle * pi/180) * radius + xcenter
            ystart = sin(start_angle * pi/180) * radius + ycenter
            angle = start_angle
            for i in range(segs):
                angle += angleincr
                xend = cos(angle * pi/180) * radius + xcenter
                yend = sin(angle * pi/180) * radius + ycenter
                coords = [xstart,ystart,xend,yend]
                stroke_list += [Line(coords)]
                xmax = max(xmax, coords[0], coords[2])
                ymax = max(ymax, coords[1], coords[3])
                xstart = xend
                ystart = yend
    return font

#=======================================================================
class Character:
    def __init__(self, key):
        self.key = key
        self.stroke_list = []

    def __repr__(self):
        return "%s" % (self.stroke_list)

    def get_xmax(self):
        try: return max([s.xmax for s in self.stroke_list[:]])
        except ValueError: return 0

    def get_ymax(self):
        try: return max([s.ymax for s in self.stroke_list[:]])
        except ValueError: return 0



#=======================================================================
class Line:

    def __init__(self, coords):
        self.xstart, self.ystart, self.xend, self.yend = coords
        self.xmax = max(self.xstart, self.xend)
        self.ymax = max(self.ystart, self.yend)

    def __repr__(self):
        return "Line([%s, %s, %s, %s])" % (self.xstart, self.ystart, self.xend, self.yend)




#=======================================================================

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
        self.PreviewCanvas = Canvas(self.PreviewFrame,width=500, height=300, bg='white', bd='3', relief = 'raised')
        self.PreviewCanvas.grid(sticky=N+S+E+W)
        self.PreviewCanvas.config(scrollregion=(0,0,10000, 300))
        self.PreviewScroll = Scrollbar(self.PreviewFrame, command=self.PreviewCanvas.xview, orient=HORIZONTAL)
        self.PreviewCanvas.config(xscrollcommand=self.PreviewScroll.set)
        self.PreviewScroll.grid(row=1,column=0, sticky=E+W)
        self.XLine = self.PreviewCanvas.create_line(15,150,65,150, fill = 'red')
        self.YLine = self.PreviewCanvas.create_line(15,160,15,100, fill = 'green')

        self.EntryFrame = Frame(self,bd=5)
        self.EntryFrame.grid(row=0, column=1)

        self.st00 = Label(self.EntryFrame, text='Engrave a Ruler\n')
        self.st00.grid(row=0, column=0, columnspan=2)

        self.st01 = Label(self.EntryFrame,text='Units')
        self.st01.grid(row=1,column=0)
        self.UnitVar = IntVar()
        self.UnitVar.set(1)
        self.UnitFrame = Frame(self.EntryFrame,bd=5)
        self.UnitFrame.grid(row=1, column=1)
        self.UnitIn = Radiobutton(self.UnitFrame, text='Inch',value=1,variable=self.UnitVar,indicatoron=0,width=6,command=self.UnitSelect)
        self.UnitIn.grid(row=1, column=0)
        self.UnitMM = Radiobutton(self.UnitFrame, text='MM',value=2,variable=self.UnitVar,indicatoron=0,width=6,command=self.UnitSelect)
        self.UnitMM.grid(row=1, column=1)

        self.st02 = Label(self.EntryFrame, text='Preamble')
        self.st02.grid(row=2, column=0)
        self.PreambleVar = StringVar()
        self.PreambleVar.set('G17 G20 G90 G64 P0.003 M3 S3000 M7 F50')
        self.Preamble = Entry(self.EntryFrame, textvariable=self.PreambleVar ,width=15)
        self.Preamble.grid(row=2, column=1)

        self.NormalColor =  self.Preamble.cget('bg')

        self.st03 = Label(self.EntryFrame, text='Length')
        self.st03.grid(row=3, column=0)
        self.RulerLengthVar = StringVar()
        self.RulerLengthVar.set('15.0')
        self.RulerLength = Entry(self.EntryFrame, textvariable=self.RulerLengthVar ,width=15)
        self.RulerLength.grid(row=3, column=1)

        self.st04 = Label(self.EntryFrame, text='Major Stripe Length')
        self.st04.grid(row=4, column=0)
        self.MajorStripeLengthVar = StringVar()
        self.MajorStripeLengthVar.set('0.500')
        self.MajorStripeLength = Entry(self.EntryFrame, textvariable=self.MajorStripeLengthVar ,width=15)
        self.MajorStripeLength.grid(row=4, column=1)

        self.st05 = Label(self.EntryFrame, text='Half Stripe Length')
        self.st05.grid(row=5, column=0)
        self.HalfStripeLengthVar = StringVar()
        self.HalfStripeLengthVar.set('0.375')
        self.HalfStripeLength = Entry(self.EntryFrame, textvariable=self.HalfStripeLengthVar ,width=15)
        self.HalfStripeLength.grid(row=5, column=1)

        self.st06 = Label(self.EntryFrame, text='Minor Stripe Length')
        self.st06.grid(row=6, column=0)
        self.MinorStripeLengthVar = StringVar()
        self.MinorStripeLengthVar.set('0.125')
        self.MinorStripeLength = Entry(self.EntryFrame, textvariable=self.MinorStripeLengthVar ,width=15)
        self.MinorStripeLength.grid(row=6, column=1)

        self.st07 = Label(self.EntryFrame, text='Start X')
        self.st07.grid(row=7, column=0)
        self.StartXVar = StringVar()
        self.StartXVar.set('0')
        self.StartX = Entry(self.EntryFrame, textvariable=self.StartXVar ,width=15)
        self.StartX.grid(row=7, column=1)

        self.st08 = Label(self.EntryFrame, text='Start Y')
        self.st08.grid(row=8, column=0)
        self.StartYVar = StringVar()
        self.StartYVar.set('0')
        self.StartY = Entry(self.EntryFrame, textvariable=self.StartYVar ,width=15)
        self.StartY.grid(row=8, column=1)

        self.st09 = Label(self.EntryFrame, text='Stripes Every')
        self.st09.grid(row=9, column=0)
        self.RulerStripesEveryVar = StringVar()
        self.RulerStripesEveryVar.set('0.125')
        self.RulerStripesEvery = Entry(self.EntryFrame, textvariable=self.RulerStripesEveryVar ,width=15)
        self.RulerStripesEvery.grid(row=9, column=1)

        self.st10 = Label(self.EntryFrame, text='Major Stripe Every')
        self.st10.grid(row=10, column=0)
        self.MajorStripeEveryVar = StringVar()
        self.MajorStripeEveryVar.set('8')
        self.MajorStripeEvery = Entry(self.EntryFrame, textvariable=self.MajorStripeEveryVar ,width=15)
        self.MajorStripeEvery.grid(row=10, column=1)


        self.st11 = Label(self.EntryFrame, text='Engraving Depth')
        self.st11.grid(row=11, column=0)
        self.DepthVar = StringVar()
        self.DepthVar.set('-0.010')
        self.Depth = Entry(self.EntryFrame, textvariable=self.DepthVar ,width=15)
        self.Depth.grid(row=11, column=1)

        self.st12 = Label(self.EntryFrame, text='Safe Z')
        self.st12.grid(row=12, column=0)
        self.SafeZVar = StringVar()
        self.SafeZVar.set('+0.125')
        self.SafeZ = Entry(self.EntryFrame, width=15, textvariable = self.SafeZVar)
        self.SafeZ.grid(row=12, column=1)

        self.st13 = Label(self.EntryFrame, text='Postamble')
        self.st13.grid(row=13, column=0)
        self.PostambleVar = StringVar()
        self.PostambleVar.set('M5 M9 M2')
        self.Postamble = Entry(self.EntryFrame, textvariable=self.PostambleVar ,width=15)
        self.Postamble.grid(row=13, column=1)

        self.st14 = Label(self.EntryFrame, text='Label Font')
        self.st14.grid(row=14, column=0)
        self.FontVar = StringVar()
        self.FontVar.set(fontList[14])
        fontfile = fontList[14]
        self.Font = OptionMenu(self.EntryFrame, self.FontVar, *fontList ,command=self.ChooseFont)
        self.Font.grid(row=14, column=1)

        self.st15 = Label(self.EntryFrame, text='Label Offset')
        self.st15.grid(row=15,  column=0)
        self.OffsetFrame = Frame(self.EntryFrame,bd=5)
        self.OffsetFrame.grid(row=15, column=1)
        
        self.st15_1 = Label(self.OffsetFrame, text='X')
        self.st15_1.grid(row=0, column=0)
        self.FontXOffsetVar = StringVar()
        self.FontXOffsetVar.set('-0.125')
        self.FontXOffset = Entry(self.OffsetFrame, textvariable=self.FontXOffsetVar ,width=5)
        self.FontXOffset.grid(row=0, column=1)
        
        self.st15_2 = Label(self.OffsetFrame, text='Y')
        self.st15_2.grid(row=0, column=3)
        self.FontYOffsetVar = StringVar()
        self.FontYOffsetVar.set('+0.0625')
        self.FontYOffset = Entry(self.OffsetFrame, textvariable=self.FontYOffsetVar ,width=5)
        self.FontYOffset.grid(row=0, column=4)
        
        self.st16 = Label(self.EntryFrame, text='Label Scale')
        self.st16.grid(row=16,  column=0)
        self.ScaleFrame = Frame(self.EntryFrame,bd=5)
        self.ScaleFrame.grid(row=16, column=1)
        
        self.st16_1 = Label(self.ScaleFrame, text='X')
        self.st16_1.grid(row=0, column=0)
        self.XScaleVar = StringVar()
        self.XScaleVar.set('0.04')
        self.XScale = Entry(self.ScaleFrame, textvariable=self.XScaleVar ,width=5)
        self.XScale.grid(row=0, column=1)
        
        self.st16_2 = Label(self.ScaleFrame, text='Y')
        self.st16_2.grid(row=0, column=3)
        self.YScaleVar = StringVar()
        self.YScaleVar.set('0.04')
        self.YScale = Entry(self.ScaleFrame, textvariable=self.YScaleVar ,width=5)
        self.YScale.grid(row=0, column=4)

        self.st17 = Label(self.EntryFrame, text='Stripe Position')
        self.st17.grid(row=17,  column=0)
        self.BaselineFrame = Frame(self.EntryFrame,bd=5)
        self.BaselineFrame.grid(row=17, column=1)
        BaselineOptions=[('Above',0),('Midway',1),('Below',2)]
        self.BaselineVar = IntVar()
        for text, value in BaselineOptions:
            Radiobutton(self.BaselineFrame, text=text,value=value,
                variable=self.BaselineVar,indicatoron=0,width=6,command=self.BaselineSelect)\
                .grid(row=0, column=value)
        self.BaselineVar.set(0)

        self.DoItButton = Button(self.EntryFrame, text='Recalculate', command=self.DoIt)
        self.DoItButton.grid(row=18, column=0)

        self.ToClipboard = Button(self.EntryFrame, text='To Clipboard', command=self.CopyClipboard)
        self.ToClipboard.grid(row=18, column=1)

        if IN_AXIS:
            self.quitButton = Button(self, text='Write to AXIS and Quit',command=self.WriteToAxis)
        else:
            self.quitButton = Button(self, text='Quit', command=self.quit)
        self.quitButton.grid(row=13, column=0, sticky=S)

    def DoIt(self):
        # range check inputs for gross errors
        try:
            self.Font.configure( bg = self.NormalColor )
            file = open(fontPath+self.FontVar.get())
        except:
            print self.FontVar.get()
            self.Font.configure( bg = 'red' )
            return

        self.MajorStripeLength.configure( bg = self.NormalColor )
        if float(self.MajorStripeLength.get()) <= 0.0:
            self.MajorStripeLength.configure( bg = 'red' )
            return

        self.MinorStripeLength.configure( bg = self.NormalColor )
        if float(self.MinorStripeLength.get()) <= 0.0:
            self.MinorStripeLength.configure( bg = 'red' )
            return

        self.RulerStripesEvery.configure( bg = self.NormalColor )
        if float(self.RulerStripesEvery.get()) <= 0.0:
            self.RulerStripesEvery.configure( bg = 'red' )
            return

        self.SafeZ.configure( bg = self.NormalColor )
        if float(self.SafeZ.get()) <= 0.0:
            self.SafeZ.configure( bg = 'red' )
            return

        self.RulerLength.configure( bg = self.NormalColor )
        if float(self.RulerLength.get()) <= 0.0 or float(self.RulerLength.get()) <= float(self.RulerStripesEvery.get()):
            self.RulerLength.configure( bg = 'red' )
            return

        # erase old segs/display objects as needed
        for seg in self.segID:
            self.PreviewCanvas.delete(seg)
        self.segID = []

        # erase old gcode as needed
        self.gcode = []

        # temps used for ruler calcs
        Unit     = int(self.UnitVar.get())
        SafeZ    = float(self.SafeZVar.get())
        StartX   = float(self.StartXVar.get())
        StartY   = float(self.StartYVar.get())
        Length   = float(self.RulerLengthVar.get())
        MajorSL  = float(self.MajorStripeLengthVar.get())
        HalfSL   = float(self.HalfStripeLengthVar.get())
        MinorSL  = float(self.MinorStripeLengthVar.get())
        Depth    = float(self.DepthVar.get())
        Every    = float(self.RulerStripesEveryVar.get())
        MEvery   = float(self.MajorStripeEveryVar.get())
        HEvery   = float(MEvery / 2)
        BaseL    = int(self.BaselineVar.get())
        FontX    = float(self.FontXOffsetVar.get())
        FontY    = float(self.FontYOffsetVar.get())
        NumTicks = int((Length / Every)+1) 
        Scale    = MajorSL * 2.0 * 1.2 / 200.0          # nominal inches(mm) / pixel for plotting
        Angle    = 0.0
        XScale   = float(self.XScaleVar.get()) #0.04
        YScale   = float(self.YScaleVar.get()) #0.04
        CSpaceP  = 25.0
        WSpaceP  = 100.0
        MajorCT  = 0

        if( Unit == 1 ):
            UnitS = 'inches'
        else:
            UnitS = 'millimeters'

        self.gcode.append('( Code generated by ruler-%s.py widget )' %(version))
        self.gcode.append('( by Andrew Williams - 2018 )')
        self.gcode.append('( Engraving a %d tick, %.3f %s long ruler )' %(NumTicks, Length, UnitS))
        self.gcode.append('#1001 = %.4f  ( Safe Z )' %(SafeZ))
        self.gcode.append('#1002 = %.4f  ( Engraving Depth Z )' %(Depth))
        self.gcode.append('#1003 = %.4f  ( Start X )' %(StartX))
        self.gcode.append('#1004 = %.4f  ( StartY )' %(StartY))
        self.gcode.append('#1005 = %.4f  ( X Scale )' %(XScale))
        self.gcode.append('#1006 = %.4f  ( Y Scale )' %(YScale))
        self.gcode.append('#1007 = %.4f  ( Angle )' %(Angle))
        self.gcode.append("(===================================================================)")
        self.gcode.append("(Subroutine to handle x,y rotation about 0,0)")
        self.gcode.append("(input x,y get scaled, rotated then offset )")
        self.gcode.append("( [#1 = 0 or 1 for a G0 or G1 type of move], [#2=x], [#3=y], [#4=realx], [#5=realy])")
        self.gcode.append("o9000 sub")
        self.gcode.append("  #28 = [#2 * #1005]  ( scaled x )")
        self.gcode.append("  #29 = [#3 * #1006]  ( scaled y )")
        self.gcode.append("  #30 = [SQRT[#28 * #28 + #29 * #29 ]]   ( dist from 0 to x,y )")
        self.gcode.append("  #31 = [ATAN[#29]/[#28]]                ( direction to  x,y )")
        self.gcode.append("  #32 = [#30 * cos[#31 + #1007]]     ( rotated x )")
        self.gcode.append("  #33 = [#30 * sin[#31 + #1007]]     ( rotated y )")
        self.gcode.append("  #<realx> = #4")
        self.gcode.append("  #<realy> = #5")
        self.gcode.append("  o9010 if [#1 LT 0.5]" )
        self.gcode.append("    G00 X[#32+#<realx>] Y[#33+#<realy>]")
        self.gcode.append("  o9010 else")
        self.gcode.append("    G01 X[#32+#<realx>] Y[#33+#<realy>]")
        self.gcode.append("  o9010 endif")
        self.gcode.append("o9000 endsub")
        self.gcode.append("(===================================================================)")
        self.gcode.append(self.PreambleVar.get())
        self.gcode.append( 'G0 Z#1001')

        font = parse(file)          # build stroke lists from font file
        file.close()

        font_line_height = max(font[key].get_ymax() for key in font)
        font_word_space =  max(font[key].get_xmax() for key in font) * (WSpaceP/100.0)
        font_char_space = font_word_space * (CSpaceP /100.0)

        for tick in range(0,NumTicks):
            # calculate co-ordinates of inner point on tick mark
            x1 = StartX + (Every * tick)
            y1 = StartY
    
            if ( (tick %  MEvery) == 0 ):
                y2 = MajorSL
                if ( tick != 0 ):
                    MajorCT += 1
            elif ( (tick % HEvery) == 0 and HalfSL != 0 ):
                y2 = HalfSL
            else:
                y2 = MinorSL

            if (BaseL == 1):
                y1 = (y1 - (y2/2)) 
                y2 = (y2/2)
            elif (BaseL == 2):
                y2 = -y2

            # move to inner radius of tick mark
            self.gcode.append( 'G0 X[%.4f+#1003]  Y[%.4f+#1004]' %(x1,y1))
            #self.gcode.append( 'G0 X[%.4f+#1003]  Y[#1004]' %(x1))

            # set to cutting height
            self.gcode.append( 'G1 Z#1002')

            # cut to the length of tick mark
            self.gcode.append( 'G1 Y[%.4f+#1004]' %(y2))

            # raise engraver
            self.gcode.append( 'G0 Z#1001')
            
            self.segID.append( self.PreviewCanvas.create_line(
                15+x1/Scale, 150-y1/Scale,15+x1/Scale, 150-(y2+StartY)/Scale, fill = 'black', width = 2))

            xoffset = 0                 # distance along raw string in font units
            oldx = oldy = -99990.0      # last engraver position

            if ((tick %  MEvery) == 0 and tick != 0): #Write the number for this major line
                String = str(MajorCT)
                RealX  = float((StartX + x1) + FontX)
                RealY  = float((StartY + y2) + FontY)
                #if (MajorCT >= 10 and MajorCT < 100):
                #    RealX -= Every
                #elif (MajorCT >= 100):
                #    RealX -= (Every * 2)
            	#if (BaseL == 2):
                #	RealY -= Every
                #self.segID.append( self.PreviewCanvas.create_text(15+(x1-Every)/Scale, 150-(y2+StartY)/Scale, fill = 'black', width = 1, text = String))
                for char in String:
                    if char == ' ':
                        xoffset += font_word_space
                        continue
                    try:
                        self.gcode.append("(character '%s')" % self.sanitize(char))

                        first_stroke = True
                        for stroke in font[char].stroke_list:
                            dx = oldx - stroke.xstart
                            dy = oldy - stroke.ystart
                            dist = sqrt(dx*dx + dy*dy)

                            x1 = stroke.xstart + xoffset
                            y1 = stroke.ystart

                            # check and see if we need to move to a new discontinuous start point
                            if (dist > 0.001) or first_stroke:
                                first_stroke = False
                                #lift engraver, rapid to start of stroke, drop tool
                                self.gcode.append("G0 Z#1001")
                                self.gcode.append('o9000 call [0] [%.4f] [%.4f] [%.4f] [%.4f]' %(x1,y1,RealX,RealY))
                                self.gcode.append("G1 Z#1002")

                            x2 = stroke.xend + xoffset
                            y2 = stroke.yend
                            self.gcode.append('o9000 call [1] [%.4f] [%.4f] [%.4f] [%.4f]' %(x2,y2,RealX,RealY))
                            oldx, oldy = stroke.xend, stroke.yend

                            # since rotation and scaling is done in gcode, we need equivalent for plotting
                            # note that plot shows true shape and orientation of chrs, but starting x,y
                            # is always at the center of the preview window (offsets not displayed)
                            x1,y1 = self.Rotn(x1,y1,XScale,YScale,Angle)
                            x2,y2 = self.Rotn(x2,y2,XScale,YScale,Angle)
                            self.segID.append( self.PreviewCanvas.create_line(
                                15+(x1+RealX)/Scale, 150-(y1+RealY)/Scale,15+(x2+RealX)/Scale, 150-(y2+RealY)/Scale,
                                fill = 'black', width = 1))

                        # move over for next character
                        char_width = font[char].get_xmax()
                        xoffset += font_char_space + char_width

                    except KeyError:
                       self.gcode.append("(warning: character '0x%02X' not found in font defn)" % ord(char))

                    # raise engraver
                    self.gcode.append( 'G0 Z#1001')
                    self.gcode.append("")       # blank line after every char block
                

        # spot drill the center point of the bezel
        #self.gcode.append( 'G0 X#1003  Y#1004')
        #self.gcode.append( 'G1 Z#1002 G4 P0.5')
        self.gcode.append( 'G0 Z#1001')

        # finish up with icing
        self.gcode.append(self.PostambleVar.get())

    def ChooseFont(self, value):
        self.FontVar.set(value)
        fontfile = value
        self.DoIt()

    def UnitSelect(self):
        selection = int(self.UnitVar.get())
        if( selection == 1): #Setup for default inches or do I convert current by 25.4
            self.PreambleVar.set('G17 G20 G90 G64 P0.003 M3 S3000 M7 F50')
            self.RulerLengthVar.set('15')
            self.MajorStripeLengthVar.set('0.500')
            self.HalfStripeLengthVar.set('0.375')
            self.MinorStripeLengthVar.set('.125')
            self.RulerStripesEveryVar.set('0.125')
            self.MajorStripeEveryVar.set('8')
            self.DepthVar.set('-0.010')
            self.SafeZVar.set('+0.125')
            self.FontXOffsetVar.set('-0.125')
            self.FontYOffsetVar.set('+0.0625')
            self.XScaleVar.set('0.04')
            self.YScaleVar.set('0.04')
            self.DoIt()
        else: #Setup for MM ditto above
            self.PreambleVar.set('G17 G21 G90 G64 P0.003 M3 S3000 M7 F150')
            self.RulerLengthVar.set('400')
            self.MajorStripeLengthVar.set('8.0')
            self.HalfStripeLengthVar.set('5.0')
            self.MinorStripeLengthVar.set('3.0')
            self.RulerStripesEveryVar.set('1.0')
            self.MajorStripeEveryVar.set('10')
            self.DepthVar.set('-1.0')
            self.SafeZVar.set('+3.0')
            self.FontXOffsetVar.set('-1.7')
            self.FontYOffsetVar.set('0.1')
            self.XScaleVar.set('0.4')
            self.YScaleVar.set('0.4')
            self.DoIt()

    def BaselineSelect(self):
        selection = int(self.BaselineVar.get())
        #Just call DoIt here to recalculate all
        self.DoIt()

    def CopyClipboard(self):
        self.clipboard_clear()
        for line in self.gcode:
            self.clipboard_append(line+'\n')

    def WriteToAxis(self):
        for line in self.gcode:
            sys.stdout.write(line+'\n')
        self.quit()
#=======================================================================
# routine takes an x and a y in raw internal format
# x and y scales are applied and then x,y pt is rotated by angle
# Returns new x,y tuple
    def Rotn(self,x,y,xscale,yscale,angle):
        Deg2Rad = 2.0 * pi / 360.0
        xx = x * xscale
        yy = y * yscale
        rad = sqrt(xx * xx + yy * yy)
        theta = atan2(yy,xx)
        newx=rad * cos(theta + angle*Deg2Rad)
        newy=rad * sin(theta + angle*Deg2Rad)
        return newx,newy


	#=======================================================================
    def sanitize(self,string):
        retval = ''
        good=' ~!@#$%^&*_+=-{}[]|\:;"<>,./?'
        for char in string:
            if char.isalnum() or good.find(char) != -1:
                retval += char
            else: retval += ( ' 0x%02X ' %ord(char))
        return retval

app = Application()
app.master.title("Ruler Generator %s by Andrew Williams " %(version))
app.mainloop()






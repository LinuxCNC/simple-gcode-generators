Simple G-Code Generators
========================

This repository contains a collection of Python scrips that generate simple G-Code for LinuxCNC. For me to fire up a high dollar CAD program and the use the POST processor to generate simple routines is a waste of time. So I'm writing a series of Python programs to do this. If you did an LinuxCNC install, or have Mac OS X, you already have all you need. 

You can either clone this repository using Git or download the whole repository as [a zip file](https://github.com/linuxcnc/simple-gcode-generators/archive/master.zip).

All of these scripts, written by various authors, are licenced under the [GNU General Public License](LICENSE.md).

The Scripts
-----------

* [Airfoil Generator](airfoil/) - 3-4 Axis XY-XYUV Foam EDM Style airfoil generator
* [Arc Generator](arcgen/) - generate an arc from the diameter, the start and end angle
* [Bezel Engraving](bezel/) - engraves a bezel like you would see on the front panel of a stereo around the volume control knobs
* [Bolt Circle Array](boltcircle/) - generates a circular array for canned drill cycles
* [Counterbore](counterbore/) - generates the G-code for counterbores for socket head cap screws
* [Drilling Speeds-n-Feeds](drill-speed/) - helps you to calculate the speeds and feeds for drilling
* [Facing Software](face/) - super simple facing Generator
* [Grid](grid/) - generate various shapes of grid to test the speed and the accuracy of a milling machine
* [Grill](grill/) - drills a circular array of holes typically used as a speaker grill or as ventilation holes in a chassis panel
* [Pocketing](pocket/) - Rectangular-Circular Pocketing Generator
* [Text Engraving](engrave/) - This software engraves a text string
* [Multi-line Text Engraving](engrave-lines/) - Engrave up to 10 lines of text
* [Ruler Engraving](ruler/) - Engrave generic ruler in metric or standard with text



Using Python scripts with Axis
------------------------------

To download a file right click on it and select "Save link as".

Do the following...

* Place the .py files in your nc directory so it is easy to find
* Right click on the .py file in your file browser and select Properties. On the Permissions tab check Execute on the Owner line.

Add the following lines to the ```[FILTER]``` section of the Axis ini file

    [FILTER]
    PROGRAM_EXTENSION = .py Python Script
    py = python

If you don't have a ```[FILTER]``` section just add it

Now use File Open in AXIS to open face.py and after you generate the G-Code select *Write to AXIS* and Quit.



Using Python scripts with Windows
---------------------------------

Rename the file from .py to .pyw

Download and install the python program from [python.org](https://www.python.org/downloads/windows/).



Other G-Code Generators
=======================


### CP1

CP1 is a conversational machining program written by Ray Henry and Matt Shaver. 
It allows you to create G-code files for rectangular and circular pocket milling, bolt circles, hexagonal and rectangular arrays of holes, and "bezels" whatever those are.

http://wiki.linuxcnc.org/cgi-bin/wiki.pl?Cp1


### Dxf2gcode - import a 2D DXF file and produce G-code

This program seems to work pretty well with DXF files from QCAD.

https://sourceforge.net/projects/dxf2gcode/


### GCMC - G-Code Meta Compiler

GCMC is a front-end language for generating G-code, SVG and DXF for CNC mills, lathes, laser cutters and other numerical controlled machines employing G-code, SVG or DXF. The language is a context-free grammar created to overcome the archaic format of G-code programming and aims to be more readable and understandable.

http://www.vagrearg.org/content/gcmc


### mGcodeGenerator

A script for Blender. It can generate gcode ideal for LinuxCNC :) it exports from mesh ( vertex / edge / edges (outlines) / objects ) to 2d, 2.5d and full 3d for (3axis mill).

http://wiki.linuxcnc.org/cgi-bin/wiki.pl?GcodeGenerator


### OpenVoronoi and OpenCAMLib

There are some sample scripts and screenshots that use OpenVoronoi and OpenCAMLib:

https://github.com/aewallin/linuxcnc-scripts


### Pycam - Drop Cutter Surfacing Software

A GPL 3D CNC Toolpath Generation program written by Lode Leroy.

http://pycam.wiki.sourceforge.net/


### TTT: Truetype Tracer
A TrueType tracer with DXF and G-Code output

http://www.timeguy.com/cradek/truetype

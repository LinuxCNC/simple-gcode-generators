Simple G-Code Generators
========================

This repository contains a collection of Python scrips that generate simple G-Code for LinuxCNC. For me to fire up a high dollar CAD program and the use the POST processor to generate simple routines is a waste of time. So I'm writing a series of Python programs to do this. If you did an LinuxCNC install, or have Mac OS X, you already have all you need. 

You can either clone this repository using Git or download the whole repository as [a zip file](https://github.com/njh/simple-gcode-generators/archive/master.zip).



The Scripts
-----------

* [Arc Generator](arcgen/) - generate an arc from the diameter, the start and end angle
* [Bezel Engraving](bezel/) - engraves a bezel like you would see on the front panel of a stereo around the volume control knobs
* [Bolt Circle Array](boltcircle/) - generates a circular array for canned drill cycles
* [Counterbore](counterbore/) - generates the G-code for counterbores for socket head cap screws
* [Drilling Speeds-n-Feeds](drill-speed/) - helps you to calculate the speeds and feeds for drilling
* [Facing Software](face/) - super simple facing Generator
* [Grid](grid/) - generate various shapes of grid to test the speed and the accuracy of a milling mashine
* [Grill](grill/) - drills a circular array of holes typically used as a speaker grill or as ventilation holes in a chassis panel
* [Pocketing](pocket/) - Rectangular-Circular Pocketing Generator
* [Text Engraving](engrave/) - This software engraves a text string
* [Multi-line Text Engraving](engrave-lines/) - Engrave up to 10 lines of text



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


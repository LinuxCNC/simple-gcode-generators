Counterbore Software
====================

**Author:** John Thornton

**Download:** [counterbore.py](https://github.com/linuxcnc/simple-gcode-generators/raw/master/counterbore/counterbore.py)

This software generates the G-code for counterbores for socket head cap screws.


Features
--------

* Pick a SHCS from one of the three lists and it puts the standard diameter and depth in for you.
* Minimum entrys needed are hole diameter/depth, tool diameter and location of the hole.
* M2 end of file option if you have to generate several size holes only use it on the last hole.
* Editing of X & Y list with mouse clicks on item. Maintains order if one is edited and put back.
* Speedy entry using number key pad and the key pad enter key for locations.


Known Issues
------------

* At this time there is a bug if you have a path that does not require a spiral.


Screenshot
-----------

![Screenshot of counterbore.py](counterbore-screenshot.png)

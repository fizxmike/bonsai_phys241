bonsai_phys241
==============

Python Scripts for running tree code for phys 241 project

[download documentation](https://github.com/fizxmike/bonsai_phys241/blob/master/doc/latex/refman.pdf?raw=true)

##Requirements
Python, Numpy, ffmpeg, libx264
mpich or openmpi is optional

##Setup
Clone this repo and the [treecode/Bonsai repo](https://github.com/fizxmike/Bonsai) into the same parent folder on your system

##Compiling Bonsai
In Bonsai/runtime do:

    cmake -DUSE_B40C=1 -DUSE_DUST=0 -DCMAKE_CXX_COMPILER=mpicxx; make

##Easy Examples
* Quick Start Example: [Plummer.ipynb](http://nbviewer.ipython.org/github/fizxmike/bonsai_phsy241/blob/master/Plummer.ipynb)

##Other Galaxies
* View Cartwheel Midterm 2014 Results: [Cartwheel.ipynb](http://nbviewer.ipython.org/github/fizxmike/bonsai_phsy241/blob/master/Cartwheel.ipynb)
* View Cartwheel Final 2014 Results: [CartwheelFinal.ipynb](http://nbviewer.ipython.org/github/fizxmike/bonsai_phsy241/blob/master/CartwheelFinal.ipynb)

##Milky Way Cartwheel:
* Milky Way Galaxy C (from galactics) Warm-up: [MWGalaxy.ipynb](http://nbviewer.ipython.org/github/fizxmike/bonsai_phsy241/blob/master/MWGalaxy.ipynb)
* Twin Milky Way Collision: [Collision.ipynb](http://nbviewer.ipython.org/github/fizxmike/bonsai_phsy241/blob/master/Collision.ipynb)


##My Other Code
* Inner solar system webApp (leapfrog): [leapint.js](https://googledrive.com/host/0By3y5bc79qIyU2c0WE4tQVFTZHM/leapFrog/leapint.htm)

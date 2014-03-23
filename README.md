bonsai_phys241
==============

Python Scripts for wrapping the Bonsai tree code and generating plots and video for phys 241 project

[download PDF documentation](https://github.com/fizxmike/bonsai_phys241/blob/master/doc/latex/refman.pdf?raw=true)

##Requirements (Preferably Linux)
CUDA, git, gcc/g++, make, cmake,  Python, Numpy, ffmpeg, libx264, mpi (optional)

##Setup
Clone this repo and the [treecode/Bonsai repo](https://github.com/fizxmike/Bonsai) into the same parent folder on your system

###Install Packages (Ubuntu 12.04 LTS)

    sudo apt-get install git python-numpy ffmpeg libavcodec-extra-* mpich2 build-essential cmake

###Repo Checkout

    git clone https://github.com/fizxmike/bonsai_phys241.git
    git clone https://github.com/treecode/Bonsai.git

##Compiling Bonsai
    
    cd Bonsai/runtime 
    cmake -DUSE_B40C=1 -DUSE_DUST=0 -DCMAKE_CXX_COMPILER=mpicxx
    make


##Easy Examples
* Quick Start Example: [Plummer.ipynb](http://nbviewer.ipython.org/github/fizxmike/bonsai_phsy241/blob/master/Plummer.ipynb)

##Other Galaxies
* View Cartwheel Midterm 2014 Results: [Cartwheel.ipynb](http://nbviewer.ipython.org/github/fizxmike/bonsai_phsy241/blob/master/Cartwheel.ipynb)
* View Cartwheel Final 2014 Results: [CartwheelFinal.ipynb](http://nbviewer.ipython.org/github/fizxmike/bonsai_phsy241/blob/master/CartwheelFinal.ipynb)

##Twin Milky Way:
* Milky Way Galaxy C (from galactics) Warm-up: [MWGalaxy.ipynb](http://nbviewer.ipython.org/github/fizxmike/bonsai_phsy241/blob/master/MWGalaxy.ipynb)
* Twin Milky Way Collision: [MWCollision.ipynb](http://nbviewer.ipython.org/github/fizxmike/bonsai_phsy241/blob/master/MWCollision.ipynb)

##My Cartwheel:
* Ball and Disk Warmup: [CollisionWarmup.ipynb](http://nbviewer.ipython.org/github/fizxmike/bonsai_phsy241/blob/master/CollisionWarmup.ipynb)
* Cannon Ball Collision: [Collision.ipynb](http://nbviewer.ipython.org/github/fizxmike/bonsai_phsy241/blob/master/Collision.ipynb)

##My Other Code
* Inner solar system webApp (leapfrog): [leapint.js](https://googledrive.com/host/0By3y5bc79qIyU2c0WE4tQVFTZHM/leapFrog/leapint.htm)

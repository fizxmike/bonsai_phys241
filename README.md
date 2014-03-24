bonsai_phys241
==============

Python Scripts for wrapping the [Bonsai Tree Code](https://github.com/fizxmike/Bonsai) and generating figures and video for phys 241 projects

For a detailed outline of this code package, please refer to the [Code Documentation](https://github.com/fizxmike/bonsai_phys241/blob/master/doc/latex/refman.pdf?raw=true)

It is recommended that you fork this repo if you would like to contribute. Then submit a pull request.

##Requirements
**Software:** CUDA, git, gcc/g++, make, cmake, Python, Numpy, Matplotlib, ffmpeg, libx264, mpi (optional), ipython notebook (optional)

I used IPyhon Notebook to manage my projects. The notebook offers real-time interaction with a python kernel through small input/output block pairs (think MATLAB meets Mathematica). It also allowed me to easily share my results through a webpage (). More info can be found on the [IPython Notebook](http://ipython.org/notebook) and [Notebook Viewer](http://nbviewer.ipython.org/) web sites.

**Hardware** One or more NVIDIA GPU with Fermi microarchitecture: [Compute capability 2.0 or Better](https://developer.nvidia.com/cuda-gpus)

Ubuntu Linix ([12.04.4 LTS](http://releases.ubuntu.com/12.04/)) is the platform I used, however, there are no known reasons why this code will not work on Windows or Mac OS. Especially since Bonsai's build scripts are wrapped with cmake which is platform independent.

###Install CUDA 5.x
You will need to install the CUDA *drivers* as well as the *SDK*. The *code samples* are optional and require many more obscure graphics libraries to comple sucessfully.
Select your platform and follow the instructions in the "Getting Started Guide" here: [CUDA Developer Downloads](https://developer.nvidia.com/cuda-downloads)

###Install *Required* Packages
Ubuntu 12.04 LTS:

    sudo apt-get install git python-numpy python-matplotlib ffmpeg libavcodec-extra-* build-essential cmake

###Install *Optional* Packages
Ubuntu 12.04 LTS:

    sudo apt-get install mpich2 ipython ipython-notebook


I will leave it to future users to detail installation procedures on Windows, Mac OS, and other Linux distros (good luck).


##Setup
You can start by cloning this and the Bonsai Tree Code repo into the same parent folder on your system. All the commands below assume you are using a linux/unix style terminal interface.

###Repo Checkout
In the command line, navigate to a desired location to work. Then do:

    git clone https://github.com/fizxmike/bonsai_phys241.git
    git clone https://github.com/treecode/Bonsai.git

Next you will need to compile the Bonsai Tree Code.

###Compiling Bonsai (without MPI)

    cd Bonsai/runtime 
    cmake -DUSE_B40C=1 -DUSE_DUST=0
    make

###Compiling Bonsai (with MPI)
    
    cd Bonsai/runtime 
    cmake -DUSE_B40C=1 -DUSE_DUST=0 -DCMAKE_CXX_COMPILER=mpicxx
    make

##Launching IPython Notebook (Optional):
Navigate to this repo's folder then launch IPython Notebook. This command will launch your web browser and take you to the IPython Notebook interface, and list all my notebooks.

    ipython notebook

###Lanuching IPython Notebook from a remote server
This requires you to tunnel local port 8888 traffic to the server. You can do this by first connecting with ssh:

    ssh user@remote-gpu-server.someplace.edu -L 8888:localhost:8888
    
Then when you launch IPython Notebook, tell it not to launch a browser window (which would be some command line/text -based web browser on your server terminal, yuck):

    ipython notebook --no-browser

Back on your local machine, navigate to http://127.0.0.1:8888/

##Easy Examples
This notebook will get you started running the tree code. You can copy and paste these commands into the python terminal or your own python script. I reccommend 

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

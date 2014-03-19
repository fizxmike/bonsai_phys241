"""
Tipsy.py module

Used to easily hadle .tipsy file format.

Offers plotting and video creation, and conversion of text to .tipsy format.

Author: Michael M. Folkerts
E-Mail: mmfolkerts@gmail.com
Project: UC San Diego Physics 241, Winter 2014, Prof. J. Kuti
"""
import matplotlib
matplotlib.use('Agg') #allows figures to be generated without $DISPLAY connected (on a remote server)

import struct, glob
from subprocess import call
from multiprocessing import Process

import numpy as np
from matplotlib import pyplot as plt
from mpl_toolkits.mplot3d import axes3d

class Stars(object):
	""" 
	The Stars object holds mass, position, velocity, and composition information extracted
	from a .tipsy file for stars only (gas and dark matter ignored).
	"""

	time = None #simulation time
	mass = None #array of star masses
	pos = None #array of star positions
	vel = None #array of star velocities
	metals = None #array of star metal composition (fraction?)
	nStars = 0 #number of stars stored in this object

	def __init__(self,tipsyFilePath):
		"""
		Constructs Stars object from a .tipsy file.

		Arguments:
		tipsyFilePath -- path to a single .tipsy file
		"""

		tfile = open(tipsyFilePath,'rb')


		#get time
		self.time, = struct.unpack('d',tfile.read(8)) #one double (the trailing ',' makes self.time a number rather than a tuple

		
		#get number of each particle
		#nTot,nDim,nGas,nDark,nStar = struct.unpack('iiiii',tfile.read(20))
		nTot,dim,nGas,nDark,self.nStars,temp = struct.unpack('iiiiii',tfile.read(24)) #c structures pad to multiple of 8 bytes?
		#print self.time
		print 'Loading Header (%s)... time:%f, nTot:%i, nStar:%i' % (tipsyFilePath, self.time, nTot, self.nStars)

		#pass the file pointer to this function for each particle
		self.mass = np.zeros((self.nStars),dtype=np.float32)
		self.pos = np.zeros((self.nStars,dim),dtype=np.float32)
		self.vel = np.zeros((self.nStars,dim),dtype=np.float32)
		self.metals = np.zeros((self.nStars),dtype=np.float32)

		if dim == 3:
			#3D
			for i in range(self.nStars):
				mass,x1,x2,x3,v1,v2,v3,metals,tform_IGNORED,eps_IGNORED,phi_IGNORED = struct.unpack('f3f3f3fi',tfile.read(44))
				self.pos[i,:] = (x1,x2,x3)
				self.vel[i,:] = (v1,v2,v3)
				self.mass[i] = mass
				self.metals[i] = metals

		else:
			raise Exception("%iD not supported"%dim)

	def save_figure(self, figure_name, lim = .8, figsize = 10, pointsize = .1, nRed = None):
		"""
		Generates a figure "[figure_name].png" for this Star object

		Keyword arguments:
		figure_name -- path where figure is to be saved
		lim -- limits the range of all axis in view (default: .8)
		figsize -- size of final image (.png)
		pointsize -- size of stars
		nRed -- colors the first nRed particles red and the remaining blue (default: None)

		Prints:
		path to file just saved
		
		Returns:
		void
		"""

		fig = plt.figure(figsize=(figsize,figsize))
		ax = fig.gca(projection='3d')
		if nRed is not None:
			ax.plot(self.pos[:nRed,0],self.pos[:nRed,1],self.pos[:nRed,2],'r.',markersize=pointsize)
			ax.plot(self.pos[nRed:,0],self.pos[nRed:,1],self.pos[nRed:,2],'b.',markersize=pointsize)
		else:	
			ax.plot(self.pos[:,0],self.pos[:,1],self.pos[:,2],'w.',markersize=pointsize)


		ax.set_xlim(-lim,lim)
		ax.set_ylim(-lim,lim)
		ax.set_zlim(-lim,lim)
		ax.set_axis_off()
		ax.set_axis_bgcolor('black')
		plt.title('time: %f'%self.time,color='white')
		plt.tight_layout()
		fig_path_string = figure_name + '.png'
		plt.savefig(fig_path_string)
		print "Saved: "+fig_path_string

def make_mp4(png_prefix, mp4_prefix, frame_rate = 20, bit_rate = '8000k', codec = 'libx264'):
	"""
	Generates "[mp4_prefix].mp4" video from a set of "[png_prefix]{number}.png" where {number} is a placeholder for consecutive integers

	Arguments:
	png_prefix -- prefix of png files
	mp4_prefix -- name of .mp4 file

	Keyword arguments:
	frame_rate -- in frames per second (default: 20)
	bit_rate -- (string) in bits per second, higer rate = higer quality (default: '10000k')
	codec -- used to encode video, may require extra libraries on system (defaut: 'libx264')
	"""
	call(['ffmpeg',
		'-r', str(frame_rate),
		'-i', png_prefix + '%d.png',
		'-vcodec',codec,
		'-b',bit_rate,
		mp4_prefix + '.mp4'])
	print "Saved: " + mp4_prefix + ".mp4"


def read_tipsy(tipsy_prefix, figures_prefix = None, lim = .8, nRed = None, nThreads = 4):
	'''
	Reads a set of "[tipsy_prefix]{number}" files, where {number} is a placeholder for consecutive dicimal numbers, and
	returns an array of Star() objects.

	Optionally, if figures_prefix is not None, will generate a set of figures "[figures_prefix]{index}.png",
	where {index} is found from sorting {number}, and returns nothing (saves RAM for large set of tipsy files)

	Arguments:
	tipsy_prefix -- prefix of tipsy files

	Keyword arguments:
	figures_prefix -- generates figures only, no array returned (default: None)
	lim -- limits the range of all axis in view (default: .8)
	nRed -- when plotting figures colors the first nRed particles red and the remaining blue (default: None)
	'''

	#comparitor for file name sorting
	def cmp(x,y):
		x_num = float(x.lstrip(tipsy_prefix))
		y_num = float(y.lstrip(tipsy_prefix))
		if x_num > y_num:
			return 1
		elif x_num < y_num:
			return -1
		else:
			return 0
	
	tipsy_list = glob.glob(tipsy_prefix+"*")
	tipsy_list.sort(cmp)

	if figures_prefix is not None:
		#run parallel processes to plot figures

		#parallel function definition
		def read_and_plot(tipsy_file,index,lim,nRed):
			temp_stars = Stars(tipsy_file)
			temp_stars.save_figure(figures_prefix+str(index),lim=lim,nRed=nRed)

#		procs = [] #array of proceedures
		index = 0
		for tipsy_file in tipsy_list:
			read_and_plot(tipsy_file,index,lim,nRed)
#			procs.append(Process(target=read_and_plot,args=(tipsy_file,index,lim,nRed)))
#			procs[-1].start()
#			index +=1
			# if index % nThreads == 0:
			# 	for i in range(nThreads):
			# 		procs[i].join()
			# 	#wait for nThreads to finish
			# 	procs = []


		# for i in range(int(self.dim.z)):
		# 	procs[i].join()
	
	else:
		stars_array = []
		for tipsy_file in tipsy_list:
			stars_array[-1] = Stars(tipsy_file)
		return stars_array



	# index = 0 #used to count and name figures

	# for tipsy_file in tipsy_list:
	# 	#TODO: make sure path is file

	# 	if figures_prefix is not None:
	# 		temp_stars = Stars(tipsy_file)
	# 		temp_stars.save_figure(figures_prefix+str(index),lim=lim,nRed=nRed)
	# 		index += 1
	# 	else:
	# 		stars_array[-1] = Stars(tipsy_file)

	# if figures_prefix is None:

def txt2tipsy(nbody_file,tipsy_file):

	# Header: # particles, eta=0.02, dt, tmax, epsilon**2=0.25
	# eta is "accuracy parameter"
	# epsilon is "softening radius" (for close objects)

	#read header
	print "Reading..."

	nbfile = open(nbody_file,'r')
	nStars, eta, dt, tmax, eps2 = map(float,nbfile.readline().rstrip().split())
	nbfile.close()


	star_data = np.loadtxt(nbody_file,skiprows=1)

	nStars = int(nStars)

	if nStars != star_data.shape[0]:
		print "Warning: number of stars in file (%i) does not match number in header (%i)..." % (star_data.shape[0],nStars)
		nStars = star_data.shape[0]

	print "Writing..."
	tfile = open(tipsy_file,'wb')

	#time first
	tfile.write(struct.pack('d',0.0)) #initial time

	tfile.write(struct.pack('iiiiii',nStars,3,0,0,nStars,0)) # nTot,dim,nGas,nDark,self.nStars,temp

	for i in range(nStars):
		 tfile.write(struct.pack('f3f3f3fi',star_data[i,0],star_data[i,1],star_data[i,2],star_data[i,3],star_data[i,4],star_data[i,5],star_data[i,6],0.0,0.0,0.0,i))
		 #mass,x1,x2,x3,v1,v2,v3,metals,tform_IGNORED,eps_IGNORED,phi_IGNORED
	
	tfile.close()

	return {'nStars':nStars,'eta':eta, 'dt':dt, 'tmax':tmax, 'eps2':eps2}
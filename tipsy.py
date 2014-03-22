## @namespace tipsy 
#  The tipsy module provides utilites for managing input and output in .tipsy format for nbody simulations

"""
Tipsy.py module

Used to easily hadle .tipsy file format.

Offers nbody.txt/.tipsy conversion, galaxy manipulation, plotting and video creation.

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
from math import pi, cos, sin


class Stars(object):
	""" 
	The Stars object holds mass, position, velocity, and particle IDs extracted	from a .tipsy file.

	Currently on stars are processed (gas and dark matter ignored). Also, the phi parameter is used as a particle ID (like Bonsai).
	"""

	## Simulation timestamp (carried over from .tipsy file)
	time = None
	## Array of star masses
	mass = None
	## Array of star positions
	pos = None
	## Array of star velocities
	vel = None
	## Array of star id numbers
	IDs = None
	## Number of stars stored in this object
	nStars = 0

	def __init__(self,tipsyFilePath):
		"""
		Constructs Stars object from a .tipsy file.

		Converts from binary .tipsy format to a python object

		@param[in] tipsyFilePath	path to a single .tipsy file

		@returns	an instance of the Stars object
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
		self.IDs = np.zeros((self.nStars),dtype=np.float32)
		# self.metals = np.zeros((self.nStars),dtype=np.float32)

		if dim == 3:
			#3D
			for i in range(self.nStars):
				mass,x1,x2,x3,v1,v2,v3,metals,tform_IGNORED,eps_IGNORED,phi_ID = struct.unpack('f3f3f3fi',tfile.read(44))
				self.pos[i,:] = (x1,x2,x3)
				self.vel[i,:] = (v1,v2,v3)
				self.mass[i] = mass
				# self.metals[i] = metals
				self.IDs[i] = phi_ID

		else:
			raise Exception("%iD not supported"%dim)

	# Probably doesn't work right, taken out
	# def scale(self,factor, invarient = True):
	# 	"""
	# 	Scale all lengths in Stars by factor.

	# 	@param[in]	factor		multiplies the position and velocity vecors
	# 	@param[in]	invarient	scales masses as well (default: True)
	# 	"""
	# 	for i in range(self.nStars):
	# 		self.pos[i] *= factor
	# 		self.vel[i] *= factor

	# 	if invarient:
	# 		for i in range(self.nStars):
	# 			self.mass[i] *= factor

	def add_star(self, mass, pos, vel):
		"""
		Add a star to the collection

		Appends a star to the Stars object

		@param[in]	mass	the particle mass
		@param[in]	pos		(3-tuple) the position of the particle
		@param[in]	vel		(3-tuple) the velocity of the particle

		@returns	None
		"""

		#make room
		self.mass.resize((self.nStars+1,))
		self.pos.resize((self.nStars+1,3))
		self.vel.resize((self.nStars+1,3))

		#save values
		self.mass[self.nStars] = mass
		self.pos[self.nStars,:] = pos
		self.vel[self.nStars,:] = vel

		#increment star count
		self.nStars +=1

	def boost(self, velocity):
		"""
		Add a net velocity (3-vector) to all stars

		The velocity vector is added to the current volocity of each star

		@param[in]	velocity	a tuple of lenght 3

		@returns	None
		"""

		velocity = np.array(velocity)

		for i in range(self.nStars):
			self.vel[i] += velocity


	def translate(self,displacement):
		"""
		Rigidly displaces all stars

		The displacement vector is added to each star location.

		@param[in]	displacement -- a vector in the direction of the desired displacement

		@returns	None
		"""

		displacement = np.array(displacement)

		for i in range(self.nStars):
			self.pos[i] += displacement


	def rotate_euler_deg(self, phi, theta, psi):
		"""
		Rotates all stars using Euler angles in degrees (http://mathworld.wolfram.com/EulerAngles.html)

		Angles are made negative within this function for "active" rotation of the star position.
		Rotations are applied in the function argument order.

		@param[in]	phi		(degrees) right hand rotation about +Z axis
		@param[in]	theta	(degrees) right hand roation about resultant +X axis
		@param[in]	psi		(degrees) right hand rotation about resultant +Z axis

		@returns	None
		"""

		self.rotate_euler(phi*pi/180., theta*pi/180., psi*pi/180)

	def rotate_euler(self, phi, theta, psi):
		"""
		Rotates all stars using Euler angles in radians (http://mathworld.wolfram.com/EulerAngles.html)

		Angles are made negative within this function for "active" rotation of the star position.
		Rotations are applied in the function argument order.

		@param[in]	phi		(radians) right hand rotation about +Z axis
		@param[in]	theta	(radians) right hand roation about resultant +X axis
		@param[in]	psi		(radians) right hand rotation about resultant +Z axis

		@returns	None
		"""

		phi = -phi
		theta = -theta
		psi = -psi

		a = np.zeros((3,3))
		a[0,0]	=	cos(psi)*cos(phi)-cos(theta)*sin(phi)*sin(psi)	
		a[0,1]	=	cos(psi)*sin(phi)+cos(theta)*cos(phi)*sin(psi)	
		a[0,2]	=	sin(psi)*sin(theta)	
		a[1,0]	=	-sin(psi)*cos(phi)-cos(theta)*sin(phi)*cos(psi)	
		a[1,1]	=	-sin(psi)*sin(phi)+cos(theta)*cos(phi)*cos(psi)	
		a[1,2]	=	cos(psi)*sin(theta)	
		a[2,0]	=	sin(theta)*sin(phi)	
		a[2,1]	=	-sin(theta)*cos(phi)	
		a[2,2]	=	cos(theta)

		for i in range(self.nStars):
			self.pos[i] = a.dot(self.pos[i])
			self.vel[i] = a.dot(self.vel[i])

	def append(self,tipsyFilePath):
		"""
		Appends stars from a tipsy file into this Stars object

		The particle IDs will continue to increment starting from Stars.nStars

		@param[in]	tipsyFilePath	path to tipsy file to be appended

		@returns	None
		"""

		tfile = open(tipsyFilePath,'rb')
		#get time
		time, = struct.unpack('d',tfile.read(8)) #one double (the trailing ',' makes self.time a number rather than a tuple

		#get number of each particle
		#nTot,nDim,nGas,nDark,nStar = struct.unpack('iiiii',tfile.read(20))
		nTot,dim,nGas,nDark,nStars_added,temp = struct.unpack('iiiiii',tfile.read(24)) #c structures pad to multiple of 8 bytes?
		#print self.time
		print 'Loading Header (%s)... time:%f, nTot:%i, nStar:%i' % (tipsyFilePath, time, nTot, nStars_added)

		#pass the file pointer to this function for each particle
		self.mass.resize((self.nStars+nStars_added,)) #= np.zeros((self.nStars),dtype=np.float32)
		self.pos.resize((self.nStars+nStars_added,dim)) #= np.zeros((self.nStars,dim),dtype=np.float32)
		self.vel.resize((self.nStars+nStars_added,dim)) #= np.zeros((self.nStars,dim),dtype=np.float32)
		self.IDs.resize((self.nStars+nStars_added,))  #= np.zeros((self.nStars),dtype=np.float32)

		if dim == 3:
			#3D
			for i in range(self.nStars, self.nStars+nStars_added):
				mass,x1,x2,x3,v1,v2,v3,metals,tform_IGNORED,eps_IGNORED,phi_ID = struct.unpack('f3f3f3fi',tfile.read(44))
				self.pos[i,:] = (x1,x2,x3)
				self.vel[i,:] = (v1,v2,v3)
				self.mass[i] = mass
				self.IDs[i] = self.nStars+phi_ID

			self.nStars += nStars_added
		else:
			raise Exception("%iD not supported"%dim)

	def save_tipsy(self,tipsyFilePath):
		"""
		Saves the Stars object in tipsy format.

		Prints saved file path to stdout

		@param[in]	tipsyFilePath	path to output file

		@returns	None
		"""
		print "Writing..."
		tfile = open(tipsyFilePath,'wb')

		#time first
		tfile.write(struct.pack('d',self.time)) #initial time

		tfile.write(struct.pack('iiiiii',self.nStars,3,0,0,self.nStars,0)) # nTot,dim,nGas,nDark,self.nStars,temp

		for i in range(self.nStars):
			 tfile.write(struct.pack('f3f3f3fi',self.mass[i],self.pos[i,0],self.pos[i,1],self.pos[i,2],self.vel[i,0],self.vel[i,1],self.vel[i,2],0.0,0.0,0.0,i))
			 #mass,x1,x2,x3,v1,v2,v3,metals,tform_IGNORED,eps_IGNORED,phi_ID
		
		tfile.close()

		print "Saved: "+tipsyFilePath

	def save_figure(self, figure_name, lim = .8, figsize = 10, pointsize = .1, nRed = None):
		"""
		Generates a figure "[figure_name].png" for this Star object

		@param[in]	figure_name		path where figure is to be saved
		@param[in]	lim				limits the range of all axis in view (default: .8)
		@param[in]	figsize			size of final image (.png)
		@param[in]	pointsize		size of stars
		@param[in]	nRed			figure colors the first nRed particles red and the remaining blue (default: None)

		@returns	path to file just saved (string)
		"""

		fig = plt.figure(figsize=(figsize,figsize))
		ax = fig.gca(projection='3d')
		if nRed is not None:

			redIdx = np.where(self.IDs < nRed)[0]
			blueIdx = np.where(self.IDs >= nRed)[0]
			ax.plot(self.pos[redIdx,0],self.pos[redIdx,1],self.pos[redIdx,2],'r.',markersize=pointsize)
			ax.plot(self.pos[blueIdx,0],self.pos[blueIdx,1],self.pos[blueIdx,2],'b.',markersize=pointsize)
		else:	
			ax.plot(self.pos[:,0],self.pos[:,1],self.pos[:,2],'k.',markersize=pointsize)


		ax.set_xlim(-lim,lim)
		ax.set_ylim(-lim,lim)
		ax.set_zlim(-lim,lim)
		ax.set_axis_off()
		#ax.set_axis_bgcolor('black')
		plt.title('time: %f'%self.time)#,color='white')
		plt.tight_layout()
		fig_path_string = figure_name + '.png'
		plt.savefig(fig_path_string)
		return fig_path_string

def make_mp4(png_prefix, mp4_prefix, frame_rate = 20, bit_rate = '8000k', codec = 'libx264'):
	"""
	Makes an MP4 video from a set of PNG files.

	Generates "[mp4_prefix].mp4" video from a set of "[png_prefix]{number}.png" where {number} is a
	placeholder for consecutive integers.

	@param[in]	png_prefix		prefix of png files
	@param[in]	mp4_prefix		name of .mp4 file
	@param[in]	frame_rate		in frames per second (default: 20)
	@param[in]	bit_rate		(string) in bits per second, higer rate = higer quality (default: '10000k')
	@param[in]	codec			used to encode video, may require extra libraries on system (defaut: 'libx264')

	@returns	None
	"""
	call(['ffmpeg','-y',
		'-r', str(frame_rate),
		'-i', png_prefix + '%d.png',
		'-vcodec',codec,
		'-b',bit_rate,
		mp4_prefix + '.mp4'])
	print "Saved: " + mp4_prefix + ".mp4"


def read_tipsy(tipsy_prefix, figures_prefix = None, lim = .8, pointsize = .1, nRed = None, nThreads = 4):
	'''
	Reads a set of tipsy files and returns an array of Star objects or plots figures

	Reads a set of "[tipsy_prefix]{number}" files, where {number} is a placeholder for consecutive
	dicimal numbers, and returns an array of Star() objects.

	Optionally, if figures_prefix is not None, will generate a set of figures
	"[figures_prefix]{index}.png", where {index} is found from sorting {number},
	and returns nothing (saves RAM for large set of tipsy files).

	@param[in]	tipsy_prefix	prefix of tipsy files
	@param[in]	figures_prefix	generates figures only, no array returned (default: None)
	@param[in]	lim				limits the range of all axis in view (default: .8)
	@param[in]	pointsize		size of points in figure
	@param[in]	nRed			figure colors the first nRed particles red and the remaining blue (default: None)

	@returns	an array of Star objects (only if figures_prefix is None)
	'''

	#comparitor for file name sorting
	def cmp(x,y):
		x_num = float(x.lstrip(tipsy_prefix+'_'))
		y_num = float(y.lstrip(tipsy_prefix+'_'))
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
		# def read_and_plot(tipsy_file,index,lim,nRed):
		# 	temp_stars = Stars(tipsy_file)
		# 	temp_stars.save_figure(figures_prefix+str(index),lim=lim,nRed=nRed)

#		procs = [] #array of proceedures
		index = 0
		for tipsy_file in tipsy_list:
			#read_and_plot(tipsy_file,index,lim,nRed)
			temp_stars = Stars(tipsy_file)
			temp_stars.save_figure(figures_prefix+str(index),lim=lim,pointsize=pointsize, nRed=nRed)
#			procs.append(Process(target=read_and_plot,args=(tipsy_file,index,lim,nRed)))
#			procs[-1].start()
			index +=1
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
	"""
	Converts a typical nbody or Aarseth text file to .tipsy format

	Header may be in one of two formats:
	@li [particle_count] [time_stamp] 
	@li [particle_count] [eta] [dt] [tmax] [eps2] 

	@param[in]	nbody_file	path to the nbody text formated file
	@param[in]	tipsy_file	path to the tipsy output file

	@returns 	None
	"""
	# Header: # particles, eta=0.02, dt, tmax, epsilon**2=0.25
	# eta is "accuracy parameter"
	# epsilon is "softening radius" (for close objects)

	nStars = None
	eta = None
	dt = None
	tmax = None
	eps2 = None

	#read header
	print "Reading..."

	nbfile = open(nbody_file,'r')
	header_line = nbfile.readline().rstrip()
	nbfile.close()

	if len(header_line.split()) == 5:
		#aarseth format
		nStars, eta, dt, tmax, eps2 = map(float,header_line.split())
	elif len(header_line.split()) == 2:
		nStars, tmax = map(float,header_line.split())
	else:
		raise Exception("Error: header format not recognized")

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
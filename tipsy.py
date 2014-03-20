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
from math import pi, cos, sin

class Stars(object):
	""" 
	The Stars object holds mass, position, velocity, and composition information extracted
	from a .tipsy file for stars only (gas and dark matter ignored).
	"""

	time = None #simulation time
	mass = None #array of star masses
	pos = None #array of star positions
	vel = None #array of star velocities
	# metals = None #array of star metal composition (fraction?)
	IDs = None #array of star id numbers (fraction?)
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

	def boost(self, velocity):
		"""
		Add a net velocity to the stars

		Arguments:
		velocity -- a velocity to add to each star
		"""

		velocity = np.array(velocity)

		for i in range(self.nStars):
			self.vel[i] += velocity


	def translate(self,displacement):
		"""
		Rigidly displaces the stars

		Arguments:
		displacement -- a vector in the direction of the desired displacement
		"""

		displacement = np.array(displacement)

		for i in range(self.nStars):
			self.pos[i] += displacement


	def rotate_euler_deg(self, phi, theta, psi):
		"""
		Rotate the stars using Euler angles in degrees (http://mathworld.wolfram.com/EulerAngles.html)
		angles are made negative in this function for "active" rotation of the star position

		Arguments (rotations applied in this order):
		phi -- right hand rotation about Z axis [degrees]
		theta -- right hand roation about resultant X axis [degrees]
		psi -- right hand rotation about resultant Z axis [degrees]

		"""

		self.rotate_euler(phi*pi/180., theta*pi/180., psi*pi/180)

	def rotate_euler(self, phi, theta, psi):
		"""
		Rotate the stars using Euler angles in radians (http://mathworld.wolfram.com/EulerAngles.html)
		angles are made negative in this function for "active" rotation of the star position

		Arguments (rotations applied in this order):
		phi -- right hand rotation about Z axis [radians]
		theta -- right hand roation about resultant X axis [radians]
		psi -- right hand rotation about resultant Z axis [radians]

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
		Appends stars from tipsy file into this Stars object

		Arguments:
		tipsyFilePath -- path to tipsy file to be appended
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

		Arguments:
		tipsyFilePath --- path to output file
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

		Keyword arguments:
		figure_name -- path where figure is to be saved
		lim -- limits the range of all axis in view (default: .8)
		figsize -- size of final image (.png)
		pointsize -- size of stars
		nRed -- colors the first nRed particles (based on phi_ID) red and the remaining blue (default: None)

		Prints:
		path to file just saved
		
		Returns:
		void
		"""

		fig = plt.figure(figsize=(figsize,figsize))
		ax = fig.gca(projection='3d')
		if nRed is not None:

			redIdx = np.where(self.IDs < nRed)[0]
			blueIdx = np.where(self.IDs >= nRed)[0]
			ax.plot(self.pos[redIdx,0],self.pos[redIdx,1],self.pos[redIdx,2],'r.',markersize=pointsize)
			ax.plot(self.pos[blueIdx,0],self.pos[blueIdx,1],self.pos[blueIdx,2],'b.',markersize=pointsize)
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


def read_tipsy(tipsy_prefix, figures_prefix = None, lim = .8, pointsize = .1, nRed = None, nThreads = 4):
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
	pointsize -- size of points in figure
	nRed -- when plotting figures colors the first nRed particles red and the remaining blue (default: None) -- broken
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
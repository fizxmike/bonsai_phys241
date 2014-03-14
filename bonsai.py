
from subprocess import call
import struct
import glob
import numpy as np

#assume this Bonsai and bonsai_phys241 are next to eachother
BONSAI_BIN = '../Bonsai/runtime/bonsai2_slowdust'

class Stars(object):

	def __init__(self,fileObj,dim,count):
		#pass the file pointer to this function for each particle
		self.mass = np.zeros((count),dtype=np.float32)
		self.pos = np.zeros((count,dim),dtype=np.float32)
		self.vel = np.zeros((count,dim),dtype=np.float32)
		self.metals = np.zeros((count),dtype=np.float32)

		if dim == 3:
			#3D
			for i in range(count):
				mass,x1,x2,x3,v1,v2,v3,metals,tform_IGNORED,eps_IGNORED,phi_IGNORED = struct.unpack('f3f3f3fi',fileObj.read(44))
				self.pos[i,:] = (x1,x2,x3)
				self.vel[i,:] = (v1,v2,v3)
				self.mass[i] = mass
				self.metals[i] = metals

		else:
			raise Exception("%iD not supported"%dim)



def run_plummer(nParticles,snap_prefix,T=2,dt=0.0625, bonsai_bin = None, mpi_n = 0, mpi_log_file = 'mpiout.log'):
	if bonsai_bin is None:
		#use default
		bonsai_bin = BONSAI_BIN

	log = False

	if mpi_n > 0:
		#run mpi
		#mpirun -n 2 --output-filename mpiout.txt ./bonsai2_slowdust -i model3_child_compact.tipsy -T1000 --logfile logfile.txt
		if call(['mpirun','-n',str(mpi_n),
				 '--output-filename',mpi_log_file,bonsai_bin,
				 '--plummer',str(nParticles),
				 '--snapname',snap_prefix,'--snapiter','1',
				 '-T',str(T),'-dt',str(dt)
				]):
			return "Error"
		else:
			return "Done"

	else:
		#single GPU mode
		if call([bonsai_bin,'--log' if log else '','--plummer',str(nParticles),'--snapname',snap_prefix,'--snapiter','1','-T',str(T),'-dt',str(dt)]):
			return "Error"
		else:
			return "Done"

def run_sphere(nParticles,snap_prefix,T=2,dt=0.0625):
	log = False

	if call([BONSAI_BIN,'--log' if log else '','--sphere',str(nParticles),'--snapname',snap_prefix,'--snapiter','1','-T',str(T),'-dt',str(dt)]):
		return "Error"
	else:
		return "Done"



def load_tipsy(tipsy_prefix):
	
	tipsy_list = glob.glob(tipsy_prefix+"*")

	snaps_array = []

	for tipsy_file in tipsy_list:
		#make sure path is file

		tfile = open(tipsy_file,'rb')

		print 'Loading Header (%s):' % tipsy_file

		#get time
		time = struct.unpack('d',tfile.read(8)) #one double

		print "Simulation Time: %i" % time
		
		snaps_array.append({'time':time,'gas':[],'dark':[],'star':[]})

		#get number of each particle
		nTot,nDim,nGas,nDark,nStar = struct.unpack('iiiii',tfile.read(20))
		print "nTot: %i, nDim: %i, nGas: %i, nDark: %i, nStar: %i" % (nTot, nDim, nGas, nDark, nStar)



		#process stars:
		if nStar > 0:
			snaps_array[-1]['star'] = Stars(tfile,nDim,nStar)

		tfile.close()

	return snaps_array
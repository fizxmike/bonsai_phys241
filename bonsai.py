from subprocess import call
#assume this Bonsai and bonsai_phys241 are next to eachother
BONSAI_BIN = '../Bonsai/runtime/bonsai2_slowdust'

def run_model(model,nParticles,snap_prefix,T,dt, dSnap, bonsai_bin, mpi_n,mpi_log_file):
	"""
	Run a Bonsai built in model ('plummer' or 'sphere')

	Keyword arguments:
	model -- "plummer" or "sphere"
	nParticles -- number of particles per mpi process
	snap_prefix -- path prefix for snapshot (tipsy) files (simulation time will be appended)
	T -- total simulation time
	dt -- internal time step
	dSnap -- interval at which snapshot files are generated
	bonsai_bin -- path to bonsai exe
	mpi_n -- specifies the number of mpi processes (0 = mpi not used)
	mpi_log_file -- single log file for mpi output (when mpi_n > 0)
	""" 

	if model != 'plummer' and model != 'sphere':
		raise Exception("Error: model '%s' is not known." % model)

	if bonsai_bin is None:
		#use default
		bonsai_bin = BONSAI_BIN

	log = False

	if mpi_n > 0:
		#run mpi
		#mpirun -n 2 --output-filename mpiout.txt ./bonsai2_slowdust -i model3_child_compact.tipsy -T1000 --logfile logfile.txt
		if call(['mpirun','-n',str(mpi_n),
				 '--output-filename',mpi_log_file,bonsai_bin,
				 '--'+model,str(nParticles),
				 '--snapname',snap_prefix,'--snapiter',str(dSnap),
				 '-T',str(T),'-dt',str(dt)
				]):
			return "Error"
		else:
			return "Done"

	else:
		#single GPU mode
		if call([bonsai_bin,'--log' if log else '','--'+model,str(nParticles),'--snapname',snap_prefix,'--snapiter',str(dSnap),'-T',str(T),'-dt',str(dt)]):
			return "Error"
		else:
			return "Done"


def run_plummer(nParticles,snap_prefix,T=2,dt=0.0625, dSnap = 0.0625, bonsai_bin = None, mpi_n = 0, mpi_log_file = 'mpiout.log'):
	"""
	Run a Bonsai's built in plummer model

	Keyword arguments:
	nParticles -- number of particles (per mpi process)
	snap_prefix -- path prefix for snapshot files (time will be appended)
	T -- total simulation time
	dt -- internal time step
	dSnap -- interval at which snapshot files are generated
	bonsai_bin -- path to bonsai exe
	mpi_n -- specifies the number of mpi processes (0 = mpi not used)
	mpi_log_file -- single log file for mpi output (when mpi_n > 0)
	"""
	run_model("plummer",nParticles,snap_prefix,T,dt, dSnap, bonsai_bin, mpi_n,mpi_log_file)


def run_sphere(nParticles,snap_prefix,T=2,dt=0.0625, dSnap = 0.0625, bonsai_bin = None, mpi_n = 0, mpi_log_file = 'mpiout.log'):
	"""
	Run a Bonsai's built in plummer model

	Keyword arguments:
	nParticles -- number of particles (per mpi process)
	snap_prefix -- path prefix for snapshot files (time will be appended)
	T -- total simulation time
	dt -- internal time step
	dSnap -- interval at which snapshot files are generated
	bonsai_bin -- path to bonsai exe
	mpi_n -- specifies the number of mpi processes (0 = mpi not used)
	mpi_log_file -- single log file for mpi output (when mpi_n > 0)
	"""
	run_model("sphere",nParticles,snap_prefix,T,dt, dSnap, bonsai_bin, mpi_n,mpi_log_file)
	
	
# def run_sphere(nParticles,snap_prefix,T=2,dt=0.0625,dSnap = 0.0625,):
# 	log = False

# 	if call([BONSAI_BIN,'--log' if log else '','--sphere',str(nParticles),'--snapname',snap_prefix,'--snapiter',str(dSnap),'-T',str(T),'-dt',str(dt)]):
# 		return "Error"
# 	else:
# 		return "Done"


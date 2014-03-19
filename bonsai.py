from subprocess import call
#assume this Bonsai and bonsai_phys241 are next to eachother
BONSAI_BIN = '../Bonsai/runtime/bonsai2_slowdust'

def run_tipsy(tipsy_file,snap_prefix,T,dt, dSnap, eps, bonsai_bin=None, mpi_n=0,mpi_log_file='mpiout.log'):
	"""
	Run a Bonsai with initial conditions

	Keyword arguments:
	tipsy_file -- containing initial conditions
	snap_prefix -- path prefix for snapshot files (time will be appended)
	T -- total simulation time
	dt -- internal time step
	dSnap -- interval at which snapshot files are generated
	bonsai_bin -- path to bonsai exe
	mpi_n -- specifies the number of mpi processes (0 = mpi not used)
	mpi_log_file -- single log file for mpi output (when mpi_n > 0)
	"""
	run_mode('infile',tipsy_file,snap_prefix,T,dt, dSnap, eps, bonsai_bin, mpi_n,mpi_log_file)


def run_mode(mode,nPart_or_file,snap_prefix,T,dt, dSnap, eps, bonsai_bin, mpi_n,mpi_log_file):
	"""
	Run Bonsai in mode 'plummer', 'sphere' or 'infile'

	Keyword arguments:
	mode -- "plummer" or "sphere" or "infile"
	nPart_or_file -- number of particles per mpi process, or path to tipsy file for 'infile' mode
	snap_prefix -- path prefix for snapshot (tipsy) files (simulation time will be appended)
	T -- total simulation time
	dt -- internal time step
	dSnap -- interval at which snapshot files are generated
	bonsai_bin -- path to bonsai exe
	mpi_n -- specifies the number of mpi processes (0 = mpi not used)
	mpi_log_file -- single log file for mpi output (when mpi_n > 0)
	""" 

	if mode != 'plummer' and mode != 'sphere' and mode != 'infile':
		raise Exception("Error: model '%s' is not known." % mode)

	if bonsai_bin is None:
		#use default
		bonsai_bin = BONSAI_BIN

	log = False

	if mpi_n > 0:
		#run mpi
		#mpirun -n 2 --output-filename mpiout.txt ./bonsai2_slowdust -i model3_child_compact.tipsy -T1000 --logfile logfile.txt
		if call(['mpirun','-n',str(mpi_n),
				 '--output-filename',mpi_log_file,bonsai_bin,
				 '--'+mode,str(nPart_or_file),
				 '--snapname',snap_prefix,'--snapiter',str(dSnap),
				 '-T',str(T),'-dt',str(dt),
				 '--eps',str(eps),
				]):
			return "Error"
		else:
			return "Done"

	else:
		#single GPU mode
		if call([bonsai_bin,'--log' if log else '','--'+mode,str(nPart_or_file),'--snapname',snap_prefix,'--snapiter',str(dSnap),'-T',str(T),'-dt',str(dt),'--eps',str(eps),]):
			return "Error"
		else:
			return "Done"


def run_plummer(nParticles,snap_prefix,T=2,dt=0.0625, dSnap = 0.0625, eps=0.05, bonsai_bin = None, mpi_n = 0, mpi_log_file = 'mpiout.log'):
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
	run_mode("plummer",nParticles,snap_prefix,T,dt, dSnap, eps, bonsai_bin, mpi_n,mpi_log_file)


def run_sphere(nParticles,snap_prefix,T=2,dt=0.0625, dSnap = 0.0625, eps=0.05, bonsai_bin = None, mpi_n = 0, mpi_log_file = 'mpiout.log'):
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
	run_mode("sphere",nParticles,snap_prefix,T,dt, dSnap, eps, bonsai_bin, mpi_n,mpi_log_file)
## @namespace bonsai 
#  The bonsai module provides a set of wrapping functions to the Bonsai tree code (https://github.com/fizxmike/Bonsai)

"""
Bonsai.py module

Used to easily hadle .tipsy file format.

Offers nbody.txt/.tipsy conversion, galaxy manipulation, plotting and video creation.

Author: Michael M. Folkerts
E-Mail: mmfolkerts@gmail.com
Project: UC San Diego Physics 241, Winter 2014, Prof. J. Kuti
"""



from subprocess import call

##\short	Path to Bonsai binary
##\details 	Default path, assuming bonsai_phys241 and Bonsai share parent folders
BONSAI_BIN = "../Bonsai/runtime/bonsai2_slowdust"

def run_tipsy(tipsy_file,snap_prefix,T,dt, dSnap, eps, bonsai_bin=None, mpi_n=0,mpi_log_file="mpiout.log"):
	"""
	Runs Bonsai with initial conditions defined by tipsy file

	@param[in]	tipsy_file		containing initial conditions
	@param[in]	snap_prefix		path prefix for snapshot files (time will be appended)
	@param[in]	T				total simulation time
	@param[in]	dt				internal time step
	@param[in]	dSnap			interval at which snapshot files are generated
	@param[in]	bonsai_bin		path to bonsai exe
	@param[in]	mpi_n			specifies the number of mpi processes (0 = mpi not used)
	@param[in]	mpi_log_file	single log file for mpi output (when mpi_n > 0)

	@returns None
	"""
	run_mode('infile',tipsy_file,snap_prefix,T,dt, dSnap, eps, bonsai_bin, mpi_n,mpi_log_file)



def run_mode(mode,nPart_or_file,snap_prefix,T,dt, dSnap, eps, bonsai_bin, mpi_n,mpi_log_file):
	"""
	Run Bonsai in mode "plummer", "sphere" or "infile"

	This is an internal function, use the other interfaces instead.

	@param[in]	mode			"plummer" or "sphere" or "infile"
	@param[in]	nPart_or_file	number of particles per mpi process, or path to tipsy file for "infile" mode
	@param[in]	snap_prefix		path prefix for snapshot (tipsy) files (simulation time will be appended)
	@param[in]	T				total simulation time
	@param[in]	dt				internal time step
	@param[in] 	dSnap			interval at which snapshot files are generated
	@param[in]	bonsai_bin		path to bonsai exe
	@param[in]	mpi_n			specifies the number of mpi processes (0 = mpi not used)
	@param[in] mpi_log_file		single log file for mpi output (when mpi_n > 0)

	@returns None
	@sa run_tipsy(), run_plummer(), run_sphere()
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


def run_plummer(nParticles,snap_prefix,T=2,dt=0.0625, dSnap = 0.0625, eps=0.05, bonsai_bin = None, mpi_n = 0, mpi_log_file = "mpiout.log"):
	"""
	Run a Bonsai's built in plummer model

	@param[in]	nParticles		number of particles (per mpi process)
	@param[in]	snap_prefix		path prefix for snapshot files (time will be appended)
	@param[in]	T				total simulation time
	@param[in]	dt				internal time step
	@param[in]	dSnap			interval at which snapshot files are generated
	@param[in]	bonsai_bin		path to bonsai exe
	@param[in]	mpi_n			specifies the number of mpi processes (0 = mpi not used)
	@param[in]	mpi_log_file	single log file for mpi output (when mpi_n > 0)

	@returns	None
	"""
	run_mode("plummer",nParticles,snap_prefix,T,dt, dSnap, eps, bonsai_bin, mpi_n,mpi_log_file)


def run_sphere(nParticles,snap_prefix,T=2,dt=0.0625, dSnap = 0.0625, eps=0.05, bonsai_bin = None, mpi_n = 0, mpi_log_file = "mpiout.log"):
	"""
	Run a Bonsai's built in plummer model

	@param[in]	nParticles		number of particles (per mpi process)
	@param[in]	snap_prefix		path prefix for snapshot files (time will be appended)
	@param[in]	T				total simulation time
	@param[in]	dt				internal time step
	@param[in]	dSnap			interval at which snapshot files are generated
	@param[in]	bonsai_bin		path to bonsai exe
	@param[in]	mpi_n			specifies the number of mpi processes (0 = mpi not used)
	@param[in]	mpi_log_file	single log file for mpi output (when mpi_n > 0)

	@returns	None
	"""
	run_mode("sphere",nParticles,snap_prefix,T,dt, dSnap, eps, bonsai_bin, mpi_n,mpi_log_file)
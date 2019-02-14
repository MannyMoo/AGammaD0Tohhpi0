#!/usr/bin/env python

import math, os, subprocess, shutil

# Range in phi [radians]
phimin = -50./180 * math.pi
phimax = 50./180 * math.pi

# Range in |q/p|
qoverpmin = 0.6
qoverpmax = 1.5

# Number of points to scan in each dimension.
# Total number of jobs will be npoints**2
npoints = 2

# Calculate step sizes.
phistep = (phimax - phimin)/(npoints - 1.)
qoverpstep = (qoverpmax - qoverpmin)/(npoints - 1.)

# Directory that'll hold the output.
outputdir = '/nfs/lhcb/malexander01/wenyan'

pwd = os.getcwd()
config = os.path.abspath('pipipi0.txt')
exe = os.path.abspath('ampFit')
envscript = os.path.abspath('mint-env.sh')

if not os.path.exists(exe) :
    raise OSError("Can't find ampFit! It must be in the current working directory.")

for i in xrange(npoints) :
    for j in xrange(npoints) :
        # phi & |q/p| values for this step.
        phi = phimin + i * phistep
        qoverp = qoverpmin + j * qoverpstep
        binname = 'phibin_' + str(i).zfill(2) + '_qoverpbin_' + str(j).zfill(2)
        
        # Make the job directory.
        jobdir = os.path.join(outputdir, binname)
        if not os.path.exists(jobdir) :
            os.makedirs(jobdir)
        # Copy the config file & set the value of phi & |q/p|.
        jobconfig = os.path.join(jobdir, 'pipipi0.txt')
        shutil.copy(config, jobconfig)
        with open(jobconfig) as fjob :
            configlines = filter(lambda line : not line.startswith('phi') and not line.startswith('qoverp'),
                                 fjob)
        configlines += ['phi    ' + str(phi) + '\n',
                        'qoverp ' + str(qoverp) + '\n']
        with open(jobconfig, 'w') as fjob :
            fjob.writelines(configlines)

        # Make the script that will run the generation.
        jobscript = os.path.join(jobdir, 'run.sh')
        with open(jobscript, 'w') as fjobscript :
            fjobscript.write('#!/bin/bash\n')
            # Copy the current environment.
            for var, val in os.environ.items() :
                if '(' in var :
                    continue
                fjobscript.write('export ' + var + '=' + repr(val) + '\n')
            fjobscript.write('. {0}\n'.format(envscript) +
                             'cd ' + jobdir + '\n'
                             '{0} < {1}\n'.format(exe, jobconfig))
        os.chmod(jobscript, 0744)

        # Submit the job.
        subprocess.call(['qsub', '-N', binname, '-q', 'medium6', '-w', jobdir, jobscript])

# Copyright 2013-2020 Lawrence Livermore National Security, LLC and other
# Spack Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

from spack import *


class Pism(CMakePackage):
    """Parallel Ice Sheet Model"""

    homepage = "http://pism-docs.org/wiki/doku.php:="
    url      = "https://github.com/pism/pism/archive/v1.1.4.tar.gz"
    git      = "https://github.com/pism/pism.git"

    maintainers = ['citibeth']

    version('develop', branch='dev')
    version('2.0.2', sha256='f316cc50d6a7cd77df9fc416c90d7c16debdc8ea050ef57deb621e1d72440403')
    version('1.2.2', sha256='ecb880af26643e80b890f74efcf0e4d7e5d60adbc921ef281d3f00904020c624')
    version('1.1.4', sha256='8ccb867af3b37e8d103351dadc1d7e77512e64379519fe8a2592668deb27bc44')
    version('0.7.x', branch='stable0.7')
    version('icebin', branch='efischer/dev')

    variant('extra', default=False,
            description='Build extra executables (testing/verification)')
    variant('shared', default=True,
            description='Build shared Pism libraries')
    variant('python', default=False,
            description='Build python bindings')
    variant('icebin', default=False,
            description='Build classes needed by IceBin')
    variant('proj', default=True,
            description='Use Proj.4 to compute cell areas, '
            'longitudes, and latitudes.')
    variant('parallel-netcdf4', default=True,
            description='Enables parallel NetCDF-4 I/O.')
    variant('parallel-netcdf3', default=False,
            description='Enables parallel NetCDF-3 I/O using PnetCDF.')
    variant('parallel-hdf5', default=False,
            description='Enables parallel HDF5 I/O.')
    # variant('tao', default=False,
    #         description='Use TAO in inverse solvers.')

    description = 'Build PISM documentation (requires LaTeX and Doxygen)'
    variant('doc', default=False, description=description)

    variant('examples', default=False,
            description='Install examples directory')

    description = 'Report errors through Everytrace (requires Everytrace)'
    variant('everytrace', default=False, description=description)

    # CMake build options not transferred to Spack variants
    # (except from CMakeLists.txt)
    #
    # option (Pism_TEST_USING_VALGRIND "Add extra regression tests
    #         using valgrind" OFF)
    # mark_as_advanced (Pism_TEST_USING_VALGRIND)
    #
    # option (Pism_ADD_FPIC "Add -fPIC to C++ compiler flags
    #         (CMAKE_CXX_FLAGS). Try turning it off if it does not work." ON)
    # option (Pism_LINK_STATICALLY
    #         "Set CMake flags to try to ensure that everything is
    #         linked statically")
    # option (Pism_LOOK_FOR_LIBRARIES
    #         "Specifies whether PISM should look for libraries. (Disable
    #         this on Crays.)" ON)
    # option (Pism_USE_TR1
    #        "Use the std::tr1 namespace to access shared pointer
    #        definitions. Disable to get shared pointers from the std
    #        namespace (might be needed with some compilers)." ON)
    # option (Pism_USE_TAO "Use TAO in inverse solvers." OFF)

    depends_on('fftw')
    depends_on('gsl')
    depends_on('mpi')
    depends_on('netcdf-c')    # Only the C interface is used, no netcdf-cxx4
    depends_on('petsc')
    depends_on('udunits')
    depends_on('proj@6:')
    depends_on('everytrace', when='+everytrace')
    depends_on('cmake@3.1:', type='build')

    extends('python', when='+python')
    depends_on('python@2.7:2.8,3.3:', when='@1.1: +python')
    depends_on('python@2.7:2.8', when='@:1.0 +python')
    depends_on('py-matplotlib', when='+python')
    depends_on('py-numpy', when='+python')

    def setup_environment(self, spack_env, run_env):
        spack_env.set('I_MPI_FABRICS', 'shm:tmi')

    def cmake_args(self):
        spec = self.spec

        return [
            '-DCMAKE_C_COMPILER=%s' % spec['mpi'].mpicc,
            '-DCMAKE_CXX_COMPILER=%s' % spec['mpi'].mpicxx,
            # Fortran not needed for PISM...
            # '-DCMAKE_Fortran_COMPILER=%s' % spec['mpi'].mpifc,
            '-DPism_BUILD_EXTRA_EXECS=%s' %
            ('YES' if '+extra' in spec else 'NO'),
            '-DBUILD_SHARED_LIBS=%s' %
            ('YES' if '+shared' in spec else 'NO'),
            '-DPism_BUILD_PYTHON_BINDINGS=%s' %
            ('YES' if '+python' in spec else 'NO'),
            '-DPism_BUILD_ICEBIN=%s' %
            ('YES' if '+icebin' in spec else 'NO'),
            '-DPism_USE_PROJ=%s' %
            ('YES' if '+proj' in spec else 'NO'),
            '-DPism_USE_PARALLEL_NETCDF4=%s' %
            ('YES' if '+parallel-netcdf4' in spec else 'NO'),
            '-DPism_USE_PNETCDF=%s' %
            ('YES' if '+parallel-netcdf3' in spec else 'NO'),
            '-DPism_USE_PARALLEL_HDF5=%s' %
            ('YES' if '+parallel-hdf5' in spec else 'NO'),
            '-DPism_BUILD_PDFS=%s' %
            ('YES' if '+doc' in spec else 'NO'),
            '-DPism_INSTALL_EXAMPLES=%s' %
            ('YES' if '+examples' in spec else 'NO'),
            '-DPism_USE_EVERYTRACE=%s' %
            ('YES' if '+everytrace' in spec else 'NO')]

    def setup_run_environment(self, env):
        env.set('PISM_PREFIX', self.prefix)
        env.set('PISM_BIN', self.prefix.bin)


# From email correspondence with Constantine Khroulev:
#
# > Do you have handy a table of which versions of PETSc are required
# > for which versions of PISM?
#
# We don't. The installation manual [1] specifies the minimum PETSc
# version for the latest "stable" release (currently PETSc 3.3). The
# stable PISM version should support all PETSc versions starting from the
# one specified in the manual and up to the latest PETSc release.
#
# The current development PISM version should be built with the latest
# PETSc release at the time (the "maint" branch of PETSc).
#
# Thanks to Git it is relatively easy to find this info, though:
#
# | PISM version | PETSc version |
# |--------------+---------------|
# |          0.7 | 3.3 and later |
# |          0.6 | 3.3           |
# |       new_bc | 3.4.4         |
# |          0.5 | 3.2           |
# |          0.4 | 3.1           |
# |          0.3 | 2.3.3 to 3.1  |
# |          0.2 | 2.3.3 to 3.0  |
# |          0.1 | 2.3.3-p2      |

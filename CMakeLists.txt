################################################################################
# Package: AGammaD0Tohhpi0
################################################################################
gaudi_subdir(AGammaD0Tohhpi0 v0r1)

gaudi_depends_on_subdirs(
	GaudiConfUtils
	AnalysisUtils
	Mint2)

find_package(PythonLibs)
find_package(Boost COMPONENTS program_options REQUIRED)
find_package(ROOT COMPONENTS Core RIO Hist Graf Graf3d Postscript Gpad
                             RooFit RooFitCore Tree MathCore Foam Physics
                             Proof ProofBench ProofDraw ProofPlayer)

# override the genreflex call to wrap it in the right environment
# set(ROOT_genreflex_CMD ${env_cmd} --xml ${env_xml} ${ROOT_genreflex_CMD})

include_directories(${Boost_INCLUDE_DIRS} ${ROOT_INCLUDE_DIRS})
# gaudi_add_dictionary(AGammaD0Tohhpi0
#                      dict/AGammaD0Tohhpi0Dict.h dict/AGammaD0Tohhpi0Dict.xml
#                      SPLIT_CLASSDEF)

# gaudi_add_library(AGammaD0Tohhpi0Lib
#                   src/*.cpp
#                   PUBLIC_HEADERS AGammaD0Tohhpi0
#                   INCLUDE_DIRS Boost ROOT Mint2
#                   LINK_LIBRARIES Boost ROOT Mint2Lib)

# # ensure that genreflex is not called twice (in parallel builds)
# add_dependencies(AGammaD0Tohhpi0Lib AGammaD0Tohhpi0Gen)

gaudi_install_python_modules()

#gaudi_add_test(QMTest QMTEST)

# gaudi_add_executable(ampFit src/bin/ampFit.cpp LINK_LIBRARIES Boost ROOT DaVinciKernelLib Mint2Lib AGammaD0Tohhpi0Lib)

# run as "source setup_env.sh"

# activate python3 environment (created using Anaconda python dist)
# containing Numpy & Pandas
source activate python3

LIBPATH="$(PWD)/lib"
echo prepending $LIBPATH to PYTHONPATH
export PYTHONPATH=$LIBPATH:$PYTHONPATH

#IPYDIR="$(PWD)/ipython"
#echo setting IPYTHONDIR to $IPYDIR
#export IPYTHONDIR="$IPYDIR

OLD_PATH=$PATH

# Installing BRIL work suite
# This is will install brilws locally for the user under the Python3 version
# specified by /cvmfs/cms-bril.cern.ch/brilconda3/bin
export PATH=$HOME/.local/bin:/cvmfs/cms-bril.cern.ch/brilconda3/bin:$PATH
pip install --user brilws

# Check installation
echo -e "\nChecking installation by printing brilcalc version:"
brilcalc --version
if [ $? == 0 ]; then
  echo "Successfully installed BRIL work suite!"
fi

# Restore old path to proceed with the rest of the installation
# Could not install brilws with LCG release, and the LCG installation
# is needed for some packages
export PATH=$OLD_PATH

# Installing CMS OMS API for this project (not to mess up with the user's installation)
echo -e "\nInstalling the CMS OMS API locally for this project"
git clone ssh://git@gitlab.cern.ch:7999/cmsoms/oms-api-client.git
mkdir external
mv oms-api-client/omsapi external
rm -rf oms-api-client

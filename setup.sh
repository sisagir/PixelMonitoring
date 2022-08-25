echo -e "\nInstalling the CMS OMS API locally for this project"
git clone ssh://git@gitlab.cern.ch:7999/cmsoms/oms-api-client.git
mv oms-api-client/omsapi .
rm -rf oms-api-client

echo -e "\nSourcing a recent LCG release to get useful packages"
source /cvmfs/sft.cern.ch/lcg/views/LCG_102/x86_64-centos7-gcc8-opt/setup.sh

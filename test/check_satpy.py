import satpy 

#check if satpy has all the dependencies installed
from satpy.utils import check_satpy
check_satpy()

#check the readers name available in satpy
print(satpy.available_readers())
#seviri_l1b_native
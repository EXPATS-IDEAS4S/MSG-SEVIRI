#################
# TODO:how to know which MSG satellite was used for the data????
# -> they have different Parameters for calculation of Brightness Temp
# TODO: understand units and double check in which unit data is given

### constants taken from www-cdn.eumetsat.int/files/2020-04/pdf_effect_rad_to_brightness.pdf

# %%
import numpy as np
import xarray as xr
import pvlib
from pvlib.location import Location

# %%
#############
############# look up tables for calculating brightness temperature
#############
# constants taken from website: 
# https://eumetsatspace.atlassian.net/wiki/spaces/DSDT/pages/1537277953/MSG15+radiances+conversion+to+BT+and+Reflectances
# and from www-cdn.eumetsat.int/files/2020-04/pdf_effect_rad_to_brightness.pdf

C1 = 1.19104*10**(-5)  # in [mW (cm−1)−4 m-2 sr−1]
C2 = 1.43877  # in [K cm]

CHANNEL_NAME = {"channel_1": "VIS 0.6", 
                "channel_2": "VIS 0.8", 
                "channel_3": "NIR 1.6", 
                "channel_4": "IR 3.9", 
                "channel_5": "WV 6.2", 
                "channel_6": "WV 7.3", 
                "channel_7": "IR 8.7", 
                "channel_8": "IR 9.7 - O3", 
                "channel_9": "IR 10.8", 
                "channel_10": "IR 12.0", 
                "channel_11": "IR 13.4 - CO2", }
# in [cm−1]
VC = {'MSG1': {"channel_4": 2567.330, "channel_5": 1598.103, "channel_6": 1362.081, "channel_7": 1149.069, 
                "channel_8": 1034.343, "channel_9": 930.647, "channel_10": 839.660, "channel_11": 752.387
                }, 
      'MSG2': {"channel_4": 2568.832, "channel_5": 1600.548, "channel_6": 1360.330, "channel_7": 1148.620, 
                "channel_8": 1035.289, "channel_9": 931.700, "channel_10": 836.445, "channel_11": 751.792
                }, 
      'MSG3': {"channel_4": 2547.771, "channel_5": 1595.621, "channel_6": 1360.377, "channel_7": 1148.130, 
                "channel_8": 1034.715, "channel_9": 929.842, "channel_10": 838.659, "channel_11": 750.653
                }, 
      'MSG4': {"channel_4": 2555.280, "channel_5": 1596.080, "channel_6": 1361.748, "channel_7": 1147.433, 
                "channel_8": 1034.851, "channel_9": 931.122, "channel_10": 839.113, "channel_11": 748.585
                }, }
# unitless
ALPHA = {'MSG1': {"channel_4": 0.9956, "channel_5": 0.9962, "channel_6": 0.9991, "channel_7": 0.9996, 
                   "channel_8": 0.9999, "channel_9": 0.9983, "channel_10": 0.9988, "channel_11": 0.9981
                   }, 
         'MSG2': {"channel_4": 0.9954, "channel_5": 0.9963, "channel_6": 0.9991, "channel_7": 0.9996, 
                   "channel_8": 0.9999, "channel_9": 0.9983, "channel_10": 0.9988, "channel_11": 0.9981
                   }, 
         'MSG3': {"channel_4": 0.9915, "channel_5": 0.9960, "channel_6": 0.9991, "channel_7": 0.9996, 
                   "channel_8": 0.9999, "channel_9": 0.9983, "channel_10": 0.9988, "channel_11": 0.9982
                   }, 
         'MSG4': {"channel_4": 0.9916, "channel_5": 0.9959, "channel_6": 0.9990, "channel_7": 0.9996, 
                   "channel_8": 0.9998, "channel_9": 0.9983, "channel_10": 0.9988, "channel_11": 0.9981
                   }, }
# in [K]
BETA = {'MSG1': {"channel_4": 3.410, "channel_5": 2.218, "channel_6": 0.478, "channel_7": 0.179, ''
                  "channel_8": 0.060, "channel_9": 0.625, "channel_10": 0.397, "channel_11": 0.578
                  },
        'MSG2': {"channel_4": 3.438, "channel_5": 2.185, "channel_6": 0.470, "channel_7": 0.179, 
                  "channel_8": 0.056, "channel_9": 0.640, "channel_10": 0.408, "channel_11": 0.561
                  },
        'MSG3': {"channel_4": 2.9002, "channel_5": 2.0337, "channel_6": 0.4340, "channel_7": 0.1714, 
                  "channel_8": 0.0527, "channel_9": 0.6084, "channel_10": 0.3882, "channel_11": 0.5390
                  },
        'MSG4': {"channel_4": 2.9438, "channel_5": 2.0780, "channel_6": 0.4929, "channel_7": 0.1731, 
                  "channel_8": 0.0597, "channel_9": 0.6256, "channel_10": 0.4002, "channel_11": 0.5635
                  }, }

# %%
#############
############# look up tables for calculating reflectances
#############
# constants taken from website: 
# https://eumetsatspace.atlassian.net/wiki/spaces/DSDT/pages/1537277953/MSG15+radiances+conversion+to+BT+and+Reflectances
# and from https://www-cdn.eumetsat.int/files/2020-04/pdf_msg_seviri_rad2refl.pdf

IRRAD = {'MSG1': {"channel_1": 65.2296, "channel_2": 73.0127, "channel_3": 62.3715},
         'MSG2': {"channel_1": 65.2065, "channel_2": 73.1869, "channel_3": 61.9923},
         'MSG3': {"channel_1": 65.5148, "channel_2": 73.1807, "channel_3": 62.0208}, 
         'MSG4': {"channel_1": 65.2656, "channel_2": 73.1692, "channel_3": 61.9416}, }


# %%
class ir_channel:
    """
    class that calls channel specific constants from look up tables above
    """
    def __init__(self, satellite, channel):

        self.name = CHANNEL_NAME[channel]
        self.vc = VC[satellite][channel]  # wavenumber in [cm−1]
        self.alpha = ALPHA[satellite][channel]  # unitless
        self.beta = BETA[satellite][channel]  # in [K]

class vis_nir_channel:
    def __init__(self, satellite, channel):
        
        self.name = CHANNEL_NAME[channel]
        self.irrad = IRRAD[satellite][channel]  # irradiance at 1AU in [mW·m-2·(cm-1)-1]

class MSG_satellite:
    def __init__(self, name):
        self.name =  name

    def _get_channel(self, channel_number):
        # return vis/nir or ir channel depending on channel number
        if channel_number <=3:
            return vis_nir_channel(satellite=self.name, channel=f"channel_{channel_number}")
        else:
            return ir_channel(satellite=self.name, channel=f"channel_{channel_number}")

    def rad_2_tb(self, channel_number, radiances):
        # error handling here:
        # TODO: raise exception when given incorrect channel_number, must be >=4

        # get constants for given channel
        channel_consts = self._get_channel(channel_number)

        # converting radiance to brightness temperature [K] with simplified equation
        numerator = C2 * channel_consts.vc
        fraction = C1 * channel_consts.vc**3 / radiances + 1
        denominator = channel_consts.alpha * (np.log(fraction))
        tb = numerator / denominator - channel_consts.beta / channel_consts.alpha  ## [K]
        return tb
    
    def _d(t):
        # Sun-Earth distance in AU at time t
        return None
    
    def _solar_zenith_angle(t, lon, lat):
        # Solar Zenith Angle in Radians at time t and location x
        return None

    def rad_2_refl(self, channel_number, radiances, t, lon, lat):
        # error handling here:
        # TODO: raise exception when given incorrect channel_number, must be <= 3

        # get constants for given channel
        channel_consts = self._get_channel(channel_number)

        numerator = np.pi * radiances * self._d(t)**2
        denominator = channel_consts.irrad * np.cos(self._solar_zenith_angle(t, lon, lat))

# %%
def radiances_2_brightnesstemp_and_reflectances(radiances, channel_number, satellite_name):
    ## radiances in [mW m−2 sr−1 (cm−1)−1)]
    # TODO: add constraint to channel_number (must be >= 4)

    # access correct satellite 
    satellite = MSG_satellite(satellite_name)
    if channel_number <= 3:
        print("not implemented yet for visible and near-infrared")

    elif channel_number >= 4 and channel_number < 12:
        # get brightness temp fro given channel
        return satellite.rad_2_tb(channel_number, radiances)
    
    else:
        print(f"This channel does not exist for satellite {satellite_name}")
        # TODO: raise exception


# %%
if __name__ == '__main__':
    # example files
    example_MSG = "/net/norte/pbigalke/Alps/data/msg/2023-07-24/HRSEVIRI_20230724T193009Z_20230724T194242Z_epct_b890f782_PC.nc"
    with xr.open_dataset(example_MSG) as dataset:
        data = dataset
        print(data)
        #for attri in data.attrs:
        #    print(attri, data.attrs[attri])

    satellite_name = data.EPCT_product_name.split('-')[0]
    print(satellite_name)

    # loop over all brightness temp channels
    for ch in np.arange(4, 12, 1):
        radiances = data[f"channel_{ch}"].values

        print(radiances)
        tb = radiances_2_brightnesstemp_and_reflectances(radiances, ch, satellite_name)
        print(tb)

# %%

# config.py
CLOUD_PRM = ['IR_108'] #list of the channels to use
APPLY_CMA = True # Set to True if you want to apply (corrected) CMA mask to IR_108 channel
CROPPING_STRATEGY = 'random' # 'random' or 'fixed', ranodom mostly used for training, fixed for testing
N_SAMPLES = 3 # Number of random crops to generate per timestamp
TIME_LENGTH = 1 # In case 
TIME_JUMP = 1
CROP_UL_LAT = 50.0
CROP_UL_LON = 6.5
MONTH_START, MONTH_END = '04', '09'
DAY_START, DAY_END = '01', '31'
HOUR_START, HOUR_END = '00', '24'
VALUE_MIN = [180.0, 200.0]
VALUE_MAX = [320.0, 260.0]
X_PIXEL, Y_PIXEL = 100, 100
DOMAIN = (5, 16, 42, 51.5)
DOMAIN_NAME = 'EXPATS'
YEARS = [2013, 2014]
MONTHS = range(4, 5)
DAYS = range(1, 32)
PATH_DIR = "/data/sat/msg/ml_train_crops/IR_108-WV_062-CMA_FULL_EXPATS_DOMAIN"
BASENAME = "merged_MSG_CMSAF"
OUTPUT_BASE = "/data1/crops"

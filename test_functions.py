



# function to check if the file is already present in the downloading directory
def is_file_present(filename, download_filenames, format):
    # Get the time string from the filenames after 'search' command 
    # example of name file before costumization: 
    # MSG4-SEVI-MSG15-0100-NA-20210714121243.449000000Z-NA 
    time_str = filename.split('.')[0].split('-')[-1]    

    
    if format == 'hrit':
        # hrit filenames: H-000-MSG4__-MSG4________-WV_073___-000003___-202107141200-__
        # for each time there is a file for each channel and divided in 8 files
        #get the part of the datestring that refers to the minutes
        min_str = time_str[10:12]
        #switch the minutes that indicate the end of the scan to the minutes that indicate the 'rounded' start of the scan
        if '00'<min_str<'15': min_str='00'
        if '15'<min_str<'30': min_str='15' 
        if '30'<min_str<'45': min_str='30'
        if '45'<min_str<'59': min_str='45'
        time_str = time_str[0:10]+min_str 
        #count how many files have the correspoding timestring in the filename
        count = sum(1 for file in download_filenames if time_str in file)
        #check if all the channels (11) and each single scan (8) are present
        if count == 11*8:
            return True
        return False
    else:   
        # Check if a file for this time period already exists
        for file in download_filenames:
            # filename after costumization depends on the format:
            if format == 'msgnative':
                #nat filenames example: MSG3-SEVI-MSG15-0100-NA-20230731215741.559000000Z-NA.subset.nat
                time_str_cust = file.split('.')[0].split('-')
            elif format == 'netcdf4':
                #nc filename example: HRSEVIRI_20210715T101510Z_20210715T102742Z_epct_34b8524d_PC.nc
                time_str = time_str = time_str[:8] + 'T' + time_str[8:] + 'Z' # Insert 'T' after the 8th character and 'Z' at the end
                time_str_cust = file.split('.')[0].split('_')
            else:
                time_str_cust = []
                print("format not recognized.")
            #check if the timestring is in the filename
            if time_str in time_str_cust:    
                return True
        return False
    
filename = 'MSG4-SEVI-MSG15-0100-NA-20210714121243.449000000Z-NA'

download_filenames_hrit = ['H-000-MSG4__-MSG4________-WV_073___-000003___-202107141245-__']
download_filenames_nat = ['MSG3-SEVI-MSG15-0100-NA-20210714121243.559000000Z-NA.subset.nat']
download_filenames_nc = ['HRSEVIRI_20210715T101510Z_20210714T121243Z_epct_34b8524d_PC.nc']
print(is_file_present(filename,download_filenames_hrit*11*8,'hrit'))
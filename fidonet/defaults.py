import os

ftn_config_dir = os.environ.get('FTN_CONFIG_DIR', '/etc/ftn')
ftn_config_file = os.path.join(ftn_config_dir, 'ftn.cfg')
ftn_data_dir = os.environ.get('FTN_DATA_DIR', '/var/lib/ftn')

if __name__ == '__main__':

    for varname, varval in locals().items():
        if varname.startswith('ftn_'):
            print varname, '=', varval



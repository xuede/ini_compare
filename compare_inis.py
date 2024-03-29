import configparser
import pandas as pd

def ini_to_dataframe(ini_path):
    config = configparser.ConfigParser(interpolation=None)
    config.read(ini_path)
    data = {'Section': [], 'Field': [], 'Value': []}
    for section in config.sections():
        for key, value in config.items(section):
            data['Section'].append(section)
            data['Field'].append(key)
            data['Value'].append(value)
    return pd.DataFrame(data)

def update_production_ini(df_oob, df_prod, prod_path):
    # Merge both dataframes on 'Section' and 'Field' to find common fields and unique fields
    merged = df_oob.merge(df_prod, on=['Section', 'Field'], how='outer', suffixes=('_oob', '_prod'))

    # Load the production INI file
    config_prod = configparser.ConfigParser(interpolation=None)
    config_prod.read(prod_path)

    # Update shared fields with the same value
    shared_same = merged.dropna(subset=['Value_oob', 'Value_prod'])
    for _, row in shared_same.iterrows():
        if row['Value_oob'] == row['Value_prod']:
            if not config_prod.has_section(row['Section']):
                config_prod.add_section(row['Section'])
            config_prod.set(row['Section'], row['Field'], row['Value_oob'])

    # Add unique fields to the Production INI from OoB INI
    unique_to_oob = merged[merged['Value_prod'].isnull()]
    for _, row in unique_to_oob.iterrows():
        if not config_prod.has_section(row['Section']):
            config_prod.add_section(row['Section'])
        config_prod.set(row['Section'], row['Field'], row['Value_oob'])

    # Write the updated Production INI file
    with open(prod_path, 'w') as configfile:
        config_prod.write(configfile)

# Define paths to the INI files
oob_ini_path = 'path_to_OoB_PWB.INI'
prod_ini_path = 'path_to_prod_PWB.INI'

# Convert the INI files to DataFrames
df_oob = ini_to_dataframe(oob_ini_path)
df_prod = ini_to_dataframe(prod_ini_path)

# Update the Production INI file with the Out-of-Box settings
update_production_ini(df_oob, df_prod, prod_ini_path)

print(f"Production INI file '{prod_ini_path}' has been updated.")

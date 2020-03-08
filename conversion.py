import csv
import json
import os

from tqdm import tqdm

postcode_lookup = {}
details_lookup = {}

# unzip https://opendatacommunities.org/imd-files/imd2019lsoa.csv?uri=http%3A%2F%2Fopendatacommunities.org%2Fdata%2Fsocietal-wellbeing%2Fimd2019%2Findices and place in data folder

with open('data/PCD_OA_LSOA_MSOA_LAD_FEB19_UK_LU.csv', 'r') as f:
    data = csv.reader(f)
    headers = next(data)

    row_i = headers.index('lsoa11cd')

    for row in tqdm(data, total=2624585):
        postcode = row[row_i]
        postcode_lookup[postcode] = row

with open('data/imd2019lsoa.csv', 'r') as f:
    data = csv.reader(f)
    headers = next(data)
    row_i = headers.index('FeatureCode')
    index_of_deprivation_i = headers.index('Indices of Deprivation')
    measurement_i = headers.index('Measurement')
    value_i = headers.index('Value')
    postcode_i = 0

    for row in tqdm(data, total=985320):

        linking_header = row[row_i]
        postcode_info = postcode_lookup[linking_header]
        postcode = postcode_info[postcode_i].replace(' ', '')

        index_of_deprivation = row[index_of_deprivation_i]
        index_of_deprivation = index_of_deprivation[3:] # first 3 characters are a. b. c. etc and so not useful
        measurement = row[measurement_i]
        value = row[value_i]

        if postcode not in details_lookup:
            details_lookup[postcode] = {'postcode_info': postcode_info, }

        if index_of_deprivation not in details_lookup[postcode]:
            details_lookup[postcode][index_of_deprivation] = {}

        if index_of_deprivation not in details_lookup[postcode][index_of_deprivation]:
            details_lookup[postcode][index_of_deprivation][index_of_deprivation] = {}

        details_lookup[postcode][index_of_deprivation][index_of_deprivation][measurement] = value

# let's group similar postcodes
postcode_characters_to_group_by = 3
grouped = {}

for postcode, data in details_lookup.items():
    abbrev_postcode = postcode[:postcode_characters_to_group_by]
    if abbrev_postcode not in grouped:
        grouped[abbrev_postcode] = []
    grouped[abbrev_postcode].append({postcode: data})

try:
    os.makedirs('grouped')
except OSError as e:
    pass

for abbrev_postcode, group in tqdm(grouped.items()):
    try:
        os.makedirs('grouped/{postcode_characters_to_group_by}chars')
    except OSError as e:
        pass
    with open(f'grouped/{postcode_characters_to_group_by}chars/{abbrev_postcode}.csv', 'w+') as f:
        f.write(json.dumps(group))



import csv
import json
import os
from pathlib import Path

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

    # Below are the possible indices to include
    # ['Income Deprivation Domain', 'Index of Multiple Deprivation (IMD)', 'Employment Deprivation Domain', 'Education, Skills and Training Domain', 'Income Deprivation Affecting Older People Index (IDAOPI)', 'Income Deprivation Affecting Children Index (IDACI)', 'Crime Domain', 'Health Deprivation and Disability Domain', 'Living Environment Deprivation Domain', 'Barriers to Housing and Services Domain']

    indices_to_include = []
    indices_to_include_use = len(indices_to_include) > 0

    for row in tqdm(data, total=985320):

        linking_header = row[row_i]
        postcode_info = postcode_lookup[linking_header]
        postcode = postcode_info[postcode_i].replace(' ', '')

        index_of_deprivation = row[index_of_deprivation_i]
        index_of_deprivation = index_of_deprivation[3:]  # first 3 characters are a. b. c. etc and so not useful
        measurement = row[measurement_i]
        value = row[value_i]

        if postcode not in details_lookup:
            details_lookup[postcode] = {'postcode_info': postcode_info, }

        if indices_to_include_use:
            if index_of_deprivation not in indices_to_include:
                continue

        if index_of_deprivation not in details_lookup[postcode]:
            details_lookup[postcode][index_of_deprivation] = {}

        if index_of_deprivation not in details_lookup[postcode][index_of_deprivation]:
            details_lookup[postcode][index_of_deprivation][index_of_deprivation] = {}

        details_lookup[postcode][index_of_deprivation][index_of_deprivation][measurement] = value

# let's group similar postcodes
min_postcode_characters_to_group_by = 2
max_postcode_characters_to_group_by = 5

for postcode_characters_to_group_by in range(min_postcode_characters_to_group_by,
                                             max_postcode_characters_to_group_by):

    grouped = {}

    for postcode, data in details_lookup.items():
        abbrev_postcode = postcode[:postcode_characters_to_group_by]
        if abbrev_postcode not in grouped:
            grouped[abbrev_postcode] = []
        grouped[abbrev_postcode].append({postcode: data})

    Path("/grouped").mkdir(parents=True, exist_ok=True)

    for abbrev_postcode, group in tqdm(grouped.items(), ):
        dir_file = f"grouped/{postcode_characters_to_group_by}chars"
        Path(dir_file).mkdir(parents=True, exist_ok=True)
        with open(f'{dir_file}/{abbrev_postcode}.json', 'w+') as f:
            f.write(json.dumps(group))

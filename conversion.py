import csv
import json
import os
from pathlib import Path

from tqdm import tqdm

postcode_lookup = {}
details_lookup = {}

# unzip https://www.arcgis.com/sharing/rest/content/items/c479d770cba14845a0e43db4e3eb5afa/data and place in data folder

# https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/853811/IoD2019_FAQ_v4.pdf p12

with open('data/PCD_OA_LSOA_MSOA_LAD_FEB19_UK_LU.csv', 'r') as f:
    data = csv.reader(f)
    headers = next(data)

    # https://en.wikipedia.org/wiki/Lower_Layer_Super_Output_Area 1000-1500 people
    row_i = headers.index('lsoa11cd')

    for row in tqdm(data, total=2624585):
        postcode_lookup_field = row[row_i]
        #postcode = row[0].replace(' ', '')
        if postcode_lookup_field in postcode_lookup:
            raise Exception('duplicate postcode_lookup_field: ' + postcode_lookup_field)
        postcode_lookup[postcode_lookup_field] = row

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
        postcode_lookup_field = postcode_info[postcode_i].replace(' ', '')

        index_of_deprivation = row[index_of_deprivation_i]
        index_of_deprivation = index_of_deprivation[3:]  # first 3 characters are a. b. c. etc and so not useful
        measurement = row[measurement_i]
        value = row[value_i]

        if postcode_lookup_field not in details_lookup:
            details_lookup[postcode_lookup_field] = {'postcode_info': postcode_info, }

        if indices_to_include_use:
            if index_of_deprivation not in indices_to_include:
                continue

        if index_of_deprivation not in details_lookup[postcode_lookup_field]:
            details_lookup[postcode_lookup_field][index_of_deprivation] = {}

        if index_of_deprivation not in details_lookup[postcode_lookup_field][index_of_deprivation]:
            details_lookup[postcode_lookup_field][index_of_deprivation][index_of_deprivation] = {}

        details_lookup[postcode_lookup_field][index_of_deprivation][index_of_deprivation][measurement] = value

# let's group similar postcodes
min_postcode_characters_to_group_by = 2
max_postcode_characters_to_group_by = 5

for postcode_characters_to_group_by in range(min_postcode_characters_to_group_by,
                                             max_postcode_characters_to_group_by):

    grouped = {}

    for postcode_lookup_field, data in details_lookup.items():
        abbrev_postcode = postcode_lookup_field[:postcode_characters_to_group_by]
        if abbrev_postcode not in grouped:
            grouped[abbrev_postcode] = []
        grouped[abbrev_postcode].append({postcode_lookup_field: data})

    Path("/grouped").mkdir(parents=True, exist_ok=True)

    for abbrev_postcode, group in tqdm(grouped.items(), ):
        dir_file = f"grouped/{postcode_characters_to_group_by}chars"
        Path(dir_file).mkdir(parents=True, exist_ok=True)
        with open(f'{dir_file}/{abbrev_postcode}.json', 'w+') as f:
            f.write(json.dumps(group))

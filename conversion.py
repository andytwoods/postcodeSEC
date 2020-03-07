import csv
from tqdm import tqdm

postcode_lookup = {}
details_lookup = {}

# unzip https://opendatacommunities.org/imd-files/imd2019lsoa.csv?uri=http%3A%2F%2Fopendatacommunities.org%2Fdata%2Fsocietal-wellbeing%2Fimd2019%2Findices and place in data folder

with open('data/PCD_OA_LSOA_MSOA_LAD_FEB19_UK_LU.csv', 'r')as f:
    data = csv.reader(f)
    headers = next(data)
    row_i = headers.index('lsoa11cd')

    for row in tqdm(data, total=2624585):
        header = row[row_i]
        postcode_lookup[header] = row

with open('data/imd2019lsoa.csv', 'r')as f:
    data = csv.reader(f)
    headers = next(data)
    row_i = headers.index('FeatureCode')
    index_of_deprivation_i = headers.index('Indices of Deprivation')
    measurement_i = headers.index('Measurement')
    value_i = headers.index('Value')

    for row in tqdm(data, total=985320):

        header = row[row_i]
        postcode_info = postcode_lookup[header]
        index_of_deprivation = row[index_of_deprivation_i]
        index_of_deprivation = index_of_deprivation[3:] # first 3 characters are a. b. c. etc and so not useful
        measurement = row[measurement_i]
        value = row[value_i]

        if header not in details_lookup:
            details_lookup[header] = {}

        if index_of_deprivation not in details_lookup[header]:
            details_lookup[header][index_of_deprivation] = {}

        if index_of_deprivation not in details_lookup[header][index_of_deprivation]:
            details_lookup[header][index_of_deprivation][index_of_deprivation] = {}

        details_lookup[header][index_of_deprivation][index_of_deprivation][measurement] = value

print(details_lookup)
# This is an edit.


import bs4 as bs
import urllib.request
from datetime import datetime
import numpy as np
import pandas as pd
import sys
import matplotlib.pyplot as plt
import lxml

#the year you want to look at
b=2014

# location of desired information in the series of tubes for the alley
source = urllib.request.urlopen(
    'https://nwis.waterservices.usgs.gov/nwis/iv/?format=waterml,2.0&sites=03070260&startDT'
    '={x}-01-01T00:00-0500&endDT={x}-12-31T23:59-0500&parameterCd=00060&siteType=ST&siteStatus=all'.format(x=b)
).read()
soup = bs.BeautifulSoup(source, 'xml')

# the lists that will hold all of the values
cfs = []
runnablecfs = []


# gathering the cfs values
def acquire_data():
    cfs = []
    timestamp = []
    for wml2 in soup.find_all('wml2:value'):
      cfs.append(float(wml2.string))
    for wml2 in soup.find_all('wml2:time'):
      timestamp.append(wml2.string)

    return cfs, timestamp


def clean_data(in_data):
    df = pd.DataFrame.from_dict(in_data, orient='index')
    df = df.reset_index()
    df = df.rename(columns={'index': 'Date', 0: 'CFS'})
    df['ReDoneDates'] = pd.DatetimeIndex(df['Date']).to_period('D')
    df['Month'] = pd.DatetimeIndex(df['Date']).month
    df['Month'] = df['Month'].astype('int32')
    df['Day'] = pd.DatetimeIndex(df['Date']).day
    df['Day'] = df['Day'].astype('int32')

    return df


'''for x in cfs:
    if 700 < x < 2000:
        runnablecfs.append(x)'''

# print(len(cfs))
# print(len(runnablecfs))

cfs_join, timestamp_join = acquire_data()

i = 0
while i < len(timestamp_join):
    date_str = timestamp_join[i][:19]
    timestamp_join[i] = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
    i += 1
del i

#I want to turn this into a function
out_df = clean_data(dict(zip(timestamp_join, cfs_join)))


new_df = out_df.loc[(out_df['CFS'] < 2000) & (out_df['CFS'] > 700)].drop_duplicates(subset=['ReDoneDates'], keep='first')

# newer_df = new_df.drop_duplicates(subset=['ReDoneDates'], keep='first')

groupdf = new_df.groupby(pd.Grouper(key='Date', freq='M')).count()
groupdf.drop(['ReDoneDates', 'Month', 'Day'], axis=1, inplace=True)
groupdf.plot()
plt.legend(['{x}'.format(x=b)])
plt.xticks()
plt.ylabel('# of Days the CFS range was between 700 and 2000')
plt.xlabel('Month')
plt.show()

print(len(new_df))
#new_df.to_excel("AlleyDaze{x}.xlsx".format(x=b),
#           sheet_name='Sheet_name_1')

sys.exit()

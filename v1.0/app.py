#24feb2023
#temperature trend projection using linear regression prediction
#celsius of a location of current date for past 10 years to estimate mean of current year
#application can be served on python playground environment such as huggingface.
#example uses data from: https://data.gov.hk/en-data/dataset/hk-hko-rss-daily-temperature-info-hko

import streamlit as st
import pandas as pd
import numpy as np

astations = [
	["hongkongobservatory","HKO",22.3022566,114.1722662,"Hong Kong Observatory"],
	["kingspark","KP",22.3115408,114.1685675,"Observatory Meteorological Station, King's Park"],
]
astationcolumns = ['akey','astationcode','alatitude','alongitude','atitle',]

acontainer1 = st.empty()
acontainer2 = st.empty()
acontainer3 = st.empty()
acontainer4 = st.empty()

def asubmit(aparam):
	import datetime
	from io import StringIO
	import os,time

	adf2 = aparam["adataframe"]
	aselecteditem = adf2.loc[adf2["atitle"]==aparam["aselected"], "astationcode"]
	aselectedrow = adf2[adf2["atitle"]==aparam["aselected"]]
	aselectedindex = adf2.index[adf2["atitle"]==aparam["aselected"]].tolist()

	adf3 = pd.DataFrame(
		[
			[
				aselectedrow["alatitude"][aselectedindex[0]],
				aselectedrow["alongitude"][aselectedindex[0]],
			]
		],
		columns=['lat', 'lon']
	)
	aparam["acontainer"].map(adf3)

	abacklogmax = 10

	atoday = datetime.date.today()
	ayear = int(atoday.strftime("%Y"))-0
	amonth = int(atoday.strftime("%m"))
	amonthday = int(atoday.strftime("%d"))

	if ("0" != ""):
		atimezone = os.environ['TZ']
		os.environ['TZ'] = 'Asia/Hong_Kong'
		time.tzset()
		anow = time.localtime()
		ayear = int(time.strftime("%Y",anow))-0
		amonth = int(time.strftime("%m",anow))
		amonthday = int(time.strftime("%d",anow))
		a24hour = int(time.strftime("%H",anow))
		aminute = int(time.strftime("%M",anow))
		asecond = int(time.strftime("%S",anow))
		acontainer4.write(("{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}").format(ayear,amonth,amonthday,a24hour,aminute,asecond))
		os.environ['TZ'] = atimezone
		time.tzset()

	atitles = aparam["acolumntitles"]

	csvString = ""
	csvString += (",").join(atitles)
	adf3 = pd.DataFrame(columns=atitles)
	for i in range((ayear-abacklogmax),ayear,1):
		alink = ("https://data.weather.gov.hk/weatherAPI/opendata/opendata.php?dataType=CLMTEMP&year={}&rformat=csv&station={}").format(str(i),aselecteditem.values[0])
		adf4 = pd.read_csv(alink, skiprows=[0,1,2], skipfooter=3, engine='python', on_bad_lines='skip')

		adf4 = adf4.reset_index()  # make sure indexes pair with number of rows
		for index, row in adf4.iterrows():
			if (row[2]!=amonth) or (row[3]!=amonthday):
				continue

			adate = ("{}{:02d}{:02d}").format(row[1], row[2], row[3])
			csvString += '\n'+(",").join([adate,str(row[4])])
			st.write(row[0],adate)
			adf3 = adf3.append({"Date":adate,"Celsius":(row[4]),}, ignore_index=True)
			break
	adf3 = pd.read_csv(StringIO(csvString), sep=",")
	aparam["acontainer"].dataframe(adf3)

	from sklearn.linear_model import LinearRegression
	lr = LinearRegression()
	lr.fit(adf3[['Date']].astype('float').astype('int32'), adf3['Celsius'])

	atrendproject = [int(("{}{:02d}{:02d}").format(ayear,amonth,amonthday))]
	st.dataframe(pd.merge(pd.DataFrame([atrendproject]), pd.DataFrame(lr.predict(np.array([atrendproject]))), left_index=True, right_index=True))

adf = pd.DataFrame(
	astations,
	columns=astationcolumns
)
aoption = acontainer1.selectbox(
	'Which station?',
	adf['atitle']
)
if acontainer2.button("Submit") == True:
	asubmit(aparam={"aselected":aoption,"acontainer":acontainer3,"adataframe":adf,"acolumntitles":['Date','Celsius'],})

import re, requests, zipfile, pandas as pd, io
headers = {'User-Agent': 'Mozilla/5.0'}
print("Fetching GDELT master list...")
r = requests.get('http://data.gdeltproject.org/gdeltv2/masterfilelist.txt', timeout=60)
matches = re.findall(r'(https?://\S+\.export\.CSV\.zip)', r.text)
daily_urls = []
seen_dates = set()
for m in matches[::-1]:
    date_str = m.split('/')[-1][:8]
    if date_str not in seen_dates:
        seen_dates.add(date_str)
        daily_urls.append(m)
    if len(daily_urls) == 7:
        break
daily_urls.reverse()
col_names = ['GlobalEventID','SQLDATE','MonthYear','Year','FractionDate','Actor1Code','Actor1Name','Actor1CountryCode','Actor1KnownGroupCode','Actor1EthnicCode','Actor1Religion1Code','Actor1Religion2Code','Actor1Type1Code','Actor1Type2Code','Actor1Type3Code','Actor2Code','Actor2Name','Actor2CountryCode','Actor2KnownGroupCode','Actor2EthnicCode','Actor2Religion1Code','Actor2Religion2Code','Actor2Type1Code','Actor2Type2Code','Actor2Type3Code','IsRootEvent','EventCode','EventBaseCode','EventRootCode','QuadClass','GoldsteinScale','NumMentions','NumSources','NumArticles','AvgTone','Actor1Geo_Type','Actor1Geo_FullName','Actor1Geo_CountryCode','Actor1Geo_ADM1Code','Actor1Geo_ADM2Code','Actor1Geo_Lat','Actor1Geo_Long','Actor1Geo_FeatureID','Actor2Geo_Type','Actor2Geo_FullName','Actor2Geo_CountryCode','Actor2Geo_ADM1Code','Actor2Geo_ADM2Code','Actor2Geo_Lat','Actor2Geo_Long','Actor2Geo_FeatureID','ActionGeo_Type','ActionGeo_FullName','ActionGeo_CountryCode','ActionGeo_ADM1Code','ActionGeo_ADM2Code','ActionGeo_Lat','ActionGeo_Long','ActionGeo_FeatureID','DATEADDED','SOURCEURL']
all_events = []
for url in daily_urls:
    print(f"Fetching {url.split('/')[-1]}...")
    r2 = requests.get(url, timeout=120)
    with zipfile.ZipFile(io.BytesIO(r2.content)) as z:
        for name in z.namelist():
            if name.endswith('.export.CSV'):
                with z.open(name) as f:
                    df = pd.read_csv(f, sep='\t', header=None, names=col_names, dtype=str, low_memory=False)
                    mask = (df['ActionGeo_CountryCode'] == 'IR') | (df['Actor1CountryCode'] == 'IR') | (df['Actor2CountryCode'] == 'IR')
                    all_events.append(df[mask])
final_df = pd.concat(all_events, ignore_index=True)
final_df.to_csv('/home/hmid/ssan-data/gdelt_iran_7days.csv', index=False, header=True, sep='\t')
print(f"Extracted {len(final_df)} real events over 7 days.")

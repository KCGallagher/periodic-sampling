# JHU CSSE COVID-19 Dataset

*(README copied from [CSSE Repo](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data))*

## Table of contents

* [Daily reports (csse_covid_19_daily_reports)](#daily-reports-csse_covid_19_daily_reports)
* [Irregular Update Schedules](#irregular-update-schedules)
* [UID Lookup Table Logic](#uid-lookup-table-logic)

---

## [Daily reports (csse_covid_19_daily_reports)](https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data/csse_covid_19_daily_reports)

This folder contains daily case reports. All timestamps are in UTC (GMT+0).

### File naming convention

MM-DD-YYYY.csv in UTC.

### Field description

* **FIPS**: US only. Federal Information Processing Standards code that uniquely identifies counties within the USA.
* **Admin2**: County name. US only.
* **Province_State**: Province, state or dependency name.
* **Country_Region**: Country, region or sovereignty name. The names of locations included on the Website correspond with the official designations used by the U.S. Department of State.
* **Last_Update**</b>: MM/DD/YYYY HH:mm:ss  (24 hour format, in UTC).
* **Lat and Long**: Dot locations on the dashboard. All points (except for Australia) shown on the map are based on geographic centroids, and are not representative of a specific address, building or any location at a spatial scale finer than a province/state. Australian dots are located at the centroid of the largest city in each state.
* **Confirmed**: Counts include confirmed and probable (where reported).
* **Deaths**: Counts include confirmed and probable (where reported).
* **Recovered**: Recovered cases are estimates based on local media reports, and state and local reporting when available, and therefore may be substantially lower than the true number. US state-level recovered cases are from [COVID Tracking Project](https://covidtracking.com/). We stopped to maintain the recovered cases (see [Issue #3464](https://github.com/CSSEGISandData/COVID-19/issues/3464) and [Issue #4465](https://github.com/CSSEGISandData/COVID-19/issues/4465)).
* **Active**: Active cases = total cases - total recovered - total deaths. This value is for reference only after we stopped to report the recovered cases (see [Issue #4465](https://github.com/CSSEGISandData/COVID-19/issues/4465))
* **Incident_Rate**: Incidence Rate = cases per 100,000 persons.
* **Case_Fatality_Ratio**</b>: Case-Fatality Ratio (%) = Number recorded deaths / Number cases.
* All cases, deaths, and recoveries reported are based on the date of initial report. Exceptions to this are noted in the "Data Modification" and "Retrospective reporting of (probable) cases and deaths" subsections below.  

### Update frequency

* Since June 15, We are moving the update time forward to occur between 04:45 and 05:15 GMT to accommodate daily updates from India's Ministry of Health and Family Welfare.
* Files on and after April 23, once per day between 03:30 and 04:00 UTC.
* Files from February 2 to April 22: once per day around 23:59 UTC.
* Files on and before February 1: the last updated files before 23:59 UTC. Sources: [archived_data](https://github.com/CSSEGISandData/COVID-19/tree/master/archived_data) and dashboard.

### Data sources

Refer to the [mainpage](https://github.com/CSSEGISandData/COVID-19).

## Irregular Update Schedules

As the pandemic has progressed, several locations have altered their reporting schedules to no longer provide daily updates. As these locations are identified, we will list them in this section of the README. We anticipate that these irregular updates will cause cyclical spikes in the data and smoothing algorithms should be applied if the data is to be used for modeling.

For all international locations, compositing with the reporting of the World Health Organization we may update more frequently than the national sources.

* Belgium: Providing data Tuesdays and Fridays.
* Bosnia and Herezegovina: Not updating data on the weekends.
* Alberta, Canada: Providing data Monday-Friday.
* British Columba, Canada: Providing data Monday-Friday.
* Manitoba, Canada: Providing data Monday-Friday.
* New Brunswick, Canada: Providing data Monday-Friday.
* Newfoundland and Labrador, Canada: Providing data Monday, Wednesday, and Friday.
* Northwest Territories, Canada: Providing data Monday-Friday.
* Saskatechewan, Canada: Providing data weekly (Thursdays).
* Yukon, Canada: Providing data Monday-Friday.
* Colombia: Weekly on Thursdays
* Costa Rica: Updating data on Wednesdays and Saturdays only.
* Denmark: Not updating case, death, or recovered data on the weekends.
* France: No longer releasing case, hospitalization, or death data on the weekends. Please see [Tableau dashboard](https://dashboard.covid19.data.gouv.fr/vue-d-ensemble?location=FRA). No update to deaths or recoveries for the weekend of August 8 and 9.
* Germany: Providing data Monday-Friday.
* Honduras: Providing data Monday-Friday.
* Ireland: Providing death data once weekly.
* Luxembourg: Not providing actionable data on weekends.
* Mexico: Providing data once weekly. Beginning November 10, recoveries are available at the national level only and will be grouped in the "Unassigned, Mexico" entry.
* Nicaragua: Providing data once weekly.
* Romania: Providing data once per week (Tuesdays).
* Spain: Providing data twice a week (Tuesdays and Fridays) (as of March 15, 2022).
* Sweden: Updating once per week (Thursdays) (as of March 24, 2022).
* Switzerland: Providing data once per week (Tuesdays).
* Turkey: Updating weekly.
* UK: Providing data Monday-Friday (as of Feb 26, 2022). Scotland, Wales, and Northern Ireland collect and report data to the central data authority where we access data.
* Northern Ireland, UK: No longer providing data as of May 20, 2022.
* Scotland, UK: Providing data once weekly (Wednesdays) as of June 8, 2022. UK deaths no longer include deaths within Scotland.
* Wales, UK: Providing data once weekly (Thursdays) as of May 26, 2022.

## Upcoming Irregular Update Schedules

United Kingdom (England, Scotland, Wales, Northern Ireland): Providing data once weekly (Wednesdays) as of July 1, 2022.

---

## [UID Lookup Table Logic](https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv)

1. All countries without dependencies (entries with only Admin0).
    * None cruise ship Admin0: UID = code3. (e.g., Afghanistan, UID = code3 = 4)
    * Cruise ships in Admin0: Diamond Princess UID = 9999, MS Zaandam UID = 8888.
\\
2. All countries with only state-level dependencies (entries with Admin0 and Admin1).
    * Demark, France, Netherlands: mother countries and their dependencies have different code3, therefore UID = code 3. (e.g., Faroe Islands, Denmark, UID = code3 = 234; Denmark UID = 208)
    * United Kingdom: the mother country and dependencies have different code3s, therefore UID = code 3. One exception: Channel Islands is using the same code3 as the mother country (826), and its artificial UID = 8261.
    * Australia: alphabetically ordered all states, and their UIDs are from 3601 to 3608. Australia itself is 36.
    * Canada: alphabetically ordered all provinces (including cruise ships and recovered entry), and their UIDs are from 12401 to 12415. Canada itself is 124.
    * China: alphabetically ordered all provinces, and their UIDs are from 15601 to 15631. China itself is 156. Hong Kong, Macau and Taiwan have their own code3.
    * Germany: alphabetically ordered all admin1 regions (including Unknown), and their UIDs are from 27601 to 27617. Germany itself is 276.
    * Italy: UIDs are combined country code (380) with `codice_regione`, which is from [Dati COVID-19 Italia](https://github.com/pcm-dpc/COVID-19). Exceptions: P.A. Bolzano is 38041 and P.A. Trento is 38042.
\\
3. The US (most entries with Admin0, Admin1 and Admin2).
    * US by itself is 840 (UID = code3).
    * US dependencies, American Samoa, Guam, Northern Mariana Islands, Virgin Islands and Puerto Rico, UID = code3. Their Admin0 FIPS codes are different from code3.
    * US states: UID = 840 (country code3) + 000XX (state FIPS code). Ranging from 8400001 to 84000056.
    * Out of [State], US: UID = 840 (country code3) + 800XX (state FIPS code). Ranging from 8408001 to 84080056.
    * Unassigned, US: UID = 840 (country code3) + 900XX (state FIPS code). Ranging from 8409001 to 84090056.
    * US counties: UID = 840 (country code3) + XXXXX (5-digit FIPS code).
    * Exception type 1, such as recovered and Kansas City, ranging from 8407001 to 8407999.
    * Exception type 2, Bristol Bay plus Lake Peninsula replaces Bristol Bay and its FIPS code. Population is 836 (Bristol Bay) + 1,592 (Lake and Peninsula) = 2,428 (Bristol Bay plus Lake Peninsula). 2148 (Hoonah-Angoon) + 579 (Yakutat) = 2727 (Yakutat plus Hoonah-Angoon). UID is 84002282, the same as Yakutat.
    * Exception type 3, Diamond Princess, US: 84088888; Grand Princess, US: 84099999.
    * Exception type 4, municipalities in Puerto Rico are regarded as counties with FIPS codes. The FIPS code for the unassigned category is defined as 72999.
\\
4. Population data sources.
    * [United Nations](https://population.un.org/wpp/Download/Standard/Population/), Department of Economic and Social Affairs, Population Division (2019). World Population Prospects 2019, Online Edition. Rev. 1.
    * [eurostat](https://ec.europa.eu/eurostat/web/products-datasets/product?code=tgs00096)
    * [The U.S. Census Bureau](https://www.census.gov/data/datasets/time-series/demo/popest/2010s-counties-total.html)
    * [Mexico population 2020 projection](http://sniiv.conavi.gob.mx/(X(1)S(kqitzysod5qf1g00jwueeklj))/demanda/poblacion_proyecciones.aspx?AspxAutoDetectCookieSupport=1): Proyecciones de población
    * [Brazil 2019 projection](ftp://ftp.ibge.gov.br/Estimativas_de_Populacao/Estimativas_2019/)
    * [Peru 2020 projection](https://www.citypopulation.de/en/peru/cities/)
    * [India 2019 population](http://statisticstimes.com/demographics/population-of-indian-states.)
    * [Belgium](https://statbel.fgov.be/en/themes/population/structure-population) (Population on 1st January 2020)
    * [Canada](https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1710000901) (Q3 2021)
    * [China](http://www.stats.gov.cn/english/PressRelease/202105/t20210510_1817188.html) (mainland - May 11, 2021)
    * [Denmark](https://www.dst.dk/en/Statistik/emner/borgere/befolkning) (mainland - 2021Q3)
    * [France](https://www.ined.fr/en/everything_about_population/data/france/population-structure/regions_departments/) (European - January 1st 2021)
    * [Germany](https://www.destatis.de/EN/Themes/Society-Environment/Population/Current-Population/Tables/population-by-laender.html) (as of 31.12.2020)
    * The Admin0 level population could be different from the sum of Admin1 level population since they may be from different sources.

Disclaimer: \*The names of locations included on the Website correspond with the official designations used by the U.S. Department of State. The presentation of material therein does not imply the expression of any opinion whatsoever on the part of JHU concerning the legal status of any country, area or territory or of its authorities. The depiction and use of boundaries, geographic names and related data shown on maps and included in lists, tables, documents, and databases on this website are not warranted to be error free nor do they necessarily imply official endorsement or acceptance by JHU.

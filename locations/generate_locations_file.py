import pandas
import os

pd = pandas.read_excel("D:\\workspace\\scraper\\locations\\UNSD_M49.xlsx",engine="openpyxl")
regions = pd.loc[:,['Sub_region_Name','Intermediate_Region_Name','Country_or_Area']]


def clean_country_names(names):
    for i,name in enumerate(names):
        new_name = name.replace(',','')
        new_name = new_name.replace('ç','c')
        new_name = new_name.replace('é','e')
        new_name = new_name.replace('ô','o')
        if '(' in name :
            new_name = new_name.split('(')[0][:-1]+new_name.split(')')[-1]
        names[i]=new_name
    return names


nulls = regions["Intermediate_Region_Name"].isnull()
tmp_region_name = ""
regions_dic={}
for i,elem in enumerate(regions['Intermediate_Region_Name']):
    #Get sub region or intermediate region name
    if nulls[i]:
        tmp_elem=regions['Sub_region_Name'][i]
    else :
        tmp_elem=elem

    if type(tmp_elem) is not str :
        #trick to eliminate the antarticta that does not have any sub region but is not interesting anyway
        continue

    if tmp_elem == tmp_region_name:
        # We're inside the same region than precedently, just add the country to the list
        regions_dic[tmp_elem].append(regions['Country_or_Area'][i])
    else :
        #first time on a new sub region, create list
        regions_dic[tmp_elem]=[regions['Country_or_Area'][i]]
    tmp_region_name = tmp_elem


locations_dir = "D:\\workspace\\THESIS\\GDS\\scraper_production\\locations\\M49\\"
for region in regions_dic :
    filename = "M49_{}.txt".format(region).replace(' ','_')
    print(filename)
    with open(os.path.join(locations_dir,filename),'w', encoding = 'utf-8') as file :
        file.write('locations\n')
        file.write(region+'\n')
        file.writelines('\n'.join(clean_country_names(regions_dic[region])))

from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import requests
import csv
import os

states = []
state_html = requests.get("https://www.sale-tax.com/").content
state_soup = BeautifulSoup(state_html, 'html.parser')
state_rows = state_soup.table.find_all('tr')

for row in state_rows:
    if row.attrs.get('data-href'):
        states.append(row.attrs.get('data-href'))


geolocator = Nominatim(user_agent="app")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=0.75)

# Creates a 'states' folder in the current directory to store the CSV files if it doesn't exist.

if not os.path.exists('states'):
    os.mkdir('states')

# Where all of the state/city information starts being added into separate CSV files.

for state in states:
    output_rows = []
    state_name = state[1:]
    url = "https://www.sale-tax.com" + state + "_"
    state_name = ''.join([' ' + s if s.isupper()  else s for s in state_name]).lstrip()
    print(state_name)
    for i in range(65, 91):
        state_url = url + chr(i)
        html = requests.get(state_url).content
        soup = BeautifulSoup(html, 'html.parser')
        if soup.table is not None:
            rows = soup.table.find_all('tr')

            for row in rows:
                city = row.find('strong')
                tax = row.find(class_='center')
                
                if tax and city:
                    tax = tax.a.string
                    city_row = []
                    location = geocode({'city': city.string, 'state': state_name, 'country': "United States"}, exactly_one=False)
                    
                    if location is not None:
                        loc = location[0]
                        loc_found = True
                        if loc.raw['display_name'].find(f", {state_name}") == -1:
                            loc_found = False
                            for l in location:
                                if l.raw['display_name'].find(f", {state_name}") > -1:
                                    loc_found = True
                                    loc = l
                                    break
                            

                        if loc_found:
                            city_row.append(city.string)
                            city_row.append(state_name)
                            city_row.append(tax[:-1])
                            city_row.append(loc.latitude)
                            city_row.append(loc.longitude)
                            print(loc)
                    if len(city_row) > 0:
                        output_rows.append(city_row)


    with open(f"states/{state_name}.csv", 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows([["City", "State", "Tax Rate", "Latitude", "Longitude"]])
        writer.writerows(output_rows)



        


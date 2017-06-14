from django.shortcuts import render
import urllib.request
from bs4 import BeautifulSoup
import csv
import requests
import geocoder #added by charlie
import json #added by charlie


# Create your views here.

def home(request):
    return render(request,"home.html")

def airasia_scrape(my_dict):
    my_dict['my_price'] = 99999
    my_dict['my_price_return'] = 99999
    if my_dict['departure_city'] == 'BKK':
        my_dict['departure_city'] = 'DMK'
    if my_dict['arrival_city'] == 'BKK':
        my_dict['arrival_city'] = 'DMK'
    departure_city = my_dict['departure_city']
    arrival_city = my_dict['arrival_city']
    departure_date = my_dict['departure_date'][6:10]+'-'+my_dict['departure_date'][0:2]+'-'+my_dict['departure_date'][3:5]
    if my_dict['return_date']:
        return_date = my_dict['return_date'][6:10]+'-'+my_dict['return_date'][0:2]+'-'+my_dict['return_date'][3:5]
    results_link = 'https://booking.airasia.com/Flight/Select?o1='+departure_city+'&d1='+arrival_city+'&culture=en-US&dd1='+departure_date+'&ADT=1&CHD=0&inl=0&s=true&mon=true&cc=USD&c=false'
    results_soup = BeautifulSoup(urllib.request.urlopen(results_link),'lxml')

    my_result = results_soup.find_all('tr',class_='fare-light-row')+results_soup.find_all('tr',class_='fare-dark-row')
    lowest_price = float(99999)
# For first leg
    for this_result in my_result:
        try:
            my_price = this_result.find_all('div',class_='avail-fare-price')[0].get_text().strip()
            this_price = float(my_price[1:-4])
        except:
            continue
        if this_price < lowest_price:
            lowest_price = this_price
            try:
                departure_time = this_result.find_all('div',class_='avail-table-bold')[0].get_text().strip()
                arrival_time = this_result.find_all('div',class_='avail-table-bold')[1].get_text()
            except:
                continue
    my_dict['my_price'] = "{0:.2f}".format(lowest_price)
    my_dict['departure_time'] = departure_time
    my_dict['arrival_time'] = arrival_time
# For returning leg
    if return_date:
        results_link = 'https://booking.airasia.com/Flight/Select?o1='+arrival_city+'&d1='+departure_city+'&culture=en-US&dd1='+return_date+'&ADT=1&CHD=0&inl=0&s=true&mon=true&cc=USD&c=false'
        results_soup = BeautifulSoup(urllib.request.urlopen(results_link),'lxml')
        my_result = results_soup.find_all('tr',class_='fare-light-row')+results_soup.find_all('tr',class_='fare-dark-row')
        lowest_price = float(99999)
        for this_result in my_result:
            try:
                my_price = this_result.find_all('div',class_='avail-fare-price')[0].get_text().strip()
                this_price = float(my_price[1:-4])
            except:
                continue
            if this_price < lowest_price:
                lowest_price = this_price
                try:
                    departure_time = this_result.find_all('div',class_='avail-table-bold')[0].get_text().strip()
                    arrival_time = this_result.find_all('div',class_='avail-table-bold')[1].get_text()
                except:
                    continue
        my_dict['my_price_return'] = "{0:.2f}".format(lowest_price)
        my_dict['departure_time_return'] = departure_time
        my_dict['arrival_time_return'] = arrival_time
    return(my_dict)

def jetstar_scrape(my_dict):
    my_dict['my_jetstar_price_return'] = 99999
    my_dict['my_jetstar_price'] = 99999
    departure_city = my_dict['departure_city']
    arrival_city = my_dict['arrival_city']
    departure_year = my_dict['departure_date'][6:10]
    departure_month = my_dict['departure_date'][0:2]
    departure_day = my_dict['departure_date'][3:5]
    if float(departure_month) < 10:
        departure_month = departure_month[1:2]
    if float(departure_day) < 10:
        departure_day = departure_day[1:2]
    if my_dict['return_date']:
        return_date = my_dict['return_date'][6:10]+'-'+my_dict['return_date'][0:2]+'-'+my_dict['return_date'][3:5]
# For first leg
    results_link = 'http://booknow.jetstar.com/LowFareFinder.aspx?culture=en-AU&RadioButtonMarketStructure=OneWay&Origin1='+departure_city+'&Destination1='+arrival_city+'&Day1='+departure_day+'&MonthYear1='+departure_year+'-'+departure_month+'&ADT=1&CHD=0&INF=0&AutoSubmit=Y&ControlGroupCalendarSearchView%24AvailabilitySearchInputCalendarSearchView%24DropDownListCurrency=USD'
    results_soup = requests.get(results_link)
    results_soup = results_soup.text
    my_string = "\""+departure_day+"/"+departure_month+"/"+departure_year+"\" data-price=\""
    my_test_string = departure_day+'/'+departure_month+'/'+departure_year
    my_location = results_soup.find(my_string)
    this_block = results_soup[my_location+18:]
    the_price = "\""
    my_location1 = this_block.find(the_price)
    this_block = this_block[1:]
    my_location2 = this_block.find(the_price)
    my_price = this_block[my_location1:my_location1+my_location2+2]
    if my_price[-1] == '\"':
        my_price = my_price[:-1]
    if len(my_price) < 10:
        my_dict['my_jetstar_price'] = my_price
    my_dict['jetstar_results_soup'] = [results_link, my_string, my_test_string, my_location, my_location1, my_location2, this_block, results_soup]
# For returning leg
    if return_date:
        departure_year = my_dict['return_date'][6:10]
        departure_month = my_dict['return_date'][0:2]
        departure_day = my_dict['return_date'][3:5]
        if float(departure_month) < 10:
            departure_month = departure_month[1:2]
        if float(departure_day) < 10:
            departure_day = departure_day[1:2]
        results_link = 'http://booknow.jetstar.com/LowFareFinder.aspx?culture=en-AU&RadioButtonMarketStructure=OneWay&Origin1='+departure_city+'&Destination1='+arrival_city+'&Day1='+departure_day+'&MonthYear1='+departure_year+'-'+departure_month+'&ADT=1&CHD=0&INF=0&AutoSubmit=Y&ControlGroupCalendarSearchView%24AvailabilitySearchInputCalendarSearchView%24DropDownListCurrency=USD'
        results_soup = requests.get(results_link)
        results_soup = results_soup.text
        my_string = "\""+departure_day+"/"+departure_month+"/"+departure_year+"\" data-price=\""
        my_location = results_soup.find(my_string)
        this_block = results_soup[my_location+18:]
        the_price = "\""
        my_location1 = this_block.find(the_price)
        this_block = this_block[1:]
        my_location2 = this_block.find(the_price)
        my_price = this_block[my_location1:my_location1+my_location2+2]
        if my_price[-1] == '\"':
            my_price = my_price[:-1]
        if len(my_price) < 10:
            my_dict['my_jetstar_price_return'] = my_price

    return(my_dict)

def search(request):
    my_dict = dict()
    departure_city = request.GET['departure']
    arrival_city = request.GET['arrival']
    departure_date = request.GET['dep_date']
    return_date = request.GET['ret_date']
    my_dict['departure_city'] = departure_city
    my_dict['arrival_city'] = arrival_city
    my_dict['departure_date'] = departure_date

    my_dict['coord'] = getCoords(departure_city, arrival_city) #added by charlie

    if return_date:
        my_dict['return_date'] = return_date
    airasia_scrape(my_dict)
    if my_dict['departure_city'] == 'DMK':
        my_dict['departure_city'] = 'BKK'
    if my_dict['arrival_city'] == 'DMK':
        my_dict['arrival_city'] = 'BKK'

    jetstar_scrape(my_dict)
    if departure_city == 'BKK' or departure_city == 'DMK':
        my_dict['departure_city_name'] = 'Bangkok'
    elif departure_city == 'DPS':
        my_dict['departure_city_name'] = 'Bali'
    elif departure_city == 'HKG':
        my_dict['departure_city_name'] = 'Hong Kong'
    elif departure_city == 'KUL':
        my_dict['departure_city_name'] = 'Kuala Lumpur'
    elif departure_city == 'SIN':
        my_dict['departure_city_name'] = 'Singapore'
    if arrival_city == 'BKK' or arrival_city == 'DMK':
        my_dict['arrival_city_name'] = 'Bangkok'
    if arrival_city == 'DPS':
        my_dict['arrival_city_name'] = 'Bali'
    if arrival_city == 'HKG':
        my_dict['arrival_city_name'] = 'Hong Kong'
    if arrival_city == 'KUL':
        my_dict['arrival_city_name'] = 'Kuala Lumpur'
    if arrival_city == 'SIN':
        my_dict['arrival_city_name'] = 'Singapore'

    my_dict['cheap_price1'] = 3
    my_dict['cheap_price2'] = 3
    my_price = my_dict['my_price']
    my_jetstar_price = my_dict['my_jetstar_price']
    my_price_return = my_dict['my_price_return']
    my_jetstar_price_return = my_dict['my_jetstar_price_return']
    if str(my_price) < str(my_jetstar_price):
        my_dict['cheap_price1'] = 1
    elif str(my_price) > str(my_jetstar_price):
        my_dict['cheap_price1'] = 2
    if str(my_price_return) < str(my_jetstar_price_return):
        my_dict['cheap_price2'] = 1
    elif str(my_price_return) > str(my_jetstar_price_return):
        my_dict['cheap_price2'] = 2



    return render(request,"flight_results.html", my_dict)



def getLatLng(city):#added by charlie
    g = geocoder.google(city + ' aiport')
    latlngCoord = g.latlng
    return latlngCoord


def getCoords(departure_city, arrival_city):#added by charlie
    departure_city = departure_city
    arrival_city = arrival_city

    departure_city_LatLng = getLatLng(departure_city)
    arrival_city_LatLng = getLatLng(arrival_city)

    latLng = {}

    latLng['departure_city_LatLng'] = departure_city_LatLng
    latLng['arrival_city_LatLng'] = arrival_city_LatLng

    coord = {}
    coord['coordinates'] = {}
    coord['coordinates']['origin_lat'] = departure_city_LatLng[0]
    coord['coordinates']['origin_lng'] = departure_city_LatLng[1]
    coord['coordinates']['dest_lat'] = arrival_city_LatLng[0]
    coord['coordinates']['dest_lng'] = arrival_city_LatLng[1]

    return coord




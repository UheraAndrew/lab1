from collections import defaultdict
from itertools import groupby
from math import isnan
import re
import folium
import requests
import os
import pandas as pd


def read_file(path):
    """
    (str) -> (list)
    Return list of lines from file (path to file)
    """
    lines_list = []
    f = open(path, encoding="utf-8", errors="ignore")
    for i in f.read().strip().split("\n"):
        lines_list.append(i)
    return lines_list


def read_locations(path):
    """
    (str) -> dict
    Return dict where place is a key and tuple
    with latitude and longitude is value
    """
    loc_dict = dict()
    f = open(path, encoding="utf-8", errors="ignore")
    f.readline()
    for line in f.readlines():
        place, lat, lng = line.strip("\n").split("\t")
        loc_dict[place] = [float(lat), float(lng)]
    return loc_dict


def film_dict(lines_list, year):
    """
    (list, int) -> (dict)
    Return dict from list of lines with country as key and name as value
    """
    f_dict = defaultdict(list)
    for line in lines_list:
        film_year = "".join(re.findall(r"\([0-9]{4}", line))[1:5]
        if film_year == str(year):
            name = line[:line.find(film_year) - 1].strip(" \"\'")
            goal = "".join(re.findall(r"\([\D]+?\)", line))
            part_name = "".join(re.findall(r"{.*}", line)).strip('{}\'\"')
            if len(part_name) > 1:
                name = name + ": " + part_name
            country = "".join(re.findall("\t[^\t(]+", line))[1:]
            feature_group = 0
            if goal == "(studio)":
                feature_group = 1
            elif goal == "(TV)":
                feature_group = 2
            elif goal == "(V)":
                feature_group = 3
            f_dict[country].append((name, feature_group))
    return f_dict


def get_location(address):
    try:
        url = 'https://maps.googleapis.com/maps/api/geocode/json'
        key = " AIzaSyBzd-NhaqTmZJBircbc11PyYKvGinR24Gg"
        params = {"sensor": "false", "address": address, "key": key}
        r = requests.get(url, params=params)
        location = r.json()["results"][0]["geometry"]["location"]
        lat_lng = [location["lat"], location["lng"]]
    except:
        return None
    return lat_lng


def write_country_count(country_dict):
    f = open("country_count.csv", "w")
    f.write("name,Count" + "\n")
    for country, count in country_dict.items():
        country = country.replace(",", "")
        if(isinstance(country,str) and isinstance(count, int)):
            f.write(country + ", " + str(count) + "\n")
    f.close()


def create_map(year):
    if(os.path.isfile("Map_" + str(year) + ".html")):
        print("Map is already made")
        return None
    essential_map = folium.Map()
    studio_group = folium.FeatureGroup(name="studio")
    tv_group = folium.FeatureGroup(name="tv")
    v_group = folium.FeatureGroup(name="v")
    others_group = folium.FeatureGroup(name="others")
    print("Finding films in file")
    f_dict = film_dict(read_file("locations.list"), year)
    print("Found films")

    country_counter_dict = defaultdict(int)

    loc_dict = dict()
    if "locations.tsv" in os.listdir():
        loc_dict = read_locations("locations.tsv")
    markers_count = len(f_dict)
    added_markers = 0
    for address, n_list in f_dict.items():

        country_counter_dict[address.split(", ")[-1]] += len(n_list)

        print("Map is ready for %.2f %%" %
              round(added_markers / markers_count * 100, 2))
        if address in loc_dict.keys():
            lat_lng = loc_dict[address]
        else:
            print("Need to geolocate")
            lat_lng = get_location(address)
        if isnan(lat_lng[0]) or isnan(lat_lng[1]):
            lat_lng = get_location(address)
        if lat_lng:
            try:
                for feature_group, names in groupby(n_list,
                                                    key=lambda x: x[1]):
                    marker_name = ""
                    for name, f_g in names:
                        marker_name = marker_name + name + '<br>'
                        marker_name = marker_name.replace("'", "\"",
                                                          len(marker_name))
                    names_count = marker_name.count("<br>")
                    if names_count < 3:
                        fill_color = "green"
                    elif names_count < 6:
                        fill_color = "yellow"
                    else:
                        fill_color = "red"
                    if feature_group == 1:
                        studio_group.add_child(folium.CircleMarker(
                            radius=3,
                            color=fill_color,
                            fill=True,
                            fill_color=fill_color,
                            fill_opacity=0.7,
                            location=lat_lng,
                            popup=marker_name))
                    elif feature_group == 2:
                        tv_group.add_child(folium.CircleMarker(
                            radius=3,
                            color=fill_color,
                            fill=True,
                            fill_color=fill_color,
                            fill_opacity=0.8,
                            location=lat_lng,
                            popup=marker_name))
                    elif feature_group == 3:
                        v_group.add_child(folium.CircleMarker(
                            radius=3,
                            color=fill_color,
                            fill=True,
                            fill_color=fill_color,
                            fill_opacity=0.9,
                            location=lat_lng,
                            popup=marker_name))
                    else:
                        others_group.add_child(folium.CircleMarker(
                            radius=3,
                            fill=True,
                            color=fill_color,
                            fill_color=fill_color,
                            fill_opacity=0.5,
                            location=lat_lng,
                            popup=marker_name))
            except ValueError:
                print(address, loc_dict[address])
            added_markers += 1

    print("Added markers to map")
    sum_all = sum(country_counter_dict.values())
    countries_group = os.path.join("", "world-countries.json")
    write_country_count(country_counter_dict)
    country_count = pd.read_csv("country_count.csv")
    essential_map.choropleth(
        geo_data=countries_group,
        name="Concentration",
        data=country_count,
        key_on="feature.properties.name",
        columns=("name", "Count"),
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.1,
        threshold_scale=[0.01*sum_all, 0.05*sum_all,
                         0.1*sum_all, 0.2*sum_all,
                         0.3*sum_all, 0.9*sum_all],
        legend_name="Concentration of films camering"
    )
    print("Added choropleth of concetration to map")
    essential_map.add_child(others_group)
    essential_map.add_child(studio_group)
    essential_map.add_child(tv_group)
    essential_map.add_child(v_group)
    essential_map.add_child(folium.LayerControl())
    essential_map.save("Map_" + str(year) + ".html")
    print("Map is done")

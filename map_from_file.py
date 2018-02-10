from collections import defaultdict
from itertools import groupby
import re
import folium
import requests


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


def create_map(year):
    essential_map = folium.Map()
    studio_group = folium.FeatureGroup(name="studio")
    tv_group = folium.FeatureGroup(name="tv")
    v_group = folium.FeatureGroup(name="v")
    others_group = folium.FeatureGroup(name="others")
    print("Finding films in file")
    f_dict = film_dict(read_file("locations.list"), year)
    print("Found films")

    for address, n_list in f_dict.items():
        print("Getting locations...")
        lat_lng = get_location(address)
        if lat_lng:
            for feature_group, names in groupby(n_list, key=lambda x: x[1]):
                marker_name = ""
                for name, f_g in names:
                    marker_name = marker_name + name + ';\n'
                marker_name = marker_name.replace("'", "\"", len(marker_name))
                if feature_group == 1:
                    studio_group.add_child(folium.Marker(
                        location=lat_lng,
                        popup=marker_name,
                        icon=folium.Icon(color='red')))
                elif feature_group == 2:
                    tv_group.add_child(folium.Marker(
                        location=lat_lng,
                        popup=marker_name,
                        icon=folium.Icon(color='purple')))
                elif feature_group == 3:
                    v_group.add_child(folium.Marker(
                        location=lat_lng,
                        popup=marker_name,
                        icon=folium.Icon(color='blue')))
                else:
                    others_group.add_child(folium.Marker(
                        location=lat_lng,
                        popup=marker_name,
                        icon=folium.Icon(color='green')))

    print("Add markers to map")
    essential_map.add_child(studio_group)
    essential_map.add_child(tv_group)
    essential_map.add_child(v_group)
    essential_map.add_child(others_group)
    essential_map.add_child(folium.LayerControl())
    essential_map.save("Map.html")

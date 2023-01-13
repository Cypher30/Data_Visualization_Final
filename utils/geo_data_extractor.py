import json
import os
from typing import List, Dict
from argparse import ArgumentParser


import pandas as pd
import numpy as np
from tqdm import tqdm


r"""
    This script is used to extract the data from original .csv file and convert it to GeoJSON format.
"""


class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


def generate_geo_data(df: pd.DataFrame, i: int, loc_attr: str) -> Dict:
    r"""
        Generate the GeoJSON format data from the original data.
        In the original data, the location is stored as a string in the form shown as below
        `POINT (100 200)`
        `POLYGON ((100 200, 100 300, 200 300, 200 200))`

        Args:
            df: the original data
            i: the index of the row
            loc_attr: the attribute of location

        Returns:
            geo_data: the GeoJSON format data
    """
    geo_data = {}
    geo_string: str = df.loc[i][loc_attr]

    # remove `(` and `)` in string
    geo_string = geo_string.replace("(", "").replace(")", "")

    # get geo type
    geo_type = geo_string.split(" ")[0].capitalize()
    geo_data.update({"type": geo_type})

    # get coordinates
    if geo_type == "Point":
        # point
        coordinates = geo_string.split(" ")[1:]
        coordinates = [float(c) for c in coordinates]
        geo_data.update({"coordinates": coordinates})
    else:
        # polygon
        coor_string = " ".join(geo_string.split(" ")[1:])
        coordinates = coor_string.split(", ")
        coordinates = [c.split(" ") for c in coordinates]

        # append the first coordianate to the end of coordinates
        coordinates.append(coordinates[0])

        geo_data.update({"coordinates": coordinates})

    return geo_data
        

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--input", type=str, default="../data/Attributes/Apartments.csv", 
                        help="input .csv file, default is ../data/Attributes/Apartments.csv")
    parser.add_argument("--output", type=str, default=None, 
                        help="output .json file, default is None (using the same name as input file)")
    args = parser.parse_args()

    if args.output is None:
        # using the same name as input file
        args.output = os.path.splitext(args.input)[0] + ".json"

    # Read the data
    df = pd.read_csv(args.input)
    df = df.fillna('null')

    # Extract the data and convert to GeoJSON format
    geo_data = {}
    geo_data.update({"type": "FeatureCollection"})
    geo_data.update({"features": []})

    # get attributes
    attributes = df.columns.tolist()

    # get location attribute
    loc_attr = next(filter(lambda x: x in ["location", "currentLocation"], attributes), None)

    # iterate over each row
    for i in tqdm(range(len(df))):
        feature = {}
        feature.update({"type": "Feature"})
        properties = {}
        for attr in attributes:
            if attr == loc_attr:
                pass
            else:
                properties.update({attr: df.loc[i][attr]})
        feature.update({"properties": properties})
        if loc_attr is not None:
            feature.update({"geometry": generate_geo_data(df, i, loc_attr)})

        geo_data["features"].append(feature)

    # save the data in json format
    with open(args.output, "w") as f:
        json.dump(geo_data, f, cls=NpEncoder, indent=4)
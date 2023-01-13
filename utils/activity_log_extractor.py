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
    parser.add_argument('--dirname', type=str, default='../data/Activity_Logs/', 
                        help='name of directory to read data from')
    parser.add_argument("--par_id", type=int, default=0, 
                        help="participant id")
    args = parser.parse_args()

    # Read the data
    df = pd.DataFrame()
    for i in tqdm(range(20)):
        # read data from csv file and concatenate to existing data
        df = pd.concat([df, pd.read_csv(os.path.join(args.dirname, f'ParticipantStatusLogs{i + 1}.csv'))], ignore_index=True)
    
    # Filter rows with participantId == args.par_id
    df = df[df["participantId"] == args.par_id]
    df = df.reset_index(drop=True)
    df = df.fillna("null")

    # Read Apartments.json
    with open(os.path.join("../data/Attributes", "Apartments.json"), "r") as f:
        apartments = json.load(f)

    # get unique apartmentId
    apartment_ids = df["apartmentId"].unique().tolist()

    # retrieve apartment information
    apartments["features"] = list(filter(lambda x: x["properties"]["apartmentId"] in apartment_ids, apartments["features"]))

    # get unique jobId
    job_ids = df["jobId"].unique().tolist()

    # Read Jobs.json
    with open(os.path.join("../data/Attributes", "Jobs.json"), "r") as f:
        jobs = json.load(f)
    
    # Read Employers.json
    with open(os.path.join("../data/Attributes", "Employers.json"), "r") as f:
        employers = json.load(f)

    extended_jobs = []
    for id in job_ids:
        job = next(filter(lambda x: x["properties"]["jobId"] == id, jobs["features"]), None)
        if job is None:
            continue
        employer = next(filter(lambda x: x["properties"]["employerId"] == job["properties"]["employerId"], employers["features"]), None)
        if employer is None:
            continue
        extended_jobs.append({"job": job, "employer": employer})

    # Extract the data and convert to GeoJSON format
    geo_data = {}
    geo_data.update({"type": "FeatureCollection"})
    geo_data.update({"features": []})

    # get attributes
    attributes = df.columns.tolist()

    # get location attribute
    loc_attr = next(filter(lambda x: x in ["location", "currentLocation"], attributes), None)
    if loc_attr is None:
        raise ValueError("Cannot find location attribute in the data.")

    # iterate over each row
    for i in tqdm(range(len(df))):
        # only preserve even rows to cut down the size of data
        if i % 2 == 1:
            continue
        feature = {}
        feature.update({"type": "Feature"})
        properties = {}
        for attr in attributes:
            if attr == loc_attr:
                pass
            elif attr == "apartmentId":
                for apartment in apartments["features"]:
                    if apartment["properties"]["apartmentId"] == df.loc[i][attr]:
                        properties.update({"apartment": apartment})
                        break
            elif attr == "jobId":
                for job in extended_jobs:
                    if job["job"]["properties"]["jobId"] == df.loc[i][attr]:
                        properties.update({"job": job["job"]})
                        properties.update({"employer": job["employer"]})
                        break
            else:
                properties.update({attr: df.loc[i][attr]})
        feature.update({"properties": properties})
        feature.update({"geometry": generate_geo_data(df, i, loc_attr)})

        geo_data["features"].append(feature)

    # save the data in json format
    with open(os.path.join(args.dirname, f"par_{args.par_id}.json"), "w") as f:
        json.dump(geo_data, f, cls=NpEncoder, indent=4)
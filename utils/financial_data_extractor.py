import json
import os
from typing import List, Dict
from argparse import ArgumentParser


import pandas as pd
import numpy as np
from tqdm import tqdm

r"""
    This script is used to extract the data from FinancialJournal.csv file and convert it to json format.
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


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument('--dirname', type=str, default='../data/Journals/', 
                        help='name of directory to read data from')
    parser.add_argument("--par_id", type=int, default=0, 
                        help="participant id")
    args = parser.parse_args()

    # read data
    df = pd.read_csv(os.path.join(args.dirname, 'FinancialJournal.csv'))

    # get the data of the participant
    df = df[df['participantId'] == args.par_id]
    df = df.reset_index(drop=True)

    # get attributes
    attributes = df.columns.tolist()

    # initialize json
    json_data = {}
    json_data.update({"type": "FeatureCollection"})
    json_data.update({"features": []})

    for i in tqdm(range(len(df))):
        feature = {}
        feature.update({"type": "Feature"})

        # get properties
        properties = {}
        for attr in attributes:
            properties.update({attr: df.loc[i][attr]})

        # update feature
        feature.update({"properties": properties})

        # append feature to json
        json_data["features"].append(feature)

    # save json
    with open(os.path.join(args.dirname, f"FinancialJournal_{args.par_id}.json"), "w") as f:
        json.dump(json_data, f, cls=NpEncoder, indent=4)
        
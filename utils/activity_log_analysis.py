import csv
import os
import ast
from typing import List, Dict
from argparse import ArgumentParser


import pandas as pd
import numpy as np
from tqdm import tqdm
import matplotlib.pyplot as plt


r"""
    This file contains functions to extract data from Activity_Logs and apply some simple data visulization on top of it.
    The data has the following attributes:
        - timestamp (datetime): the time when the status was logged, e.g. 2022-03-01T00:00:00Z
        - currentLocation (point): the location of the participant within the city at the time the status was logger e.g. POINT (-2724.6277665310454 6866.2081834436985)
        - participantId (integer): unique ID assigned to each participant
        - currentMode(string): a string representing the mode the participant is in at the time the status was logged, one of 
        {"AtHome", "Transport", "AtRecreation", "AtRestaurant", "AtWork" }.
        - hungerStatus (string): a string representing the participant`s hunger status at the time the status was logged, one of 
        {'JustAte', 'BecameFull', 'BecomingHungry', 'Hungry', 'Starving'}
        - sleepStatus (string): a string representing the participant`s sleep status at the time the status was logged, one of 
        {'Sleeping', 'Awake', 'PrepareToSleep', 'Unkonwn'}
        - apartmentId (integer): the integer ID corresponding to the apartment in which the participant resides at the time the status was logged
        - availableBalance (float): the balance in the participant`s financial account (negative if in debt)
        - jobId (integer): the integer ID corresponding to the job the participant holds at the time the status was logged, N/A if unemployed (we will convert it to -1)
        - financialStatus (string): a string representing the participant`s sleep status at the time the status was logged, one of {'Stable', 'Unstable', 'Unknown'}
        - dailyFoodBudget (double): the amount of money the participant has budgeted for food that day
        - weeklyExtraBudget (double): the amount of money the participant has budgeted for miscellaneous expenses that week
"""


def post_processing(data: pd.DataFrame):
    """
    This is the post processing function for the data.
    NOTE: Once you modify the this function, don't forget to remove full_data.csv so that it could be updated.
    """
    # convert timestamp to datetime object
    data['timestamp'] = pd.to_datetime(data['timestamp'])

    # convert timestamp to EST
    data['timestamp'] = data['timestamp'].dt.tz_convert('US/Eastern')

    # convert currentLocation to tuple
    data['currentLocation'] = data['currentLocation'].apply(lambda x: tuple(map(float, x[7:-1].split(' '))))

    # correct wrong hunger status
    data['hungerStatus'] = data['hungerStatus'].apply(lambda x: 'BecomingHungry' if x == 'Beco' else x)

    # convert nan sleep status to 'Unknown'
    data['sleepStatus'] = data['sleepStatus'].apply(lambda x: 'Unknown' if pd.isna(x) else x)

    # convert nan jobId to -1
    data['jobId'] = data['jobId'].apply(lambda x: -1 if pd.isna(x) else x)

    # convert nan financial status to 'Unknown'
    data['financialStatus'] = data['financialStatus'].apply(lambda x: 'Unknown' if pd.isna(x) else x)

    return data


def extract_participant_location(par_id: int, par_data: pd.DataFrame, time_list: List):
    """
    Get participant location data and visualize it using scatter plot.
    """
    # get locations
    loc_data = par_data['currentLocation'].tolist()

    # get x and y coordinates
    x = [loc[0] for loc in loc_data]
    y = [loc[1] for loc in loc_data]

    # plot data
    plt.scatter(x, y, s=0.5)

    # save plot in results/par_{par_id}/locations_{par_id}.png
    plt.savefig(f'./results/par_{par_id}/locations_{par_id}.png')

    # clear plot
    plt.clf()


def extract_participant_mode(par_id: int, par_data: pd.DataFrame, time_data: List):
    """
    Get participant mode data and visualize it over time.
    """
    # map mode to integer
    mode_map = {'AtHome': 0, 'Transport': 1, 'AtRecreation': 2, 'AtRestaurant': 3, 'AtWork': 4}
    color_map = {0: 'green', 1: 'blue', 2: 'yellow', 3: 'orange', 4: 'red'}
    mode_data = par_data['currentMode'].apply(lambda x: mode_map[x]).tolist()
    
    # plot data with scatter plot
    plt.scatter(time_data, mode_data, s=0.5, c=[color_map[mode] for mode in mode_data])

    # save plot in results/par_{par_id}/modes_{par_id}.png
    plt.savefig(f'./results/par_{par_id}/modes_{par_id}.png')

    # clear plot
    plt.clf()


def extract_participant_hunger(par_id: int, par_data: pd.DataFrame, time_data: List):
    """
    Get participant hunger data and visualize it over time.
    """
    # map hunger status to integer
    hunger_map = {'JustAte': 0, 'BecameFull': 1, 'BecomingHungry': 2, 'Hungry': 3, 'Starving': 4}
    color_map = {0: 'green', 1: 'blue', 2: 'yellow', 3: 'orange', 4: 'red'}
    hunger_data = par_data['hungerStatus'].apply(lambda x: hunger_map[x]).tolist()

    # plot data with scatter plot
    plt.scatter(time_data, hunger_data, s=0.5, c=[color_map[x] for x in hunger_data])

    # save plot in results/par_{par_id}/hunger_{par_id}.png
    plt.savefig(f'./results/par_{par_id}/hunger_{par_id}.png')

    # clear plot
    plt.clf()


def extract_participant_sleep(par_id: int, par_data: pd.DataFrame, time_data: List):
    """
    Get participant sleep data and visualize it over time.
    """
    # map sleep status to integer
    sleep_map = {'Sleeping': 0, 'Awake': 1, 'PrepareToSleep': 2, 'Unknown': 3}
    color_map = {0: 'green', 1: 'blue', 2: 'yellow', 3: 'red'}
    sleep_data = par_data['sleepStatus'].apply(lambda x: sleep_map[x]).tolist()

    # plot data with scatter plot
    plt.scatter(time_data, sleep_data, s=0.5, c=[color_map[x] for x in sleep_data])

    # save plot in results/par_{par_id}/sleep_{par_id}.png
    plt.savefig(f'./results/par_{par_id}/sleep_{par_id}.png')

    # clear plot
    plt.clf()


def extract_participant_apartment(par_id: int, par_data: pd.DataFrame, time_data: List):
    """
    Get participant apartment data and visualize it over time.
    """
    # get apartment data
    apartment_data = par_data['apartmentId'].tolist()

    # plot data
    plt.plot(time_data, apartment_data)

    # save plot in results/par_{par_id}/apartments_{par_id}.png
    plt.savefig(f'./results/par_{par_id}/apartments_{par_id}.png')

    # clear plot
    plt.clf()


def extract_participant_available_balance(par_id: int, par_data: pd.DataFrame, time_data: List):
    """
    Get participant available balance data and visualize it over time.
    """
    # get available balance data
    available_balance_data = par_data['availableBalance'].tolist()

    # plot data
    plt.plot(time_data, available_balance_data)

    # save plot in results/par_{par_id}/available_balance_{par_id}.png
    plt.savefig(f'./results/par_{par_id}/available_balance_{par_id}.png')

    # clear plot
    plt.clf()


def extract_participant_job(par_id: int, par_data: pd.DataFrame, time_data: List):
    """
    Get participant job data and visualize it over time.
    """
    # get job data
    job_data = par_data['jobId'].tolist()

    # plot data
    plt.plot(time_data, job_data)

    # save plot in results/par_{par_id}/jobs_{par_id}.png
    plt.savefig(f'./results/par_{par_id}/jobs_{par_id}.png')

    # clear plot
    plt.clf()


def extract_participant_financial_status(par_id: int, par_data: pd.DataFrame, time_data: List):
    """
    Get participant financial status data and visualize it over time.
    """
    # map financial status to integer
    financial_status_map = {'Stable': 0, 'Unstable': 1, 'Unknown': 2}
    financial_status_data = par_data['financialStatus'].apply(lambda x: financial_status_map[x]).tolist()

    # plot data
    plt.plot(time_data, financial_status_data)

    # save plot in results/par_{par_id}/financial_status_{par_id}.png
    plt.savefig(f'./results/par_{par_id}/financial_status_{par_id}.png')

    # clear plot
    plt.clf()


def extract_participant_daily_food_budget(par_id: int, par_data: pd.DataFrame, time_data: List):
    """
    Get participant daily food budget data and visualize it over time.
    """
    # get daily food budget data
    daily_food_budget_data = par_data['dailyFoodBudget'].tolist()

    # plot data
    plt.plot(time_data, daily_food_budget_data)

    # save plot in results/par_{par_id}/daily_food_budget_{par_id}.png
    plt.savefig(f'./results/par_{par_id}/daily_food_budget_{par_id}.png')

    # clear plot
    plt.clf()


def extract_participant_weekly_extra_budget(par_id: int, par_data: pd.DataFrame, time_data: List):
    """
    Get participant weekly extra budget data and visualize it over time.
    """
    # get weekly extra budget data
    weekly_extra_budget_data = par_data['weeklyExtraBudget'].tolist()

    # plot data
    plt.plot(time_data, weekly_extra_budget_data)

    # save plot in results/par_{par_id}/weekly_extra_budget_{par_id}.png
    plt.savefig(f'./results/par_{par_id}/weekly_extra_budget_{par_id}.png')

    # clear plot
    plt.clf()


if __name__ == '__main__':
    # add argument parser
    parser = ArgumentParser()
    parser.add_argument('--dirname', type=str, default='../data/Activity_Logs/', help='name of directory to read data from')
    parser.add_argument('--num_of_par', type=int, default=-1, help='number of participant to extract data from')
    args = parser.parse_args()
    
    func_list = [extract_participant_sleep, 
                 extract_participant_hunger, 
                 extract_participant_mode, 
                 extract_participant_location, 
                 extract_participant_apartment, 
                 extract_participant_available_balance, 
                 extract_participant_job, 
                 extract_participant_financial_status, 
                 extract_participant_daily_food_budget, 
                 extract_participant_weekly_extra_budget]

    # read data from each .csv file in the directory
    print("reading data from directory: {}".format(args.dirname))
    # if full_data.csv exists, read from it
    if os.path.exists(os.path.join(args.dirname, 'full_data.csv')):
        print("full_data.csv exists, reading from it...")
        # read timestamp as datetime object and currentLocation as tuple
        data = pd.read_csv(os.path.join(args.dirname, 'full_data.csv'), parse_dates=['timestamp'], converters={'currentLocation': ast.literal_eval})
    else:
        print("full_data.csv does not exist, reading from individual files...")
        data = pd.DataFrame()
        for i in tqdm(range(20)):
            # read data from csv file and concatenate to existing data
            data = pd.concat([data, pd.read_csv(os.path.join(args.dirname, f'ParticipantStatusLogs{i + 1}.csv'))], ignore_index=True)

        # post process data
        print("post processing data...")
        data = post_processing(data)
        print("post processing done!!")

        # save full data to full_data.csv
        print("saving full data to full_data.csv...")
        data.to_csv(os.path.join(args.dirname, 'full_data.csv'), index=False)

    print("data read!!")
    print(data.dtypes)

    # visualize data for participants
    if args.num_of_par <= 0 or args.num_of_par > 1000:
        args.num_of_par = 1000
    print("extracting data for {} participants...".format(args.num_of_par))
    for i in tqdm(range(args.num_of_par)):
        # make directory for each participant if it does not exist
        if not os.path.exists('./results/par_{}'.format(i)):
            os.makedirs('./results/par_{}'.format(i))
        par_data = data[data['participantId'] == i]
        time_stamp = par_data['timestamp'].tolist()
        for func in func_list:
            func(i, par_data, time_stamp)

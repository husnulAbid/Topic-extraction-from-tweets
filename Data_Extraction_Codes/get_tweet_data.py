import time
import json
import requests
from os import path
import pandas as pd
import subprocess


class MainClass:

    def __init__(self):  
        self.api_req_count = 0


    def start_process(self):

        input_file_name = 'top_50_accounts.csv'
        top_50_df = pd.read_csv(input_file_name, delimiter='\t')
        account_list = top_50_df['Account'].tolist()

        for account in account_list:
            account_name = account[1:]
            subprocess.run(f'twint -u {account_name} -o output_tweets/{account_name}.csv', shell=True)


if __name__ == '__main__':

    MainClass().start_process()
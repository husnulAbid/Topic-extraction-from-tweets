import time
import json
import requests
from os import path
import pandas as pd


class MainClass:

    def __init__(self):  
        self.api_token = '###### PUT YOUR API TOKEN - TWITTER V2 #######'
        self.api_req_count = 0
    

    def read_from_text_file(self, input_file):
        all_lines = []
        with open(input_file) as f:
            all_lines = [line.rstrip() for line in f]
        
        return all_lines
    

    def append_in_text_file(self, file_name, input_str):
        with open(file_name, 'a') as myfile:
            myfile.write(input_str + '\n')
    

    def clear_text_file(self, input_file):
        f = open(input_file, 'r+')
        f.truncate(0)


    def log_message(self, msg, filename=None):
        print(msg)

        if filename is not None:
            self.append_in_text_file(filename, msg)


    def check_request_count_to_wait(self):
        if self.api_req_count % 14 == 0:
            print('\n\nResting for 15 minutes\n')
            time.sleep((15 * 60) + 5)       # 15 mins wait


    def get_user_id(self, account_name):
        user_id = ''
        url = f'https://api.twitter.com/2/users/by/username/{account_name}'

        payload={}
        headers = {
            'Authorization': f'Bearer {self.api_token}'
        }

        try:
            response = requests.request('GET', url, headers=headers, data=payload)

            if response.status_code == 200:
                user_id = json.loads(response.text)['data']['id']
                return user_id
        except:
            pass
        
        return user_id
    

    def get_data_of_following_request(self, user_id, is_first_call, pagination_token):
        response_data = ''
        max_results = 1000

        if is_first_call:
            url = f'https://api.twitter.com/2/users/{user_id}/following?max_results={max_results}'
        else:
            url = f'https://api.twitter.com/2/users/{user_id}/following?max_results={max_results}&pagination_token={pagination_token}'

        payload={}
        headers = {
            'Authorization': f'Bearer {self.api_token}'
        }

        try:
            response = requests.request('GET', url, headers=headers, data=payload)
            print(response)

            if response.status_code == 200:
                response_data = response.text.encode('utf-8', errors='ignore')
                response_data = json.loads(response_data)
        except:
            pass
        
        return response_data

    
    def get_following_list(self, account):
        following_username = []
        account_name = account[1:]
        user_id = self.get_user_id(account_name)

        self.api_req_count = self.api_req_count + 1
        self.check_request_count_to_wait()
        
        if user_id:
            is_first_call = True
            pagination_token = ''

            response_data = self.get_data_of_following_request(user_id, is_first_call, pagination_token)

            try:
                following_list_data = response_data['data']

                for following_data in following_list_data:
                    following_username.append(following_data['username'])

                self.api_req_count = self.api_req_count + 1
                self.check_request_count_to_wait()
            except:
                pass

            try:
                pagination_token = response_data['meta']['next_token']
            except:
                pagination_token = ''


            while pagination_token:
                is_first_call = False

                response_data = self.get_data_of_following_request(user_id, is_first_call, pagination_token)

                if not response_data:           # second try
                    print('\n\nSleeping\n')
                    time.sleep (15 * 61)
                    self.api_req_count = 0
                    
                    response_data = self.get_data_of_following_request(user_id, is_first_call, pagination_token)

                    self.api_req_count = self.api_req_count + 1
                    self.check_request_count_to_wait()
                
                try:
                    following_list_data = response_data['data']

                    for following_data in following_list_data:
                        following_username.append(following_data['username'])
                except:
                    pass

                self.api_req_count = self.api_req_count + 1
                self.check_request_count_to_wait()

                try:
                    pagination_token = response_data['meta']['next_token']
                except:
                    pagination_token = ''

        return following_username



    def start_process(self):

        input_file_name = 'top_50_accounts.csv'
        top_50_df = pd.read_csv(input_file_name, delimiter='\t')
        account_list = top_50_df['Account'].tolist()

        # account_list = ['@katyperry', '@SportsCenter', '@NiallOfficial']

        for account in account_list:
            following_username = self.get_following_list(account)

            print('\n')
            print(account, '\t: ', len(following_username))

            df = pd.DataFrame(list(zip(following_username)), columns = ['following account'])
            df['account'] = account[1:]

            df.to_csv('following_file.csv', mode='a', header=False, index=False)


if __name__ == '__main__':

    MainClass().start_process()
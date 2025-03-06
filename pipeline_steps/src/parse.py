'''
This script serves as a parser script for api responses
'''

class parse:

    def __init__(self):
          
        print("Successfully initialized api response parser")


    def parse_names(self, response):  # parse object names and ids from api response
            
        names = {}

        for element in response['value']: 
            element_id = element['id']
            element_name = element['displayName']
            names[element_name] = element_id

        return names
        

    def get_report_names(self, response):  # get report names

        names = self.parse_names(response=response)

        return names
    

    def get_dataset_names(self, response):  # get model names

        names = self.parse_names(response=response)

        return names 
        
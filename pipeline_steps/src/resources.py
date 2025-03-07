import os

'''
This script dynamically obtains all files found in the resources folder of .pbip reports
'''

class resources:

    def __init__(self):

        print("Gathering report resource files")

    
    def get_resources(self, directory, report_name):  # get all resource files

        file_dict = {}
        path = f"{directory}/{report_name}.Report/StaticResources/RegisteredResources/"  # path to resource files

        if os.path.exists(path=path):  # check if registeredresources folder exists
            for resource in os.listdir(path):  # fill a dictionary with information of all resource files with filename:path
                file_name = f"{path}{resource}"
                file_dict[resource] = file_name
        else:
            file_dict = {}

        return file_dict
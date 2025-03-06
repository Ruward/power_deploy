import sys
import os

'''
This script serves as a parser script for commit files and stage checking
'''

class names:

    def __init__(self, artifact_dir: str, goal: str, stage: str):

        self.artifact_dir = artifact_dir
        self.goal = goal 
        self.stage = stage


    def get_files_from_artifact(self) -> list[str]:  # get the names of the files that were changed in the most recent commit

        file_list = []
        for root, dirs, files in os.walk(self.artifact_dir):

            for file in files: 
                path = os.path.join(root, file)
                file_list.append(path)
    
        return file_list


    def get_names(self, commit_file: str) -> str:  # parse object names from a commit file

        name = commit_file.split('/')[9].split('.')[0]
        folder = commit_file.split('/')[8]
            
        return name, folder

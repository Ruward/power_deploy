import requests
import json

from src.encode import encode

'''
This script contains all the fabric api endpoint, header, and body logic for the power bi deployment pipelines for model and report deployment
'''

class api:

    def __init__(self, tenant_id: str, client_id: str, client_secret: str) -> None:

        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = self.get_token()  # get bearer token for api authorization
        self.headers = {"Content-Type": "application/json"
                   , "Authorization": f"Bearer {self.token}"}
        self.encode_obj = encode()  # init encoding logic

    
    def get_token(self) -> str:  # get token for fabric api

        url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"  # service principal url
        body = f'grant_type=client_credentials&client_id={self.client_id}&client_secret={self.client_secret}&scope=https://analysis.windows.net/powerbi/api/.default'

        # GET call for fabir token
        response = requests.get(url=url,
                            data=body)

        token = response.json()['access_token']  # get token from API response

        return str(token)


    def parse_bytes(self, bytes: bytes) -> str:  # use parser object to parse bytes for python interpretation

        parsed_bytes = str(bytes).strip("b\'")

        return parsed_bytes 
    

    def get(self, workspace_id: str, goal: str):  # generic fabric get api endpoint

        url = f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/{goal}"
        headers = self.headers

        response = requests.get(url=url, headers=headers)

        response = response.json() 

        return response 
    

    def get_model(self, workspace_id: str, model_id: str):  # generic fabric get model api endpoint

        url = f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/semanticModels/{model_id}"
        headers = self.headers

        response = requests.get(url=url, headers=headers)

        response = response.json() 

        return response 
    
    
    def post(self, workspace_id: str, goal: str, body: str):  # generic fabric post api endpoint for uploads

        url = f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/{goal}"
        headers = self.headers
        body = json.dumps(body)
      
        response = requests.post(url=url, headers=headers, data=body)

        return response 
    

    def update(self, workspace_id: str, goal: str, id: str, body: str):  # generic fabric post api endpoint for updates

        url = f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/{goal}/{id}/updateDefinition"
        headers = self.headers
        body = json.dumps(body)

        response = requests.post(url=url, headers=headers, data=body)

        return response
    

    def get_names(self, goal: str, workspace_id: str):  # execute get statement to get report/model names on workspace

        names = self.get(workspace_id=workspace_id, goal=goal)

        return names
    

    def define_resources(self, file_dict: dict) -> list:  # logic to add all required resource files for report upload/update

        path = "StaticResources/RegisteredResources"  # path to resource files
        resource_body = []

        for file in file_dict.keys():  # loop over specified resource files 

            if '.json' in file:  # .json resource files are non-binary
                bytes_file = self.encode_obj.encode_str(txt_file=file_dict[file])  # encode string to base64
            else:  # treat all other resource files as binary
                bytes_file = self.encode_obj.encode_bin(bin_file=file_dict[file])  # encode binary to base64
            
            encoded_file = self.parse_bytes(bytes_file)  # parse bytes for python interpretation

            body = {}

            # create part of api call body for each resource file dynamically
            body["path"] = f"{path}/{file}"
            body["payload"] = f"{encoded_file}"
            body["payloadType"] = "InlineBase64"

            resource_body.append(body)  # append to main api body

        return resource_body


    def post_report(self, report_name: str, deployment_dict: dict, file_dict: dict, workspace_id: str):  # logic to upload a new report to workspace

        payload_list = []

        for deployment_file in deployment_dict.keys():  # loop over deployment files
            file_type = deployment_dict[deployment_file]  # string or bin file
            file_name = str(deployment_file).rsplit('/', 1)[-1]  # get name of file

            if file_type == 'str':  # treat file contents as string
                payload_bytes = self.encode_obj.encode_str(txt_file=deployment_file)  # base64 encoded contents
                payload = self.parse_bytes(payload_bytes)  # parse base64 bytes
            elif file_type == 'bin':  # treat file contents as binary
                payload_bytes = self.encode_obj.encode_bin(bin_file=deployment_file)  # base64 encoded contents
                payload = self.parse_bytes(payload_bytes)  # parse base64 bytes
            
            payload = {
                "path": file_name, 
                "payload": payload, 
                "payloadType": "InlineBase64"
            }

            payload_list.append(payload)  # total list of deployment file payload specifications

        if len(file_dict) != 0:
            resource_body = self.define_resources(file_dict)  # obtain dynamic api body for resource files
        else:
            resource_body = []

        parts = payload_list + resource_body  # create total api call 'parts' overview

        # create total api call body
        body = {
            "displayName": report_name,
            "description": "",
            "definition": {
                "parts": parts
            }
        }

        response = self.post(workspace_id=workspace_id, goal="reports", body=body)  # execute upload logic

        return response
    

    def post_model(self, model_name: str, deployment_dict: dict, workspace_id: str):  # logic to upload a new model to workspace

        payload_list = []

        for deployment_file in deployment_dict.keys():  # loop over deployment files
            file_type = deployment_dict[deployment_file]  # string or bin file
            file_name = str(deployment_file).rsplit('/', 1)[-1]  # get name of file

            if file_type == 'str':  # treat file contents as string
                payload_bytes = self.encode_obj.encode_str(txt_file=deployment_file)  # base64 encoded contents
                payload = self.parse_bytes(payload_bytes)  # parse base64 bytes
            elif file_type == 'bin':  # treat file contents as binary
                payload_bytes = self.encode_obj.encode_bin(bin_file=deployment_file)  # base64 encoded contents
                payload = self.parse_bytes(payload_bytes)  # parse base64 bytes
            
            payload = {
                "path": file_name, 
                "payload": payload, 
                "payloadType": "InlineBase64"
            }

            payload_list.append(payload)  # total list of deployment file payload specifications

        # specify api call body
        body = {
            "displayName": f"{model_name}",
            "description": "",
            "definition": {
                "parts": payload_list
            }
        }

        response = self.post(workspace_id=workspace_id, goal="semanticModels", body=body)  # execute upload logic

        return response
    

    def update_report(self, id: str, deployment_dict: dict, file_dict: dict, workspace_id: str):  # logic to update a report in workspace

        payload_list = []

        for deployment_file in deployment_dict.keys():  # loop over deployment files
            file_type = deployment_dict[deployment_file]  # string or bin file
            file_name = str(deployment_file).rsplit('/', 1)[-1]  # get name of file

            if file_type == 'str':  # treat file contents as string
                payload_bytes = self.encode_obj.encode_str(txt_file=deployment_file)  # base64 encoded contents
                payload = self.parse_bytes(payload_bytes)  # parse base64 bytes
            elif file_type == 'bin':  # treat file contents as binary
                payload_bytes = self.encode_obj.encode_bin(bin_file=deployment_file)  # base64 encoded contents
                payload = self.parse_bytes(payload_bytes)  # parse base64 bytes
            
            payload = {
                "path": file_name, 
                "payload": payload, 
                "payloadType": "InlineBase64"
            }

            payload_list.append(payload)  # total list of deployment file payload specifications

        if len(file_dict) != 0:
            resource_body = self.define_resources(file_dict)  # obtain dynamic api body for resource files
        else:
            resource_body = []

        parts = payload_list + resource_body  # create total api call 'parts' overview

        # create total api call body
        body = {
            "definition": {
                "parts": parts
            }
        }

        response = self.update(workspace_id=workspace_id, goal="reports", id=id, body=body)  # execute update logic

        return response
    

    def update_model(self, id: str, deployment_dict: dict, workspace_id: str):  # logic to update a model in workspace

        payload_list = []

        for deployment_file in deployment_dict.keys():  # loop over deployment files
            file_type = deployment_dict[deployment_file]  # string or bin file
            file_name = str(deployment_file).rsplit('/', 1)[-1]  # get name of file

            if file_type == 'str':  # treat file contents as string
                payload_bytes = self.encode_obj.encode_str(txt_file=deployment_file)  # base64 encoded contents
                payload = self.parse_bytes(payload_bytes)  # parse base64 bytes
            elif file_type == 'bin':  # treat file contents as binary
                payload_bytes = self.encode_obj.encode_bin(bin_file=deployment_file)  # base64 encoded contents
                payload = self.parse_bytes(payload_bytes)  # parse base64 bytes
            
            payload = {
                "path": file_name, 
                "payload": payload, 
                "payloadType": "InlineBase64"
            }

            payload_list.append(payload)  # total list of deployment file payload specifications

        # specify api call body
        body = {
            "definition": {
                "parts": payload_list
            }
        }

        response = self.update(workspace_id=workspace_id, goal="semanticModels", id=id, body=body)  # execute update logic

        return response
    

    def get_ownership(self, workspace_id: str, dataset_id: str):  # give the service principal ownership of the dataset that needs to be updated 

        url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/Default.TakeOver"
        headers = self.headers

        response = requests.post(url,
                            headers=headers)

        return response
    

    def update_datasource(self, workspace_id: str, dataset_id: str, server: str, old_dwh: str, new_dwh: str):  # update the data source for the specified dataset

        url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/Default.UpdateDatasources"
        headers = self.headers

        body = {
            "updateDetails": [
            {
                "datasourceSelector": {
                    "datasourceType": "Sql",
                    "connectionDetails": {
                        "server": server,
                        "database": old_dwh.lower()
                        }
                    },
                    "connectionDetails": {
                        "server": server,
                        "database": new_dwh.lower()
                    }
                }
            ]
        }
        
        json_body = json.dumps(body)

        response = requests.post(url,
                        headers=headers, data=json_body)

        return response
    

    def bind_gateway(self, workspace_id: str, dataset_id: str, gateway_id: str, datasource_id: str):  # bind model to on-premise gateway 

        url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/datasets/{dataset_id}/Default.BindToGateway"
        headers = self.headers 

        body = {
            "gatewayObjectId": gateway_id,
            "datesourceObjectIds": [
                datasource_id
            ]
        }

        json_body = json.dumps(body)

        response = requests.post(url,
                        headers=headers, data=json_body)
        
        return response
    

    def lro(self, location_header: str):  # logic to trace long running operations api call status
        
        completed = False 
        success = False

        while not completed:  # lro process has not completed
            response = requests.get(url=location_header,
                        headers=self.headers)  # get status from location url
            
            if response.ok:  # location url queried successfully
                response = response.json() 

                if response['status'] != "Running":  # lro process has completed
                    completed = True 
            else:  # location url query failed
                raise Exception("Error: LRO status check failed") 
            
        if response['status'] == "Succeeded":  # lro process completed successfully
            success = True 
            error = ''
            return success, error
        else:  # lro process failed, set error message
            error = response['error']
            return success, error

from src.api import api 
from src.parse import parse
from src.names import names
from src.model_source import model_source

import os 
import time
from dotenv import load_dotenv

'''
This script contains the main logic to automatically deploy power bi semantic models that are stored in .pbip format
'''

def main():

    env_path = os.getenv('env_dir')

    load_dotenv(env_path)

    tenant_id = os.getenv("tenantid")
    client_id = os.getenv("clientid")
    client_secret = os.getenv("clientsecret")
    stage = os.getenv("stage")
    model_dir = os.getenv('dir')
    gateway_id = os.getenv('gateway_id')
    catalog_char = os.getenv('catalog')
    db_host = os.getenv('db_host')
    db_http = os.getenv('db_http')
    datasource_id = os.getenv('datasource_id')

    location = os.path.realpath(os.path.dirname(__file__))  # location of this python script
    os.chdir(location)  # change python working directory to the location of this python script
    artifact_dir = f"{os.getcwd()}/../{model_dir}/"

    goal = "semanticModels"  # parameter for semantic model api url endpoints

    # init objects
    api_obj = api(tenant_id, client_id, client_secret) 
    parse_obj = parse()
    name_obj = names(artifact_dir=artifact_dir, goal=goal, stage=stage)

    artifact_files = name_obj.get_files_from_artifact()  # get the files from the most recent git commit

    for artifact_file in artifact_files:
        if 'model.bim' in artifact_file:  # model.bim must contain changes for pipeline to execute
            model_name, dir = name_obj.get_names(artifact_file)  # get model name from commit files
            print(f"\nDeploying Power BI Semantic Model {model_name}")

            deployment_dir = f"{os.getcwd()}/../{model_dir}/{dir}/{model_name}.SemanticModel"

            model_file = f"{deployment_dir}/model.bim"  # path to model.bim
            definition_file = f"{deployment_dir}/definition.pbism"  # path to definition.pbism       

            deployment_dict = {model_file: 'str', definition_file: 'str'}
                    
            model_source(model_file, catalog_char, db_host, db_http).write_new_content()
            print(f"Successfully updated model {model_name} datasource")

            if catalog_char == "p":  # current stage is prod
                if dir == "general":  # model is of type general
                    workspace = os.getenv("general_workspace")  # set target workspace to prd-general
                elif dir == "management":  # model is of type management
                    workspace = os.getenv("management_workspace")  # set target workspace to prd-management
            else:  # current stage is not prod
                workspace = os.getenv("workspace")  # set target workspace to tst or acc

            models = api_obj.get_names(goal=goal, workspace_id=workspace)  # get all models in target workspace
            model_names = parse_obj.get_dataset_names(response=models)  # parse the model names

            if model_name in model_names:  # model exists in workspace
                print("Model found on service, updating model...")
                id = model_names[model_name]  # get model id from name
                response = api_obj.update_model(id, deployment_dict, workspace)  # execute update logic
                if response.ok and response.status_code != 202:  # update logic was successful without lro 
                    print(f"Model {model_name} successfully updated, {response}")
                elif response.status_code == 202:  # update logic uses lro (response code 202)
                    time.sleep(10)
                    lro_status_url = response.headers['location']  # status url received with 202 response
                    lro_response, error = api_obj.lro(lro_status_url)  # use status url to trace lro status
                    if lro_response:  # update was successful
                        print(f"Model {model_name} successfully updated, {response}")
                    else:  # update failed, return lro error message
                        print(f"Error while updating model {model_name}, lro error: {error}")
                        raise Exception("LRO update error")
                else:  # update logic failed
                    print(f"Error while updating model {model_name}, {response}")
                    raise Exception("Update error")
            else:  # model does not exist in workspace
                print("Model not found on service, creating model...")
                response = api_obj.post_model(model_name, deployment_dict, workspace)  # execute upload logic
                if response.ok and response.status_code != 202:  # upload logic was successful without lro
                    print(f"Model {model_name} successfully created, {response}")
                elif response.status_code == 202:  # upload logic uses lro (response code 202)
                    lro_status_url = response.headers['location']  # status url received with 202 response
                    lro_response, error = api_obj.lro(lro_status_url)  # use status url to trace lro status
                    if lro_response:  # upload was successful
                        print(f"Model {model_name} successfully created, {response}")
                    else:  # upload failed, return lro error message
                        print(f"Error while creating model {model_name}, lro error: {error}")
                        raise Exception("LRO creation error")
                else:  # upload logic failed
                    print(f"Error while creating model {model_name}, {response}")
                    raise Exception("Creation error")

            time.sleep(15)  # delay so Power BI can process that the model has been deployed
            models_new = api_obj.get_names(goal=goal, workspace_id=workspace)  # get all models in workspace
            model_names_with_newest = parse_obj.get_dataset_names(response=models_new)  # parse the model names
            new_id = model_names_with_newest[model_name]  # get model id from name
            own_response = api_obj.get_ownership(workspace, new_id)  # give ownership of model to service principal

            if own_response.ok:  # ownership successfully acquired
                print("Acquired ownership of model")
            else:  # ownership not acquired
                print(f"Error while taking over model, {own_response}")
                raise Exception("Ownership error")

            bind_response = api_obj.bind_gateway(workspace, new_id, gateway_id, datasource_id)  # bind model to gateway 
            
            if bind_response.ok:  # model bound to gateway
                print(f"Successfully bound model to gateway source connection, {bind_response}")
            else:  # model not bound to gateway
                print(f"Error while binding model to gateway source connection, {bind_response}")
                raise Exception("Gateway bind error")

if __name__ == "__main__":
    main()
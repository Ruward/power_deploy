from src.api import api 
from src.parse import parse
from src.names import names
from src.source import source
from src.resources import resources

import os 
from dotenv import load_dotenv

'''
This script contains the main logic to automatically deploy power bi reports that are stored in .pbip format
'''

def main():
    
    env_path = os.getenv('env_dir')

    load_dotenv(env_path) 

    tenant_id = os.getenv("tenantid")
    client_id = os.getenv("clientid")
    client_secret = os.getenv("clientsecret")
    workspace_list = [os.getenv("tst_workspace"), os.getenv("acc_workspace"), os.getenv("prd_gen_workspace"), os.getenv("prd_man_workspace")]
    stage = os.getenv("stage")
    report_dir = os.getenv('dir')
    env = os.getenv('env')

    location = os.path.realpath(os.path.dirname(__file__))  # location of this python script
    os.chdir(location)  # change python working directory to the location of this python script
    artifact_dir = f"{os.getcwd()}/../{report_dir}/"

    goal = "reports"  # parameter for report api url endpoints

    # init objects
    api_obj = api(tenant_id, client_id, client_secret) 
    parse_obj = parse()
    name_obj = names(artifact_dir=artifact_dir, goal=goal, stage=stage)
    resource_obj = resources()

    artifact_files = name_obj.get_files_from_artifact()  # get the files from the most recent git commit

    for artifact_file in artifact_files:
        if 'report.json' in artifact_file and 'Model' not in artifact_file:  # report.json must contain changes for pipeline to execute
            report_name, dir = name_obj.get_names(artifact_file)  # get report name from commit files
            print(f"\nDeploying Power BI Report {report_name}")

            deployment_dir = f"{os.getcwd()}/../{report_dir}/{dir}/{report_name}.Report"

            report_file = f"{deployment_dir}/report.json"  # path to report.json
            definition_file = f"{deployment_dir}/definition.pbir"  # path to definition.pbir
            file_dict = resource_obj.get_resources(f"{os.getcwd()}/../{report_dir}/{dir}", report_name)

            deployment_dict = {report_file: 'str', definition_file: 'bin'}

            source_obj = source(definition_file)  # init source update logic
            old_source_id = source_obj.get_source()  # get id of datasource in definition file

            for otap_workspace in workspace_list: 
                # get the names of all semantic models in each workspace 
                otap_model_names = api_obj.get_names(goal="semanticModels", workspace_id=otap_workspace)

                # look for the model whose id matches that of the source of the report to be deployed
                if any(otap_model['id']==old_source_id for otap_model in otap_model_names['value']):
                    old_source_workspace = otap_workspace  # workspace of the source model
                    break 
                else:
                    continue
            
            if env == "p":  # current stage is prod
                if dir == "general":  # report is of type general
                    workspace = os.getenv("general_workspace")  # set target workspace to prd-general
                elif dir == "management":  # report is of type management
                    workspace = os.getenv("management_workspace")  # set target workspace to prd-management
            else:  # current stage is not prod
                workspace = os.getenv("workspace")  # set target workspace to tst or acc

            old_source_info = api_obj.get_model(old_source_workspace, old_source_id)  # get all information of datasource
            model_names = api_obj.get_names(goal="semanticModels", workspace_id=workspace)  # get all datasources in current stage

            response = source_obj.update_source(old_source_info, model_names)  # update report datasource to current stage
            print(response)

            reports = api_obj.get_names(goal=goal, workspace_id=workspace)  # get all reports in workspace
            report_names = parse_obj.get_report_names(response=reports)  # parse the report names

            if report_name in report_names:  # report exists in workspace
                print("Report found on service, updating report...") 
                id = report_names[report_name]  # get report id from name
                response = api_obj.update_report(id, deployment_dict, file_dict, workspace)  # execute update logic
                if response.ok:  # update logic was successful
                    print(f"Report {report_name} successfully updated, {response}")
                else:  # update logic failed
                    print(f"Error while updating report {report_name}, {response}")
                    raise Exception("Update error")
            else:  # report does not exist in workspace
                print("Report not found on service, creating report...")
                response = api_obj.post_report(report_name, deployment_dict, file_dict, workspace)  # execute upload logic
                if response.ok:  # upload logic was successful
                    print(f"Report {report_name} successfully created, {response}")
                else:  # upload logic failed
                    print(f"Error while creating report {report_name}, {response}")
                    raise Exception("Creation error")


if __name__ == "__main__": 
    main()
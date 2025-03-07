# Power_deploy

Power_deploy is a python based ci/cd solution for Power BI (PBI) reports and semantic models that does not require a premium PBI license. It was designed to make the lives of the Power BI frontend developers easier by enabling version control and automated deployment of Power BI resources. 

## Usage

The current version of power_deploy is based on an Azure based environment. Therefore it assumes that the code is hosted in an Azure DevOps git environment, and that Azure DevOps deployment pipelines are used as the pipeline environment, in turn using Azure Agent Pools to execute the logic. Additionally it was built for an Azure Databricks solution and therefore assumes Databricks to be the source warehouse. Lastly, it assumes PBI resources are stored in .pbip format. 

This was done due to the initial use case of the project. In the future I may expand the solution to become more generic for solutions hosted on other git services such as Gitlab or Github, and possibly also other warehouses. 

The pipeline is set up to follow a DTAP flow (development, testing, acceptance, production). For production, the pipeline makes a distinction between models and reports with a 'management' and 'general' target workspace in Power BI. For all other phases this distinction is not made. A development stage does not exist in the current version (only TAP) but can be easily added. A separate version of each pipeline exists for the deployment to the testing environment for quicker deployment possibilities when developing and testing Power BI resources. 

## Flow

The pipeline consists of three main parts: the Azure DevOps pipeline configuration (.yml), the git staging logic (.sh), and the python logic (.py). These are connected in the following flow of operations: 
1. The configuration yaml files contain the overarching logic of the pipeline. This file contains the actions that the deployment agent must execute, be they inline scripts or references to other scipt files (.sh or .py). It also forms the layout of the pipeline, e.g. the stages, jobs, parameters, and ordering of the tasks. 
2. The git staging logic shell script is responsible for determining which files have changed in the last commit. This ensures that only PBI models and reports that changed in this commit are deployed to the PBI service. This is particularly useful if you have many PBI resources, but only a few change in a commit. This step however is not required and my be redesigned to always include all PBI resources if desired, even though this may increase the pipeline runtime significantly.
3. The python logic .py scripts contain the actual PBI deployment logic. It uses the resources selected by the staging logic script and deploys these to the PBI service using the REST API endpoints. Surrounding logic, such as base64 encoding, authorization, and parsing api responses, are also included in the python scripts. 

## Requirements 

This code does not immediately run out-of-the-box. A number of required setup steps should be completed first: 
1. Enable the Power BI REST API functionality from the PBI admin portal 
2. Create an Azure app registration that is authorized to distribute Bearer Tokens on behalf of Power BI 
3. Install or enable an Azure DevOps Agent (either self-hosted or shared) which has bash, python, and pip installed
4. Create a .env secret file containing at least:
    1. the app registration client_id 
    2. the app registration client_secret 
5. Fill in the required Azure, Databricks, and Power BI parameters in the pipeline .yml files
6. Enable the Power BI projects (.pbip) setting in PBI desktop 
7. Put your Power BI resources in the following folder structure
    1. root folder: folder containing the pipeline_steps and .pipelines folders
    2. semanticmodels: root folder -> models -> general_models/management_models -> < put model resources here > 
    3. reports: root folder -> reports -> general_reports/management_reports -> < put report resources here >

During execution, the folder structure that is created on the deployment agent is determined by the pipeline. 

## Limitations 

As mentioned before, the current version of this pipeline only works in an Azure DevOps environment with Databricks as the warehouse. In the future this pipeline may be made more generic to fit other solutions, but in the meantime it may already serve as a valuable starting point for other implementations. 

One major technical limitation is the fact that the staging_artifact_dirs.sh script is only able to determine which PBI resources to deploy if these are in the latest git commit. If multiple commits are pushed at the same time, it only considers the newest commit. Therefore a user must make sure that the latest commit contains the changes that need to be deployed. 

## Contributing 

At the moment this project is not under active development by me, but I am open to any feedback or ideas. You may also use the code to create your own version if desired. 

## Author 

Made by Ruward Karper, licensed under MIT license. 
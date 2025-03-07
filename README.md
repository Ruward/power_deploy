# power_deploy

Power_deploy is a python based ci/cd solution for Power BI reports and semantic models. It was designed to make the lives of the Power BI frontend devlopers easier by enabling version control and automated deployment of Power BI resources. 

## usage

The current version of power_deploy is based on an Azure based environment. Therefore it assumes that the code is hosted in an Azure DevOps git environment, and that Azure DevOps deployment pipelines are used as the pipeline environment, in turn using Azure Agent Pools to execute the logic. Additionally it was built for an Azure Databricks solution and therefore assumes Databricks to be the source warehouse. Lastly, it assumes PBI resources are stored in .pbip format. 

This was done due to the initial use case of the project. In the future I may expand the solution to become more generic for solutions hosted on other git services such as Gitlab or Github, and possibly also other warehouses. 

The pipeline is set up to follow a DTAP flow (development, testing, acceptance, production). For production, the pipeline makes a distinction between models and reports with a 'management' and 'general' target workspace in Power BI. For all other phases this distinction is not made. A development stage does not exist in the current version (only TAP) but can be easily added. A separate version of each pipeline exists for the deployment to the testing environment for quicker deployment possibilities when developing and testing Power BI resources. 

## requirements 

This code does not immediately run out-of-the-box. A number of required setup steps should be completed first: 
1. Enable the Power BI REST API functionality from the PBI admin portal 
2. Create an Azure app registration that is authorized to distribute Bearer Tokens on behalf of Power BI 
3. Install or enable an Azure DevOps Agent (either self-hosted or shared) which has bash, python, and pip installed
4. Create a .env secret file containing at least:
    a. the app registration client_id 
    b. the app registration client_secret 
5. fill in the required Azure, Databricks, and Power BI parameters in the pipeline .yml files
6. Enable the Power BI projects (.pbip) setting in PBI desktop 
7. Put your Power BI resources in the following folder structure
    a. root folder: folder containing the pipeline_steps and .pipelines folders
    b. semanticmodels: root folder -> models -> general_models/management_models -> model resources 
    c. reports: root folder -> reports -> genera_reports/management_reports -> report resources

During execution, the folder structure that is created on the deployment agent is determined by the pipeline. 

## limitations 

As mentioned before, the current version of this pipeline only works in an Azure DevOps environment with Databricks as the warehouse. In the future this pipeline may be made more generic to fit other solutions, but in the meantime it may already serve as a valuable starting point for other implementations. 

## contributing 

At the moment this project is not under active development by me, but I am open to any feedback or ideas. You may also use the code to create your own version if desired. 

## author 

Made by Ruward Karper, licensed under MIT license. 
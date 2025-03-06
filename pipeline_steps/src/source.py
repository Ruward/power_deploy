import json

'''
This script contains the logic to dynamically update the live connection datasource of a pbi report prior to deployment
'''

class source:

    def __init__(self, definition_file):

        self.definition_file = definition_file


    def get_source(self) -> str:  # get source connection model id from definition.pbir

        with open(self.definition_file, 'r') as file_as_source:
            content = file_as_source.read() 
            file_as_source.close()

        content_as_json = json.loads(content)

        datasource_id = content_as_json['datasetReference']['byConnection']['pbiModelDatabaseName']  # source model id

        return str(datasource_id)
    

    def get_new_source(self, source_info, model_names) -> str:  # get the id of the target source connection model using the id and name of the old source

        source_name = source_info['displayName']  # name of the current source

        model_found = False
        
        for model in model_names['value']:
            if model['displayName'] == source_name:  # use the name of the current source to obtain the id of the new source
                new_source_id = model['id']  # id of the new source
                model_found = True
                break
            else:
                continue 
        
        if model_found == False:
            print("Error: required Power BI model not found in workspace")
            raise Exception("Model not found")
        
        return str(new_source_id)
    

    def update_source(self, source_info: str, model_names):  # update the source connection model id in definition.pbir

        with open(self.definition_file, 'r') as file_as_source:
            content = file_as_source.read() 
            file_as_source.close()

        content_as_json = json.loads(content)

        new_source_id = self.get_new_source(source_info, model_names)  # execute the logic to get the new id

        content_as_json['datasetReference']['byConnection']['pbiModelDatabaseName'] = new_source_id  # update id

        updated_content = json.dumps(content_as_json)

        with open(self.definition_file, 'w') as file_as_target:  # write new content to definition.pbir
            file_as_target.write(updated_content)
            file_as_target.close()

        response = "Definition datasource successfully updated"

        return response
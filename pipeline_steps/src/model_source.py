import re

'''
This script contains the logic to update the source of a semantic model prior to deployment
'''

class model_source:

    def __init__(self, model_file, catalog_char: str, new_db_host: str, new_db_http: str):

        self.model_file = model_file
        self.catalog_char = catalog_char
        self.new_db_host = new_db_host
        self.new_db_http = new_db_http
    

    def read_content(self):  # read the contents of model.bim

        with open(self.model_file, 'r') as model_content:
            content = model_content.read() 
            model_content.close()
        
        return content 
    

    def update_datasource_specifications(self):

        content = self.read_content()

        for word in re.split(r"\s", content): 
            if 'fi_' in word and '_gold' in word and (',' not in word or 'DefaultValue' in word):  # find databricks catalog definition and update it
                replace_char = word[word.find('fi_') + len('fi_') -1 : word.find('_gold') + 1 ]
                new_word = word.replace(replace_char, f"_{self.catalog_char}_")
                content = content.replace(word, new_word)
            elif 'azuredatabricks' in word and (',' not in word or 'DefaultValue' in word):  # find databricks host name and update it
                replace_substring = word[word.find('adb-') + len('adb-') - 4 : word.find('.net') + 4]
                new_host_ref = f"{self.new_db_host}.azuredatabricks.net"
                new_word = word.replace(replace_substring, new_host_ref)
                content = content.replace(word, new_word)
            elif 'protocolv1' in word and (',' not in word or 'DefaultValue' in word):  # find databricks host http path and update it
                replace_substring = word[word.find('sql/') + len('sql/') - 4 : word.rfind('\\"')]
                new_http_ref = f"sql/protocolv1/o/{self.new_db_http}"
                new_word = word.replace(replace_substring, new_http_ref)
                content = content.replace(word, new_word)
            
        return content
            
    
    def write_new_content(self):  # write the model.bim content with updated source specifications back to model.bim

        new_content = self.update_datasource_specifications()

        with open(self.model_file, 'w') as new_file: 
            new_file.write(new_content)
            new_file.close() 

import abc
import re
import glamorise
import spacy

class NlidbBase(metaclass=abc.ABCMeta):    

    def __init__(self):
        self._nlp = None

    def check_none_values(self, value):
        if value == None:
            return ''
        return value

    def _query_specific_synonym(self, synonym):
        try:
            synonym = synonym.lower().replace(' ', '_').replace('.', '_')
            if glamorise.config_glamorise_interface.get('nlidb_field_synonym'):
                if glamorise.config_glamorise_interface['nlidb_field_synonym'].get(synonym):
                    field =   glamorise.config_glamorise_interface['nlidb_field_synonym'][synonym]
                elif glamorise.config_glamorise_interface['nlidb_field_synonym'].get(self._alternative_compound_name(synonym, '_')):
                    field = glamorise.config_glamorise_interface['nlidb_field_synonym'][self._alternative_compound_name(synonym, '_')]
            return field
        except:
            return ''

    def _query_all_synonyms(self):
        try:
            if  glamorise.config_glamorise_interface.get('nlidb_field_synonym'):
                    synonym_list = list(  glamorise.config_glamorise_interface['nlidb_field_synonym'])        
            return synonym_list    
        except:
            return []    

    def _alternative_compound_name(self, str, sep):
        words = re.split(' |_', str)
        if 'de' in words:
            ## reversing the words using reversed() function
            words = list(reversed(words))
            words.remove('de')
            ## joining the words and printing
            return sep.join(words)
        else:    
            ## reversing the words using reversed() function
            words = list(reversed(words))
            ## joining the words and printing
            return (sep + "de " + sep).join(words)
    
    # has to use the medium model (en_core_web_md)
    # the small has no word vectors for similarity
    def _find_by_similarity(self, str1, list, lang="pt_core_news_md"):
        if not self._nlp:
            self._nlp = spacy.load(lang)  # make sure to use larger model!        
        doc1 = self._nlp(str1)
        similarity = 0
        similar_field = ''
        for str2 in list:            
            doc2 = self._nlp(str2.lower().replace('_', ' ').replace('.', ' '))
            new_similarity = doc1.similarity(doc2)
            if new_similarity > similarity:
                similarity = new_similarity
                similar_field = str2
        return similar_field


    def field_synonym(self, synonym, replace_dot = True):
        # responsible for the translation of the field to the appropriated column
        try:            
            field = self._query_specific_synonym(synonym)

            #if field is not found, use the word vector similarity to find the closest one
            if not field:
                synonym_list = self._query_all_synonyms()                
                synonym = self._find_by_similarity(synonym, synonym_list)
                field = self._query_specific_synonym(synonym)

            if replace_dot:
                field = field.replace('.', '_')
            return field
        except Exception as e:
            print('Exception: No field found, returning synonym. ({})'.format(e))
            return synonym

    def _get_fields_in_sql(self, sql, regex, sql_list_position, group_num, separator):
        try:
            sql_list = sql.split('\n')
            result = re.search(regex, sql_list[sql_list_position], re.IGNORECASE|re.MULTILINE)        
            fields_str = result.group(group_num)
            fields = list(dict.fromkeys([x.strip() for x in fields_str.split(separator)]))
            return fields, result, sql_list
        except:
            return [], '', []     

    def _change_select(self, sql, columns):
        fields, result, sql_list = self._get_fields_in_sql(sql, '(SELECT )(DISTINCT )*(.*)$', 0, 3, ',')
        all_fields = []
        transformed_fields = []        
        columns_dict = {x[0] : x[1] for x in columns}
        nlidb_aggregation_exceptions = []
        group_by_fields = []
        if   glamorise.config_glamorise_interface.get('nlidb_aggregation_exceptions'):
             nlidb_aggregation_exceptions = [field.lower() for field in   glamorise.config_glamorise_interface['nlidb_aggregation_exceptions']]
        for field in fields:            
            if field not in all_fields:            
                all_fields.append(field)                    
                field_without_table = field[field.find('.')+1:]
                if   glamorise.config_glamorise_interface.get('nlidb_aggregation') and   glamorise.config_glamorise_interface['nlidb_aggregation'] \
                and columns_dict[field_without_table] in ['REAL', 'INTEGER'] \
                and field.lower() not in nlidb_aggregation_exceptions:
                    transformed_fields.append('sum(' + field + ') as ' + field.replace('.', '_').replace('(', '_').replace(')', ''))
                else:    
                    transformed_fields.append(field + ' as ' + field.replace('.', '_').replace('(', '_').replace(')', ''))
                    group_by_fields.append(field)
        result_group_1 = self.check_none_values(result.group(1))
        result_group_2 = self.check_none_values(result.group(2))
        sql = result_group_1 + result_group_2 + ', '.join(transformed_fields) + '\n'
        for i in range(1, len(sql_list)):
            sql += sql_list[i] + '\n'
        if glamorise.config_glamorise_interface.get('nlidb_aggregation') and glamorise.config_glamorise_interface['nlidb_aggregation'] and group_by_fields:
            sql += 'GROUP BY ' + ', '.join(group_by_fields) + '\n'
        sql = sql[:-1]
        return sql           


    @abc.abstractmethod
    def execute_query(self, nlq, timer_nlidb_execution_first_and_second_attempt, timer_nlidb_execution_third_attempt, timer_nlidb_json_result_set, nlidb_attempt_level, fields):
        pass
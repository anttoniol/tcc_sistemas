from simple_sqlite import SimpleSQLite
from nlidb_mock import NlidbMock
from nlidb_nalir import NlidbNalir
from nlidb_danke import NlidDanke
from glamorise import Glamorise
from copy import deepcopy


# this child class is aware of the NLIDB
# the implementation has to be changed to contemplate new NLIDBs
class GlamoriseNlidb(Glamorise):

    def __init__(self, lang="pt_core_news_md", NLIDB='Mock', config_glamorise_param='',
                 config_glamorise_interface_param='', config_db='', tokens=''):
        super(GlamoriseNlidb, self).__init__(lang, config_glamorise_param=config_glamorise_param,
                                             config_glamorise_interface_param=config_glamorise_interface_param)
        # customize as needed customize as needed according to integration with other NLIDBs.
        # Don't forget to create the specific class for NLIDB following the model of NalirNlid

        # NLIDB instance
        if NLIDB == 'Mock':
            self.__nlidb = NlidbMock()
        elif NLIDB == 'NaLIR':
            self.__nlidb = NlidbNalir(config_db, tokens)
        elif NLIDB == 'Danke':
            self.__nlidb = NlidDanke()

            #
        # add more NLIDBs here
        #

        self._nlidb_interface_sql = ''
        self._nlidb_interface_first_attempt_sql = ''
        self._nlidb_interface_second_attempt_sql = ''
        self._nlidb_interface_third_attempt_sql = ''

    @property
    def nlidb_interface_sql(self):
        return self._nlidb_interface_sql

    @property
    def nlidb_interface_first_attempt_sql(self):
        return self._nlidb_interface_first_attempt_sql

    @property
    def nlidb_interface_second_attempt_sql(self):
        return self._nlidb_interface_second_attempt_sql

    @property
    def nlidb_interface_third_attempt_sql(self):
        return self._nlidb_interface_third_attempt_sql

    def _nlidb_interface(self):
        # danke first execute query then _translate_all_fields
        if isinstance(self.__nlidb, NlidDanke):
            columns, result_set, self._nlidb_interface_sql = self.__nlidb.execute_query(self.pre_prepared_query,
                                                                                        self._timer_nlidb_execution_first_and_second_attempt,
                                                                                        self._timer_nlidb_json_result_set)
            self._translate_all_fields()
            return columns, result_set
            # the field translation is done by the child class that is aware of the NLIDB column names
        self._translate_all_fields()
        if self._config_glamorise_interface.get('nlidb_nlq_translate_fields') and self._config_glamorise_interface[
            'nlidb_nlq_translate_fields']:
            self._nlidb_nlq_translate_fields()
        # send the NLQ question and receive the JSON with the columns and result set
        nlidb_attempt_level = 1
        if self._config_glamorise_interface.get('nlidb_attempt_level'):
            nlidb_attempt_level = self._config_glamorise_interface['nlidb_attempt_level']
            # customize as needed customize as needed according to integration with other NLIDBs.
        # Don't forget to create the specific class for NLIDB following the model of NlidbNalir

        if isinstance(self.__nlidb, NlidbMock):
            columns, result_set, self._nlidb_interface_sql = self.__nlidb.execute_query(self.pre_prepared_query,
                                                                                        self._timer_nlidb_execution_first_and_second_attempt,
                                                                                        self._timer_nlidb_json_result_set)
        elif isinstance(self.__nlidb, NlidbNalir):
            columns, result_set, self._nlidb_interface_sql, self._nlidb_interface_first_attempt_sql, \
            self._nlidb_interface_second_attempt_sql, self._nlidb_interface_third_attempt_sql = self.__nlidb.execute_query(
                self.pre_prepared_query,
                self._timer_nlidb_execution_first_and_second_attempt,
                self._timer_nlidb_execution_third_attempt,
                self._timer_nlidb_json_result_set,
                nlidb_attempt_level,
                self._all_fields)

        #
        # add more NLIDBs here
        #

        else:
            columns = result_set = None

        return columns, result_set

    def _nlidb_nlq_translate_fields(self):
        self._pre_prepared_query_before_field_translation = self._pre_prepared_query
        self._pre_prepared_query, self._nlidb_interface_fields = self.__nlidb.translate_all_field_synonyms_in_nlq(
            self._pre_prepared_query, self._nlidb_interface_fields)

    def _translate_fields(self, fields, replace_dot=True):
        fields = deepcopy(fields)
        # translate the field to the appropriate column name
        for i in range(len(fields)):
            # ask the NLIDB for the appropriate column name
            fields[i] = self.__nlidb.field_synonym(fields[i], replace_dot)
        # the trick to convert fields that were converted to more than one column
        # E.g.: month -> year,month
        if fields:
            fields_str = ','.join(fields)
            fields = fields_str.split(',')
            fields = [field.strip() for field in fields]
        return fields

    def _translate_all_fields(self):
        # prepare a set with all fields identified by GLAMORISE to help the NLIDB to improve the SQL
        self._all_fields = list(dict.fromkeys(self._nlidb_interface_fields +
                                              self._translate_fields(self._pre_aggregation_fields, replace_dot=False) +
                                              self._translate_fields(self._pre_group_by_fields, replace_dot=False) +
                                              self._translate_fields(self._pre_subquery_aggregation_fields,
                                                                     replace_dot=False) +
                                              self._translate_fields(self._pre_subquery_group_by_fields,
                                                                     replace_dot=False) +
                                              self._translate_fields(self._pre_having_fields, replace_dot=False)))

        # translate all fields that GLAMORISE is aware of
        self._pre_aggregation_fields = self._translate_fields(self._pre_aggregation_fields)
        self._pre_group_by_fields = self._translate_fields(self._pre_group_by_fields)
        self._pre_subquery_aggregation_fields = self._translate_fields(self._pre_subquery_aggregation_fields)
        self._pre_subquery_group_by_fields = self._translate_fields(self._pre_subquery_group_by_fields)
        self._pre_having_fields = self._translate_fields(self._pre_having_fields)





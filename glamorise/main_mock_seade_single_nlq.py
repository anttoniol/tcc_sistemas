#
# Developed by Alexandre Novello (PUC-Rio) and adapted to Portuguese by Antônio Carlos Santos de Lima (USP)
#

from glamorise_nlidb import GlamoriseNlidb
import main_common as mc

with open('./config/environment/glamorise_mock.json') as json_file:
    config_glamorise = json_file.read()

with open('./config/environment/glamorise_interface_mock_danke_anp.json') as json_file:
    config_glamorise_interface = json_file.read()

glamorise = GlamoriseNlidb(config_glamorise_param = config_glamorise, config_glamorise_interface_param = config_glamorise_interface)
    
nlq = 'retorne o max da idade dos pacientes do município de "São Bernardo do Campo".'
mc.print_results(glamorise, nlq)

mc.print_total_timers()
del glamorise

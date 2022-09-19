#
# Originally Developed by Alexandre Novello (PUC-Rio) and adapted to Portuguese by Antônio Carlos Santos de Lima (USP)
#

from glamorise_nlidb import GlamoriseNlidb
import main_common as mc
from xml.etree.ElementTree import fromstring

with open('config/environment/nalir_tokens_adapted.xml') as xml_file:
    nalir_tokens = xml_file.read()
    nalir_tokens = fromstring(nalir_tokens)

with open('./config/environment/nalir_seade_db.json') as json_file:
    config_db = json_file.read()

with open('config/environment/glamorise_nalir_adapted.json') as json_file:
    config_glamorise = json_file.read()

with open('./config/environment/glamorise_interface_nalir_seade.json') as json_file:
    config_glamorise_interface = json_file.read()

nlqs = [
    # Sem agregações e sem cláusula 'WHERE'
    "retorne todos os municípios em casos",

    # Sem agregações e com cláusula 'WHERE'
    "retorne todas as idades dos casos onde o município é São Paulo",
    "retorne todas as idades dos casos do município de São Paulo",

    # Agregações sem agrupamentos e sem cláusula 'WHERE'
    "devolva quantos óbitos existem em casos",
    "Devolva quantos casos há",
    "devolva a máxima idade em casos",
    "devolva a mínima idade em casos",
    "devolva as idades somadas em casos",
    "devolva a idade média em casos",

    # Agregações sem agrupamentos e com cláusula 'WHERE'
    "devolva quantos óbitos do tipo positivo existem em casos",
    "devolva quantos óbitos do tipo positivo onde o município é São Paulo",
    "devolva quantos óbitos do tipo positivo há no município de São Paulo",

    "devolva a máxima idade no município de São Paulo",
    "devolva a mínima idade no município de São Paulo",
    "devolva as idades somadas no município de São Paulo",
    "devolva a idade média no município de São Paulo",

    # Agregações com agrupamentos e sem cláusula 'WHERE'
    "devolva quantos casos há por município",
    "devolva a máxima idade por município",
    "devolva a mínima idade por município",
    "devolva as idades somadas por município",
    "devolva a idade média por município",

    # Agregações com agrupamentos e com cláusula 'WHERE'
    "devolva quantos óbitos do tipo positivo há no município de São Paulo por raça",
    "devolva a máxima idade no município de São Paulo por raça",
    "devolva a mínima idade no município de São Paulo por raça",
    "devolva as idades somadas no município de São Paulo por raça",
    "devolva a idade média no município de São Paulo por raça",

    "devolva quantos óbitos do tipo positivo há no município de São Paulo por diagnóstico",
    "devolva quantos diagnóstico há agrupados por raça e por sexo e por diagnóstico",
    "devolva a máxima idade no município de São Paulo por diagnóstico",
    "devolva a mínima idade no município de São Paulo por diagnóstico",
    "devolva as idades somadas no município de São Paulo por diagnóstico",
    "devolva a idade média no município de São Paulo por diagnóstico"
]

extension = ".html"
skip = "</br>"

size = len(nlqs)
for i in range(size):
    # create GLAMORISE object (the child class is instantiated)
    glamorise = GlamoriseNlidb(NLIDB='NaLIR', config_glamorise_param=config_glamorise,
                               config_glamorise_interface_param=config_glamorise_interface, config_db=config_db,
                               tokens=nalir_tokens)
    file = open("outputs/nlqs" + str(i) + extension, "w")
    nlq_str, result, dep, ent = mc.print_results(glamorise, nlqs[i], skip)
    result2 = mc.print_total_timers()

    if extension == ".html":
        file.write('SENTENÇA: ' + nlqs[i] + '</br></br>' + result + glamorise.pd.to_html() + result2)
    elif extension == ".txt":
        file.write('SENTENÇA: ' + nlqs[i] + '\n\n' + result + glamorise.pd.to_string() + result2)

    file.close()
    del glamorise


# Adaptação para a língua portuguesa de ferramentas text-to-SQL

Este repositório contém o código relacionado ao trabalho de
conclusão de curso descrito [aqui](https://www.linux.ime.usp.br/~anttonio/mac0499/).

# Instruções para utilização do repositório

# Configurar MySQL

1. Instalar o MySQL: https://dev.mysql.com/doc/mysql-apt-repo-quick-guide/en/
2. No MySQL, criar um usuário root com senha igual a "root"
3. Executar o comando `mysql -p -u root seade < seade.sql`

# Configurar outros programas e pacotes

1. Instalar o Python 3.10: https://www.python.org/downloads/
2. Instalar/atualizar os seguintes pacotes, sem utilizar o comando pip3 -r requirements.txt:
    1. pip (versão 22.1.2)
    2. setuptools (versão 62.6.0)
    3. wheel (versão 0.37.1)
3. Executar os comandos: 
	1. `sudo apt-get install python3-mysql.connector`
   	2. `python3 -m nltk.downloader popular` 
4. Alterar os campos "zfiles_path" e "jars_path" no arquivo "tcc_sistemas/glamorise/config/environment/nalir_seade_db.json", 
e os campos "nalir_relative_path" e "glamorise_relative_path" no arquivo "tcc_sistemas/glamorise/config/environment/path.json", 
para o caminho ser válido na máquina de quem está rodando este projeto.
5. Criar e ativar um ambiente virtual, conforme explicado em: https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/#creating-a-virtual-environment
6. Acessar o diretório "/tcc_sistemas" e executar o comando `pip3 install -r requirements.txt`
7. No diretório "tcc_sistemas/glamorise", executar o comando `python3 main_nalir_seade_single_nlq.py` 



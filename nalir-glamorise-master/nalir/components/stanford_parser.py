import os
from copy import deepcopy

from nltk.parse.stanford import StanfordDependencyParser as STDParser
from nltk.parse.stanford import StanfordParser as STParser
import spacy

from ..data_structure.parse_tree import ParseTree

ID_IDX = 0
WORD_IDX = 1
POSTAG_IDX = 2
PARENT_IDX = 3
PARENT_WORD = 4

nlp = spacy.load('pt_core_news_md')


class StanfordParser:
    def print_tree_table(self, query):
        print("\nTree Table:\n")
        for value in query.tree_table:
            print(value)
        print("")

    def __init__(self,query,config):
        jars_path = config.jars_path

        os.environ['STANFORD_PARSER'] = jars_path
        os.environ['STANFORD_MODELS'] = jars_path
        os.environ['CLASSPATH'] = jars_path

        self.parse_adapted(query)
        
        self.build_tree(query)
        self.fix_conj(query)

        self.print_tree_table(query)

        print("Parse Tree:\n")
        print(query.parse_tree)
        print("")

    def get_dependency_list_aux(self, dep, elem, checkedTokens):
        parentTuple = (elem.text, elem.pos_)
        subtree = elem.children
        for token in subtree:
            if token != elem:
                depConn = token.dep_
                tokenTuple = (token.text, token.pos_)
                if (parentTuple, depConn, tokenTuple) not in dep:
                    dep.append((parentTuple, depConn, tokenTuple))
                    self.get_dependency_list_aux(dep, token, checkedTokens)

    def get_dependency_list(self, result):
        dep = []
        checkedTokens = []
        for elem in result:
            if elem not in checkedTokens:
                checkedTokens.append(elem)
                self.get_dependency_list_aux(dep, elem, checkedTokens)
        return dep

    def parse_adapted(self, query):
        text = str(" ".join(query.sentence.output_words))
        result = nlp(text)

        self.map_words = {'ROOT': [0]}
        self.map_words_index = {'ROOT': 0}
        self.parent_index = {}

        for idx in range(len(query.sentence.output_words)):
            if self.map_words.get(query.sentence.output_words[idx], None) is None:
                self.map_words[query.sentence.output_words[idx]] = []
            self.map_words[query.sentence.output_words[idx]] += [idx + 1]
            self.map_words_index[query.sentence.output_words[idx]] = 0

        self.parent_index = deepcopy(self.map_words_index)
        dependency_list = self.get_dependency_list(result)

        dep_root_item = [(('ROOT', 'ROOT'), 'root', dependency_list[0][0])]
        dep_dict = {}

        for item in dep_root_item + dependency_list:
            if dep_dict.get(item[2][0], None) is None:
                dep_dict[item[2][0]] = []
            dep_dict[item[2][0]] += [item]
        tokens = []
        for token in result:
            tokens.append(token)
        lemmas = {}
        for token in tokens:
            lemma = token.lemma_
            if token.dep_ == "ROOT": #and lemma not in dep_dict:
                dep_dict[lemma] = [(('ROOT', 'ROOT'), 'root', lemma)]

        tree_table = []
        for idx in range(len(query.sentence.output_words)):
            word = query.sentence.output_words[idx]

            real_idx = idx + 1

            idx_dep = self.map_words_index[word]

            try:
                dependency = dep_dict[word][idx_dep]
            except:
                doc = nlp(word)
                lemma = str(doc[0].lemma_)
                dependency = dep_dict[lemma][idx_dep]
            relation = dependency[1]
            tag = dependency[2][1]
            parent_word = dependency[0][0]
            parent_idx = self.parent_index[word]
            parent_word_idx = self.map_words[parent_word][0]  # STRONGLY ASSUMPTION
            tree_table_item = [real_idx, word, tag, parent_word_idx, parent_word, relation] # word.replace('_', ' ')
            tree_table += [tree_table_item]
            if relation.lower().startswith('conj'):
                query.conj_table += [str(parent_word_idx) + ' ' + str(real_idx)]

            self.map_words_index[word] = idx_dep + 1
            self.parent_index[word] = parent_idx + 1

        query.tree_table = tree_table

    def parse(self,query):
        self.depParser = STDParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")
        self.parser = STParser(model_path="edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz")

        result = self.depParser.parse_sents([query.sentence.output_words])

        self.map_words = { 'ROOT' :  [0] }
        self.map_words_index = {'ROOT': 0 }
        self.parent_index = {}

        for idx in range(len(query.sentence.output_words)):
            if self.map_words.get(query.sentence.output_words[idx], None) is None:
                self.map_words[query.sentence.output_words[idx]] = []
            self.map_words[query.sentence.output_words[idx]] += [idx + 1]
            self.map_words_index[query.sentence.output_words[idx]] = 0

        
        self.parent_index = deepcopy(self.map_words_index)
        item = next(result)
        dep = next(item)

        self.tree = dep.tree()
        dependency_list =  list(dep.triples())
        dep_root_item = [(('ROOT', 'ROOT'),'root',dependency_list[0][0])]
        dep_dict = {}

        for item in dep_root_item + dependency_list:
            
            process_items = [item[0], item[2]]

            if dep_dict.get(item[2][0], None) is None:
                dep_dict[item[2][0]] = []
            dep_dict[item[2][0]] += [item]

        tree_table = []
        #treeTable[0] = (1, )
        #for item in self.
        for idx in range(len(query.sentence.output_words)):
            real_idx = idx + 1

            word = query.sentence.output_words[idx]
            idx_dep = self.map_words_index[word]

            dependency = dep_dict[word][idx_dep]
            relation = dependency[1]
            tag = dependency[2][1]

            parent_word = dependency[0][0]
            parent_idx =  self.parent_index[word]
            parent_word_idx = self.map_words[parent_word][0] #STRONGLY ASSUMPTION

            tree_table_item = [real_idx, word.replace('_',' '), tag, parent_word_idx, parent_word, relation]
            tree_table += [tree_table_item]
            

            if relation.lower().startswith('conj'):
                query.conj_table += [str(parent_word_idx)+' '+str(real_idx)]

            self.map_words_index[word] = idx_dep + 1
            self.parent_index[word] = parent_idx + 1

        query.tree_table = tree_table
        

    def build_tree(self,query):
        
        query.parse_tree = ParseTree()
        done_list = [False] * len(query.tree_table)
        i = 0

        for tree_table_item in query.tree_table:
            if tree_table_item[PARENT_IDX] == 0:
                done_list[i] = True
                query.parse_tree.build_node(tree_table_item)
            i+=1

        finished = False
        while not finished:
            i = 0
            for i in range(len(query.tree_table)):
                if not done_list[i]:
                    if query.parse_tree.build_node(query.tree_table[i]):
                        done_list[i] = True
                        break

            finished = True
            for done_list_item in done_list:
                if not done_list_item:
                    finished = False
                    break

    def fix_conj(self, query):
        
        if len(query.conj_table) == 0:
            return
        i = 0
        
        for conj_table_item in query.conj_table:
            numbers = conj_table_item.split(' ')
            gov_idx = int(numbers[0])
            dep_idx = int(numbers[1])
            gov_node = query.parse_tree.search_node_by_order(gov_idx)
            dep_node = query.parse_tree.search_node_by_order(dep_idx)
            logic = ','

            if query.parse_tree.search_node_by_order(dep_node.word_order-1) is not None:
                logic = query.parse_tree.search_node_by_order(dep_node.word_order-1).label

            if logic.lower() == 'ou':
                query.conj_table[i] = query.conj_table[i]
                dep_node.left_rel = 'ou'
                for j in range(len(gov_node.parent.children)):
                    if gov_node.parent.children[j].left_rel == ',':
                        gov_node.parent.children[j].left_rel = 'ou'

            elif logic.lower() == 'e' or logic.lower() == 'mas':
                query.conj_table[i] = query.conj_table[i]
                dep_node.left_rel = 'e'

                for j in range(len(gov_node.parent.children)):
                    if gov_node.parent.children[j] == ',':
                        gov_node.parent.children[j].left_rel = 'e'

            elif logic.lower() == ',':
                dep_node.left_rel = ','

            dep_node.parent = gov_node.parent
            gov_node.parent.children += [dep_node]
            gov_node.children.remove(dep_node)
            dep_node.relationship = gov_node.relationship
            i+=1

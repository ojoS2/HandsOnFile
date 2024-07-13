###############################################

###############################################
####  translation and text verification     ###
###############################################

###############################################

import language_tool_python as ltp
import deep_translator as dt
import re
from canivete import filter_matches_portugues, filter_matches_english, get_LaTex_sintaxe, get_flags_back

def init_engines(engine=None):
    if engine is None:
        return ltp.LanguageTool('en-US'), ltp.LanguageTool('pt-BR')
    elif engine == 'en':
        return ltp.LanguageTool('en-US')
    elif engine == 'pt':
        return ltp.LanguageTool('pt-BR')
    else:
        print("Opção não conhecida.\n\t Digite en para inglês (US) \n\t Digite pt para português (Br) \n\t ou None para ambos\n")
        engine = input('')
        return init_engines(engine)


def sentences_checking(engine, text):
    correct = engine.correct(text)
    return correct

def select_translation_rules(engine, string, mode = 'en'):
    matches = engine.check(string)
    if mode == 'en':
        return [rule for rule in matches if not filter_matches_english(rule)]
    elif mode == 'pt':
        return [rule for rule in matches if not filter_matches_portugues(rule)]
    else:
        print("Opção desconhecida para o argumento mode!\n\t digite en para inglês \n\t ou pt para português")
        mode = input('')
        return select_translation_rules(engine, string, mode)

def text_checking(text, engine, mode = 'en'):
    return ltp.utils.correct(text, select_translation_rules(engine = engine,
                                                            string = text,
                                                            mode = mode))

def port_checking(text, engine):
    return ltp.utils.correct(text, select_translation_rules(engine = engine,
                                                            string = text,
                                                            mode = 'pt'))

def engl_checking(text, engine):
    return ltp.utils.correct(text, select_translation_rules(engine = engine,
                                                            string = text,
                                                            mode = 'en'))

def translate_snippet(text, language = 'pt'):
    translated = dt.GoogleTranslator(source='auto', target=language).translate(text)
    return translated

def process_LaTex_list(text_list):
        text = []
        for item in text_list:
            if ('\chapter' in item) or ('\label' in item) or ('\\footnote' in item):
                temp = re.findall(r'\{(.*?)\}', item)[0]
                try:
                    item = re.sub(r'\{(.*?)\}', '{' + port_checking(translate_snippet(temp)) + '}', item)
                except:
                    pass
                item.replace('\{', '{')
                item.replace('\}', '}')
                text.append(item)
            elif '\par' in item:
                text.append('\n' + item + '\n')
            else:
                item.replace('\{', '{')
                item.replace('\}', '}')
                try:
                    item = re.sub(r'(\\color{blue} \d+)', r'{\1}', item)
                except:
                    pass
                text.append(item)
            
        return text

def translate(text, processed_LaTex, engine):
    text = re.sub("([A-Z])\.", r"\1aaa", text)
    text_list = text.split('\n999999\n')
    overall_list = []
    for text in text_list:
        if len(text) > 0:
            text = text.replace('aaa', '.')
            overall_list.append(port_checking(engine = engine, text = translate_snippet(text)))
        else:
            overall_list.append(' ')   
    processed_text = ''
    for text in overall_list:
        processed_text = processed_text + text + '\n999999\n'
    corpus = get_flags_back(data = processed_text,
                            saved_lists = [processed_LaTex],
                            flags_list = ['999999'])
    
    return corpus#processed_text, bag_3_wrd, bag_2_wrd, bag_1_wrd, bag_0_wrd

def test_trans(path, engine):
#path = '/home/ricardo/Documents/CienciaDeDados/TraducoesProject/teste.tex'
    with open(path, 'r') as file:
        data = file.read()
        data, LaTex_list = get_LaTex_sintaxe(data)
        processed_LaTex = process_LaTex_list(LaTex_list)
        #preprocessed_text, bag_wrd_3, bag_wrd_2, bag_wrd_1, bag_wrd_0 = get_names(data, processed_LaTex)
        #corpus = get_names(data, processed_LaTex)
        corpus = translate(text = data, processed_LaTex = processed_LaTex, engine = engine)
    return corpus    



###############################################
#### some helping tools #######################
###############################################
# ferramentas últeis em diversos contextos

import re

def seq(init, end):
    """
    Uma função simples que retorna uma sequencia de inteiros.
    Apresenta dois argumentos:

    init, an integer. Marca o começo a sequencia (inclusivo)
    
    end, an integre. Marca o término da sequencia (inclusivo)

    retorna a sequencia natural entre init e end incluso
    """
    return [i for i in range(init, end + 1)]

def splitstring(s, w):
    '''
        Uma função simples que divide uma string em pedaços de no máximo um
    dado valor. toma dois valores e retorna uma lista.

    s, a string. O string a ser dividido

    w, an integer. O numero maximo de caracteres para os itens da lista

    retorna o string dividido em uma lista de pedaços de no máximo tamanho w
    '''
    return [s[i:i + w] for i in range(0, len(s), w)]

def print_to_file(path_to_save, string):
    '''
        Função simples que toma um string e salva num arquivo. Não retorna nada.
    
    path_to_save, a string. O endereço em que o string será salvo

    string, a string. O string a ser salvo em um arquivo
    '''
    with open(path_to_save, "w") as text_file:
        text_file.write(string)
        text_file.close()
    return None

def cleaning_with_regex(string):
    '''
        Uma função simples que faz correções especificas usando regex.

        args: string, un string. o String a ser corrigido

        retorna o string corrigido
    '''
    #Limpando titulos do tipo [A B C D]
    string = re.sub(r'[A-Z]\s[A-Z]\s[A-Z]+', '', string)
    # Limpando numeros como 9 8 0 9 8
    string = re.sub(r'[0-9]\s[0-9]\s[0-9]+', '', string)
    #transformando sentenças do tipo aAa em aaa 
    string = re.sub("([a-z])([A-Z])([a-z])", lambda pat: (pat.group(1) + ' ' + pat.group(2).lower() + pat.group(3)), string)
    #transformando sentenças do tipo a.Aa em a. \n A 
    string = re.sub("([a-z])([.!?])([A-Z])", r"\1 \2 \n \3", string)
    #transformando sentenças do tipo a-A em aa
    string = re.sub("([a-z])-([A-Z])", lambda pat: (pat.group(1) + pat.group(2).lower()), string)
    #transformando sentenças do tipo a- a em aa
    string = re.sub("([a-z])-\s+([a-z])", r'\1\2', string)

def build_string_vectors():
    '''
        Esta função simples cria iterativamente vetores de paragrafos para serem 
    ajeitados como citações ou notas de rodapé. Não recebe argumentos e retorna 
    dois vetores de strings que contém flags dos textos a serem destacados.

    returns: citation_vec, um vetor de strings com tamanho mínimo de 20 caracteres que 
    caracterizam o começo das frases a serem destacadas.
    
    returns: footnote_vec, um vetor de strings com tamanho mínimo de 20 caracteres que 
    caracterizam o começo das frases a serem destacadas.
    '''
    citation_vec = []
    footnote_vec = []
    pfl_size = 20
    print("Iniciando vetor de citações.\n")
    temp = input("Entre com as primeiras palavras do texto a ser cunhado como citação\
                  (pelo menos {x} caracteres) ou digite 'quit' para sair\n".format(x = pfl_size))
    while temp != 'quit':
        if len(temp) < pfl_size:
            print("frase com poucos caracteres, tente outra vez.\n")
        else:
            citation_vec.append(temp[0:pfl_size])
        temp = input("Entre com as primeiras palavras do texto a ser cunhado como citação\
                  (pelo menos {x} caracteres) ou digite 'quit' para sair\n".format(x = pfl_size))
    print("Encerrando vetor de citações e iniciando vetor de notas de rodapé.\n")
    temp = input("Entre com as primeiras palavras do texto a ser cunhado como nota de rodapé\
                  (pelo menos {x} caracteres) ou digite 'quit' para sair\n".format(x = pfl_size))
    while temp != 'quit':
        if len(temp) < pfl_size:
            print("frase com poucos caracteres, tente outra vez.\n")
        else:
            footnote_vec.append(temp[0:pfl_size])
        temp = input("Entre com as primeiras palavras do texto a ser cunhado como citação\
                  (pelo menos {x} caracteres) ou digite 'quit' para sair\n".format(x = pfl_size))
    return citation_vec, footnote_vec

def build_chapter_pages_vector():
    '''
        Esta função simples cria iterativamente vetores de numeros das
    páginas pelos quais serão divididos os capitulos do livro. Não recebe
    argumentos e retorna  uma tupla de numeros inteiros
    '''
    beginning = []
    ending = []
    epigraph = []
    print("Iniciando coleta de páginas.\n")
    beg_temp = input("Insira a página em que se inicializa o capitulo a ser adicionado (a pagina 0\
           é contada, logo a pagina x do pdf deve ser considerada como numero x-1) ou aperte [Enter]\
           para sair.\n")
    end_temp = input("Insira a página em que se finaliza o capitulo a ser adicionado (a pagina 0\
           é contada, logo a pagina x do pdf deve ser considerada como numero x-1) ou aperte [Enter]\
           para sair.\n")
    epi_temp = input("Insira 'True' se o capitulo tem uma citação inicial ou 'False' caso contrário.\n")
    while len(beg_temp) > 0 and len(end_temp) > 0:
        beginning.append(int(beg_temp))
        ending.append(int(end_temp))
        epigraph.append(bool(epi_temp))
        beg_temp = input("Insira a página em que se inicializa o capitulo a ser adicionado (a pagina 0\
           é contada, logo a pagina x do pdf deve ser considerada como numero x-1) ou aperte [Enter]\
           para sair.\n")
        while not beg_temp.isnumeric():
            beg_temp = input("Opção não reconhecida, tente novamente\n.")
        end_temp = input("Insira a página em que se finaliza o capitulo a ser adicionado (a pagina 0\
           é contada, logo a pagina x do pdf deve ser considerada como numero x-1) ou aperte [Enter]\
           para sair.\n")
        while not end_temp.isnumeric():
            end_temp = input("Opção não reconhecida, tente novamente\n.")
        epi_temp = bool(input("Insira 'True' se o capitulo tem uma citação inicial ou 'False' caso contrário.\n"))

    return zip(beginning, ending, epigraph)

def capa_manual_input():
    '''
        Função simples para entrar manualmnete com os dados da capa.
    Não recebe argumentos e retorna quatro strings'''

    autor = input("Entre com os autores da obra.\n")
    assunto = input("Entre com o assunto da obra.\n")
    titulo = input("Entre com o título da obra.\n")
    sub_titulo = input("Entre com o subtitulo da obra.\n")
    return autor, assunto, titulo, sub_titulo

def include_citations(corpus, ref_list):
    """
        A simple function that uses regex to input back LaTex keywords in the text. It returns the corrected sentence
    args: corpus, a string. O texto em que se deseja recolocar as palavras chave
    args: ref_list, a list of strings. Uma lista de keywords a serem incluidas no texto
    returns: corpus. A sentença corrigida.
    """
    text_list = corpus.split('XXXXXX')
    corpus = ''
    for text, ref in zip(text_list, ref_list):
        corpus = corpus + text + ' ' + ref + ' '
    return corpus

def filter_matches_portugues(rule):
    '''Filtro simples dos erros ortográficos a serem ignorados, como por exemplo a correção de nomes próprios.'''
    return rule.message == 'Encontrado possível erro de ortografia.' and len(rule.replacements) and rule.replacements[0][0].isupper()

def filter_matches_english(rule):
    '''Filtro simples dos erros ortográficos a serem ignorados, como por exemplo a correção de nomes próprios.'''
    return rule.message == 'Possible spelling mistake found.' and len(rule.replacements) and rule.replacements[0][0].isupper()

def get_LaTex_sintaxe(data):
    '''
        Função simples que resguarda as palavras-chave da linguagem LaTex além de trechos que não serão
    traduzidos.

    args: data, a string. O texto a ser processado

    returns  data, a string. O texto processado
     
    returns LaTex_list, uma lista de strings. A lista de palavras-chave extraída do texto
    '''
    flag_open = 0
    get = True
    temp = ''
    for char in data:
        if char == '{':
            flag_open = flag_open + 1
            if get:
                temp += 'XXB'
                get = False
            else:
                temp +='{'
        elif char == '}':
            flag_open = flag_open - 1
            if flag_open == 0:
                temp +='XXE'
                get = True
            else:
                temp +='}'
        else:
            temp += char
    LaTex_list = re.findall(r'XXB(.*?)XXE', temp)
    data = re.sub(r'XXB(.*?)XXE', "\n999999\n", temp)
    
    return data, LaTex_list 

def strip_init_space(txt):
    """Extrair espaços à esquerda"""
    return txt.lstrip()

def strip_init_tab(txt):
    """Extrair o caracter \t à esquerda"""
    return txt.lstrip('\t')

def strip_init_nl(txt):
    """Extrair o caracter \n à esquerda"""
    return txt.lstrip('\n')

def get_names(text):
    '''
        Essa função divide um texto em frases e substitui nas frases nomes próprios de até três elementos,
        siglas e nomes abreviados por palavras-chave que escapam a tradução.'''
    text = re.sub("([A-Z])\.", r"\1aaa", text)
    text_list = text.split('\n999999\n')
    bag_3_wrd = []
    bag_2_wrd = []
    bag_1_wrd = []
    bag_0_wrd = []
    overall_list = []
    for text in text_list:
        if len(text) > 0:
            punctuation_list = re.findall('[.!?]', text) 
            raw_phrase_list = re.split('[.!?]', text)
            raw_phrase_list = map(strip_init_space, raw_phrase_list)
            raw_phrase_list = map(strip_init_tab, raw_phrase_list)
            raw_phrase_list = map(strip_init_nl, raw_phrase_list)
            treated_phrase_list = []
            for phrase in raw_phrase_list:
                if len(phrase) == 0:
                    treated_phrase_list.append(' ')
                    continue
                else:
                    bag_3_wrd.append(re.findall(r"(?<!^)[A-Z][a-z]+\s[A-Z][a-z]+\s[A-Z][a-z]+", phrase))#([\.,-]?)
                    phrase = re.sub(r"(?<!^)[A-Z][a-z]+\s[A-Z][a-z]+\s[A-Z][a-z]+", r"XXXX3", phrase)
                    bag_2_wrd.append(re.findall(r"(?<!^)[A-Z][a-z]+\s[A-Z][a-z]+", phrase))
                    phrase = re.sub(r"(?<!^)[A-Z][a-z]+\s[A-Z][a-z]+", r"XXXX2", phrase)
                    bag_1_wrd.append(re.findall(r"(?<!^)[A-Z][a-z]+", phrase))
                    phrase = re.sub(r"(?<!^)[A-Z][a-z]+", r"XXXX1", phrase)
                    bag_0_wrd.append(re.findall("[A-Z]{2,}[\s\.]", phrase))
                    phrase = re.sub("[A-Z]{2,}([\s\.])", r"XXXX0\1", phrase)
                    treated_phrase_list.append(phrase)
            processed_text = ''
            for text, punctuation in zip(treated_phrase_list, punctuation_list):
                processed_text = processed_text + text + punctuation + ' '
            overall_list.append(processed_text)
        else:
            overall_list.append(' ')
            continue
    processed_text = ''
    for text in overall_list:
        processed_text = processed_text + text + '\n999999\n'
    return processed_text, bag_3_wrd, bag_2_wrd, bag_1_wrd, bag_0_wrd

def reenter_lists(corpus, reference_list, to_split):
    temp = ''
    split = corpus.split(to_split)
    idx = 0
    for main, to_introduce in zip(split, reference_list):
        if main == '' or main == []:
            main = ' '
        temp = temp + main + ' ' + to_introduce + ' '
        idx = idx + 1
    if len(split) > idx:
        temp = temp + ' ' + to_split.join(split[idx:])
    return temp

def get_flags_back(data, saved_lists, flags_list):
    data.replace('aaa', '.')
    for flag, list in zip(flags_list, saved_lists):
        if any(list):
            data = reenter_lists(data, reference_list = list, to_split = flag)
    return data

def naive_refence(string):
    if string is None or len(string) == 0:
        return ''
    new = re.sub(r'([\s\.])(\d{1})([\s\.\)])', r'\1{\\color{blue}\2}\3', string)
    new = re.sub(r'([\s\.”\t])\s*(\d{1})$', r'\1{\\color{blue}\2}', new)
    new = re.sub(r'([\s\.])(\d{2})([\s\.\)])', r'\1{\\color{blue}\2}\3', new)
    new = re.sub(r'([\s\.”\t])\s*(\d{2})$', r'\1{\\color{blue}\2}', new)
    new = re.sub(r'([\s\.])(\d{3})([\s\.\)])', r'\1{\\color{blue}\2}\3', new)
    new = re.sub(r'([\s\.”\t])\s*(\d{3})$', r'\1{\\color{blue}\2}', new)
    # not taken references
    new = re.sub(r'([\.”])\s*(\d+)\s*\}', r'\1 {\\color{blue} \2 } }', new)
    new = re.sub(r'([\.”])\s*(\d+)\s*([,A-Z])', r'\1 {\\color{blue} \2 } {\\par} \3', new)
    return new

def generate_simple_pattern(n, to_repeat, end_string = '', capture_all = False):
    if capture_all:
        pattern = '('
        for i in range(n):
            pattern = pattern + to_repeat
        pattern = pattern + end_string + ')'
    else:
        pattern = ''
        for i in range(n):
            pattern = pattern + to_repeat
        pattern = pattern + end_string
    return pattern
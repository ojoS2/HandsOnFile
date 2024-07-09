# Programa para tradução de textos direcionado ao nucleo de TI da UP
# Deve ser capaz de: 
# 1 - extrair informações de um pdf
# 2 - organizar tais informações de forma coerente
# 3 - oferecer traduções de qualidade para estas informações
# 4 - retornar um texto estruturado em LaTex, pronto para compilação com necessidade mínima de correção
#
#
# Principais probelmas encontrados na tradução de textos reais: 
# 1 - problemas na estruturação detalhada do texto. Textos em diferentes fontes ou diferentes
# ajustamentos do texto
# 2 - problemas na junção entre os textos retirados de páginas diferentes 


import unstructured
import language_tool_python as ltp
import deep_translator as dt
import re
import numpy as np
import os
from string import ascii_uppercase, ascii_lowercase
from unstructured.partition.pdf import partition_pdf
from PyPDF2 import PdfWriter, PdfReader
from distutils.dir_util import copy_tree
from shutil import rmtree, copyfile
import textwrap
import awkward as ak


tool_en = ltp.LanguageTool('en-US')
tool_po = ltp.LanguageTool('pt-BR')

book_path = "/home/ricardo/Downloads/The Reactionary Mind_ Conservatism from Edmund Burke to Sarah Palin ( PDFDrive ) (1).pdf"
folder_to_save = "/home/ricardo/Desktop"
rmtree("/home/ricardo/Desktop/teste")
os.mkdir("/home/ricardo/Desktop/teste")
os.mkdir("/home/ricardo/Desktop/teste/sections")
os.mkdir("/home/ricardo/Desktop/teste/sections/transposed")
os.mkdir("/home/ricardo/Desktop/teste/sections/translated")
#os.mkdir("/home/ricardo/Desktop/teste/images")
#os.mkdir("/home/ricardo/Desktop/teste/template")
#os.mkdir("./Docs")
copy_tree("/home/ricardo/Documents/CienciaDeDados/TraducoesProject/latex_str/resources",
          "/home/ricardo/Desktop/teste/resources")
#copy_tree("/home/ricardo/Documents/CienciaDeDados/TraducoesProject/latex_str/images",
#          "/home/ricardo/Desktop/teste/images")
#copy_tree("/home/ricardo/Documents/CienciaDeDados/TraducoesProject/latex_str/template",
#          "/home/ricardo/Desktop/teste/template")
copyfile("/home/ricardo/Documents/CienciaDeDados/TraducoesProject/latex_str/lix.sty",
         "/home/ricardo/Desktop/teste/lix.sty")
copyfile("/home/ricardo/Documents/CienciaDeDados/TraducoesProject/latex_str/main.tex",
         "/home/ricardo/Desktop/teste/main.tex")
copyfile("/home/ricardo/Documents/CienciaDeDados/TraducoesProject/latex_str/novel.cls",
         "/home/ricardo/Desktop/teste/novel.cls")
chapter_path_transposed = "/home/ricardo/Desktop/teste/sections/transposed"
chapter_path_translated = "/home/ricardo/Desktop/teste/sections/translated"
main_path = "/home/ricardo/Desktop/teste"


###############################################
####  helping tools ###########################
###############################################
def seq(init, end):
    """
    Uma função simples que retorna uma sequencia de inteiros.
    Apresenta dois argumentos:

    init, an integer. Marca o começo a sequencia (inclusivo)
    
    end, an integre. MArca o término da sequencia (inclusivo)
    """
    return [i for i in range(init, end + 1)]

def splitstring(s, w):
    '''
        Uma função simples que divide uma string em pedaços de no máximo um
    dado valor. toma dois valores e retorna uma lista.

    s, a string. O string a ser dividido

    w, an integer. O numero maximo de caracteres para os itens da lista
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

def page_eval(path):
    elements = partition_pdf(path)
    test = zip([type(element) for element in elements], [element.text for element in elements])
    for i, j in test:
        print(i, ":", j, '\n')

def cleaning_with_regex(string):
    '''
    '''
    #Limpando titulos do tipo [A B C D]
    string = re.sub(r'[A-Z]\s[A-Z]\s[A-Z]+', '', string)
    string = re.sub(r'[0-9]\s[0-9]\s[0-9]+', '', string)
    #transformando sentenças do tipo aAa em a aa 
    string = re.sub("([a-z])([A-Z])([a-z])", lambda pat: (pat.group(1) + ' ' + pat.group(2).lower() + pat.group(3)), string)
    #transformando sentenças do tipo a.Aa em a. \n\nA 
    string = re.sub("(.)([A-Z])", r"\1 \n\n\2", string)
    #transformando sentenças do tipo a-a em aa
    string = re.sub("([a-z])-([A-Z])", r'\1\2', string)
    #transformando sentenças do tipo a-A em aa
    string = re.sub("([a-z])-([A-Z])", lambda pat: (pat.group(1) + pat.group(2).lower()), string)
    
    return string

def build_string_vectors():
    '''
        Esta função simples cria iterativamente vetores de paragrafos para serem 
    ajeitados como citações ou notas de rodapé. Não recebe argumentos e retorna 
    dois vetores de strings
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
    text_list = corpus.split('XXXXXX')
    corpus = ''
    for text, ref in zip(text_list, ref_list):
        corpus = corpus + text + ' ' + ref + ' '
    return corpus


def filter_matches(rule):
    return rule.message == 'Encontrado possível erro de ortografia.' and len(rule.replacements) and rule.replacements[0][0].isupper()

def select_translation_rules(string):
    matches = tool_po.check(string)
    return [rule for rule in matches if not filter_matches(rule)]


def get_LaTex_sintaxe(data):
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
    return txt.lstrip()

def strip_init_tab(txt):
    return txt.lstrip('\t')

def strip_init_nl(txt):
    return txt.lstrip('\n')

def get_names(text):
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

###############################################

###############################################
####  LaTex writing ###########################
###############################################
def create_context(autor, titulo, sub_titulo, assunto):
    Context = "%===========================================================\n"
    Context = Context + "%               VARIABLES                        \n"
    Context = Context + "%===========================================================\n"
    Context = Context + "\\newcommand{\\AUTHOR}{" + f"{autor}" + "}" + "\n"
    Context = Context + "\\newcommand{\\TITLE}{" + f"{titulo}" + "}" + "\n"
    Context = Context + "\\newcommand{\\SUBTITLE}{" + f"{sub_titulo}" + "}" + "\n"
    Context = Context + "\\newcommand{\\SUBJECT}{" + f"{assunto}" + "}"
    print_to_file(main_path + "context.tex",
                  Context)
    return None

def include_chapter(name, corpus):
    print_to_file(path_to_save = chapter_path_transposed + "/" + name + ".tex", string = corpus)
    return None

def wrap_up_main(include_list):
    
    autor = "Corey Robin"
    titulo = "A mente reacionária"
    sub_titulo = "Conservadorismo: de Edmund Burke até Sarah Palin"
    begining = '\\documentclass{novel}' + '\n' + \
    '\\lang      {portuguese}' + '\n' + \
    '\\title     {' + '{x}'.format(x = titulo) + '}\n' + \
    '\\subtitle  {' + '{x}'.format(x = sub_titulo) + '}\n' + \
    '\\authors   {' + '{x}'.format(x = autor) + '}\n' + \
    '\\cover     {resources/novel_front.pdf}{resources/novel_back.pdf}' + '\n' + \
    '\\license   {CC}{by-nc-sa}{3.0}' + \
    '\\isbn      {--}' + \
    '\\publisher {--}' + \
    '\\edition   {1}{2024}' + \
    "\\dedicate  {para Laura}{--}" + \
    '%\\thank     {Thank you to me for being the best}' + '\n' + \
    '%\\keywords  {fiction, template, packages}' + '\n'

    include = ''
    for item in include_list:
        include = include + '\\input{' + f'{item}' + '}' + '\n'
    ending = '\\end{document}'

    main = begining + include + ending
    print(main)
    print_to_file(main_path + '/main.tex', main)

def build_chap_by_chap(beginings, endings, epigraphs, para_list, foot_list, pfl_size):
    #autor, assunto, titulo, sub_titulo = capa_manual_input()
    autor, assunto, titulo, sub_titulo = "Corey Robin", "Sociologia", "A mente reacionária", "Conservadorismo: de Edmund Burke até Sarah Palin"
    #create_context(autor, titulo, sub_titulo, assunto)
    # Contexto criado, agora implementamos os capitulos
    idx = 0
    cap_list = []
    #for i, j, k in build_chapter_pages_vector():
    for i, j, k in zip(beginings, endings, epigraphs):
        corpus = get_cap_info(path = book_path,
                              beginning = i,
                              ending = j,
                              epigraph = k,
                              translate = True,
                              params_list = para_list,
                              footnote_list = foot_list,
                              pfl_size = pfl_size)
        #corpus = port_checking(corpus)
        print(corpus)
        
        #corpus = cleaning_with_regex(string = corpus)
        #corpus = naive_refence(string = corpus)

        print_to_file(path_to_save = chapter_path_transposed + '/cap_' + str(idx) + '.tex',
                       string = corpus)
        cap_list.append('sections/cap_' + str(idx))
        idx = idx + 1
    # capitulos escritos, agora incluimos as referencias 
    beginning = 263#int(input("Entre com a pagina inicial das referencias:"))
    ending = 293#int(input("Entre com a pagina final das referencias:"))
    corpus = get_refrences(path = book_path,
                           beginning = beginning,
                           ending = ending)
    #corpus = naive_refence(string = corpus)
    #corpus = cleaning_with_regex(string = corpus)

    print_to_file(path_to_save = chapter_path_transposed + '/references.tex',
                       string = corpus)
    cap_list.append('sections/references')
    # capitulos escritos, agora o main 
    wrap_up_main(include_list = cap_list)
    pass

###############################################

###############################################
####  Pdf editing   ###########################
###############################################
def split_doc(doc_path, pages, mode):
    '''
        Uma função simples que divide um documento pdf em páginas ou 
    capitulos e os salva em documentos independentes. Dependendo dos
    valores dos argumentos, retorna uma lista com os caminhos para 
    as páginas extraídas ou o caminho para o capitulo extraído.
    Recebe três argumentos:

    doc_path, a string: o caminho para o documento que se deseja analisar.

    pages, an integer or a list of integers: o numero das páginas a serem
    salvas em documentos cujo nome e número variam conforma a escolha do 
    agumento [mode] apresentado a seguir.

    mode, a string. A modalidade em que se deseja dividir o arquivo. Apresenta
    dois valores possíveis. [page] salva n arquivos onde n é o numero de paginas
    selecionado pelo argumento pages, cada qual portando os dados da respectiva
    página. [chapter] salva um único arquivo contendo n páginas do documento onde
    n é o numero de páginas especificado no argumento [pages]
    '''
    inputpdf = PdfReader(open(doc_path, "rb"))
    pages_path_list = []
    if mode == "page":
        if type(pages) == int:
            output = PdfWriter()
            output.add_page(inputpdf.pages[pages])
            with open("./Docs/document-page%s.pdf" % pages, "wb") as outputStream:
                output.write(outputStream)
                pages_path_list.append("./Docs/document-page%s.pdf" % pages)
        elif type(pages) == list:
            for i in pages:
                output = PdfWriter()
                output.add_page(inputpdf.pages[i])
                with open("./Docs/document-page%s.pdf" % i, "wb") as outputStream:
                    output.write(outputStream)
                    pages_path_list.append("./Docs/document-page%s.pdf" % i)
        else:
            print('split_doc function error page type:', type(pages), "non supported.")    
            return None
        return pages_path_list
    elif mode == 'chapter':
        pages_path_list = []
        output = PdfWriter()
        if type(pages) == list:
            for i in pages:
                output.add_page(inputpdf.pages[i])
        else:
            print('split_doc function error page type:', type(pages), "non supported.")
            print("If the [mode] argument is set to chapter then the [pages] argument must be a list")
            return None
        with open("./Docs/document-chapter.pdf", "wb") as outputStream:
            output.write(outputStream)
            pages_path_list.append("./Docs/document-chapter.pdf")
        return pages_path_list

###############################################

###############################################
####  information extraction     ##############
###############################################
def page_eval(path):
    elements = partition_pdf(path)
    test = zip([type(element) for element in elements], [element.text for element in elements])
    for i, j in test:
        print(i, ":", j, '\n')

def open_page(doc_path, pages_to_open):
    '''
        Função simples que abre um capitulo dividindo-o em páginas salvas em
    aquivos diferentes. Recebe dois argumentos:

    doc_path, a string. O caminho para o documento a ser analisado

    pages_to_open, an integer or a list of integers. A lista de páginas a
    serem abertas 
    '''
    pages_path_list = split_doc(doc_path, pages_to_open, mode='page')

    return pages_path_list

def open_chapter(doc_path, pages_to_open):
    '''
        O mesmo que a função open_page, mas que abre capitulos
    '''
    pages_path_list = split_doc(doc_path, pages_to_open, mode='chapter')

    return pages_path_list

def close_pages(page_to_close, mode):
    '''
        Função simples que deleta um arquivo na pasta ./Docs. Recebe 
    dois argumentos:

    page_to_close, an integer or a list of integers. O identificador da página
    a ser deletada ou uma lista contendo tais identificadores

    mode, a string. O tipo contextual de documento a ser deletado, se for page
    deleta páginas, se for chapter deleta capitulos
    '''
    if mode == 'page':
        if type(page_to_close) == int:
            os.remove("./Docs/document-page%s.pdf" % page_to_close)
        elif type(page_to_close) == list:
            for i in page_to_close:
                os.remove("./Docs/document-page%s.pdf" % i)
    elif mode == 'chapter':
        print("Aviso. É possível abrir e fechar apenas um capitulo por vez")
        os.remove("./Docs/document-chapter.pdf" % page_to_close)
    return None

def cap_first_page(file_path,
                   paragraphs_flag_list,
                   footnote_list,
                   pfl_size,
                   epigraph = True):
    '''
        Função complexa que toma a primeira página de um capitulo, extrai as informações pertinentes e
    reescreve, traduzido ou não, num novo LaTex texto. Recebe 6 argumentos:

    file_path, a string. O endereço para a primeira página do capítulo em questão

    paragraphs_flag_list, a list of strings or null. Uma lista contendo as primeiras sequencias de
    palavras compondo paragrafos em que não se deseja a tradução por serem citações, por exemplo, e 
    que se deseja destacar no texto.
    '''
    elements = partition_pdf(file_path)
    chapter_title = ''
    epigraph_title = ''
    epigraph_text = ''
    chapter_text = '\t'
    title_flag = True
    epigraph_flag = True
    for item in elements:
        item_type = type(item)
        item_text = item.text
        if item_type == unstructured.documents.elements.Title or \
            item_type == unstructured.documents.elements.Text:
            if (not item_text.isnumeric()) and len(item_text.strip()) > 5:
                if title_flag:
                    chapter_title = sentences_checking(item_text)
                    title_flag = False
                elif epigraph:
                    epigraph_title = sentences_checking(item_text)
        elif item_type == unstructured.documents.elements.NarrativeText:
            if epigraph and epigraph_flag:
                epigraph_text = sentences_checking(item_text)
                epigraph_flag = False
            elif item_text[:pfl_size] in paragraphs_flag_list:
                chapter_text = chapter_text + '{\\textbf{\\textit{'+ sentences_checking(item_text) +'} }} {\\par} '
            elif item_text[:pfl_size] in footnote_list:
                chapter_text =  '{\\footnote{'+ sentences_checking(item_text) +'} }' + chapter_text 
            else:
                if item_text[0] in ascii_uppercase and chapter_text[-1] == '.':
                    chapter_text = chapter_text + '{\\par} \t' + sentences_checking(item_text)
                else:
                    chapter_text = chapter_text + sentences_checking(item_text)
    corpus = '{\\chapter{' + chapter_title + '} } {\\label{' + chapter_title + '} }' + '{\\par}'
    corpus = corpus + '{\\textit{\t'+ epigraph_text +'} }' + ' {\\par}'
    corpus = corpus + '{\\par} {\\textbf{\\textit{\t'+ epigraph_title + '} } }' + ' {\\par} \n'
    corpus = corpus + chapter_text
    return corpus

def cap_pages(file_path,
              paragraphs_flag_list,
              last_page_final_char,
              footnote_list,
              pfl_size,
              translate = False):
    '''
        Função complexa que toma a primeira página de um capitulo, extrai as informações pertinentes e
    reescreve, traduzido ou não, num novo LaTex texto. Recebe 6 argumentos:

    file_path, a string. O endereço para a primeira página do capítulo em questão

    paragraphs_flag_list, a list of strings or null. Uma lista contendo as primeiras sequencias de
    palavras compondo paragrafos em que não se deseja a tradução por serem citações, por exemplo, e 
    que se deseja destacar no texto.
    '''
    elements = partition_pdf(file_path)
    chapter_text = ''
    for item in elements:
        item_type = type(item)
        item_text = item.text
        if item_type == unstructured.documents.elements.NarrativeText:
            if item_text[:pfl_size] in paragraphs_flag_list:
                chapter_text = chapter_text + '{\\par} {\\textbf{\\textit{' + sentences_checking(item_text) + '} } }{\\par} '
            elif item_text[:pfl_size] in footnote_list:
                chapter_text = chapter_text + '{\\footnote{'+ sentences_checking(item_text) +'} }'
            
            else:
                if item_text[0] in ascii_lowercase and last_page_final_char == '.':
                    chapter_text = chapter_text + '{\\par} \t' + sentences_checking(item_text)
                else:
                    chapter_text = chapter_text + sentences_checking(item_text)
    return chapter_text

def references_list(file_path):
    '''
        Função simples que toma uma pagina de referencias e retorna a enumeração das referencias
    apresentadas. Recebe um argumento e retorna um string

    file_path, a string. O endereço para a pagina contendo referencias
    '''
    elements = partition_pdf(file_path)
    references_list = ''
    for item in elements:
        item_type = type(item)
        try:
            item_text = port_checking(translate_snippet(item.text))#item.text
        except:
            item_text = item.text
        if item_type == unstructured.documents.elements.ListItem:
            to_find = re.compile(r"^[^.]*")
            init_chars = re.search(to_find, item_text).group(0)
            jump = len(init_chars)
            references_list = references_list + '\n\n\n\t' +\
                              '{\\color{blue}' + init_chars + '}' + \
                              item_text[jump:]
        elif item_type == unstructured.documents.elements.Title:
            references_list = references_list + '\n\n\n' + '\\section{' +\
                                item_text + '}'
    return references_list

def get_refrences(path, beginning, ending):
    corpus = ''
    for i in range(beginning, ending+1):
        page = open_page(path, i)
        print("Analisando referencias contidas na página:\t", page)
        for item in page:
            corpus = corpus + references_list(file_path = item)
        close_pages(page_to_close = i, mode='page')
    return corpus

def get_cap_info(path, beginning, ending, epigraph,
                 params_list, footnote_list,
                 pfl_size):
    first_page_path = open_page(path, beginning)
    print("primeira página aberta e salva em:\t", first_page_path)
    for item in first_page_path:
        corpus = cap_first_page(file_path=item,
                                paragraphs_flag_list=params_list,
                                footnote_list = footnote_list,
                                epigraph = epigraph,
                                pfl_size = pfl_size)
        close_pages(page_to_close=beginning, mode='page')
        print('primeira pagina fechada')
    for i in range(beginning+1, ending+1):
        page = open_page(path, i)
        print("outras paginas abertas e salvas em:\t", page)
        for item in page:
            corpus = corpus + cap_pages(file_path = item,
                                    paragraphs_flag_list = params_list,
                                    last_page_final_char = corpus.rstrip()[-1],
                                    footnote_list = footnote_list,
                                    pfl_size = pfl_size)            
            close_pages(page_to_close = i, mode='page')
            print('pagina fechada')
    corpus = naive_refence(string = corpus)
    #corpus = cleaning_with_regex(string = corpus)
    return corpus
    
def close_cap(beginning, ending):
    for number in range(beginning, ending + 1):
        close_pages(number)
    return None

def naive_refence(string):
    new = re.sub(r'([\s\.])(\d{1})([\s\.\)])', r'\1{\\color{blue} \2 }\3', string)
    new = re.sub(r'([\s\.])(\d{2})([\s\.\)])', r'\1{\\color{blue} \2 }\3', new)
    new = re.sub(r'([\s\.])(\d{3})([\s\.\)])', r'\1{\\color{blue} \2 }\3', new)
    # not taken references
    new = re.sub(r'([\.”])\s*(\d+)\s*\}', r'\1 {\\color{blue} \2 } }', new)
    new = re.sub(r'([\.”])\s*(\d+)\s*([,A-Z])', r'\1 {\\color{blue} \2 } {\\par} \3', new)
    return new

###############################################

###############################################
####  translation and text verification     ###
###############################################

###############################################
def sentences_checking(text):
    correct = tool_en.correct(text)
    return correct

def port_checking(text):
    return ltp.utils.correct(text, select_translation_rules(string = text))

def translate_snippet(text):
    translated = dt.GoogleTranslator(source='auto', target='portuguese').translate(text)
    return translated

def translate_paragraph(paragraph):
    #print("Inside \n" + paragraph)
    text = re.sub("([A-Z])\.", r"\1aaa", paragraph)
    phrases_list = text.split('.')
    phrases_list = map(str.lstrip(), phrases_list)
    translated_phrases = []
    for phrase in phrases_list:
        wrd_bag = re.findall(r"(?<!^)[A-Z][a-z]+", phrase)
        if len(wrd_bag) == 0:
            translated_phrases.append(port_checking(translate_snippet(phrase)))
        else:
            bag_3_wrd = re.findall(r"(?<!^)[A-Z][a-z]+\s[A-Z][a-z]+\s[A-Z][a-z]+", phrase)#([\.,-]?)
            phrase = re.sub(r"(?<!^)[A-Z][a-z]+\s[A-Z][a-z]+\s[A-Z][a-z]+", r"XXXX3", phrase)
            bag_2_wrd = re.findall(r"(?<!^)[A-Z][a-z]+\s[A-Z][a-z]+", phrase)
            phrase = re.sub(r"(?<!^)[A-Z][a-z]+\s[A-Z][a-z]+", r"XXXX2", phrase)
            bag_1_wrd = re.findall(r"(?<!^)[A-Z][a-z]+", phrase)
            mod_phrase = re.sub(r"(?<!^)[A-Z][a-z]+", r"XXXX1", phrase)
            trans_phrase = port_checking(translate_snippet(mod_phrase))
            #print("Antes")
            #print(trans_phrase)
            trans_phrase = reenter_lists(corpus = trans_phrase,
                                           reference_list = bag_3_wrd,
                                           to_split = "XXXX3")
            trans_phrase = reenter_lists(corpus = trans_phrase,
                                           reference_list = bag_2_wrd,
                                           to_split = "XXXX2")
            trans_phrase = reenter_lists(corpus = trans_phrase,
                                           reference_list = bag_1_wrd,
                                           to_split = "XXXX1")
            #temp = ' '.join(trans_phrase)
            #temp = re.sub("aaa", ".", temp)     
            trans_phrase = re.sub("aaa", ".", trans_phrase)
            #translated_phrases.append(temp)
            translated_phrases.append(trans_phrase)
    translated_paragraph = '. '.join(translated_phrases)
    return translated_paragraph

def translate_chapter(path):
    # Abrir o arquivo salvo em inglês e dividí-lo em paragrafos usando o LaTex comando \par
    with open(path, 'r') as file:
        data = file.read()
        ref_list = re.findall('{.color{blue} \d }', data)
        data = re.sub('{.color{blue} \d }', '999999', data)
        paragraph_list = data.split("\par")
        # É traduzido paragrafo a paragrafo
        trans_parag_list = []
        for paragraph in paragraph_list:
            phrases_vec = []
            # flag para saber se o texto vai ser traduzido ou mantido
            take_text = False
            phrase = ''
            n_to_trans = ''
            for char in paragraph:
                # Se fecha o parentesis, terminamos a parte a ser ignorada, 
                # a salvamos no ordenadamente no texto final e iniciamos a 
                # guardar o texto a ser traduzido
                #print(char)
                if char == '}':
                    #n_to_trans = n_to_trans + '}'
                    take_text = True
                    phrases_vec.append(n_to_trans + '}')
                    n_to_trans = ''
                    continue
                elif char == '{':
                    # Se o parentesis se abre, então terminamos a coleta do texto a 
                    # ser processado e traduzido e iniciamos a contagem do texto a ser ignorado
                    n_to_trans = n_to_trans + '{'
                    take_text = False
                    # Eliminar espaços vazios no começo do parágrafo e após os pontos finais
                    phrase = re.sub(r'\.[^A-Z]+', '.', phrase)
                    phrase = re.sub(r'^[^A-Z]+', '', phrase)
                    phrases_vec.append(translate_paragraph(phrase))
                    phrase = ''
                    continue
                else:
                    if take_text:
                        phrase = phrase + char
                    else:
                        n_to_trans = n_to_trans + char
                
            temp = ' '.join(phrases_vec)
            
            #temp = re.sub('XXXXXX', r'color{blue} \1}', temp) 
            #temp = re.sub(' }} ', '', temp)
            #temp = re.sub('}{2,}', '', temp)
            temp = re.sub(r'\.\.', '.', temp)
            trans_parag_list.append(temp)
        
        corpus = '{\par'.join(trans_parag_list)
        print(corpus)
        corpus = include_citations(corpus, ref_list)
            
        #return corpus #(include_citations(corpus, ref_list))
        
    return corpus 
    

###############################################
#cap_book_A_Mente_Reacionaria()

def teste():
    begin_chap_pages = [9]#,17,55,75,90,111,123,144,165,175,198,215,231,260]
    ending_chap_pages = [11]#,52,74,89,110,122,143,161,174,197,214,230,259,262]
    pfl_size = 20
    epigraph = [False]#,True,True,False,False,False,False,False,False,True,True,False,True,False]
    paragraphs_flag_list = ["The so-called sympathetic Seattle strike was an",
                            "The occupation of an hair-dresser, or of",
                            "I am the only Negro passenger at Tallahassee’s shambles",
                            "face, the atmosphere would darken, and",
                            "On such small signs and symbols does",
                            "We have been told that our struggle has loosened",
                            "My object for some years past, that which I have",
                            "The formation of a free government on an",
                            "Conservatives do not believe that political",
                            "Typically, the conservative attempts to conserve",
                            "Eminently conservative—while we are revolutionary,",
                            "The recognition that race is the substratum",
                            "superior race is a sort of comfortable couch on which",
                            "Such have been called ",
                            "great leaders in the development of the industrial",
                            "We Germans, too, should go through the world",
                            "But aristocracy has its obligations, and this",
                            "But it may be truly said, that men too much",
                            "I have been much concerned that so many",
                            "You start out in 1954 by saying,",
                            "all these things you’re talking about are",
                            "I’m not saying that. But I’m saying that if",
                            "The mere presence of relations of domination",
                            "anyone else; we must always hold",
                            "She described the show as a",
                            "The great creators—the thinkers, the artists,",
                            "Since his baptism in medieval times, Aristotle has",
                            "I quote from Galt’s speech:",
                            "You maintain, gentlemen, that the German",
                            "Everything positive, good and valuable that has",
                            "The exceptional men, the innovators, the",
                            "The man at the top of the intellectual",
                            "You have the courage to tell the masses",
                            "It is from the shadow of a cloister that there",
                            "Another Christian concept, no less crazy, has",
                            "I beg you, look for the words",
                            "You know I could never be happy",
                            "I could start my own business",
                            "In the spring of 2000, Alex Star, editor",
                            "There is another reason I have not revised",
                            "their training with only the most passing",
                            "His violent preoccupation with blood",
                            "Jack Bauer saved Los Angeles.",
                            "They were being raised in a culture tha",
                            "It has been rendered the solemn duty",
                            "a failure to make reasonable modifications",
                            "to afford such goods, services, facilities,",
                            "Now upscalers who once spent hours",
                            "Prada bags at Bloomingdales are suddenly",
                            "Well, I think the problem is we understand",
                            "We are fighting on such distant fronts",
                            "what up to now only a few German cities",
                            "Is a shouted insult a form of torture?",
                            "person’s anus? Pulling out fingernails?",
                            "reminiscent of “stag parties,” featuring copious amounts",
                            "Today, not all the bosses support their",
                            "Their domestic politics is rooted in a loathing",
                            "To the historian who lives in the world",
                            "unintelligent, and enervated periods that have played",
                            "The minds of this generation, exhausted,",
                            "from dark-blue horizons, I felt as if I sailed",
                            "Not only the poorest mechanic, but the man",
                            "We have continually about us animals",
                            "conformity to our will; but to act agreeably",
                            "The restoration of the throne would mean a",
                            "The great virtues turn principally on dangers,",
                            "Let me say, then, that when I came to search",
                            "What did “deprivation of light and auditory",
                            "detainee be held in a coffin? What about"]
    footnote_list = ["This chapter originally appeared in",
                    "This chapter originally appeared as a review",
                    "This chapter originally appeared as a review",
                    "This chapter originally appeared as a review",
                    "This chapter originally appeared as",
                    "This chapter originally appeared as a review",
                    "This chapter originally appeared as a review",
                    "This chapter originally appeared as",
                    "This chapter originally appeared as a review",
                    "This chapter originally appeared as a review",
                    "This chapter originally appeared as"]
    paragraphs_flag_list = [item[:pfl_size] for item in paragraphs_flag_list]
    footnote_list = [item[:pfl_size] for item in footnote_list]
    translate = True
    

    autor, assunto, titulo, sub_titulo = "Corey Robin", "Sociologia", "A mente reacionária", "Conservadorismo: de Edmund Burke até Sarah Palin"
    #create_context(autor, titulo, sub_titulo, assunto)
    # Contexto criado, agora implementamos os capitulos
    idx = 0
    cap_list = []
    #for i, j, k in build_chapter_pages_vector():
    for i, j, k in zip(begin_chap_pages,
                       ending_chap_pages,
                       epigraph):
        corpus = get_cap_info(path = book_path,
                              beginning = i,
                              ending = j,
                              epigraph = k,
                              params_list = paragraphs_flag_list,
                              footnote_list = footnote_list,
                              pfl_size = 20)
        # consertar os problemas decorrentes da concatenação dos textos entre páginas 
        corpus = re.sub(r'([a-z])([A-Z])', lambda pat: (pat.group(1) + ' ' + pat.group(2).lower()), corpus)
        corpus = re.sub(r'([a-z])(-)([A-Z])', lambda pat: (pat.group(1) + pat.group(3).lower()), corpus)
        corpus = re.sub(r'([a-z])(\.)([A-Z])', r'\1\2' + r'{\\par} \3', corpus)
        #print(corpus)
        print_to_file(path_to_save = chapter_path_transposed + '/cap_' + str(idx) + '.tex',
                       string = corpus)
        #cap_list.append('sections/cap_' + str(idx))
        #print_to_file(path_to_save = 'teste_eng.tex',
        #               string = corpus)
        if translate:
            with open(chapter_path_transposed + '/cap_' + str(idx) + '.tex', 'r') as file:
                data = file.read().split("\par")
                sentences = []
                print("Iniciando tradução")
                for text in data:
                    text = re.sub(r'color{blue} (\d+) }', r'color1blue2 \1}', text) 
                    phrases_vec = []
                    take_text = False
                    phrase = ''
                    n_to_trans = ''
                    for char in text:
                        if char == '}':
                            take_text = True
                            phrases_vec.append('{' + n_to_trans + '}')
                            n_to_trans = ''
                            continue
                        elif char == '{':
                            take_text = False
                            phrases_vec.append(port_checking(translate_snippet(phrase)))
                            phrase = ''
                            continue
                        if take_text:
                            phrase = phrase + char
                        else:
                            n_to_trans = n_to_trans + char

                    temp = ' '.join(phrases_vec)
                    temp = re.sub(r'\\chapter(.*)}', lambda pat: r'\\chapter{' + port_checking(translate_snippet(pat.group(1))) + r'\1}}', temp)
                    temp = re.sub(r'\\label(.*)}', lambda pat: r'\\label{' + port_checking(translate_snippet(pat.group(1))) + r'\1}}', temp)
                    temp = re.sub(r'\\footnote(.*)}', r'\\footnote{\1}}', temp)
                    temp = re.sub(r'\\textbf(.*)}', r'\\textbf{\1}}', temp)
                    temp = re.sub(r'\\textit(.*)}', r'\\textit{\1}}', temp)
                    temp = re.sub(r'color1blue2 (\d+)}', r'color{blue} \1}', temp) 
                    temp = re.sub(r'\{\}', '', temp)
                    sentences.append(temp)    

            corpus = '{\\par}'.join(sentences)
            print("Tradução concluída")

            print_to_file(path_to_save = 'teste_pt.tex',
                       string = corpus)
    
    return None

def get_flags_back(data, saved_lists, flags_list):
    data.replace('aaa', '.')
    for flag, list in zip(flags_list, saved_lists):
        if any(list):
            data = reenter_lists(data, reference_list = list, to_split = flag)
    return data


def get_names(text, processed_LaTex):
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
            overall_list.append(port_checking(translate_snippet(processed_text)))
        else:
            overall_list.append(' ')
            continue
    processed_text = ''
    for text in overall_list:
        processed_text = processed_text + text + '\n999999\n'
    bag_0_wrd = ak.flatten(bag_0_wrd)
    bag_1_wrd = ak.flatten(bag_1_wrd)
    bag_2_wrd = ak.flatten(bag_2_wrd)
    bag_3_wrd = ak.flatten(bag_3_wrd)
    corpus = get_flags_back(data = processed_text,
                            saved_lists = [bag_0_wrd, bag_1_wrd, bag_2_wrd, bag_3_wrd, processed_LaTex],
                            flags_list = ['XXXX0', 'XXXX1', 'XXXX2', 'XXXX3', '999999'])
    
    return corpus#processed_text, bag_3_wrd, bag_2_wrd, bag_1_wrd, bag_0_wrd


def translate(text, processed_LaTex):
    is_bad_rule = lambda rule: rule.message == 'Encontrado possível erro de ortografia.' and len(rule.replacements) and rule.replacements[0][0].isupper()
    text = re.sub("([A-Z])\.", r"\1aaa", text)
    text_list = text.split('\n999999\n')
    overall_list = []
    for text in text_list:
        if len(text) > 0:
            text = text.replace('aaa', '.')
            overall_list.append(port_checking(translate_snippet(text)))
        else:
            overall_list.append(' ')   
    processed_text = ''
    for text in overall_list:
        processed_text = processed_text + text + '\n999999\n'
    corpus = get_flags_back(data = processed_text,
                            saved_lists = [processed_LaTex],
                            flags_list = ['999999'])
    
    return corpus#processed_text, bag_3_wrd, bag_2_wrd, bag_1_wrd, bag_0_wrd

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

def test_trans(path):
#path = '/home/ricardo/Documents/CienciaDeDados/TraducoesProject/teste.tex'
    with open(path, 'r') as file:
        data = file.read()
        data, LaTex_list = get_LaTex_sintaxe(data)
        processed_LaTex = process_LaTex_list(LaTex_list)
        #preprocessed_text, bag_wrd_3, bag_wrd_2, bag_wrd_1, bag_wrd_0 = get_names(data, processed_LaTex)
        #corpus = get_names(data, processed_LaTex)
        corpus = translate(data, processed_LaTex)
    return corpus    

def cap_book_A_Mente_Reacionaria():
    begin_chap_pages = [9,17,55,75,90,111,123,144,165,175,198,215,231,260]
    ending_chap_pages = [11,52,74,89,110,122,143,161,174,197,214,230,259,262]
    pfl_size = 20
    epigraph = [False,True,True,False,False,False,False,False,False,True,True,False,True,False]
    paragraphs_flag_list = ["The so-called sympathetic Seattle strike was an",
                            "The occupation of an hair-dresser, or of",
                            "I am the only Negro passenger at Tallahassee’s shambles",
                            "face, the atmosphere would darken, and",
                            "On such small signs and symbols does",
                            "We have been told that our struggle has loosened",
                            "My object for some years past, that which I have",
                            "The formation of a free government on an",
                            "Conservatives do not believe that political",
                            "Typically, the conservative attempts to conserve",
                            "Eminently conservative—while we are revolutionary,",
                            "The recognition that race is the substratum",
                            "superior race is a sort of comfortable couch on which",
                            "Such have been called ",
                            "great leaders in the development of the industrial",
                            "We Germans, too, should go through the world",
                            "But aristocracy has its obligations, and this",
                            "But it may be truly said, that men too much",
                            "I have been much concerned that so many",
                            "You start out in 1954 by saying,",
                            "all these things you’re talking about are",
                            "I’m not saying that. But I’m saying that if",
                            "The mere presence of relations of domination",
                            "anyone else; we must always hold",
                            "She described the show as a",
                            "The great creators—the thinkers, the artists,",
                            "Since his baptism in medieval times, Aristotle has",
                            "I quote from Galt’s speech:",
                            "You maintain, gentlemen, that the German",
                            "Everything positive, good and valuable that has",
                            "The exceptional men, the innovators, the",
                            "The man at the top of the intellectual",
                            "You have the courage to tell the masses",
                            "It is from the shadow of a cloister that there",
                            "Another Christian concept, no less crazy, has",
                            "I beg you, look for the words",
                            "You know I could never be happy",
                            "I could start my own business",
                            "In the spring of 2000, Alex Star, editor",
                            "There is another reason I have not revised",
                            "their training with only the most passing",
                            "His violent preoccupation with blood",
                            "Jack Bauer saved Los Angeles.",
                            "They were being raised in a culture tha",
                            "It has been rendered the solemn duty",
                            "a failure to make reasonable modifications",
                            "to afford such goods, services, facilities,",
                            "Now upscalers who once spent hours",
                            "Prada bags at Bloomingdales are suddenly",
                            "Well, I think the problem is we understand",
                            "We are fighting on such distant fronts",
                            "what up to now only a few German cities",
                            "Is a shouted insult a form of torture?",
                            "person’s anus? Pulling out fingernails?",
                            "reminiscent of “stag parties,” featuring copious amounts",
                            "Today, not all the bosses support their",
                            "Their domestic politics is rooted in a loathing",
                            "To the historian who lives in the world",
                            "unintelligent, and enervated periods that have played",
                            "The minds of this generation, exhausted,",
                            "from dark-blue horizons, I felt as if I sailed",
                            "Not only the poorest mechanic, but the man",
                            "We have continually about us animals",
                            "conformity to our will; but to act agreeably",
                            "The restoration of the throne would mean a",
                            "The great virtues turn principally on dangers,",
                            "Let me say, then, that when I came to search",
                            "What did “deprivation of light and auditory",
                            "detainee be held in a coffin? What about"]
    footnote_list = ["This chapter originally appeared in",
                    "This chapter originally appeared as a review",
                    "This chapter originally appeared as a review",
                    "This chapter originally appeared as a review",
                    "This chapter originally appeared as",
                    "This chapter originally appeared as a review",
                    "This chapter originally appeared as a review",
                    "This chapter originally appeared as",
                    "This chapter originally appeared as a review",
                    "This chapter originally appeared as a review",
                    "This chapter originally appeared as"]
    paragraphs_flag_list = [item[:pfl_size] for item in paragraphs_flag_list]
    footnote_list = [item[:pfl_size] for item in footnote_list]
    translate = True
    autor, assunto = "Corey Robin", "Sociologia"
    titulo, sub_titulo = "A mente reacionária", "Conservadorismo: de Edmund Burke até Sarah Palin"
    idx = 0
    cap_list = []
    for i, j, k in zip(begin_chap_pages, ending_chap_pages, epigraph):
        # Pegar as informações do pdf e transformando-os em string com ortografia corrigida
        corpus = get_cap_info(path = book_path,
                              beginning = i,
                              ending = j,
                              epigraph = k,
                              params_list = paragraphs_flag_list,
                              footnote_list = footnote_list,
                              pfl_size = pfl_size)
        # Correção dos erros que aparecem na junção entre páginas
        corpus = re.sub(r'([a-z])([A-Z])', lambda pat: (pat.group(1) + ' ' + pat.group(2).lower()), corpus)
        corpus = re.sub(r'([a-z])(-)([A-Z])', lambda pat: (pat.group(1) + pat.group(3).lower()), corpus)
        corpus = re.sub(r'([a-z])(\.)([A-Z])', r'\1\2' + r'{\\par} \3', corpus)
        corpus = corpus + "{\par}"
        # Salvando o documento em inglês
        
        print_to_file(path_to_save = chapter_path_transposed + '/cap_' + str(idx) + '.tex',
                       string = corpus)
        # Se vamos traduzir o texto, precisamos de mais processamento e salvá-lo em outro arquivo
        if translate:
            # Abrimos o arquivo salvo em inglês
            corpus = test_trans(path=chapter_path_transposed + '/cap_' + str(idx) + '.tex')
            print_to_file(path_to_save = chapter_path_translated + '/cap_' + str(idx) + '.tex',
                       string = corpus)
            cap_list.append('teste/sections/translated/cap_' + str(idx))
        else:
            cap_list.append('teste/sections/transposed/cap_' + str(idx))
        idx = idx + 1
    # capitulos escritos, agora incluimos as referencias 
    
    
    beginning = 263#int(input("Entre com a pagina inicial das referencias:"))
    ending = 293#int(input("Entre com a pagina final das referencias:"))
    corpus = get_refrences(path = book_path,
                           beginning = beginning,
                           ending = ending)
    
    #corpus = naive_refence(string = corpus)
    #corpus = cleaning_with_regex(string = corpus)

    #print_to_file(path_to_save = chapter_path_transposed + '/references.tex',
    #                   string = corpus)
    cap_list.append('sections/references')
    
    # capitulos escritos, agora o main 
    wrap_up_main(include_list = cap_list)

    return None






cap_book_A_Mente_Reacionaria()

from distutils.dir_util import copy_tree
from shutil import rmtree, copyfile
from PyPDF2 import PdfWriter, PdfReader
from unstructured.partition.pdf import partition_pdf
from string import ascii_uppercase, ascii_lowercase
from translate_unity import sentences_checking, translate_snippet, init_engines, text_checking
from canivete import naive_refence, cleaning_with_regex, print_to_file, generate_simple_pattern
import os
import unstructured
import re
import gc
import regex


def get_file(doc_path):
    #doc_path = input("Entre com o endereço do documento a ser tratado:\n")
    try:
        os.mkdir('data/temp')
    except:
        pass
    #doc_path = "data/example_files/The Reactionary Mind_ Conservatism from Edmund Burke to Sarah Palin.pdf"
    path_to_save = input("\n\nEntre com o endereço onde o documento tratado será salvo ou aperte enter para salvar em um arquivo local. Todo conteúdo do caminho selecionado será deletado:\n")
    if not len(path_to_save) > 0:
        path_to_save = '.'
    path_to_save = path_to_save + "/temp_files"
    try:
        rmtree(path_to_save)
    except: 
        pass
    chapter_transposed_path = path_to_save + "/sections/transposed"
    chapter_translated_path = path_to_save + "/sections/translated"
    os.mkdir(path_to_save)
    print('\n\n ' + path_to_save + " criado")
    os.mkdir(path_to_save + "/sections")
    os.mkdir(chapter_transposed_path)
    os.mkdir(chapter_translated_path)
    os.mkdir(path_to_save + "/images")

    copy_tree("data/latex_str/resources", path_to_save + "/resources")
    copyfile("data/latex_str/lix.sty", path_to_save + "/lix.sty")
    copyfile("data/latex_str/main.tex", path_to_save + "/main.tex")
    copyfile("data/latex_str/novel.cls", path_to_save + "/novel.cls")
    main_path = path_to_save
    return doc_path, main_path, chapter_translated_path, chapter_transposed_path

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
    #os.mkdir('data/temp')
    if mode == "page":
        if type(pages) == int:
            output = PdfWriter()
            output.add_page(inputpdf.pages[pages])
            with open("data/temp/document-page%s.pdf" % pages, "wb") as outputStream:
                output.write(outputStream)
                pages_path_list.append("data/temp/document-page%s.pdf" % pages)
        elif type(pages) == list:
            for i in pages:
                output = PdfWriter()
                output.add_page(inputpdf.pages[i])
                with open("data/temp/document-page%s.pdf" % i, "wb") as outputStream:
                    output.write(outputStream)
                    pages_path_list.append("data/temp/document-page%s.pdf" % i)
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
        with open("data/temp/document-chapter.pdf", "wb") as outputStream:
            output.write(outputStream)
            pages_path_list.append("data/temp/document-chapter.pdf")
        return pages_path_list

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
            os.remove("data/temp/document-page%s.pdf" % page_to_close)
        elif type(page_to_close) == list:
            for i in page_to_close:
                os.remove("data/temp/document-page%s.pdf" % i)
    elif mode == 'chapter':
        print("Aviso. É possível abrir e fechar apenas um capitulo por vez")
        os.remove("data/temp/document-chapter.pdf" % page_to_close)
    return None

def cap_first_page(file_path,
                   paragraphs_flag_list,
                   footnote_list,
                   pfl_size,
                   engine,
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
                    chapter_title = sentences_checking(engine, item_text)
                    title_flag = False
                elif epigraph:
                    epigraph_title = sentences_checking(engine, item_text)
        elif item_type == unstructured.documents.elements.NarrativeText:
            if epigraph and epigraph_flag:
                epigraph_text = sentences_checking(engine, item_text)
                epigraph_flag = False
            elif item_text[:pfl_size] in paragraphs_flag_list:
                chapter_text = chapter_text + '{\\textbf{\\textit{'+ sentences_checking(engine, item_text) +'} }} {\\par} '
            elif item_text[:pfl_size] in footnote_list:
                chapter_text =  '{\\footnote{'+ sentences_checking(engine, item_text) +'} }' + chapter_text 
            else:
                if item_text[0] in ascii_uppercase and chapter_text[-1] == '.':
                    chapter_text = chapter_text + '{\\par} \t' + sentences_checking(engine, item_text)
                else:
                    chapter_text = chapter_text + sentences_checking(engine, item_text)
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
              engine,
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
                chapter_text = chapter_text + '{\\par} {\\textbf{\\textit{' + sentences_checking(engine, item_text) + '} } }{\\par} '
            elif item_text[:pfl_size] in footnote_list:
                chapter_text = chapter_text + '{\\footnote{'+ sentences_checking(engine, item_text) +'} }'
            
            else:
                if item_text[0] in ascii_lowercase and last_page_final_char == '.':
                    chapter_text = chapter_text + '{\\par} \t' + sentences_checking(engine, item_text)
                else:
                    chapter_text = chapter_text + sentences_checking(engine, item_text)
    return chapter_text

def references_list(file_path, language):
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
            item_text = translate_snippet(item, language = language)
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
            references_list = references_list + '\n\n\n' + '\\section\*{' +\
                                item_text + '}'
    references_list = re.sub('\.\s+(\d{1,3})\.',
                             '.\n\n\n\t{color{blue}' + r'\1' + '}.',
                             references_list)
    references_list = re.sub('([%$_])', '\\' + r'\1', references_list)
    return references_list

def get_refrences(path, beginning, ending, language):
    corpus = ''
    for i in range(beginning, ending+1):
        page = open_page(path, i)
        print("Analisando referencias contidas na página:\t", page)
        for item in page:
            corpus = corpus + references_list(file_path = item, language = language)
        close_pages(page_to_close = i, mode='page')
    return corpus

def get_cap_info(path, beginning, ending, epigraph,
                 params_list, footnote_list,
                 pfl_size, engine):
    first_page_path = open_page(path, beginning)
    print("página aberta e salva em:\t", first_page_path)
    for item in first_page_path:
        corpus = cap_first_page(file_path=item,
                                paragraphs_flag_list=params_list,
                                footnote_list = footnote_list,
                                epigraph = epigraph,
                                pfl_size = pfl_size,
                                engine = engine)
        close_pages(page_to_close=beginning, mode='page')
        print('pagina fechada')
    for i in range(beginning+1, ending+1):
        page = open_page(path, i)
        print("página aberta e salva em:\t", page)
        for item in page:
            corpus = corpus + cap_pages(file_path = item,
                                    paragraphs_flag_list = params_list,
                                    last_page_final_char = corpus.rstrip()[-1],
                                    footnote_list = footnote_list,
                                    pfl_size = pfl_size,
                                    engine=engine)            
            close_pages(page_to_close = i, mode='page')
            print('texto fechada')
    corpus = naive_refence(string = corpus)
    #corpus = cleaning_with_regex(string = corpus)
    return corpus
    
def close_cap(beginning, ending):
    for number in range(beginning, ending + 1):
        close_pages(number)
    return None

def join_text_list(vec):
    joined = []
    for idx in range(len(vec)-1):
        item = (vec[idx].rstrip()).lstrip()
        next = (vec[idx+1].rstrip()).lstrip()
        if len(next) == 0:
            continue
        if len(item) == 0:
            continue
        elif  not item[-1] == '.' and next[0] in ascii_lowercase:
            joined.append(item + ' ' + next)
            vec[idx+1] = ''
        else:
            joined.append(item)
    joined.append(vec[-1])
    return joined

def clean_text_list(vec):
    clean = []
    for item in vec:
        if item == "TTTTTT" or item == "EEEEEE" or item == "FFFFFF" or item == "SSSSSS":
            clean.append(item)
        else:
            item = re.sub("([a-z])-\s+([a-z])", r'\1\2', item)
            clean.append(item)
    return clean

def wrap_up_main(include_list, main_path, autor, titulo, sub_titulo):
    
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
    "\\dedicate  { }{--}" + \
    '%\\thank     {Uma tarefa execultada pelo grupo de T.I da Unidade Popular pelo Socialismo}' + '\n' + \
    '%\\keywords  { }' + '\n' + \
    '\\begin{document}' + \
    '\\toc'

    include = ''
    for item in include_list:
        include = include + '\\input{' + f'{item}' + '}' + '\n'
    ending = '\\end{document}'

    main = begining + include + ending
    print_to_file(main_path + '/main.tex', main)
    print(main)
    print('\n Escrito em:\t' + main_path + '/main.tex')
    
def input_equations(string):    
    pat_n1 = generate_simple_pattern(n = 1, to_repeat = '\s[a-zA-Z]\'?[0-9]\s[\+><-]', end_string = '\s[a-zA-Z][0-9][\?!,:\s.]', capture_all= False)
    pat_n2 = generate_simple_pattern(n = 2, to_repeat = '\s[a-zA-Z]\'?[0-9]\s[\+><-]', end_string = '\s[a-zA-Z][0-9][\?!,:\s.]', capture_all= False)
    pat_n3 = generate_simple_pattern(n = 3, to_repeat = '\s[a-zA-Z]\'?[0-9]\s[\+><-]', end_string = '\s[a-zA-Z][0-9][\?!,:\s.]', capture_all= False)
    pat_n4 = generate_simple_pattern(n = 4, to_repeat = '\s[a-zA-Z]\'?[0-9]\s[\+><-]', end_string = '\s[a-zA-Z][0-9][\?!,:\s.]', capture_all= False)
    string = re.sub('–', '-', string)
    lv4_eq = re.findall(pat_n4, string)
    lv3_eq = re.findall(pat_n3, string)
    lv2_eq = re.findall(pat_n2, string)
    lv1_eq = re.findall(pat_n1, string)
    lv4_eq = [re.sub(r'([a-zA-Z])([0-9])', r'\1_{' + r'\2}',s) for s in lv4_eq]
    lv3_eq = [re.sub(r'([a-zA-Z])([0-9])', r'\1_{' + r'\2}',s) for s in lv3_eq]
    lv2_eq = [re.sub(r'([a-zA-Z])([0-9])', r'\1_{' + r'\2}',s) for s in lv2_eq]
    lv1_eq = [re.sub(r'([a-zA-Z])([0-9])', r'\1_{' + r'\2}',s) for s in lv1_eq]
    string = re.sub(pat_n4, ' eeeeee4 ', string) 
    string = re.sub(pat_n3, ' eeeeee3 ', string) 
    string = re.sub(pat_n2, ' eeeeee2 ', string) 
    string = re.sub(pat_n1, ' eeeeee1 ', string)
    idx_4 = 0
    idx_3 = 0
    idx_2 = 0
    idx_1 = 0
    temp = string.split(' ')
    new = []
    for s in temp:
        if  s == 'eeeeee4':
            new.append(" $$" + lv4_eq[idx_4] + "$$ ")
            idx_4 = idx_4 + 1
        elif  s == 'eeeeee3':
            new.append(" $$" + lv3_eq[idx_3] + "$$ ")
            idx_3 = idx_3 + 1
        elif  s == 'eeeeee2':
            new.append(" $$" + lv2_eq[idx_2] + "$$ ")
            idx_2 = idx_2 + 1
        elif  s == 'eeeeee1':
            new.append(" $$" + lv1_eq[idx_1] + "$$ ")
            idx_1 = idx_1 + 1
        else :
            new.append(s)
    done = ' '.join(new)
    return done

    




class page():
    def __init__(self):
        self.Title = []
        self.Sections = []
        self.Text = []
        self.Footnote = []
        self.Special = []
        self.Epigraph = []
        self.Epigraph_citation = []
        self.Corpus = []
        self.equations = []
        self.figures = []

    def add_main_elements(self, path, raw = False):
        elements = partition_pdf(path)
        for el, typ in zip([el.text for el in elements], [type(el) for el in elements]):
            el.replace('–', '-')
            if typ == unstructured.documents.elements.Title:
                if not el.isnumeric() and len(el) > 5:
                    temp = (el.lstrip()).rstrip()
                    if not temp in self.Title:
                        self.Text.append("TTTTTT")
                        self.Title.append(temp)
                        
            elif typ == unstructured.documents.elements.NarrativeText or unstructured.documents.elements.Text:
                    self.Text.append((el.lstrip()).rstrip())
        if not raw:        
            self.Text = join_text_list(self.Text)
            self.Text = clean_text_list(self.Text)
            
    def add_footnotes(self, footnote_list, len_flag):
        text = []
        for el in self.Text:
            if el[:len_flag] in footnote_list:
                self.Footnote.append(el)
                text.append("FFFFFF")
            else:
                text.append(el)
        self.Text = text

    def add_special(self, special_list, len_flag):
        text = []
        for el in self.Text:
            if el[:len_flag] in special_list:
                self.Special.append(el)
                text.append("SSSSSS")
            else:
                text.append(el)
        self.Text = text

    def add_epigraph(self, epigraph_list, len_flag):
        text = []
        for el in self.Text:
            if el[:len_flag] in epigraph_list:
                self.Epigraph.append(el)
                text.append("EEEEEE")
            else:
                text.append(el)
        self.Text = text

    def correct_text(self, language = 'en'):
        engine = init_engines(language)
        corrected = []
        for sentence in self.Text:
            corrected.append(text_checking(sentence, engine, language))
        self.Text = clean_text_list(corrected)
        corrected = []
        for sentence in self.Title:
            corrected.append(text_checking(sentence, engine, language))
        self.Title = clean_text_list(corrected)
        corrected = []
        for sentence in self.Footnote:
            corrected.append(text_checking(sentence, engine, language))
        self.Footnote = clean_text_list(corrected)
        corrected = []
        for sentence in self.Epigraph:
            corrected.append(text_checking(sentence, engine, language))
        self.Epigraph = clean_text_list(corrected)
        corrected = []
        for sentence in self.Special:
            corrected.append(text_checking(sentence, engine, language))
        self.Special = clean_text_list(corrected)

    def translate_text(self, language = 'pt', mode = 'Text'):
        mode = mode.lower()
        if mode == 'text':
            translated = []
            for sentence in self.Text:
                if sentence == 'TTTTTT' or \
                   sentence == 'EEEEEE' or \
                   sentence == 'SSSSSS' or \
                    sentence == 'FFFFFF':
                    translated.append(sentence)
                else:
                    translated.append(translate_snippet(sentence, language = language))
            self.Text = translated
        elif mode == 'title':
            translated = []
            for sentence in self.Title:
                translated.append(translate_snippet(sentence, language = language))
            self.Title = translated
        elif mode == 'footnote':
            translated = []
            for sentence in self.Footnote:
                translated.append(translate_snippet(sentence, language = language))
            self.Footnote = translated
        elif mode == 'epigraph':
            translated = []
            for sentence in self.Epigraph:
                translated.append(translate_snippet(sentence, language = language))
            self.Epigraph = translated
        elif mode == 'special':
            translated = []
            for sentence in self.Special:
                translated.append(translate_snippet(sentence, language = language))
            self.Special = translated
        else:
            print('Opção desconhecia para tradução, as opções atuais são [text, title, footnote, epigraph, special], digite uma das opções e tente novamente')
            return None

    def write_latex(self):
        self.Corpus = ''
        corpus = []
        chap_title_flag = True
        if len(self.Epigraph) > 0:
            epigraph_flag = True
        else:
            epigraph_flag = False
        idx_title = 0
        idx_footnote = 0
        idx_epigraph = 0
        idx_special = 0
        for item in self.Text:
            if item == 'TTTTTT':
                if chap_title_flag:
                    chap_title_flag = False
                    temp = '\chapter{' + self.Title[idx_title] + '}' + '\label{' + self.Title[idx_title] + '}'
                    corpus.append(temp)
                    idx_title = idx_title + 1
                elif epigraph_flag:
                    epigraph_flag = False
                    temp = '\\textbf{\\textit{' + self.Title[idx_title] + '} }'
                    corpus.append(temp)
                    idx_title = idx_title + 1
                elif len(re.findall('[A-Z]+[\s+<>\-\+\=][A-Z]+', self.Title[idx_title])) > 0:
                    temp = '\\[' + self.Title[idx_title] + '\\]'
                    corpus.append(temp)
                    idx_title = idx_title + 1
                elif self.Title[idx_title][:5] == "Figur":
                    temp = '\\begin\{figure\}[h]\n\\centering\n\\includegraphics[width=0.25\\textwidth]{ }\n\\caption{'
                    temp = temp + self.Title[idx_title] + '}\n\\label\{\}\n\\end\{figure\}'
                    idx_title = idx_title + 1
                else :
                    temp = '\section{' + self.Title[idx_title] + '}'
                    corpus.append(temp)
                    idx_title = idx_title + 1
            elif item == 'FFFFFF':
                temp = '\\footnote{' + self.Footnote[idx_footnote] + '}' 
                corpus.append(temp)
                idx_footnote = idx_footnote + 1
            elif item == 'EEEEEE':
                temp = '\\textit{' + self.Epigraph[idx_epigraph] + '}' 
                corpus.append(temp)
                idx_epigraph = idx_epigraph + 1
            elif item == 'SSSSSS':
                temp = naive_refence(self.Special[idx_special]) 
                corpus.append('\\textit\\textbf{ {' + temp + '} }')
                idx_special = idx_special + 1
            else:
                temp = naive_refence(item)
                temp = input_equations(temp)
                corpus.append(temp)
        self.Corpus = '\n \par \n'.join(corpus)

    def corpus_to_file(self, path):
        print_to_file(path_to_save = path,
                       string = self.Corpus)

class chapter():
    len_flag = 8
    def __init__(self, book_path, 
                 epigraphs = None,
                 footnotes = None,
                 specials = None):
        self.Path = book_path
        self.References = ''
        if epigraphs is not None:
            self.Epigraph_list = epigraphs
        else: 
            self.include_list(self, mode = 'epigraph')
        if footnotes is not None:
            self.Footnote_list = footnotes
        else: 
            self.include_list(self, mode = 'footnote')
        if specials is not None:
            self.Special_list = specials
        else: 
            self.include_list(self, mode = 'special')

    def include_list(self, mode, List = None):
        mode = mode.lower()
        if mode == 'epigraph':
            if List is None:
                List = []
                item = 'A'
                while True:
                    item = input('Entre com o começo do epigrafo a ser destacado do texto ou [Enter] para encerrar:\n')
                    if len(item) == 0:
                        break
                    List.append(item)
            self.Epigraph_list = [item[:chapter.len_flag] for item in List]
            self.Epigraph_list = List
            print("Lista de termos selecionados:\n")
            for item in self.Epigraph_list:
                print(item)
        elif mode == 'footnote':
            if List is None:
                List = []
                item = 'A'
                while True:
                    item = input('Entre com o começo da nota de rodapé a ser destacada do texto ou [Enter] para encerrar:\n')
                    if len(item) == 0:
                        break
                    List.append(item)
            self.Footnote_list = [item[:chapter.len_flag] for item in List]
            self.Footnote_list = List
            print("Lista de termos selecionados:\n")
            for item in self.Footnote_list:
                print(item)
        elif mode == 'special':
            if List is None:
                List = []
                item = 'A'
                while True:
                    item = input('Entre com o começo do texto a ser destacada do texto ou [Enter] para encerrar:\n')
                    if len(item) == 0:
                        break
                    List.append(item)
            self.Special__list = [item[:chapter.len_flag] for item in List]
            self.Special_list = List
            print("Lista de termos selecionados:\n")
            for item in self.Special_list:
                print(item)

    def chap_to_file(self, chap_pages_list, mode, 
                      path_to_save_en,
                      path_to_save_pt):
        Chap = page()
        for path in chap_pages_list:
            Chap.add_main_elements(path, raw=True)
        Chap.add_footnotes(self.Footnote_list, chapter.len_flag)
        Chap.add_epigraph(self.Epigraph_list, chapter.len_flag)
        Chap.add_special(self.Special_list, chapter.len_flag)
        Chap.Text = join_text_list(Chap.Text)
        Chap.Text = clean_text_list(Chap.Text)
        Chap.correct_text(language = 'en')

        if mode == 'en':
            Chap.write_latex()
            Chap.corpus_to_file(path = path_to_save_en)
        elif mode == 'pt':
            Chap.translate_text(language = 'pt', mode = 'Title')
            Chap.translate_text(language = 'pt', mode = 'Text')
            Chap.translate_text(language = 'pt', mode = 'Footnote')
            Chap.translate_text(language = 'pt', mode = 'Epigraph')
            Chap.translate_text(language = 'pt', mode = 'Special')
            Chap.write_latex()
            Chap.corpus_to_file(path = path_to_save_pt)
        elif mode == 'both':
            Chap.write_latex()
            Chap.corpus_to_file(path = path_to_save_en)
            Chap.translate_text(language = 'pt', mode = 'Title')
            Chap.translate_text(language = 'pt', mode = 'Text')
            Chap.translate_text(language = 'pt', mode = 'Footnote')
            Chap.translate_text(language = 'pt', mode = 'Epigraph')
            Chap.translate_text(language = 'pt', mode = 'Special')
            Chap.write_latex()
            Chap.corpus_to_file(path = path_to_save_pt)
        del Chap
        gc.collect()
        
    def write_chapter(self, init_page, end_page, path_to_save_en, path_to_save_pt, mode):
        path_list = open_page(doc_path = self.Path,
                              pages_to_open = [i for i in range(init_page, end_page + 1)])
        self.chap_to_file(chap_pages_list = path_list,
                          path_to_save_en=path_to_save_en,
                          path_to_save_pt=path_to_save_pt,
                          mode=mode)
        for idx in range(init_page, end_page+1):
            close_pages(idx, mode='page')
        
    def write_references(self, ref_init, ref_end, ref_lang):
        def references_list(file_path, language):
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
                    item_text = translate_snippet(item, language = language)
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
            references_list = re.sub('\.\s+(\d{1,3})\.',
                                    '.\n\n\n\t{color{blue}' + r'\1' + '}.',
                                    references_list)
            return references_list
 
        corpus = ''
        for i in range(ref_init, ref_end + 1):
            page = open_page(self.Path, i)
            print("Analisando referencias contidas na página:\t", page)
            for item in page:
                corpus = corpus + references_list(file_path = item, language = ref_lang)
            print('Pronto!')
            close_pages(page_to_close = i, mode='page')
        self.References = corpus

    def text_to_file(self, path, file):
        print_to_file(path_to_save = path,
                       string = file)

    def write_book(self, inits_list, ends_list, reference_pages, autor,
                   titulo, sub_titulo, writing_mode = 'both', slow = False,
                   from_the_top = True):
        if from_the_top:
            doc_path, main_path, chapter_translated_path, chapter_transposed_path = get_file(self.Path)
        else:
            main_path = 'temp_files/sections'
            chapter_translated_path = 'temp_files/sections/translated'
            chapter_transposed_path = 'temp_files/sections/transposed'
            get_from = int(input('A partir de qual capitulo deseja continuar?\n'))
        include_list = []
        for init, end, chap in zip(inits_list, ends_list, [i for i in range(len(inits_list))]):
            if not from_the_top:
                if chap < get_from:
                    continue
            print("Escrevendo capitulo:\t" + str(chap))
            print("Entre as páginas {x} e {y}\n".format(x=init, y=end))
            path_to_save_en = chapter_transposed_path + '/cap_' + str(chap) + '.tex'
            path_to_save_pt = chapter_translated_path + '/cap_' + str(chap) + '.tex'
            if writing_mode == 'both':
                self.write_chapter(init, end, path_to_save_en, path_to_save_pt, mode = 'both')
                include_list.append(path_to_save_pt)
            elif writing_mode == 'pt':
                self.write_chapter(init, end, path_to_save_en, path_to_save_pt, mode = 'pt')
                include_list.append(path_to_save_pt)
            elif writing_mode == 'en':
                self.write_chapter(init, end, path_to_save_en, path_to_save_pt, mode = 'en')
                include_list.append(path_to_save_en)
            else: 
                print("Opção para writing_mode desconhecida")
                return None
            print("Pronto! \n")
            
            if slow:
                test = input('Aperte [enter] para continuar\n')
        if writing_mode == 'both':
            self.write_references(ref_init = reference_pages[0],
                                    ref_end = reference_pages[1],
                                    ref_lang = 'en')
            self.text_to_file(path = chapter_transposed_path + '/references.tex', file = self.References)
            self.write_references(ref_init = reference_pages[0],
                                    ref_end = reference_pages[1],
                                    ref_lang = 'pt')
            self.text_to_file(path = chapter_translated_path + '/references.tex', file = self.References)
        elif writing_mode == 'en':
            self.write_references(ref_init = reference_pages[0],
                                    ref_end = reference_pages[1],
                                    ref_lang = 'en')
            self.text_to_file(path = chapter_transposed_path + '/references.tex', file = self.References)
            include_list.append(chapter_transposed_path + '/references.tex')
        elif writing_mode == 'pt':
            self.write_references(ref_init = reference_pages[0],
                                    ref_end = reference_pages[1],
                                    ref_lang = 'pt')
            self.text_to_file(path = chapter_translated_path + '/references.tex', file = self.References)
            include_list.append(chapter_translated_path + '/references.tex')
        print('Escrevendo o arquivo main.tex')
        wrap_up_main(include_list, 'temp_files', autor, titulo, sub_titulo)
        print("Pronto!")
        return main_path

    def write_article(self, inits_list, ends_list, reference_pages, autor,
                   titulo, sub_titulo, writing_mode = 'both', slow = False,
                   from_the_top = True):
        if from_the_top:
            doc_path, main_path, chapter_translated_path, chapter_transposed_path = get_file(self.Path)
        else:
            main_path = 'temp_files/sections'
            chapter_translated_path = 'temp_files/sections/translated'
            chapter_transposed_path = 'temp_files/sections/transposed'
            get_from = int(input('A partir de qual capitulo deseja continuar?\n'))
        include_list = []
        for init, end, chap in zip(inits_list, ends_list, [i for i in range(len(inits_list))]):
            if not from_the_top:
                if chap < get_from:
                    continue
            print("Escrevendo capitulo:\t" + str(chap))
            print("Entre as páginas {x} e {y}\n".format(x=init, y=end))
            path_to_save_en = chapter_transposed_path + '/cap_' + str(chap) + '.tex'
            path_to_save_pt = chapter_translated_path + '/cap_' + str(chap) + '.tex'
            if writing_mode == 'both':
                self.write_chapter(init, end, path_to_save_en, path_to_save_pt, mode = 'both')
                include_list.append(path_to_save_pt)
            elif writing_mode == 'pt':
                self.write_chapter(init, end, path_to_save_en, path_to_save_pt, mode = 'pt')
                include_list.append(path_to_save_pt)
            elif writing_mode == 'en':
                self.write_chapter(init, end, path_to_save_en, path_to_save_pt, mode = 'en')
                include_list.append(path_to_save_en)
            else: 
                print("Opção para writing_mode desconhecida")
                return None
            print("Pronto! \n")
            
            if slow:
                test = input('Aperte [enter] para continuar\n')
        if writing_mode == 'both':
            self.write_references(ref_init = reference_pages[0],
                                    ref_end = reference_pages[1],
                                    ref_lang = 'en')
            self.text_to_file(path = chapter_transposed_path + '/references.tex', file = self.References)
            self.write_references(ref_init = reference_pages[0],
                                    ref_end = reference_pages[1],
                                    ref_lang = 'pt')
            self.text_to_file(path = chapter_translated_path + '/references.tex', file = self.References)
        elif writing_mode == 'en':
            self.write_references(ref_init = reference_pages[0],
                                    ref_end = reference_pages[1],
                                    ref_lang = 'en')
            self.text_to_file(path = chapter_transposed_path + '/references.tex', file = self.References)
            include_list.append(chapter_transposed_path + '/references.tex')
        elif writing_mode == 'pt':
            self.write_references(ref_init = reference_pages[0],
                                    ref_end = reference_pages[1],
                                    ref_lang = 'pt')
            self.text_to_file(path = chapter_translated_path + '/references.tex', file = self.References)
            include_list.append(chapter_translated_path + '/references.tex')
        print('Escrevendo o arquivo main.tex')
        wrap_up_main(include_list, 'temp_files', autor, titulo, sub_titulo)
        print("Pronto!")

class extrato():
    def __init__(self):
        pass
        
class artigo():
    def __init__(self):
        self.Title = []
        self.Sections = []
        self.Text = []
        self.Footnote = []
        self.Special = []
        self.Abstract = []
        self.Author = []
        self.Corpus = ''
        self.equations = []
        self.figures = []

    def add_main_elements(self, path, title_flag, abstract_flag, sections_flag_list, raw = False):
        section_len = len(sections_flag_list[0])
        elements = partition_pdf(path)
        for el, typ in zip([el.text for el in elements], [type(el) for el in elements]):
            if el[:len(title_flag)] in title_flag:
                self.Title = el
                continue
            elif el[:len(abstract_flag)] in abstract_flag:
                self.Abstract = el
                continue
            el.replace('–', '-')
            if typ == unstructured.documents.elements.Title:
                if el[:section_len] in sections_flag_list:
                    temp = (el.lstrip()).rstrip()
                    self.Text.append("SSSSSS")
                    self.Sections.append(temp)
            elif typ == unstructured.documents.elements.NarrativeText or unstructured.documents.elements.Text:
                    self.Text.append((el.lstrip()).rstrip())
        if not raw:        
            self.Text = join_text_list(self.Text)
            self.Text = clean_text_list(self.Text)

    def write_article(self):

        corpus = '\\documentclass[twocolumn,amsmath,amssymb,aps,pre,floatfix]{revtex4-2}\n'
        corpus = corpus + '\\usepackage{url}\n'
        corpus = corpus + '\\usepackage[colorlinks=true, allcolors=blue]{hyperref}\n'
        corpus = corpus + '\\usepackage{float}\n'
        corpus = corpus + '\\usepackage[utf8]{inputenc}\n'
        corpus = corpus + '\\usepackage[T1]{fontenc}\n'
        corpus = corpus + '\\usepackage{lineno}\n'
        corpus = corpus + '\\usepackage{amsthm}\n'
        corpus = corpus + '\\usepackage{}\n'
        corpus = corpus + '\\newtheorem{theorem}{Auxiliary result}\n'
        corpus = corpus + '\\newtheorem{corollary}{Main result}\n'
        corpus = corpus + '\\newtheorem{definition}{Definition}\n'
        corpus = corpus + '\\newtheorem*{gen}{General properties}\n'
        corpus = corpus + '\\newtheorem{prop}{ Appendix result}\n'
        corpus = corpus + '\\newtheorem{secondary}{Appendix\' secondary result}\n'
        corpus = corpus + '\\usepackage{nicematrix}\n'
        corpus = corpus + '\\usepackage{bm}\n'
        corpus = corpus + '\\usepackage{dsfont}\n'
        corpus = corpus + '\\usepackage{amsfonts}\n'
        corpus = corpus + '\\usepackage{indentfirst}\n'
        corpus = corpus + '\\usepackage{graphicx}\n'
        corpus = corpus + '\\usepackage{dcolumn}\n'
        corpus = corpus + '\\usepackage{bm}\n'
        corpus = corpus + '\\usepackage{color}\n'
        corpus = corpus + '\\usepackage{wasysym}\n'
        corpus = corpus + '\\begin{document}\n'

        engine = init_engines('pt')

        corpus = corpus + '\\title{' +\
            text_checking(translate_snippet(self.Title, language = 'pt'), engine, 'pt') +\
                  '}\n'
        corpus = corpus + '\\author{' + self.Author + '}\n'
        corpus = corpus + '\\begin{abstract}' +\
              text_checking(translate_snippet(self.Abstract, language = 'pt'), engine, 'pt') +\
                   '\\end{abstract}\n'
        sect_idx = 0
        text_vec = []
        for item in self.Text:
            if item == 'SSSSSS':
                text_vec.append('\n\\section{' +\
                    text_checking(translate_snippet(self.Sections[sect_idx], language = 'pt'), engine, 'pt') +\
                   '}\n')
                sect_idx = sect_idx + 1
            else:
                try:
                    temp = text_checking(translate_snippet(item, language = 'pt'), engine, 'pt')
                except:
                    temp = translate_snippet(item, language = 'pt')
                if temp is not None:
                    text_vec.append(temp)
                
        corpus = corpus + '\n\\par\n'.join(text_vec)
        corpus = corpus + '\n\\end{document}\n'
        self.Corpus = corpus

    def corpus_to_file(self, path):
        print_to_file(path_to_save = path,
                       string = self.Corpus)




path = '/home/ricardo/Downloads/Has_Socialism_Failed-Analysis_of_Health_Indicators-Navarro_Vincente-1992.pdf'
#open_page(doc_path = path, pages_to_open=0)
#open_page(doc_path = path, pages_to_open=1)

#path = 'data/temp/document-page0.pdf'
#page_eval(path)

test = artigo()
#test.Title = 'HAS SOCIALISM FAILED? AN ANALYSIS OF HEALTH INDICATORS UNDER SOCIALISM'
#test.Abstract = 'This article analyzes the widely held assumption in academia and the mainstream press that capitalism has proven superior to socialism in responding to human needs.'

title_flag = 'HAS SOCIALISM'
abstract_flag = 'This article analyzes'
sections_flag_list = ['A CONTINENT', 'SOCIALISM IN', 'HOW TO EVALUATE', 'CONCLUSIONS', 'REFERENCES']
sections_flag_list = [item[:10] for item in sections_flag_list]
test.Author = 'Vicente Navarro'
test.add_main_elements(path = path, title_flag = title_flag, abstract_flag = abstract_flag, sections_flag_list = sections_flag_list)
test.write_article()
test.corpus_to_file('data/temp/teste.tex')

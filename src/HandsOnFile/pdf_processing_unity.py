from distutils.dir_util import copy_tree
from shutil import rmtree, copyfile
from PyPDF2 import PdfWriter, PdfReader
from unstructured.partition.pdf import partition_pdf
from string import ascii_uppercase, ascii_lowercase
from translate_unity import sentences_checking, translate_snippet, port_checking
from canivete import naive_refence
import os
import unstructured
import re



def get_file():
    #doc_path = input("Entre com o endereço do documento a ser tratado:\n")
    try:
        os.mkdir('data/temp')
    except:
        pass
    doc_path = "data/example_files/The Reactionary Mind_ Conservatism from Edmund Burke to Sarah Palin.pdf"
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
            item_text = port_checking(translate_snippet(item.text))
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





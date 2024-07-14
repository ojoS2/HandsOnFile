###############################################

###############################################
####  LaTex writing ###########################
###############################################
from canivete import print_to_file
from pdf_processing_unity import get_refrences, get_cap_info


def create_context(autor, titulo, sub_titulo, assunto, main_path):
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

def include_chapter(name, corpus, path):
    print_to_file(path_to_save = path + "/" + name + ".tex", string = corpus)
    return None

def wrap_up_main(include_list, main_path, autor, titulo, sub_titulo):
    
    #autor = "Corey Robin"
    #titulo = "A mente reacionária"
    #sub_titulo = "Conservadorismo: de Edmund Burke até Sarah Palin"
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
    '%\\keywords  { }' + '\n'

    include = ''
    for item in include_list:
        include = include + '\\input{' + f'{item}' + '}' + '\n'
    ending = '\\end{document}'

    main = begining + include + ending
    print_to_file(main_path + '/main.tex', main)
    print(main)
    print('\n Escrito em:\t' + main_path + '/main.tex')
    


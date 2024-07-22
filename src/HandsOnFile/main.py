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

from pdf_processing_unity import chapter
import translate_unity as t_u
import LaTex_unity as l_u
import canivete
import re
import gc


def test_print_out_book_The_Reactionary_Mind():
    footnote_list = ["This chapter originally"]
    epigraph_list = ['A political party may ﬁnd that',
                    'Whoever ﬁ gets monsters should',
                    'Busy giddy minds',
                    'Men may dream in demonstrations',
                    'I enjoy wars. Any']
    begin_chap_pages = [9,17,55,75,90,111,123,144,165,175,198,215,231,260]
    ending_chap_pages = [11,52,74,89,110,122,143,161,174,197,214,230,259,262]
    special_list = ["The so-called sympathetic Seattle strike was an",
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
    autor = "Corey Robin"
    titulo = "A mente reacionária"
    sub_titulo = "Conservadorismo: de Edmund Burke até Sarah Palin"

    Chap = chapter(book_path='data/example_files/The Reactionary Mind_ Conservatism from Edmund Burke to Sarah Palin.pdf',
                epigraphs=epigraph_list,
                footnotes=footnote_list,
                specials=special_list)

    book_path = Chap.write_book(inits_list = begin_chap_pages,
                    ends_list = ending_chap_pages,
                    reference_pages = [263, 293], 
                    autor = autor,
                    titulo = titulo, 
                    sub_titulo = sub_titulo,
                    writing_mode = 'pt',
                    slow = True)
    print('Deletando os objetos e liberando memória')

    del Chap
    gc.collect()
    print("Pronto!")
    print("Os escritos podem ser encontrados na pasta temp_files")
    print('Os arquivos escritos foram feito para compilação online no site https://www.overleaf.com/ de forma que para produzir o livro, entre neste site abrindo uma conta gratuita e carregue a partir de lá, a pasta temp_files. Com o editor aberto no arquivo main.tex compile e avalie o trabalho prestando atenção aos erros que eventualmente aparecem')

def test_print_out_book_Marx_Capital():
    footnote_list = []
    epigraph_list = []
    begin_chap_pages =  [9, 10, 17, 29, 44, 62, 70, 81, 94,  105, 111, 126, 135, 142, 153, 165, 178]
    ending_chap_pages = [9, 15, 28, 43, 61, 69, 80, 93, 104, 110, 125, 134, 141, 152, 164, 177, 191]
    special_list = ['Men make their own history,']
    autor = "Ben Fine e Alfredo Saad-Filho"
    titulo = "O 'Capital' de Marx (sexta edição)"
    sub_titulo = "Uma introdução simples ao livro O Capital"
    Chap = chapter(book_path='data/example_files/ben-fine-marxs-capital-6th-edition.pdf',
                   epigraphs=epigraph_list,
                   footnotes=footnote_list,
                   specials=special_list)
    
    book_path = Chap.write_book(inits_list = begin_chap_pages,
                    ends_list = ending_chap_pages,
                    reference_pages = [192, 201], 
                    autor = autor,
                    titulo = titulo, 
                    sub_titulo = sub_titulo,
                    writing_mode = 'pt',
                    slow = False,
                    from_the_top = False)
    print('Deletando os objetos e liberando memória')

    del Chap
    gc.collect()
    print("Pronto!")
    print("Os escritos podem ser encontrados na pasta temp_files")
    print('Os arquivos escritos foram feito para compilação online no site https://www.overleaf.com/ de forma que para produzir o livro, entre neste site abrindo uma conta gratuita e carregue a partir de lá, a pasta temp_files. Com o editor aberto no arquivo main.tex compile e avalie o trabalho prestando atenção aos erros que eventualmente aparecem')

#test_print_out_book_Marx_Capital()

def test_print_out_an_article():
    footnote_list = ['International Journal of']
    epigraph_list = []
    begin_chap_pages =  [0]
    ending_chap_pages = [17]
    special_list = ['This article analyzes', 'Should capitalism be the goal', 'resulting responsability']
    autor = "Vicente Navarro"
    titulo = "O SOCIALISMO FALHOU? UMA ANÁLISE DE INDICADORES DE SAÚDE SOB O SOCIALISMO"
    sub_titulo = ""
    Chap = chapter(book_path='/home/ricardo/Downloads/Has_Socialism_Failed-Analysis_of_Health_Indicators-Navarro_Vincente-1992.pdf',
                   epigraphs=epigraph_list,
                   footnotes=footnote_list,
                   specials=special_list)
    
    book_path = Chap.write_article(inits_list = begin_chap_pages,
                    ends_list = ending_chap_pages,
                    reference_pages = [17, 18], 
                    autor = autor,
                    titulo = titulo, 
                    sub_titulo = sub_titulo,
                    writing_mode = 'pt',
                    slow = False,
                    from_the_top = True)


test_print_out_an_article()

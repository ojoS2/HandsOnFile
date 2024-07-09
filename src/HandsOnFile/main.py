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

import pdf_processing_unity as pdf_u
import translate_unity as t_u
import LaTex_unity as l_u
import canivete
import re
#import page_to_page
print("\n\n Iniciando trabalhos")
doc_path, main_path, translated_chapter_path, transposed_chapter_path = pdf_u.get_file()
print(" \n\n Pronto")
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
    print(" \n\n Iniciando engines")
    eng_engine, port_engine = t_u.init_engines()
    print("\n\n Pronto")
    for i, j, k in zip(begin_chap_pages, ending_chap_pages, epigraph):
        # Pegar as informações do pdf e transformando-os em string com ortografia corrigida
        corpus = pdf_u.get_cap_info(path = doc_path,
                                    beginning = i,
                                    ending = j,
                                    epigraph = k,
                                    params_list = paragraphs_flag_list,
                                    footnote_list = footnote_list,
                                    pfl_size = pfl_size,
                                    engine = eng_engine)
        # Correção dos erros que aparecem na junção entre páginas
        corpus = re.sub(r'([a-z])([A-Z])', lambda pat: (pat.group(1) + ' ' + pat.group(2).lower()), corpus)
        corpus = re.sub(r'([a-z])(-)([A-Z])', lambda pat: (pat.group(1) + pat.group(3).lower()), corpus)
        corpus = re.sub(r'([a-z])(\.)([A-Z])', r'\1\2' + r'{\\par} \3', corpus)
        corpus = corpus + "{\par}"
        # Salvando o documento em inglês
        
        canivete.print_to_file(path_to_save = transposed_chapter_path + '/cap_' + str(idx) + '.tex',
                       string = corpus)
        # Se vamos traduzir o texto, precisamos de mais processamento e salvá-lo em outro arquivo
        if translate:
            print("\n\nTraduzindo capitulos")
            # Abrimos o arquivo salvo em inglês
            corpus = t_u.test_trans(path=transposed_chapter_path + '/cap_' + str(idx) + '.tex',
                                    engine = port_engine)
            canivete.print_to_file(path_to_save = translated_chapter_path + '/cap_' + str(idx) + '.tex',
                       string = corpus)
            cap_list.append(translated_chapter_path + '/cap_' + str(idx))
            print("\n\nPronto")
        else:
            cap_list.append(transposed_chapter_path + '/cap_' + str(idx))
        idx = idx + 1
    # capitulos escritos, agora incluimos as referencias 
    print("\n\nColhendo referencias")
    beginning = 263#int(input("Entre com a pagina inicial das referencias:"))
    ending = 293#int(input("Entre com a pagina final das referencias:"))
    corpus = pdf_u.get_refrences(path = doc_path,
                           beginning = beginning,
                           ending = ending)
    print('\n\nPronto')
    #corpus = naive_refence(string = corpus)
    #corpus = cleaning_with_regex(string = corpus)

    #print_to_file(path_to_save = chapter_path_transposed + '/references.tex',
    #                   string = corpus)
    cap_list.append('sections/references')
    
    # capitulos escritos, agora o main 
    l_u.wrap_up_main(include_list = cap_list, main_path=main_path)
    print("\n\nDocumento escrito e disponível em" + main_path)
    return None

cap_book_A_Mente_Reacionaria()

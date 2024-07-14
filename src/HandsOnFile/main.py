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


test_print_out_book_The_Reactionary_Mind()
'''
path = pdf_u.open_page(doc_path = 'data/example_files/The Reactionary Mind_ Conservatism from Edmund Burke to Sarah Palin.pdf',
                            pages_to_open = [i for i in range(55, 75)])


footnote_list = ["This chapter originally"]
epigraph_list = ['Whoever ﬁ gets monsters should']
special_list = ['But it may be truly said, that men', 'I have been much concerned that',
                'You start out in 1954 by saying', 'all these things you’re talking',
                'I’m not saying that. But I’m saying']
len_flag = 10
footnote_list = [footnote[:len_flag] for footnote in footnote_list]
epigraph_list = [epigraph[:len_flag] for epigraph in epigraph_list]
special_list = [special[:len_flag] for special in special_list]
#filter_len = 15
#footnote_list = [item[:15] for item in footnote_list]
Chap = pdf_u.page()
Chap.add_main_elements(path[0], raw=True)
for idx in range(1, len(path)):
    Chap.add_main_elements(path[idx], raw=True)
Chap.add_footnotes(footnote_list, len_flag)
Chap.add_epigraph(epigraph_list, len_flag)
Chap.add_special(special_list, len_flag)
Chap.correct_text(language = 'en')
Chap.write_latex()
Chap.corpus_to_file(path = 'temp_files/sections/transposed/test.tex')
Chap.translate_text(language = 'pt', mode = 'Title')
Chap.translate_text(language = 'pt', mode = 'Text')
Chap.translate_text(language = 'pt', mode = 'Footnote')
Chap.translate_text(language = 'pt', mode = 'Epigraph')
Chap.translate_text(language = 'pt', mode = 'Special')
Chap.write_latex()
Chap.corpus_to_file(path = 'temp_files/sections/translated/test.tex')



#Chap.correct_text(language = 'pt')
#Chap.write_to_file(path='./teste.tex')

'''


'''
for item in Chap.Text:
    print('\n\n')
    print(item)
print(Chap.Title)
print(Chap.Footnote)
print(Chap.Epigraph)
print(Chap.Special)
'''
#print(corpus)

# HandsOnFile Package

Este é um pacote para processar documentos no formato pdf de origens diversas.

É modularizado de forma que os diferentes níveis de processamento são independentes uns dos outros e podem ser usados de forma independente e em outras formas de texto.

A tarfea é dividida em várias etapas:

. transferencia de formato do pdf pata txt em pedaços específicos

. identificação do papel textual dos diferentes pedaços de texto de acordo com algoritmos de reconhecimento de imagem baseados na posição do texto em questão no pdf


. busca de termos especificos ou correções pontuais usando regex

. correção ortográfica e tradução de paragrafos destacados do documento txt

. escrita do texto corrigido e traduzido em outro arquivo, desta feita um arquivo escrito em LaTex pronto para compilação em sites como o Overleaf



O software é versátil em termos de possibilidade de processamento de estruturas de textos diferentes e ações diferentes dentro de cada módulo

 
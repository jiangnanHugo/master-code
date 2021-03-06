from configs.char_to_char import base
from data.alphabet import Alphabet

class Model(base.Model):
    # overwrite config
    name = 'char_to_char/wmt-deen'
    train_x_files = ['data/train/europarl-v7.de-en.de.tok',
                     'data/train/commoncrawl.de-en.de.tok',
                     'data/train/news-commentary-v10.de-en.de.tok']
    train_t_files = ['data/train/europarl-v7.de-en.en.tok',
                     'data/train/commoncrawl.de-en.en.tok',
                     'data/train/news-commentary-v10.de-en.en.tok']
    valid_x_files = ['data/valid/newstest2013.de.tok']
    valid_t_files = ['data/valid/newstest2013.en.tok']
    test_x_files = ['data/valid/newstest2014.deen.de.tok']
    test_t_files = ['data/valid/newstest2014.deen.en.tok']

    # settings that are local to the model
    alphabet_src = Alphabet('data/alphabet/dict_wmt_tok.de-en.de', eos='*') 
    alphabet_tar = Alphabet('data/alphabet/dict_wmt_tok.de-en.en', eos='*', sos='')

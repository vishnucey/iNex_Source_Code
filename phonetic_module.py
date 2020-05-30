import numpy as np
from pyphonetics import Soundex
from pyphonetics import Metaphone
from pyphonetics import RefinedSoundex
from pyphonetics import FuzzySoundex
import nltk
from nltk import word_tokenize
from nltk.corpus import stopwords
import pandas as pd
from functions import *
import re
import string


def phonetic(data,text):


    def clean_text(raw_text):
        regex = re.compile('[^a-zA-Z\s:]')
        # First parameter is the replacement, second parameter is your input string
        filtered_text = regex.sub('', raw_text)
        # Eliminate multiple spaces
        filtered_text = re.sub(r'[\s]+', ' ', filtered_text)
        # Strip out terminal and leading spaces
        return filtered_text.strip()


    words = data
    sanitized_text=clean_text(text)


    token = word_tokenize(sanitized_text)
    # load stop words
    stop_words = stopwords.words('english')

    # Remove stop words
    token = [word for word in token if word not in stop_words]
    n = len(token)

    soundex = Soundex()
    metaphone = Metaphone()
    rs = RefinedSoundex()
    fs = FuzzySoundex()
    algorithms = [soundex, metaphone, rs, fs]

    cc = dict()
    # conversion of list of tuple to list of list
    for i in range(1, n):
        ngram_list = list(nltk.ngrams(token, i))
        ngram = [" ".join(i) for i in ngram_list]
        cc[str(i)] = ngram

    ngrams = sum(cc.values(), [])
    ngrams = [item for item in ngrams if not item.isdigit()]



    dict1 = dict()


    # Iterating over values
    for i in ngrams:
        for j in words:

            total = 0
            for entry in algorithms:
                code1 = entry.phonetics(i)
                code2 = entry.phonetics(j)

                similar = entry.sounds_like(i,j)
                if similar == True:
                    total += 1

            if total >= 3:
                dict1[str(i)] = j


            total = 0

    dict1= dict(reversed(list(dict1.items())))
    print(dict1)

    def multipleReplace(sentence, dict):
        punct= list(string.punctuation)
        punct=[i for i in punct if i not in [","]]
        punct="".join(punct)
        a=[]
        for i in sentence.split():
            j=i.translate(str.maketrans('','',punct))
            a.append(j)
        sentence=' '.join(a)


        """
        take a text and replace words that match the key in a dictionary
        with the associated value, return the changed text
        """
        for key in dict:
            sentence = sentence.replace(key, dict[key])
        return sentence

    result= multipleReplace(text, dict1)
    print(result)

    return result







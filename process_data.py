# -*- coding: utf-8 -*-
import os
from nltk.tokenize import RegexpTokenizer
import warnings
import codecs
import re as re
import json
from tqdm import tqdm
warnings.filterwarnings('ignore')


def count_words_and_letters_per_text(text_lines, count_words_dict, count_letters_dict, tokenizer):
    """
    Counts the number of occurrencies of a word in a text and adds its frequency to a dictionary

    Parameters
    ----------
    text_lines: list
        List containing the text of the article
    count_words_dict: dict
        Has information about the frequency of each word
    count_letters_dict: dict
        Has information about the frequency of each letter
    tokenizer: nltk.tokenize.regexp.RegexpTokenizer
        Used tokenizer

    Returns
    -------
    count_words_dict: dict
        Updated information about the frequency of each word
    """
    for line in text_lines:
        # We transform each line to lowercase, take away accents and tokenize it
        line = line.lower()
        line = re.sub(u"[àáâãäå]", 'a', line)
        line = re.sub(u"[èéêë]", 'e', line)
        line = re.sub(u"[ìíîï]", 'i', line)
        line = re.sub(u"[òóôõö]", 'o', line)
        line = re.sub(u"[ùúûü]", 'u', line)
        line = re.sub(u"[ýÿ]", 'y', line)
        tokenized_line = tokenizer.tokenize(line)

        # We evaluate each 5-letter word and do the following logic:
        #   - If the word is in the dictionary, we add 1 to its frequency
        #   - If not, we create it in the dictionary, with a frequency of 1

        # We repeat the same procedure with the words' letters
        for word in tokenized_line:
            if len(word) == 5:
                if word in count_words_dict.keys():
                    count_words_dict[word] += 1
                else:
                    count_words_dict[word] = 1

                for letter in word:
                    if letter not in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
                        if letter in count_letters_dict.keys():
                            count_letters_dict[letter] += 1
                        else:
                            count_letters_dict[letter] = 1
                    else:
                        count_letters_dict[letter] = 0

    return count_words_dict, count_letters_dict


def create_words_stats_dict(count_words_dict, count_letters_dict):
    """
    Creates a final dictionary of words with the following structure:
    word: {'frequency': word frequency, 'letter_score': sum of the total frequency of its words}

    Parameters
    ----------
    count_words_dict: dict
        Has information about the frequency of each word
    count_letters_dict: dict
        Has information about the frequency of each letter

    Returns
    -------
    word_stats_dict: dict
        Has information about the frequency of each word and its letters
    """
    word_stats_dict = {}
    for word in count_words_dict:
        # For each word, we sum the frequency of its letters
        letter_score = 0
        for letter in word:
            letter_score += count_letters_dict[letter]
        # After this has been calculated, we create the stats for this word
        word_stats_dict[word] = {
            'frequency': count_words_dict[word],
            'letter_score': letter_score
        }
    return word_stats_dict


if __name__ == '__main__':
    # First, we get the filenames that should be read
    articles_wd = os.getcwd() + '\\data\\articles_data\\spanish_corpus\\'
    for r, d, filenames in os.walk(articles_wd):
        pass

    # Create output dict
    count_words_dict = {}
    count_letters_dict = {}

    # Create tokenizer
    tokenizer = RegexpTokenizer(r'\w+')

    # We count words per text
    for file in tqdm(filenames):
        # We set the complete path and read the file
        filename = articles_wd + file
        try:
            with codecs.open(filename, encoding='latin-1') as f:
                text_lines = f.readlines()

            # We count the frequency of each word and letter
            count_words_dict, count_letters_dict = count_words_and_letters_per_text(
                text_lines,
                count_words_dict,
                count_letters_dict,
                tokenizer
            )
        except FileNotFoundError as e:
            pass

    # We calculate the frequency of each word and its letters and save into a single dictionary
    word_stats_dict = create_words_stats_dict(count_words_dict, count_letters_dict)

    # We save both dictionaries to our disk
    with open('./processed_data/words_data.json', 'w', encoding='utf-8') as fp:
        json.dump(count_words_dict, fp, ensure_ascii=False)

    with open('./processed_data/letters_data.json', 'w', encoding='utf-8') as fp:
        json.dump(count_letters_dict, fp, ensure_ascii=False)

    with open('./processed_data/words_stats.json', 'w', encoding='utf-8') as fp:
        json.dump(word_stats_dict, fp, ensure_ascii=False)

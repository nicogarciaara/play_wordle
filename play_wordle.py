import pandas as pd
import numpy as np
import json
import warnings
warnings.filterwarnings('ignore')


def add_text_flag(text, input_word, result_dict, result_code):
    """
    We build a function that indicates if a word still qualifies as a solution or not.
    A word will qualify for a solution if:
        For letters that appear once in input_word (or twice but have one same result)
            - It doesn't have a letter with score 1
            - Has the letters with score 2 in a position different that the one it has in input_word
            - Has the letters with score 3 in the same position that in input_word
        For letters that appear twice in input_word (with two different results)
            - If one result is 1 and the other 2: Has to have that letter just once, and it has to have it in a position
              different that the one that had a score of 2
            - If one result is 1 and the other 3: Has to have that letter just once, and have it in the same position
              that the one that had a score of 3
            - If one result is 2 and the other 3: Has to have that letter twice: one in the position with the score of 3
              and the other one in a different position than the one that had a score of 2

    Parameters
    ----------
    text: str
        Evaluated word
    input_word: str
        Selected word for Wordle
    result_dict: dict
        Information of the best result per word
    result_code: str
        Information about the result that was given to input_word.
        Remember:
            1 means the letter isn't in the word
            2 means the letter is in the word, but in other order
            3 means the letter is in the world

    Returns
    -------
    qualifies_dummy: int
        Variable that indicates if the word could still be used to play
    """
    qualifies_dummy = 1

    # We check if the conditions isn't being checked
    for p in range(len(input_word)):
        letter = input_word[p]
        if qualifies_dummy == 1:
            result_list = result_dict[letter]
            if len(result_list) == 1:
                result = result_list[0]
                # We disqualify this word if it has a letter it shouldn't
                if result == 1:
                    if letter in text:
                        qualifies_dummy = 0
                        return qualifies_dummy
                elif result == 2:
                    # We disqualify this word if the letter isn't in the text or if it is in the wrong position
                    if letter not in text or text[p] == letter:
                        qualifies_dummy = 0
                        return qualifies_dummy
                else:
                    # We disqualify this word if the letter isn't in the text or if it is in the wrong order
                    if letter not in text or text[p] != letter:
                        qualifies_dummy = 0
                        return qualifies_dummy
            else:
                # If the letter appears twice in input_word, we check the best and worst result (according to our score)
                # and the position that letter appears
                worst_idx = 0
                worst_result = 3
                best_idx = 0
                best_result = 1
                for q in range(len(input_word)):
                    if input_word[q] == letter:
                        res_ix = int(result_code[q])
                        if res_ix < worst_result:
                            worst_idx = q
                            worst_result = res_ix
                        if res_ix > best_result:
                            best_idx = q
                            best_result = res_ix
                # We apply the filter according to our results

                # If one result is 1 and the other 2: Has to have that letter just once,
                # and it has to have it in a position different that the one that had a score of 2
                if worst_result == 1 and best_result == 2:
                    if text.count(letter) != 1 or text[best_idx] == letter:
                        qualifies_dummy = 0
                        return qualifies_dummy
                # If one result is 1 and the other 3: Has to have that letter just once,
                # and have it in the same position that the one that had a score of 3
                if worst_result == 1 and best_result == 3:
                    if text.count(letter) != 1 or text[best_idx] != letter:
                        qualifies_dummy = 0
                        return qualifies_dummy
                # If one result is 2 and the other 3: Has to have that letter twice:
                # one in the position with the score of 3 and the other one in a different position
                # than the one that had a score of 2
                if worst_result == 2 and best_result == 3:
                    if text.count(letter) != 2 or text[worst_idx] == letter:
                        qualifies_dummy = 0
                        return qualifies_dummy

    return qualifies_dummy


def process_result(input_word, result):
    """
    We save the result of each distinct letter of input_word into a dictionary.
    This lets us identify a letter that is duplicated in input_word

    Parameters
    ----------
    input_word: str
        Selected word for Wordle
    result: str
        Result of the try.
        Remember:
            1 means the letter isn't in the word
            2 means the letter is in the word, but in other order
            3 means the letter is in the world

    Returns
    -------
    result_dict: dict
        Information of the best result per word
    """
    result_dict = {}
    for k in range(len(input_word)):
        # We check the letter and the result
        letter = input_word[k]
        result_n = int(result[k])
        # We check if the letter is in the result dict...
        if letter in result_dict:
            # If it is, we check if this result is greater than the current value
            if result_n not in result_dict[letter]:
                result_dict[letter].append(result_n)
        else:
            # If the letter isn't in the result dict, we add it
            result_dict[letter] = [result_n]
    return result_dict

if __name__ == '__main__':
    print("######### WORDLE (ES) #########")
    # Read data
    with open('./processed_data/words_stats.json', 'r', encoding='utf-8') as fp:
        word_stats_dict = json.load(fp)

    # Format dataframe
    df = pd.DataFrame.from_dict(word_stats_dict).T.reset_index().rename(columns={'index': 'word'}).sort_values(
        by='frequency', ascending=False).reset_index(drop=True)

    # For each one of the six tries...
    for i in range(1, 7):
        print(f'### Try # {i} out of 6')
        # We make the suggestion...
        print(f'Possible Words: {df.shape[0]}')
        print(f'The suggested words are...')
        print(df[['word']].head())

        # Make the user write the selected word and the result

        input_word = input('Write the chosen word \n \n')
        result = input('''Write the result.
        Remember:
        1 means the letter isn't in the word
        2 means the letter is in the word, but in other order
        3 means the letter is in the word and in that order \n \n
        ''')

        # Print checks for the user
        oks = []
        in_other_order = []
        not_ok = []
        for a in range(len(input_word)):
            if int(result[a]) == 1:
                not_ok.append(input_word[a])
            elif int(result[a]) == 2:
                in_other_order.append(input_word[a])
            else:
                oks.append(input_word[a])
        print(f'''Results:
        Letters not in the final word: {not_ok}
        Letters in the final word (in other order): {in_other_order}
        Letters in the final word (in that same order): {oks}
        ''')
        if result == '33333':
            print('Congrats, you won!')
            quit(0)
        # We process the result
        result_dict = process_result(input_word, result)

        # We calculate the new allowed words
        df['filter'] = np.vectorize(add_text_flag)(df['word'], input_word, result_dict, result)
        # We filter and process the df
        df = df[df['filter'] == 1].sort_values(by='frequency', ascending=False).reset_index(drop=True)

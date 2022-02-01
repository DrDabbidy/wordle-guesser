from dataclasses import dataclass
import re
from webbrowser import get
import requests
import pickle


def get_freqs(word_list: list) -> dict:
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    freqs = {}

    for i in range(26):
        char = alphabet[i]
        for word in word_list:
            if char in freqs:
                freqs[char] = freqs[char] + word.count(char)
            else:
                freqs[char] = word.count(char)

    return freqs


def get_props(word_list: list) -> dict:
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    props = {}

    for i in range(26):
        char = alphabet[i]
        for word in word_list:
            if char in props:
                props[char] += word.count(char)
            else:
                props[char] = word.count(char)
        props[char] = abs(0.5 - props[char] / len(word_list))  # gives distance from 50%

    return props


def score_word_freqs(word: str, freqs: dict) -> float:
    """Gives a relative score for a give word based on 
    the frequency of letters in the word list.
    """
    word = ''.join(set(word))
    score = 0
    for char in word:
        score += freqs[char]
    return score


def score_word_props(word: str, freqs: dict) -> float:
    """Gives a relative score for a give word based on the proportion 
    of words in the word list that contain its letters.
    """
    word = ''.join(set(word))
    score = 0
    f = lambda x: 50 - x * 10

    for char in word:
        score += f(freqs[char])

    return score


def best_word_freqs(word_list: list) -> str:
    """Returns the best first guess in the word list.
    """
    freqs = get_freqs(word_list)
    best_word = ''
    best_score = 0

    for word in word_list:
        score = score_word_freqs(word, freqs)
        if score > best_score:
            best_word = word
            best_score = score

    return best_word


def best_word_props(word_list: list) -> str:
    """Returns the best first guess in the word list.
    """
    props = get_props(word_list)
    best_word = ''
    best_score = 0

    for word in word_list:
        score = score_word_props(word, props)
        if score > best_score:
            best_word = word
            best_score = score

    return best_word


def get_word_list(word_list: list, data: dict) -> list:
    new_list = []

    for word in word_list:
        valid = True
        if 'exclude' in data:
            for char in data['exclude']:
                if char in word:
                    valid = False
                    break
        if 'include' in data:
            for char in data['include']:
                if char not in word:
                    valid = False
                    break
        if 'known' in data:
            for datum in data['known']:
                if word[datum['index']] != datum['letter']:
                    valid = False
                    break
        if valid:
            new_list.append(word)

    return new_list
                

def process_data(word: str, user_input: str, data: dict) -> None:
    for i in range(5):
        flag = user_input[i]
        char = word[i]
        if flag == 'B':
            if 'exclude' in data:
                if char not in data['exclude']:
                    data['exclude'].append(char)
            else:
                data['exclude'] = [char]
        elif flag == 'O':
            if 'include' in data:
                if char not in data['include']:
                    data['include'].append(char)
            else:
                data['include'] = [char]
        elif flag == 'G':
            if 'known' in data:
                already_recorded = False
                for datum in data['known']:
                    if datum['index'] == i:
                        already_recorded = True
                if not already_recorded:
                    data['known'].append({'letter': char, 'index': i})
            else:
                data['known'] = [{'letter': char, 'index': i}]


def play_manually(word_list: list) -> int:
    data = {}
    i = 0

    while True:
        i += 1
        word_list = get_word_list(word_list, data)
        guess = best_word_props(word_list)
        word_list.remove(guess)
        print(guess)
        user_input = input('> ')
        if user_input == 'correct':
            return i
        process_data(guess, user_input, data)


def check(guess: str, word: str) -> str:
    output = ['','','','','']
    for i in range(5):
        if guess[i] == word[i]:
            output[i] = 'G'
        elif guess[i] in word:
            output[i] = 'O'
        else:
            output[i] = 'B'
    return ''.join(output)


def play_automatically(word: str, word_list: list) -> int:
    data = {}
    i = 0

    while True:
        i += 1
        word_list = get_word_list(word_list, data)
        guess = best_word_props(word_list)
        word_list.remove(guess)
        user_input = check(guess, word)
        if user_input == 'GGGGG':
            return i
        process_data(guess, user_input, data)


if __name__ == '__main__':
    # r = requests.get("https://www.powerlanguage.co.uk/wordle/main.e65ce0a5.js")
    # text = r.text

    # la = re.search(r"La=(\[(.*?)\])", text)
    # ta = re.search(r"Ta=(\[(.*?)\])", text)

    # list_la = la.group(1)[2:-2].split("\",\"")
    # list_ta = ta.group(1)[2:-2].split("\",\"")


    # word_list = list_la + list_ta
    with open('word_list.pkl', 'rb') as f:
        word_list = pickle.load(f)
    print(word_list[35])
    # print('done import')
    # print(word_list[155])
    # print(word_list)
    # print(get_freqs(word_list))
    # print(best_word(word_list))
    print(play_manually(word_list))
    # print(play_automatically('radio', word_list))
    # data = []
    # i = 1
    # for word in word_list:
    #     print(word)
    #     data.append(play_automatically(word, word_list))
    #     print(f'{i}/{len(word_list)}')
    #     i+=1
    #     if i == 1000:
    #         break
    # print(f'Max: {max(data)}\nMean: {math.mean(data)}')

    # word 35 fails.

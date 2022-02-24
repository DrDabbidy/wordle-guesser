from concurrent.futures import process
import re
from webbrowser import get
import requests
import pickle
import math
import statistics

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
    props = [0 for _ in range(26)]

    for word in word_list:
        for char in word:
            props[ord(char) - 97] += 1

    return [0.5 - prop / len(word_list) for prop in props]


def score_word_freqs(word: str, freqs: dict) -> float:
    """
    Return a relative score for a give word based on 
    the frequency of letters in the word list.
    """
    word = ''.join(set(word))
    score = 0
    for char in word:
        score += freqs[char]
    return score


def score_word_props(word: str, props: list) -> float:
    """
    Return a relative score for a give word based on the proportion 
    of words in the word list that contain its letters.
    """
    word = ''.join(set(word))
    score = 0
    f = lambda x: 50 - x * 10

    for char in word:
        score += f(props[ord(char) - 97])

    return score


def best_word_freqs(word_list: list) -> str:
    """
    Return the best first guess in the word list.
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
    """
    Return the best first guess in the word list.
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


def score_word_greedy(word: str, word_list: str) -> int:
    """
    Return the score for the given word, deefined as the maximum
    possible length of the word list if this word is chosen.
    """
    lengths = {}

    for w in word_list:
        result = check(word, w)
        if result in lengths:
            lengths[result] += 1
        else:
            lengths[result] = 1

    return max(list(lengths.values()))


def best_word_greedy(full_word_list: list, cur_word_list: list) -> str:
    """
    Return the best possible word in the word list according to 
    criteria given in the scoring algorithm.
    """
    best_word = ''
    best_score = math.inf
    i=1
    for word in full_word_list:
        score = score_word_greedy(word, cur_word_list)
        if score < best_score:
            best_score = score
            best_word = word
        i+=1

    return best_word


def get_word_list(word_list: list, data: dict) -> list:
    new_list = []

    for word in word_list:
        valid = True
        for i, char in enumerate(word):
            char = ord(char) - 97
            # make sure word doesn't include excluded letters
            if data[0][char]:
                valid = False
                break
            # make sure not green letters aren't where they shouldn't be
            if data[2][i] != -1 and data[2][i] != char:
                valid = False
                break
            # make sure known letters are included
            if data[3][i][char]:
                valid = False
                break
        # make sure word includes all included letters
        for char in data[1]:
            if char not in word:
                valid = False
                break

        if valid:
            new_list.append(word)

    return new_list


def process_data(word: str, user_input: str, data: list) -> None:
    for i in range(5):
        flag = user_input[i]
        char = word[i]
        int_char = ord(word[i]) - 97

        if flag == 'B':
            # add the char to the exclude list
            data[0][int_char] = True
        elif flag == 'O':
            # add the char to the include list
            if char not in data[1]:
                data[1].append(char)
            # add the char to the not green list
            data[3][i][int_char] = True
        elif flag == 'G':
            # add the char to the green list
            data[2][i] = int_char


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


def empty_data() -> list:
    return [
        [False for _ in range(26)],
        [],
        [-1 for _ in range(5)],
        [[False for _ in range(26)] for _ in range(26)]
    ]


def play_manual(word_list: list) -> int:
    data = empty_data()
    i = 0

    while True:
        i += 1
        word_list = get_word_list(word_list, data)
        guess = best_word_props(word_list)
        word_list.remove(guess)
        print(guess)
        user_input = input('> ')
        if user_input == 'GGGGG':
            return i
        process_data(guess, user_input, data)


def play_auto(word: str, word_list: list, verbose=True) -> int:
    data = empty_data()
    i = 0

    while True:
        i += 1
        word_list = get_word_list(word_list, data)
        guess = best_word_props(word_list)
        word_list.remove(guess)
        if verbose: print(guess)
        user_input = check(guess, word)
        if user_input == 'GGGGG':
            return i
        process_data(guess, user_input, data)


def play_greedy_manual(word_list: list, ans_list: list, second_guess=None) -> int:
    data = empty_data()
    i = 0

    while True:
        i += 1
        ans_list = get_word_list(ans_list, data)

        if i > 2:
            print(ans_list)

        if len(ans_list) == 1:
            guess = ans_list[0]
        elif i == 1:
            guess = 'aesir'
        elif second_guess is not None and i == 2:
            guess = second_guess[user_input]
        else:
            guess = best_word_greedy(word_list, ans_list)
        
        try:
            ans_list.remove(guess)
        except:
            pass
        
        print(guess)
        
        user_input = input('> ')
        if user_input == 'GGGGG':
            return i
        
        process_data(guess, user_input, data)


def play_greedy_auto(word: str, word_list: list, ans_list: list, verbose=True, second_guess=None) -> int:
    data = empty_data()
    i = 0

    while True:
        i += 1
        ans_list = get_word_list(ans_list, data)
        if len(ans_list) == 1:
            guess = ans_list[0]
        elif i == 1:
            guess = 'aesir'
        elif second_guess is not None and i == 2:
            guess = second_guess[user_input]
        else:
            guess = best_word_greedy(word_list, ans_list)

        try:
            ans_list.remove(guess)
        except:
            pass

        if verbose: 
            print(guess)

        user_input = check(guess, word)
        if user_input == 'GGGGG':
            return i

        process_data(guess, user_input, data)


def get_second_words(word_list: list, ans_list: list, first_word: str) -> None:
    d = {}
    word_list.remove(first_word)

    for i, word in enumerate(ans_list):
        feedback = check(first_word, word)
        if feedback not in d:
            data = empty_data()
            process_data(first_word, feedback, data)
            d[feedback] = best_word_greedy(word_list, get_word_list(ans_list, data))
        print(i)

    with open('second_guess_two.pkl', 'wb') as g:
        pickle.dump(d, g)

def get_coloring_scheme(word_list: list) -> None:
    for w1 in word_list:
        d = {}
        for w2 in word_list:
            if w1 != w2:
                d[w2] = check(w1, w2)
        with open(f'colour_codes/{w1}_codes.pkl', 'wb') as f:
            pickle.dump(d, f)
        print(w1)


if __name__ == '__main__':
    # r = requests.get("https://www.powerlanguage.co.uk/wordle/main.e65ce0a5.js")
    # text = r.text

    # la = re.search(r"La=(\[(.*?)\])", text)
    # ta = re.search(r"Ta=(\[(.*?)\])", text)

    # list_la = la.group(1)[2:-2].split("\",\"")
    # list_ta = ta.group(1)[2:-2].split("\",\"")


    # word_list = list_ta + list_la
    # answer_list = list_la
    with open('word_list.pkl', 'rb') as f:
        word_list = pickle.load(f)
        # pickle.dump(word_list, f)
    with open('ans_list.pkl', 'rb') as f:
        ans_list = pickle.load(f)
        # pickle.dump(answer_list, f)
    with open('second_guess_two.pkl', 'rb') as f:
        second_guess_two = pickle.load(f)
    with open('second_guess.pkl', 'rb') as f:
        second_guess = pickle.load(f)

    alg = input('Algorithm: ')
    if alg == 'm':
        print(play_manual(word_list))
    elif alg == 'a':
        print(play_auto(input('Word: '), word_list))
    elif alg == 'gm':
        print(play_greedy_manual(word_list, ans_list))
    elif alg == 'ga':
        print(play_greedy_auto(input('Word: '), word_list, ans_list))
    elif alg == 'gaa':
        print(play_greedy_auto(input('Word: '), word_list, ans_list, second_guess=second_guess_two))

    # data = []
    # i = 1
    # for word in ans_list:
    #     data.append(play_greedy_auto(word, word_list, ans_list, verbose=False, second_guess=second_guess_two))
    #     print(f'{i}: {word} {data[i-1]}')
    #     i+=1
    # count = 0
    # for datum in data:
    #     if datum <= 6: 
    #         count += 1
    # print(f'mean: {statistics.mean(data)}\nmedian: {statistics.median(data)}\nmax: {max(data)}\nsuccess rate: {count / len(data)}')
    
    
    # with open('data.txt') as f:
    #     data=[]
    #     count = 0
    #     for line in f:
    #         ln = line.split(' ')
    #         word, val = ln[1], int(ln[2])
    #         data.append(val)
    #         if val < 6: 
    #             count += 1
    #         else:
    #             print(word)
    #     print(f'mean: {statistics.mean(data)}\nmedian: {statistics.median(data)}\nmax: {max(data)}\nsuccess rate: {count / len(data)}')

    # with open('data.txt') as f:
    #     with open('data.csv', 'w') as g:
    #         g.write('num_guesses\n')
    #         for line in f:
    #             g.write(line.split(' ')[2])

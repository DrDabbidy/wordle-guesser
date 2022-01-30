import re
import requests

r = requests.get("https://www.powerlanguage.co.uk/wordle/main.e65ce0a5.js")
text = r.text

la = re.search(r"La=(\[(.*?)\])", text)
ta = re.search(r"Ta=(\[(.*?)\])", text)

list_la = la.group(1)[2:-2].split("\",\"")
list_ta = ta.group(1)[2:-2].split("\",\"")

word_list = list_la + list_ta

alphabet = "abcdefghijklmnopqrstuvwqyz"
freq = []

for letter in alphabet:
    occurances = 0
    for word in word_list:
        if letter in word:
            occurances += 1
    freq.append(occurances)

print(dict(zip(alphabet, freq)))

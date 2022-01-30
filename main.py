import re
import requests

r = requests.get("https://www.powerlanguage.co.uk/wordle/main.e65ce0a5.js")
text = r.text

list_1 = re.search(r"La=\[(.*?)\]", text)
list_2 = re.search(r"Ta=\[(.*?)\]", text)

print(list_1.group())
print(list_2.group())

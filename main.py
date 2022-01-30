import requests as req

r = req.get("https://www.powerlanguage.co.uk/wordle/")
mainpage = r.text

print(mainpage)
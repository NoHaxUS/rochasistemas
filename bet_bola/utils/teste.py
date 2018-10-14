# tem cabelo grande, joga lol, nasceu de 95 pra cima; é viado

a = [1,1,1]
b = [1,1,0]
c = [0,1,0]
d = [0,1,1]

dados = [a,b,c,d]
marcacoes = [1,1,1,1]

from sklearn.naive_bayes import MultinomialNB

modelo = MultinomialNB()

modelo.fit(dados,marcacoes)

misterioso = [1,1,0]

print(modelo.predict(misterioso))
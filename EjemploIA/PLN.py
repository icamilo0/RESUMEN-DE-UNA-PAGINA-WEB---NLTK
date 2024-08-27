import bs4 as bs  
import re
import nltk
from inscriptis import get_text
from googletrans import Translator                                      # Librería para la traducción automática --v 4.0.0rc1
import requests                                                         # Librería para realizar solicitudes HTTP --v 2.32.3
from bs4 import BeautifulSoup                                           # Librería para la extracción de datos y contenidos de contenido web --v 4.12.3


# Descarga de recursos necesarios para NLTK (tokenización y stopwords)
# nltk.download('punkt_tab')    
#     La tokenización es el proceso de dividir un texto en unidades más pequeñas llamadas tokens.
#     El recurso 'punkt_tab' es un modelo que NLTK utiliza para dividir el texto en oraciones
#     (sent_tokenize) y palabras (word_tokenize). Esta descarga es crucial para que las funciones
#     como nltk.sent_tokenize (tokenización de oraciones)    y nltk.word_tokenize (tokenización de palabras
#     ) funcionen correctamente.
    
# nltk.download('stopwords')
#     Las stopwords son palabras comunes que generalmente no aportan mucho significado en un análisis
#     de texto. Esta lista se usa para excluir palabras comunes al calcular la frecuencia de las palabras
#     en el texto, mejorando la precisión al identificar las palabras clave más relevantes.
nltk.download('punkt_tab')
nltk.download('stopwords')

# Solicita el enlace de la página que deseas resumir
enlace = input('Ingrese el link de la pagina que desea resumir\n')
minLetters = int(input('Digite el mínimo de palabras que desea tener el resumen\n'))

# Se añade un User-Agent en la solicitud para evitar bloqueos (error 403)
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(enlace, headers=headers)

# Si la solicitud fue exitosa (código 200), se continúa
if response.status_code == 200:
    html = response.text                                                # Se obtiene el contenido HTML de la página
else:
    print(f"Error {response.status_code} al intentar acceder a la página.")
    exit()                                                              # Termina el programa si hay un error en la solicitud

# Convierte el contenido HTML a texto plano (sin etiquetas)
text = get_text(html)
article_text = text.replace("[ edit ]", "")                             # Limpia el texto de marcas innecesarias

# Importa métodos para la tokenización
from nltk import word_tokenize, sent_tokenize

# Limpia el texto de caracteres especiales y espacios redundantes
article_text = re.sub(r'\[[0-9]*\]', ' ', article_text)  
article_text = re.sub(r'\s+', ' ', article_text)  

# Elimina todo excepto letras y convierte múltiples espacios en uno solo
formatted_article_text = re.sub('[^a-zA-Z]', ' ', article_text )  
formatted_article_text = re.sub(r'\s+', ' ', formatted_article_text)  

# Tokeniza el artículo en oraciones
sentence_list = nltk.sent_tokenize(article_text)  

# Obtiene las palabras que no aportan al significado (stopwords) en inglés
stopwords = nltk.corpus.stopwords.words('english')

# Calcula la frecuencia de las palabras en el artículo
word_frequencies = {}  
for word in nltk.word_tokenize(formatted_article_text):  
    if word not in stopwords:                                           # Ignora las stopwords
        if word not in word_frequencies.keys():
            word_frequencies[word] = 1
        else:
            word_frequencies[word] += 1

# Obtiene la frecuencia máxima para normalizar las frecuencias de las palabras
maximum_frequncy = max(word_frequencies.values())

# Normaliza las frecuencias dividiendo cada frecuencia por la máxima
for word in word_frequencies.keys():  
    word_frequencies[word] = (word_frequencies[word]/maximum_frequncy)

# Asigna un puntaje a cada oración según la frecuencia de las palabras contenidas en ella
sentence_scores = {}  
for sent in sentence_list:  
    for word in nltk.word_tokenize(sent.lower()):
        if word in word_frequencies.keys():
            if len(sent.split(' ')) < minLetters:                       # Asegura que la oración no sea demasiado larga
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_frequencies[word]
                else:
                    sentence_scores[sent] += word_frequencies[word]

# Solicita al usuario si desea traducir el resumen generado
opc = input('¿Desea traducir el resumen? y/n \n')

# Selecciona las 7 oraciones con los puntajes más altos para formar el resumen
import heapq  
summary_sentences = heapq.nlargest(7, sentence_scores, key=sentence_scores.get)
summary = ' '.join(summary_sentences)                                   # Une las oraciones seleccionadas para formar el resumen

# Muestra el resumen, y si el usuario eligió traducir, realiza la traducción al español
if opc == 'n':
    print(summary)                                                      # Imprime el resumen en inglés
else:
    translator = Translator()                                           # Inicializa el traductor
    translate = translator.translate(summary, src="en", dest="es")      # Traduce el resumen al español
    print("***************************TRADUCCIÓN*******************************")
    print(translate.text)                                               # Muestra la traducción en pantalla

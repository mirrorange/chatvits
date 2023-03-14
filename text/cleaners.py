from text.symbols import symbols
import re
from unidecode import unidecode
import pyopenjtalk


# Regular expression matching Japanese without punctuation marks:
_japanese_characters = re.compile(r'[A-Za-z\d\u3005\u3040-\u30ff\u4e00-\u9fff\uff11-\uff19\uff21-\uff3a\uff41-\uff5a\uff66-\uff9d]')

# Regular expression matching non-Japanese characters or punctuation marks:
_japanese_marks = re.compile(r'[^A-Za-z\d\u3005\u3040-\u30ff\u4e00-\u9fff\uff11-\uff19\uff21-\uff3a\uff41-\uff5a\uff66-\uff9d]')


def custom_cleaners(text:str):
  '''Remove char not in symbols'''
  text = text.replace("Atri","アトリ").replace("ATRI","アトリ").replace("亜托莉","アトリ") # 避免她把自己的名字读成 'A'、'T'、'R'、'I'
  text = get_romaji_with_space_and_accent(text)
  text = ''.join([char for char in text if char in symbols])
  return text

def get_romaji(text):
    '''Pipeline for romanizing Japanese text.'''
    sentences = re.split(_japanese_marks, text)
    marks = re.findall(_japanese_marks, text)
    text = ''
    for i, mark in enumerate(marks):
        if re.match(_japanese_characters, sentences[i]):
            text += pyopenjtalk.g2p(sentences[i], kana=False).replace('pau','').replace(' ','')
        text += unidecode(mark).replace(' ','')
    if re.match(_japanese_characters, sentences[-1]):
        text += pyopenjtalk.g2p(sentences[-1], kana=False).replace('pau','').replace(' ','')
    if re.match('[A-Za-z]',text[-1]):
        text += '.'
    return text


def get_romaji_with_space(text):
    '''Pipeline for dividing Japanese text into romanized phrases.'''
    sentences = re.split(_japanese_marks, text)
    marks = re.findall(_japanese_marks, text)
    text = ''
    for i, sentence in enumerate(sentences):
        if re.match(_japanese_characters, sentence):
            if text != '':
                text += ' '
            labels = pyopenjtalk.extract_fullcontext(sentence)
            for n, label in enumerate(labels):
                phoneme = re.search(r'\-([^\+]*)\+', label).group(1)
                if phoneme not in ['sil','pau']:
                    text += phoneme
                else:
                    continue
                a3 = int(re.search(r"\+(\d+)/", label).group(1))
                if re.search(r'\-([^\+]*)\+', labels[n + 1]).group(1) in ['sil','pau']:
                    a2_next=-1
                else:
                    a2_next = int(re.search(r"\+(\d+)\+", labels[n + 1]).group(1))
                # Accent phrase boundary
                if a3 == 1 and a2_next == 1:
                    text += ' '
        if i<len(marks):
            text += unidecode(marks[i]).replace(' ','')
    if re.match('[A-Za-z]',text[-1]):
        text += '.'
    return text


def get_romaji_with_space_and_accent(text):
    '''Pipeline for notating accent in Japanese text.'''
    '''Reference https://r9y9.github.io/ttslearn/latest/notebooks/ch10_Recipe-Tacotron.html'''
    sentences = re.split(_japanese_marks, text)
    marks = re.findall(_japanese_marks, text)
    text = ''
    for i, sentence in enumerate(sentences):
        if re.match(_japanese_characters, sentence):
            if text!='':
                text+=' '
            labels = pyopenjtalk.extract_fullcontext(sentence)
            for n, label in enumerate(labels):
                phoneme = re.search(r'\-([^\+]*)\+', label).group(1)
                if phoneme not in ['sil','pau']:
                    text += phoneme.replace('ch','ʧ').replace('sh','ʃ').replace('cl','Q').replace('ts','ʦ')
                else:
                    continue
                n_moras = int(re.search(r'/F:(\d+)_', label).group(1))
                a1 = int(re.search(r"/A:(\-?[0-9]+)\+", label).group(1))
                a2 = int(re.search(r"\+(\d+)\+", label).group(1))
                a3 = int(re.search(r"\+(\d+)/", label).group(1))
                if re.search(r'\-([^\+]*)\+', labels[n + 1]).group(1) in ['sil','pau']:
                    a2_next=-1
                else:
                    a2_next = int(re.search(r"\+(\d+)\+", labels[n + 1]).group(1))
                # Accent phrase boundary
                if a3 == 1 and a2_next == 1:
                    text += ' '
                # Falling
                elif a1 == 0 and a2_next == a2 + 1 and a2 != n_moras:
                    text += '↓'
                # Rising
                elif a2 == 1 and a2_next == 2:
                    text += '↑'
        if i<len(marks):
            text += unidecode(marks[i]).replace(' ','')
    if re.match('[A-Za-z]',text[-1]):
        text += '.'
    return text
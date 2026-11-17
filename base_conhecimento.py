import re
import unicodedata
from datetime import datetime
from pathlib import Path

from orientacao import Orientacao


CAMPOS = [
    'id', 'categoria', 'titulo', 'palavras_chave', 'resposta',
    'documentos', 'onde', 'fonte', 'verificado_em'
]


def normalizar(texto):
    texto = unicodedata.normalize('NFD', texto.lower().strip())
    texto = ''.join(letra for letra in texto if unicodedata.category(letra) != 'Mn')
    texto = re.sub(r'[^a-z0-9\s]', ' ', texto)
    return ' ' + ' '.join(texto.split()) + ' '


class BaseConhecimento:
    def __init__(self, caminho):
        self.caminho = Path(caminho)
        self.orientacoes = []

    def carregar(self):
        self.orientacoes = []
        try:
            with open(self.caminho, 'r', encoding='utf-8-sig') as arquivo:
                cabecalho = arquivo.readline().strip().split(';')
                if cabecalho != CAMPOS:
                    print('Aviso: formato inválido em base_conhecimento.csv.')
                    return

                ids = set()
                for numero_linha, linha in enumerate(arquivo, start=2):
                    if not linha.strip():
                        continue
                    campos = linha.rstrip('\r\n').split(';')
                    if len(campos) != len(CAMPOS):
                        print(f'Aviso: linha {numero_linha} ignorada (quantidade de campos).')
                        continue
                    dados = dict(zip(CAMPOS, [campo.strip() for campo in campos]))
                    try:
                        identificador = int(dados['id'])
                        if identificador <= 0 or identificador in ids:
                            raise ValueError('identificador inválido ou repetido')
                        if any(not valor for valor in dados.values()):
                            raise ValueError('campo vazio')
                        if len([p for p in dados['palavras_chave'].split('|') if p.strip()]) < 3:
                            raise ValueError('menos de 3 palavras-chave')
                        if not dados['fonte'].startswith('https://'):
                            raise ValueError('fonte inválida')
                        datetime.strptime(dados['verificado_em'], '%Y-%m-%d')
                        orientacao = Orientacao(dados)
                    except (ValueError, TypeError) as erro:
                        print(f'Aviso: linha {numero_linha} ignorada ({erro}).')
                        continue
                    ids.add(identificador)
                    self.orientacoes.append(orientacao)
        except (OSError, UnicodeError) as erro:
            print(f'Aviso: não foi possível carregar a base: {erro}')
        if not self.orientacoes:
            print('Nenhuma orientação disponível. Verifique data/base_conhecimento.csv.')

    def categorias(self):
        return sorted({orientacao.categoria for orientacao in self.orientacoes})

    def por_categoria(self, categoria):
        return [orientacao for orientacao in self.orientacoes
                if orientacao.categoria == categoria]

    def pontuar(self, pergunta, orientacao):
        pergunta_normalizada = normalizar(pergunta)
        titulo_normalizado = normalizar(orientacao.titulo)
        pontos = 0

        for palavra_chave in orientacao.palavras_chave:
            chave = normalizar(palavra_chave).strip()
            if chave and f' {chave} ' in pergunta_normalizada:
                pontos += 3

        palavras_pergunta = set(pergunta_normalizada.split())
        palavras_titulo = set(titulo_normalizado.split())
        for palavra in palavras_pergunta:
            if len(palavra) >= 4 and palavra in palavras_titulo:
                pontos += 1
        return pontos

    def buscar(self, pergunta):
        resultados = []
        for orientacao in self.orientacoes:
            pontos = self.pontuar(pergunta, orientacao)
            if pontos > 0:
                resultados.append((pontos, orientacao))
        resultados.sort(key=lambda item: (-item[0], item[1].id))
        return resultados

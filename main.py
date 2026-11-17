from pathlib import Path

from assistente import Assistente
from base_conhecimento import BaseConhecimento


def main():
    caminho = Path(__file__).resolve().parent / 'data' / 'base_conhecimento.csv'
    base = BaseConhecimento(caminho)
    base.carregar()
    assistente = Assistente('Citizen Assist AI', base)
    assistente.executar()


if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print('\nPrograma encerrado.')

import re
import time
from datetime import datetime
from pathlib import Path


CABECALHO_HISTORICO = (
    'data;origem;pergunta;id_orientacao;encontrou;ajudou;tentativas;tempo_segundos'
)


class Assistente:
    def __init__(self, nome, base):
        self.nome = nome
        self.base = base
        self.historico = []
        self.notas_facilidade = []
        self.caminho_historico = base.caminho.parent / 'historico.csv'
        self.caminho_exportacao = base.caminho.parent / 'atendimentos.csv'
        self.historico_valido = True
        self.carregar_historico()

    @staticmethod
    def contem_dados_pessoais(pergunta):
        return '@' in pergunta or len(re.findall(r'\d', pergunta)) >= 8

    @staticmethod
    def ler_opcao(limite):
        while True:
            escolha = input('Escolha uma opção: ').strip()
            try:
                opcao = int(escolha)
            except ValueError:
                print('Opção inválida. Tente novamente.')
                continue
            if escolha.isdigit() and 0 <= opcao <= limite:
                return opcao
            print('Opção inválida. Tente novamente.')

    @staticmethod
    def ler_sim_nao(mensagem):
        while True:
            resposta = input(mensagem).strip().lower()
            if resposta in ('s', 'n'):
                return resposta == 's'
            print('Resposta inválida. Digite s ou n.')

    @staticmethod
    def esperar_voltar():
        while input('\nDigite 0 para voltar: ').strip() != '0':
            print('Opção inválida. Digite 0 para voltar.')

    def carregar_historico(self):
        try:
            with open(self.caminho_historico, 'r', encoding='utf-8-sig') as arquivo:
                if arquivo.readline().strip() != CABECALHO_HISTORICO:
                    print('Aviso: formato inválido em historico.csv. A gravação foi suspensa.')
                    self.historico_valido = False
                    return
                for numero_linha, linha in enumerate(arquivo, start=2):
                    if not linha.strip():
                        continue
                    valores = linha.rstrip('\r\n').split(';')
                    if len(valores) != 8:
                        print(f'Aviso: linha {numero_linha} do histórico ignorada.')
                        continue
                    try:
                        registro = dict(zip(CABECALHO_HISTORICO.split(';'), valores))
                        if registro['origem'] not in ('pergunta', 'categoria'):
                            raise ValueError
                        if registro['encontrou'] not in ('sim', 'nao'):
                            raise ValueError
                        if registro['ajudou'] not in ('sim', 'nao'):
                            raise ValueError
                        if int(registro['tentativas']) < 1 or float(registro['tempo_segundos']) < 0:
                            raise ValueError
                    except ValueError:
                        print(f'Aviso: linha {numero_linha} do histórico ignorada.')
                        continue
                    self.historico.append(registro)
        except FileNotFoundError:
            try:
                self.caminho_historico.parent.mkdir(parents=True, exist_ok=True)
                with open(self.caminho_historico, 'w', encoding='utf-8') as arquivo:
                    arquivo.write(CABECALHO_HISTORICO + '\n')
            except OSError as erro:
                self.historico_valido = False
                print(f'Aviso: histórico indisponível: {erro}')
        except (OSError, UnicodeError) as erro:
            self.historico_valido = False
            print(f'Aviso: não foi possível ler o histórico: {erro}')

    def registrar(self, origem, pergunta, orientacao, encontrou, ajudou, tentativas, inicio):
        registro = {
            'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'origem': origem,
            'pergunta': pergunta.replace(';', ',').replace('\r', ' ').replace('\n', ' '),
            'id_orientacao': str(orientacao.id) if orientacao else '',
            'encontrou': 'sim' if encontrou else 'nao',
            'ajudou': 'sim' if ajudou else 'nao',
            'tentativas': str(tentativas),
            'tempo_segundos': str(round(time.time() - inicio, 1))
        }
        self.historico.append(registro)
        if not self.historico_valido:
            print('Aviso: atendimento guardado só nesta execução (histórico inválido).')
            return
        try:
            with open(self.caminho_historico, 'a', encoding='utf-8') as arquivo:
                arquivo.write(';'.join(registro.values()) + '\n')
        except OSError as erro:
            print(f'Aviso: atendimento não foi gravado em disco: {erro}')

    def perguntar(self):
        print('\n=== FAZER UMA PERGUNTA ===')
        print('Digite 0 para voltar. Não informe dados pessoais.')
        inicio = time.time()
        tentativas = 0
        ultima_pergunta = ''
        while True:
            pergunta = input('\nDigite sua dúvida (0 para voltar): ').strip()
            if pergunta == '0':
                if tentativas:
                    self.registrar('pergunta', ultima_pergunta, None, False, False,
                                   tentativas, inicio)
                return
            if not pergunta:
                print('A pergunta não pode ficar vazia.')
                continue
            if self.contem_dados_pessoais(pergunta):
                print('Atenção: não digite CPF, telefone ou e-mail. Reescreva.')
                continue

            tentativas += 1
            ultima_pergunta = pergunta
            resultados = self.base.buscar(pergunta)
            if not resultados or resultados[0][0] < 3:
                print('Não encontrei uma orientação para essa dúvida.')
                print('Tente usar outras palavras ou consulte as categorias.')
                if self.ler_sim_nao('Deseja reformular a pergunta? (s/n): '):
                    continue
                self.registrar('pergunta', ultima_pergunta, None, False, False,
                               tentativas, inicio)
                return

            pontos, orientacao = resultados[0]
            confianca = 'ALTA' if pontos >= 6 else 'MÉDIA'
            print(f'\nConfiança da resposta: {confianca} ({pontos} pontos)')
            orientacao.exibir()
            alternativas = [(p, item) for p, item in resultados[1:] if p >= 3][:2]
            if alternativas:
                print('\nOutras orientações possíveis:')
                for p, item in alternativas:
                    print(f' - {item.titulo} ({p} pontos)')
            ajudou = self.ler_sim_nao('\nEssa orientação respondeu sua dúvida? (s/n): ')
            self.registrar('pergunta', ultima_pergunta, orientacao, True, ajudou,
                           tentativas, inicio)
            return

    def navegar(self):
        inicio = time.time()
        while True:
            categorias = self.base.categorias()
            print('\n=== CATEGORIAS ===')
            if not categorias:
                print('Nenhuma categoria disponível.')
                return
            for indice, categoria in enumerate(categorias, start=1):
                print(f'{indice} - {categoria}')
            print('0 - Voltar')
            escolha = self.ler_opcao(len(categorias))
            if escolha == 0:
                return
            categoria = categorias[escolha - 1]
            orientacoes = self.base.por_categoria(categoria)
            while True:
                print(f'\n=== {categoria.upper()} ===')
                for indice, orientacao in enumerate(orientacoes, start=1):
                    print(f'{indice} - {orientacao.titulo}')
                print('0 - Voltar')
                escolha_orientacao = self.ler_opcao(len(orientacoes))
                if escolha_orientacao == 0:
                    break
                orientacao = orientacoes[escolha_orientacao - 1]
                print('Confiança: orientação selecionada por categoria (sem busca por pontos).')
                orientacao.exibir()
                ajudou = self.ler_sim_nao('\nEssa orientação respondeu sua dúvida? (s/n): ')
                self.registrar('categoria', f'Consulta por categoria: {orientacao.titulo}',
                               orientacao, True, ajudou, 1, inicio)
                inicio = time.time()

    def indicadores(self):
        total = len(self.historico)
        encontrados = [r for r in self.historico if r['encontrou'] == 'sim']
        ajudaram = [r for r in self.historico if r['ajudou'] == 'sim']
        print('\n=== INDICADORES ===')
        print(f'Total de atendimentos: {total}')
        print(f'Respostas encontradas: {len(encontrados) / total * 100:.1f}%'
              if total else 'Respostas encontradas: 0.0%')
        print(f'Taxa de acerto (ajudou): {len(ajudaram) / total * 100:.1f}%'
              if total else 'Taxa de acerto (ajudou): 0.0%')
        if encontrados:
            media_tempo = sum(float(r['tempo_segundos']) for r in encontrados) / len(encontrados)
            print(f'Tempo médio para encontrar: {media_tempo:.1f} segundos')
        else:
            print('Tempo médio para encontrar: sem dados')
        if total:
            media_tentativas = sum(int(r['tentativas']) for r in self.historico) / total
            print(f'Tentativas por atendimento: {media_tentativas:.2f}')
        else:
            print('Tentativas por atendimento: sem dados')
        if self.notas_facilidade:
            media_nota = sum(self.notas_facilidade) / len(self.notas_facilidade)
            print(f'Facilidade de uso (nesta execução): {media_nota:.1f}/5')
        else:
            print('Facilidade de uso: ainda não avaliada nesta execução')
        print('Dúvidas sem solução:')
        sem_solucao = [r['pergunta'] for r in self.historico
                       if r['encontrou'] == 'nao' or r['ajudou'] == 'nao']
        if sem_solucao:
            for pergunta in sem_solucao:
                print(f' - {pergunta}')
        else:
            print(' - Nenhuma')

    def exportar_csv(self):
        try:
            with open(self.caminho_exportacao, 'w', encoding='utf-8') as arquivo:
                arquivo.write(CABECALHO_HISTORICO + '\n')
                for registro in self.historico:
                    arquivo.write(';'.join(registro[campo]
                                           for campo in CABECALHO_HISTORICO.split(';')) + '\n')
            print(f'Atendimentos exportados: {self.caminho_exportacao}')
        except OSError as erro:
            print(f'Não foi possível exportar: {erro}')

    def avaliar_facilidade(self):
        while True:
            nota = input('De 1 a 5, qual a facilidade de uso do assistente? ').strip()
            if nota in ('1', '2', '3', '4', '5'):
                self.notas_facilidade.append(int(nota))
                return
            print('Nota inválida. Digite um número de 1 a 5.')

    def executar(self):
        while True:
            print(f'\n=== {self.nome.upper()} ===')
            print('1 - Fazer uma pergunta')
            print('2 - Consultar por categoria')
            print('3 - Ver indicadores')
            print('4 - Exportar atendimentos para CSV')
            print('0 - Sair')
            escolha = self.ler_opcao(4)
            if escolha == 0:
                self.avaliar_facilidade()
                self.indicadores()
                print('Atendimento encerrado.')
                break
            if escolha == 1:
                self.perguntar()
            elif escolha == 2:
                self.navegar()
            elif escolha == 3:
                self.indicadores()
                self.esperar_voltar()
            elif escolha == 4:
                self.exportar_csv()
                self.esperar_voltar()

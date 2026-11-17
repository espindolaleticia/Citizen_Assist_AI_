class Orientacao:
    def __init__(self, dados):
        self.id = int(dados['id'])
        self.categoria = dados['categoria']
        self.titulo = dados['titulo']
        self.palavras_chave = dados['palavras_chave'].split('|')
        self.resposta = dados['resposta']
        self.documentos = dados['documentos'].split('|')
        self.onde = dados['onde']
        self.fonte = dados['fonte']
        self.verificado_em = dados['verificado_em']

    def exibir(self):
        print(f'\n>> {self.titulo} [{self.categoria}]')
        print(self.resposta)
        print('\nDocumentos necessários:')
        for documento in self.documentos:
            print(f' - {documento}')
        print(f'Onde: {self.onde}')
        print(f'Fonte: {self.fonte} (verificado em {self.verificado_em})')
        print('Aviso: este assistente NÃO é um canal oficial.')

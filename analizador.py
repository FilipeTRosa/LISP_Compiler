# =============================================================
# ANALISADOR LÉXICO, SINTÁTICO E MÁQUINA VIRTUAL PARA LISP
# Projeto Integrador III - UNIPAMPA
# Grupo 9 - Filipe Rosa e Lucas Moreira
# =============================================================

import ply.lex as lex
import ply.yacc as yacc
import pprint
import sys
import os

# Nomes dos arquivos de saída (Globais)
ARQ_IN = 'codigo_fonte.lisp'
ARQ_TOKENS = 'saida_lexer.txt'
ARQ_AST = 'saida_parser_ast.txt'
ARQ_COD = 'saida_codigo_intermediario.txt'

# =============================================================
# 1. ANALISADOR LÉXICO (LEXER)
# =============================================================

# Dicionário de palavras reservadas
reserved = {
    'div' : 'DIVISAOINT', 'mod' : 'RESTO', 'gt' : 'MAIOR', 'lt' : 'MENOR',
    'geq' : 'MAIORIGUAL', 'leq' : 'MENORIGUAL', 'eq' : 'IGUAL', 'neq' : 'DIFERENTE',
    'cond' : 'COND', 'and' : 'AND', 'or' : 'OR', 'not' : 'NOT',
    'defun' : 'DEFUN', 'nil' : 'NIL', 'car' : 'CAR', 'cdr' : 'CDR',
    'cons' : 'CONS', 'if' : 'IF', 'print': 'PRINT'
}

tokens = [
    'IDENTIFICADOR', 'NUMERO', 'MAIS', 'MENOS', 
    'DIVISAO', 'MULTIPLICACAO', 'PARENTESE_ESQ', 'PARENTESE_DIR'
] + list(reserved.values())

t_MAIS, t_MENOS = r'\+', r'-'
t_DIVISAO, t_MULTIPLICACAO = r'/', r'\*'
t_PARENTESE_ESQ, t_PARENTESE_DIR = r'\(', r'\)'
t_ignore = ' \t'

def t_NUMERO(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_IDENTIFICADOR(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value.lower(), 'IDENTIFICADOR')
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Caractere ilegal '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()

# =============================================================
# 2. ANALISADOR SINTÁTICO (PARSER)
# =============================================================

start = 'programa'

def p_programa(p):
    '''programa : programa expressao
                | expressao'''
    if len(p) == 3: p[0] = p[1] + [p[2]]
    else: p[0] = [p[1]]

def p_expressao(p):
    '''expressao : atomo
                 | definicao_funcao
                 | expressao_if
                 | expressao_aritmetica
                 | expressao_comparacao
                 | expressao_logica
                 | expressao_lista
                 | expressao_io
                 | lista_generica'''
    p[0] = p[1]

def p_atomo(p):
    '''atomo : NUMERO
             | IDENTIFICADOR
             | NIL'''
    p[0] = p[1]

def p_expressao_aritmetica(p):
    '''expressao_aritmetica : PARENTESE_ESQ op_aritmetico lista_de_expressoes PARENTESE_DIR'''
    p[0] = (p[2], p[3]) 

def p_op_aritmetico(p):
    '''op_aritmetico : MAIS
                     | MENOS
                     | MULTIPLICACAO
                     | DIVISAOINT
                     | DIVISAO
                     | RESTO'''
    p[0] = p[1]

def p_expressao_comparacao(p):
    '''expressao_comparacao : PARENTESE_ESQ op_comparacao expressao expressao PARENTESE_DIR'''
    p[0] = (p[2], p[3], p[4])

def p_op_comparacao(p):
    '''op_comparacao : IGUAL
                     | DIFERENTE
                     | MAIOR
                     | MENOR
                     | MAIORIGUAL
                     | MENORIGUAL'''
    p[0] = p[1]

def p_expressao_logica(p):
    '''expressao_logica : PARENTESE_ESQ NOT expressao PARENTESE_DIR
                        | PARENTESE_ESQ AND expressao expressao PARENTESE_DIR
                        | PARENTESE_ESQ OR expressao expressao PARENTESE_DIR'''
    if p[2].lower() == 'not': p[0] = (p[2], p[3])
    else: p[0] = (p[2], p[3], p[4])

def p_expressao_lista(p):
    '''expressao_lista : PARENTESE_ESQ CAR expressao PARENTESE_DIR
                       | PARENTESE_ESQ CDR expressao PARENTESE_DIR
                       | PARENTESE_ESQ CONS expressao expressao PARENTESE_DIR'''
    if p[2].lower() == 'cons': p[0] = (p[2], p[3], p[4])
    else: p[0] = (p[2], p[3])

def p_expressao_io(p):
    '''expressao_io : PARENTESE_ESQ PRINT expressao PARENTESE_DIR'''
    p[0] = (p[2], p[3])

def p_definicao_funcao(p):
    'definicao_funcao : PARENTESE_ESQ DEFUN IDENTIFICADOR lista_parametros expressao PARENTESE_DIR'
    p[0] = ('defun', p[3], p[4], p[5])

def p_lista_parametros(p):
    'lista_parametros : PARENTESE_ESQ lista_de_expressoes PARENTESE_DIR'
    p[0] = p[2]

def p_expressao_if(p):
    'expressao_if : PARENTESE_ESQ IF expressao expressao expressao PARENTESE_DIR'
    p[0] = ('if', p[3], p[4], p[5])

def p_lista_generica(p):
    'lista_generica : PARENTESE_ESQ lista_de_expressoes PARENTESE_DIR'
    p[0] = p[2]

def p_lista_de_expressoes(p):
    '''lista_de_expressoes : expressao lista_de_expressoes
                           | ''' 
    if len(p) == 3: p[0] = [p[1]] + p[2]
    else: p[0] = []

def p_error(p):
    if p: print(f"Erro de sintaxe: '{p.value}' linha {p.lineno}")
    else: print("Erro de sintaxe: fim inesperado.")

parser = yacc.yacc()

# =============================================================
# 3. GERADOR DE CÓDIGO INTERMEDIÁRIO
# =============================================================

codigo_intermediario = []
tabela_global_funcoes = {}

mapa_op = {
    '+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV', 'div': 'DIV', 'mod': 'MOD',
    'eq': 'EQ', 'gt': 'GT', 'lt': 'LT', 'geq': 'GEQ', 'leq': 'LEQ', 'neq': 'NEQ',
    'car': 'CAR', 'cdr': 'CDR', 'cons': 'CONS',
    'not': 'NOT', 'and': 'AND', 'or': 'OR', 'print': 'PRINT'
}

def gerar_codigo(node, escopo_local=None):
    if escopo_local is None: escopo_local = {}

    if not isinstance(node, (list, tuple)):
        if isinstance(node, int): codigo_intermediario.append(f'PUSH {node}')
        elif isinstance(node, str):
            if node in escopo_local: codigo_intermediario.append(f'LOAD_PARAM {escopo_local[node]}')
            elif node == 'nil': codigo_intermediario.append('PUSH_NIL')
            else: codigo_intermediario.append(f'PUSH_LITERAL {node}')
        return

    if not node:
        codigo_intermediario.append('PUSH_NIL')
        return

    op = node[0]

    if op == 'defun':
        nome, params, corpo = node[1], node[2], node[3]
        label = f'FUNC_{nome.upper()}'
        tabela_global_funcoes[nome] = {'label': label, 'n_params': len(params)}
        novo_escopo = {nome: i for i, nome in enumerate(params)}
        
        fim_func = f'END_FUNC_{nome.upper()}'
        codigo_intermediario.append(f'JUMP {fim_func}')
        codigo_intermediario.append(f'{label}:')
        gerar_codigo(corpo, novo_escopo)
        codigo_intermediario.append('RET')
        codigo_intermediario.append(f'{fim_func}:')
        
    elif op == 'if':
        cond, then_b, else_b = node[1], node[2], node[3]
        lbl_else = f'L_ELSE_{len(codigo_intermediario)}'
        lbl_fim = f'L_FIM_{len(codigo_intermediario)}'

        gerar_codigo(cond, escopo_local)
        codigo_intermediario.append(f'JUMP_FALSE {lbl_else}')
        gerar_codigo(then_b, escopo_local)
        codigo_intermediario.append(f'JUMP {lbl_fim}')
        codigo_intermediario.append(f'{lbl_else}:')
        gerar_codigo(else_b, escopo_local)
        codigo_intermediario.append(f'{lbl_fim}:')

    else:
        # Tratamento de argumentos
        lista_args = []
        if op in ['+', '-', '*', '/', 'div', 'mod']:
             if isinstance(node, tuple) and len(node) == 2 and isinstance(node[1], list):
                 lista_args = node[1]
             else:
                 lista_args = node[1:]
        else:
             lista_args = node[1:]

        for arg in lista_args:
            gerar_codigo(arg, escopo_local)

        if op in mapa_op:
            codigo_intermediario.append(mapa_op[op])
        elif op in tabela_global_funcoes:
            lbl = tabela_global_funcoes[op]['label']
            codigo_intermediario.append(f'CALL {lbl}')
        else:
             codigo_intermediario.append(f'CALL_BY_NAME {op}')

# =============================================================
# 4. MÁQUINA VIRTUAL (AMBIENTE DE EXECUÇÃO)
# =============================================================

class MaquinaVirtual:
    def __init__(self, tabela_funcoes):
        self.codigo = []
        self.labels = {}
        self.tabela_funcoes = tabela_funcoes
        self.ip = 0 
        self.stack = [] 
        self.call_stack = [] 
        self.local_scope = [] 

    def adicionar_codigo_e_executar(self, texto_novo):
        lines = texto_novo.split('\n')
        inicio_execucao = len(self.codigo)
        
        for line in lines:
            line = line.strip()
            if not line: continue
            if line.endswith(':'):
                self.labels[line[:-1]] = len(self.codigo)
            else:
                self.codigo.append(line)
        
        self.ip = inicio_execucao
        self.run()

    def run(self):
        
        while self.ip < len(self.codigo):
            line = self.codigo[self.ip]
            parts = line.split()
            op = parts[0]
            arg = parts[1] if len(parts) > 1 else None
            
            if op == 'PUSH': self.stack.append(int(arg))
            elif op == 'PUSH_LITERAL': self.stack.append(arg)
            elif op == 'PUSH_NIL': self.stack.append([])
            elif op == 'LOAD_PARAM': self.stack.append(self.local_scope[int(arg)])
            
            elif op == 'ADD': b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a + b)
            elif op == 'SUB': b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a - b)
            elif op == 'MUL': b, a = self.stack.pop(), self.stack.pop(); self.stack.append(a * b)
            elif op == 'DIV': b, a = self.stack.pop(), self.stack.pop(); self.stack.append(int(a / b))
            
            elif op == 'EQ':
                b, a = self.stack.pop(), self.stack.pop()
                self.stack.append(1 if a == b else [])
            
            elif op == 'CAR':
                lst = self.stack.pop()
                self.stack.append(lst[0] if lst else [])
            elif op == 'CDR':
                lst = self.stack.pop()
                self.stack.append(lst[1:] if lst else [])
            elif op == 'CONS':
                b, a = self.stack.pop(), self.stack.pop()
                if isinstance(b, list): self.stack.append([a] + b)
                else: self.stack.append([a, b])

            elif op == 'JUMP':
                self.ip = self.labels[arg]
                continue
            elif op == 'JUMP_FALSE':
                val = self.stack.pop()
                if not val or val == []:
                    self.ip = self.labels[arg]
                    continue
            
            elif op == 'CALL' or op == 'CALL_BY_NAME':
                func_name = arg
                if op == 'CALL_BY_NAME':
                    for nome, dados in self.tabela_funcoes.items():
                        if nome == arg:
                             func_name = dados['label']
                             break
                        if dados['label'] == arg:
                             func_name = arg
                             break
                
                nome_real = None
                for n, d in self.tabela_funcoes.items():
                    if d['label'] == func_name:
                        nome_real = n
                        break
                
                if nome_real and nome_real in self.tabela_funcoes:
                    meta = self.tabela_funcoes[nome_real]
                    n_params = meta['n_params']
                    novos_args = []
                    for _ in range(n_params):
                        if self.stack: novos_args.insert(0, self.stack.pop())
                        else: novos_args.insert(0, [])
                    
                    self.call_stack.append((self.ip + 1, self.local_scope))
                    self.local_scope = novos_args
                    self.ip = self.labels[meta['label']]
                    continue
                else:
                    print(f"Erro Runtime: Função '{arg}' não encontrada.")
                    self.ip += 1
                    continue

            elif op == 'RET':
                ret_ip, old_scope = self.call_stack.pop()
                self.local_scope = old_scope
                self.ip = ret_ip
                continue
            
            elif op == 'PRINT':
                if self.stack:
                    val = self.stack.pop()
                    print(f"=> {val}")
                else:
                    print("=> (Vazio)")

            self.ip += 1

# =============================================================
# 5. UTILITÁRIOS E MAIN
# =============================================================

# FUNÇÃO DESENHAR_ARVORE
def desenhar_arvore(node, level=0):
    indent = "  " * level
    if not isinstance(node, (list, tuple)):
        print(f"{indent}'-' {repr(node)}")
        return
    if not node:
        print(f"{indent}- NIL")
        return
    print(f"{indent}+ [{repr(node[0])}]")
    for filho in node[1:]:
        desenhar_arvore(filho, level + 1)

# =============================================================
# 6. SHELL INTERATIVO 
# =============================================================

def shell_interativo(vm):
    print("\n[+] Modo Interativo LISP (Digite 'sair' para encerrar)")
    print(f"[+] Saídas estão sendo salvas em '{ARQ_TOKENS}' e '{ARQ_COD}'.")
    
    while True:
        try:
            texto = input("\nLISP > ")
            if texto.lower() in ['sair', 'exit', 'quit']:
                break
            if not texto.strip(): continue

            # --- 1. Captura Tokens para Log (APPEND) ---
            log_lexer = lex.lex()
            log_lexer.input(texto)
            tokens_log = []
            for tok in log_lexer:
                tokens_log.append(str(tok))
            
            if tokens_log:
                with open(ARQ_TOKENS, 'a', encoding='utf-8') as f:
                    f.write('\n' + '\n'.join(tokens_log))

            # --- 2. Lexer/Parser para Execução ---
            novo_lexer = lex.lex()
            novo_lexer.input(texto)
            ast = parser.parse(texto, lexer=novo_lexer)

            if ast:
                tam_antes = len(codigo_intermediario)
                
                for expr in ast:
                    gerar_codigo(expr)
                
                novo_codigo_lista = codigo_intermediario[tam_antes:]
                novo_codigo_texto = '\n'.join(novo_codigo_lista)
                
                # --- 3. Salva Código Intermediário para Log (APPEND) ---
                if novo_codigo_texto:
                    with open(ARQ_COD, 'a', encoding='utf-8') as f:
                        f.write('\n' + novo_codigo_texto)
                    
                    # --- 4. Executa na VM ---
                    vm.adicionar_codigo_e_executar(novo_codigo_texto)
            
        except Exception as e:
            print(f"Erro: {e}")

if __name__ == "__main__":
    # Inicializa arquivos de log vazios
    open(ARQ_TOKENS, 'w', encoding='utf-8').close()
    open(ARQ_AST, 'w', encoding='utf-8').close() 
    open(ARQ_COD, 'w', encoding='utf-8').close()

    try:
        with open(ARQ_IN, 'r', encoding='utf-8') as f: data = f.read()
    except FileNotFoundError:
        data = ""
        print(f"Aviso: '{ARQ_IN}' não encontrado. Iniciando vazio.")

    # Se o arquivo estiver vazio
    if not data.strip():
        print("--- Arquivo de entrada vazio ou inexistente ---")
        print("Iniciando VM vazia...")
        vm = MaquinaVirtual(tabela_global_funcoes)
        shell_interativo(vm)
    
    else:
        print(f"--- Carregando '{ARQ_IN}' ---")
        
        # 1. Lexer
        lexer.input(data)
        lista_tokens = []
        for tok in lexer: lista_tokens.append(str(tok))
        with open(ARQ_TOKENS, 'w', encoding='utf-8') as f: f.write('\n'.join(lista_tokens))
        
        # 2. Parser
        lexer.input(data)
        ast = parser.parse(data, lexer=lexer)
        
        if ast:
            # --- GERAÇÃO DO ARQUIVO DA AST 
            with open(ARQ_AST, 'w', encoding='utf-8') as f:
                f.write("=== Árvore de Sintaxe Abstrata (AST) ===\n")
                f.write(pprint.pformat(ast, indent=2, width=120))
                f.write("\n\n=== Visualização Gráfica ===\n")
                
                # Redireciona o print da função desenhar_arvore para o arquivo
                original_stdout = sys.stdout
                sys.stdout = f
                for expr in ast:
                    desenhar_arvore(expr)
                sys.stdout = original_stdout # Devolve o print para o terminal
            
            print(f"--> AST salva em '{ARQ_AST}'")

            # 3. Gerador
            for expr in ast: gerar_codigo(expr)
            cod_inicial = '\n'.join(codigo_intermediario)
            with open(ARQ_COD, 'w', encoding='utf-8') as f: f.write(cod_inicial)
            
            # 4. VM
            vm = MaquinaVirtual(tabela_global_funcoes)
            vm.adicionar_codigo_e_executar(cod_inicial)
            
            # Entra no shell
            shell_interativo(vm)
        else:
            print("Erro ao processar o arquivo inicial. Verifique a sintaxe.")
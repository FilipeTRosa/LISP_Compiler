# =============================================================
# ANALISADOR LÉXICO E SINTÁTICO PARA LINGUAGEM LISP-LIKE
# Projeto Integrador III - UNIPAMPA
# Grupo 9 - Filipe Rosa e Lucas Moreira
# =============================================================

import ply.lex as lex
import ply.yacc as yacc
import pprint

# =============================================================
# 1. ANALISADOR LÉXICO (LEXER)
# =============================================================

# Dicionário de palavras reservadas
reserved = {
   'div' : 'DIVISAOINT',
   'mod' : 'RESTO',
   'gt' : 'MAIOR',
   'lt' : 'MENOR',
   'geq' : 'MAIORIGUAL',
   'leq' : 'MENORIGUAL',
   'eq' : 'IGUAL',
   'neq' : 'DIFERENTE',
   'cond' : 'COND',
   'and' : 'AND',
   'or' : 'OR',
   'not' : 'NOT',
   'defun' : 'DEFUN',
   'nil' : 'NIL',
   'car' : 'CAR',
   'cdr' : 'CDR',
   'cons' : 'CONS',
   'if' : 'IF'
}

# Lista de todos os tokens (incluindo os reservados)
tokens = [
    'IDENTIFICADOR', 
    'NUMERO', 
    'MAIS', 
    'MENOS',
    'DIVISAO', 
    'MULTIPLICACAO', 
    'PARENTESE_ESQ', 
    'PARENTESE_DIR'
] + list(reserved.values())

# --- Regras de Expressões Regulares para tokens simples ---
t_MAIS          = r'\+'
t_MENOS         = r'-'
t_DIVISAO       = r'/'
t_MULTIPLICACAO = r'\*'
t_PARENTESE_ESQ = r'\('
t_PARENTESE_DIR = r'\)'
t_ignore        = ' \t' # Ignorar espaços e tabulações

# --- Funções para regras de tokens complexas ---
def t_NUMERO(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_IDENTIFICADOR(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    # Verifica se a palavra é reservada, senão é um identificador comum
    t.type = reserved.get(t.value.lower(), 'IDENTIFICADOR')
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Caractere ilegal '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.skip(1)

# --- Construção do Lexer ---
lexer = lex.lex()

# =============================================================
# 2. ANALISADOR SINTÁTICO (PARSER)
# =============================================================

# Regra inicial da gramática. O parser começa por aqui.
start = 'programa'

def p_programa(p):
    'programa : expressao'
    p[0] = p[1]
    print("--- ANÁLISE SINTÁTICA CONCLUÍDA ---")
    print(p[0])

# expressão
def p_expressao(p):
    '''expressao : atomo
                 | definicao_funcao
                 | expressao_if
                 | lista_generica'''
    p[0] = p[1]

#REGRA PARA ÁTOMOS
def p_atomo(p):
    '''atomo : NUMERO
             | IDENTIFICADOR
             | MAIS 
             | MENOS 
             | MULTIPLICACAO 
             | DIVISAO
             | DIVISAOINT 
             | RESTO
             | MAIOR 
             | MENOR 
             | MAIORIGUAL 
             | MENORIGUAL
             | IGUAL 
             | DIFERENTE
             | COND 
             | AND 
             | OR 
             | NOT
             | NIL 
             | CAR 
             | CDR 
             | CONS'''
    p[0] = p[1]

# REGRA ESPECÍFICA para (defun ...)
def p_definicao_funcao(p):
    'definicao_funcao : PARENTESE_ESQ DEFUN IDENTIFICADOR lista_parametros expressao PARENTESE_DIR'
    p[0] = ('defun', p[3], p[4], p[5]) # (defun, nome, (params), corpo)

def p_lista_parametros(p):
    'lista_parametros : PARENTESE_ESQ lista_de_expressoes PARENTESE_DIR'
    p[0] = p[2]

# REGRA ESPECÍFICA para (if ...) 
def p_expressao_if(p):
    'expressao_if : PARENTESE_ESQ IF expressao expressao expressao PARENTESE_DIR'
    p[0] = ('if', p[3], p[4], p[5]) # (if, condição, bloco_then, bloco_else)

# REGRA GENÉRICA para qualquer outra lista
def p_lista_generica(p):
    'lista_generica : PARENTESE_ESQ lista_de_expressoes PARENTESE_DIR'
    # O valor é a própria lista de itens
    p[0] = p[2]

# --- Regras para construir a lista de itens dentro dos parênteses ---

def p_lista_de_expressoes_multipla(p):
    'lista_de_expressoes : expressao lista_de_expressoes'
    p[0] = [p[1]] + p[2]

def p_lista_de_expressoes_unica(p):
    'lista_de_expressoes : expressao'
    p[0] = [p[1]]

def p_lista_de_expressoes_vazia(p):
    'lista_de_expressoes : '
    p[0] = []

# --- Tratamento de Erro Sintático ---
def p_error(p):
    if p:
        print(f"Erro de sintaxe no token '{p.value}', tipo '{p.type}', na linha {p.lineno}")
    else:
        print("Erro de sintaxe: fim inesperado do código!")

# --- CONSTRUÇÃO DO PARSER ---
parser = yacc.yacc()

#Funcao para imprimir a arvore
def desenhar_arvore(node, level=0):
    """
    Função recursiva para desenhar a AST de forma gráfica no terminal.
    """
    indentacao = "  " * level  
    if not isinstance(node, (list, tuple)):
        print(f"{indentacao}'-' {repr(node)}") 
        return
    print(f"{indentacao}+ [{repr(node[0])}]")
    for filho in node[1:]:
        desenhar_arvore(filho, level + 1)

# =============================================================
# 3. BLOCO DE TESTE PRINCIPAL
# =============================================================
if __name__ == "__main__":
    
    ARQUIVO_ENTRADA = 'codigo_fonte.lisp'
    ARQUIVO_SAIDA_LEXER = 'saida_lexer.txt'
    ARQUIVO_SAIDA_PARSER = 'saida_parser_ast.txt'

    # --- LER O ARQUIVO DE ENTRADA ---
    try:
        with open(ARQUIVO_ENTRADA, 'r', encoding='utf-8') as f_in:
            data = f_in.read()
        print(f"Lendo código de '{ARQUIVO_ENTRADA}'...")
    except FileNotFoundError:
        print(f"ERRO: Arquivo de entrada '{ARQUIVO_ENTRADA}' não foi encontrado.")
        exit()

    # --- 1. PROCESSAR E EXIBIR SAÍDA DO LEXER ---
    print("\n--- INICIANDO ANÁLISE LÉXICA ---")
    lexer.input(data)
    
    # Guarda a representação em string de cada token em uma lista
    saida_lexer_lista = []
    for tok in lexer:
        saida_lexer_lista.append(str(tok))

    # Junta a lista em uma única string com quebras de linha
    saida_lexer_string = '\n'.join(saida_lexer_lista)

    # Imprime no terminal
    print(saida_lexer_string)

    # Salva no arquivo .txt
    with open(ARQUIVO_SAIDA_LEXER, 'w', encoding='utf-8') as f_out:
        f_out.write(saida_lexer_string)
    print(f"--> Saída do Lexer também foi salva em '{ARQUIVO_SAIDA_LEXER}'")

    # --- 2. PROCESSAR E EXIBIR SAÍDA DO PARSER ---
    print("\n--- INICIANDO ANÁLISE SINTÁTICA ---")
    
    # O parser.parse(data) automaticamente reinicia o lexer
    resultado_ast = parser.parse(data)
    
    if resultado_ast:
        # Usa pprint para formatar a árvore de forma legível
        #pprint.pformat(resultado_ast, indent=2) #retorna a string formatada
        saida_parser_string = pprint.pformat(resultado_ast, indent=2, width=120)

        # Imprime no terminal
        print("Árvore de Sintaxe Abstrata (AST) gerada:")
        print(saida_parser_string)

        # Salva no arquivo .txt
        with open(ARQUIVO_SAIDA_PARSER, 'w', encoding='utf-8') as f_out:
            f_out.write(saida_parser_string)
        print(f"--> Saída do Parser (AST) também foi salva em '{ARQUIVO_SAIDA_PARSER}'")
        print("\n--- Visualização da AST em formato de árvore ---")
        desenhar_arvore(resultado_ast)
    else:
        print("Análise sintática falhou ou não produziu resultado.")


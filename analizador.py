# =============================================================
# ANALISADOR LÉXICO PARA LINGUAGEM LISP
# =============================================================

import ply.lex as lex
import ply.yacc as yacc

# ----------------- ANALISADOR LÉXICO (LEXER) -----------------

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
    'LETRA', 
    'IDENTIFICADOR', 
    'NUMERO', 
    'MAIS', 
    'MENOS',
    'DIVISAO', 
    'MULTIPLICACAO', 
    'PARENTESE_ESQ', 
    'PARENTESE_DIR'
] + list(reserved.values())

# --- Regras de Expressões Regulares ---

# Para tokens simples que são símbolos
t_MAIS          = r'\+'
t_MENOS         = r'-'
t_DIVISAO       = r'/'
t_MULTIPLICACAO = r'\*'
t_PARENTESE_ESQ = r'\('
t_PARENTESE_DIR = r'\)'
t_ignore        = ' \t' # Ignorar espaços e tabulações

# Regra para letra
t_LETRA = r'[a-zA-Z]'

# --- Funções para regras complexas ---

def t_NUMERO(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_IDENTIFICADOR(t): #Provavelmente já cobre o tokien letra (redundante)
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value.lower(), 'IDENTIFICADOR') # .lower() para não diferenciar maiúsculas/minúsculas
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Caractere ilegal '{t.value[0]}' na linha {t.lexer.lineno}")
    t.lexer.skip(1)

# --- CONSTRUÇÃO DO LEXER ---
#Chamada simples parao lexer
lexer = lex.lex()

# =============================================================
# CÓDIGO PARA RODAR O TESTE
# =============================================================

# --- LÓGICA PRINCIPAL ---
if __name__ == "__main__":
    
    ARQUIVO_ENTRADA = 'codigo_fonte.lisp'
    ARQUIVO_SAIDA = 'tokens_saida.txt'

# --- LER O ARQUIVO DE ENTRADA ---
try:
    with open(ARQUIVO_ENTRADA, 'r', encoding='utf-8') as f_in:
        data = f_in.read()
    print(f"Lendo código de '{ARQUIVO_ENTRADA}'...")
except FileNotFoundError:
    print(f"ERRO: Arquivo de entrada '{ARQUIVO_ENTRADA}' não encontrado.")
    exit() # Encerra o script se o arquivo não existir

# --- PROCESSAR OS TOKENS ---
lexer.input(data)

lista_de_tokens = []
while True:
    tok = lexer.token()
    if not tok:
        break
    lista_de_tokens.append(str(tok))

# --- SALVAR A SAÍDA NO ARQUIVO ---
try:
    with open(ARQUIVO_SAIDA, 'w', encoding='utf-8') as f_out:
        f_out.write('\n'.join(lista_de_tokens))
    print(f"Análise concluída. Saída salva em '{ARQUIVO_SAIDA}'.")
except IOError:
    print(f"ERRO: Não foi possível escrever no arquivo de saída '{ARQUIVO_SAIDA}'.")


# imprimir todos os tokens no terminal se formatação
print(lista_de_tokens)

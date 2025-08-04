#!/usr/bin/env python3

import re
import os
from typing import List, Tuple, Optional
import graphviz

PRECEDENCE = {
    '*': 3,
    '.': 2,
    '|': 1,
}

def is_operator(c: str) -> bool:
    """Chequea si el caracter es un operador."""
    return c in "*.|"

def is_left_assoc(op: str) -> bool:
    """Chequea si el operador es asociativo por la izquierda."""
    return op != '*'

def expand_escapes(input_str: str) -> str:
    """Expande secuencias de escape en la cadena de entrada."""
    return input_str.replace('\\n', '\n').replace('\\t', '\t').replace('\\{', '{').replace('\\}', '}').replace('\\\\', '\\')

def is_literal(c: str) -> bool:
    """Chequea si el caracter es un literal (letra, digito, o epsilon)."""
    return c.isalnum() or c == 'ε'

def insert_concat_operators(regex: str) -> str:
    """Inserta operadores de concatenacion (.) donde sea necesario."""
    result = []
    i = 0
    escaped = False
    
    while i < len(regex):
        c = regex[i]
        
        if escaped:
            result.append('\\')
            result.append(c)
            escaped = False
            i += 1
            continue
            
        if c == '\\':
            escaped = True
            i += 1
            continue
            
        result.append(c)
        
        #Chequea si se necesita insertar un operador de concatenacion
        if i + 1 < len(regex):
            next_char = regex[i + 1]
            if ((is_literal(c) or c in '*)+?') and 
                (is_literal(next_char) or next_char in '(' or next_char == '\\')):
                result.append('.')
        
        i += 1
    
    return ''.join(result)

def handle_extensions(expr: str) -> str:
    """Maneja las extensiones de regex: + y ? operadores."""
    output = []
    i = 0
    escaped = False
    
    while i < len(expr):
        c = expr[i]
        
        if escaped:
            output.append('\\')
            output.append(c)
            escaped = False
            i += 1
            continue
            
        if c == '\\':
            escaped = True
            i += 1
            continue
            
        if c in '+?' and output:
            # Encuentra el grupo al que se le aplica el operador
            group = []
            if output[-1] == ')':
                # Encuentra el parentesis de apertura correspondiente
                count = 0
                j = len(output) - 1
                while j >= 0:
                    if output[j] == ')':
                        count += 1
                    elif output[j] == '(':
                        count -= 1
                    group.insert(0, output[j])
                    if count == 0:
                        output = output[:j]
                        break
                    j -= 1
            else:
                # Un solo caracter
                group = [output[-1]]
                output = output[:-1]
            
            if c == '+':
                # a+ se convierte en aa*
                output.extend(['(', *group, ')', '.', '(', *group, ')', '*'])
            elif c == '?':
                # a? se convierte en (a|ε)
                output.extend(['(', *group, '|', 'ε', ')'])
        else:
            output.append(c)
        
        i += 1
    
    return ''.join(output)

def shunting_yard(expr: str) -> Tuple[str, List[str]]:
    """Convierte la expresion infix a postfix usando el algoritmo Shunting Yard."""
    output = []
    stack = []
    steps = []
    
    i = 0
    while i < len(expr):
        c = expr[i]
        
        # Maneja caracteres escapados
        if c == '\\' and i + 1 < len(expr):
            output.append('\\')
            output.append(expr[i + 1])
            steps.append(f"Escaped char: \\{expr[i + 1]} -> Output: {''.join(output)}")
            i += 2
            continue
        
        if is_literal(c):
            output.append(c)
            steps.append(f"Token {c} -> Output: {''.join(output)}")
        elif c == '(':
            stack.append(c)
            steps.append(f"Push '(' -> Stack: {''.join(stack)}")
        elif c == ')':
            while stack and stack[-1] != '(':
                op = stack.pop()
                output.append(op)
                steps.append(f"Pop {op} -> Output: {''.join(output)}")
            if stack and stack[-1] == '(':
                stack.pop()  # Elimina '('
        elif is_operator(c):
            while stack:
                top = stack[-1]
                if (is_operator(top) and 
                    ((is_left_assoc(c) and PRECEDENCE[c] <= PRECEDENCE[top]) or 
                     (not is_left_assoc(c) and PRECEDENCE[c] < PRECEDENCE[top]))):
                    op = stack.pop()
                    output.append(op)
                    steps.append(f"Pop {op} -> Output: {''.join(output)}")
                else:
                    break
            stack.append(c)
            steps.append(f"Push {c} -> Stack: {''.join(stack)}")
        
        i += 1
    
    # Vacia el stack de operadores
    while stack:
        op = stack.pop()
        output.append(op)
        steps.append(f"Flush Stack -> Output: {''.join(output)}")
    
    return ''.join(output), steps

class ASTNode:
    """Clase nodo para el Arbol de Sintaxis Abstracta."""
    
    def __init__(self, value: str, left: Optional['ASTNode'] = None, right: Optional['ASTNode'] = None):
        self.value = value
        self.left = left
        self.right = right

def build_ast(postfix: str) -> ASTNode:
    """Construye el Arbol de Sintaxis Abstracta a partir de la expresion postfix."""
    stack = []
    
    for c in postfix:
        if c in "*":
            if len(stack) < 1:
                raise ValueError(f"Error: operator {c} without operand")
            node = ASTNode(c, left=stack.pop())
            stack.append(node)
        elif c in ".|":
            if len(stack) < 2:
                raise ValueError(f"Error: binary operator {c} without operands")
            right = stack.pop()
            left = stack.pop()
            node = ASTNode(c, left=left, right=right)
            stack.append(node)
        else:
            stack.append(ASTNode(c))
    
    if len(stack) != 1:
        raise ValueError(f"Error: malformed AST. Final stack size: {len(stack)}")
    
    return stack[0]

def export_ast_to_dot(root: ASTNode, filename: str):
    """Exporta el AST a formato DOT para visualizacion."""
    dot = graphviz.Digraph(comment='AST')
    dot.attr(rankdir='TB')
    
    def add_node(node: ASTNode, node_id: int) -> int:
        if node is None:
            return -1
        
        current_id = node_id
        dot.node(f'node{current_id}', node.value)
        
        if node.left:
            left_id = add_node(node.left, node_id + 1)
            dot.edge(f'node{current_id}', f'node{left_id}')
            node_id = left_id
        
        if node.right:
            right_id = add_node(node.right, node_id + 1)
            dot.edge(f'node{current_id}', f'node{right_id}')
            node_id = right_id
        
        return max(current_id, node_id)
    
    add_node(root, 0)
    
    try:
        import os
        dot_dir = r"C:\Program Files\Graphviz\bin"
        if os.path.exists(dot_dir):
            old_path = os.environ.get('PATH', '')
            os.environ['PATH'] = dot_dir + os.pathsep + old_path
            try:
                dot.render(filename, format='png', cleanup=True)
                print(f"AST exported to: {filename}.png")
            finally:
                os.environ['PATH'] = old_path
        else:
            dot.render(filename, format='png', cleanup=True)
            print(f"AST exported to: {filename}.png")
    except Exception as e:
        # Si el sistema Graphviz no esta disponible, solo guarda el archivo DOT
        print(f"Warning: Could not generate PNG image: {e}")
        print(f"Graphviz system executable not found. DOT file saved as: {filename}.dot")
        with open(f"{filename}.dot", 'w', encoding='utf-8') as f:
            f.write(dot.source)

def main():
    """Funcion principal para procesar expresiones regulares desde el archivo de entrada."""
    try:
        with open('input.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        for line_number, raw_line in enumerate(lines, 1):
            raw = raw_line.strip()
            if not raw:
                continue
                
            print(f"\nExpresión original ({line_number}): {repr(raw)}")
            
            # Preprocesa la expresion
            expanded = expand_escapes(raw)
            preprocessed = insert_concat_operators(handle_extensions(expanded))
            
            print(f"Preprocesada: {preprocessed}")
            
            # Convierte a postfix
            postfix, steps = shunting_yard(preprocessed)
            
            # Construye el AST
            try:
                ast = build_ast(postfix)
                
                # Exporta a DOT y genera PNG
                filename = f"ast_{line_number}"
                export_ast_to_dot(ast, filename)
                
                print(f"Resultado postfix: {postfix}")
                print("Pasos:")
                for step in steps:
                    print(f" - {step}")
                    
            except Exception as e:
                print(f"Error al construir el AST: {e}")
                print(f"Postfix resultante: {postfix}")
            
            print("-" * 40)
            
    except FileNotFoundError:
        print("Error: No se encontró el archivo input.txt")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 
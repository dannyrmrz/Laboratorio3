# Regular Expression to AST Converter

Este proyecto convierte expresiones regulares de notación infija a postfija usando el algoritmo Shunting Yard y construye Árboles de Sintaxis Abstracta (AST) para su visualización.

## Características

- Conversión de expresiones regulares de infija a postfija
- Manejo de extensiones de regex (`+` y `?`)
- Construcción de Árboles de Sintaxis Abstracta (AST)
- Visualización de AST usando Graphviz
- Procesamiento de archivos de entrada con múltiples expresiones

## Requisitos

- Python 3.7 o superior
- Graphviz (biblioteca Python y sistema)

### Instalación de dependencias

```bash
pip install -r requirements.txt
```

### Instalación de Graphviz (sistema)

#### Windows:
```bash
# Usando chocolatey
choco install graphviz

# O descargar desde: https://graphviz.org/download/
```

#### macOS:
```bash
brew install graphviz
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt-get install graphviz
```

## Uso

1. Asegúrate de tener un archivo `input.txt` con las expresiones regulares (una por línea)
2. Ejecuta el programa:

```bash
python main.py
```

## Formato de entrada

El archivo `input.txt` debe contener expresiones regulares, una por línea. Ejemplos:

```
(a*|b*)+
((ε|a)|b*)*
(a|b)*abb(a|b)*
0?(1?)?0*
```

## Salida

El programa generará:

1. **Salida en consola**: Mostrará el proceso de conversión paso a paso
2. **Archivos PNG**: Imágenes de los AST generados (`ast_1.png`, `ast_2.png`, etc.)
3. **Archivos DOT**: Archivos fuente para Graphviz (`ast_1.dot`, `ast_2.dot`, etc.)

## Funcionalidades implementadas

### 1. Preprocesamiento de expresiones
- **Manejo de escapes**: Expande secuencias de escape como `\n`, `\t`, etc.
- **Extensiones de regex**: 
  - `a+` se convierte en `aa*`
  - `a?` se convierte en `(a|ε)`
- **Inserción de concatenación**: Añade operadores de concatenación (`.`) donde sea necesario

### 2. Algoritmo Shunting Yard
- Convierte expresiones infijas a postfijas
- Maneja precedencia de operadores
- Gestiona asociatividad

### 3. Construcción de AST
- Crea árboles de sintaxis abstracta desde notación postfija
- Estructura jerárquica de nodos
- Visualización gráfica

### 4. Visualización
- Genera archivos DOT para Graphviz
- Crea imágenes PNG de los AST
- Estructura clara y legible

## Estructura del código

- `main.py`: Archivo principal con toda la lógica
- `requirements.txt`: Dependencias de Python
- `input.txt`: Archivo de entrada con expresiones regulares
- `README.md`: Este archivo de documentación

## Ejemplo de ejecución

```
Expresión original (1): '(a*|b*)+'
Preprocesada: ((a*|b*).(a*|b*)*)
Resultado postfix: a*b*|a*b*|*.
Pasos:
 - Token a -> Output: a
 - Push * -> Stack: *
 - Pop * -> Output: a*
 - Token b -> Output: a*b
 - Push * -> Stack: *
 - Pop * -> Output: a*b*
 - Push | -> Stack: |
 - Token a -> Output: a*b*|a
 - Push * -> Stack: |*
 - Pop * -> Output: a*b*|a*
 - Token b -> Output: a*b*|a*b
 - Push * -> Stack: |*
 - Pop * -> Output: a*b*|a*b*
 - Pop | -> Output: a*b*|a*b*|
 - Flush Stack -> Output: a*b*|a*b*|*.
AST exported to: ast_1.png
```

## Notas técnicas

- El programa maneja caracteres especiales como `ε` (epsilon)
- Soporta operadores de regex: `*`, `+`, `?`, `|`, `.`
- La visualización usa Graphviz para generar árboles claros y legibles
- El código está completamente documentado en español

## Video demostración
https://drive.google.com/file/d/1jUxHqOQ3vB3qXVALq1qN_BACNfTM2JaM/view?usp=sharing

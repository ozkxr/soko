# SOKO

Lenguaje SOKO.

## Requisitos

Tener previamente instalado Java, Python, pip, ANTLR(en el path):

## Generar la gramatica

Generar lexer, parser y listener Java:

```bash
antlr4 SOKO.g4
```

Generar lexer, parser y visitor Python:

```bash
antlr4 -Dlanguage=Python3 -visitor SOKO.g4
```

Estos comandos actualizan archivos como `SOKOLexer.py`, `SOKOParser.py`, `SOKOVisitor.py`, `SOKOLexer.java` y `SOKOParser.java`.

## Compilar los archivos Java

```bash
antlr4 *.java
```

La compilacion genera archivos `.class` en la misma carpeta.

## Ejecutar el test con Python

`main.py` lee `test.soko` por defecto:

```bash
python3 main.py
```
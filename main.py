from antlr4 import CommonTokenStream, InputStream
from SOKOLexer import SOKOLexer
from SOKOParser import SOKOParser
from Visitor import Visitor

def ejecutar(ruta_archivo="test.soko"):
    with open(ruta_archivo, encoding="utf-8") as archivo:
        src_code = archivo.read()

    input_stream = InputStream(src_code)
    tokens = SOKOLexer(input_stream)
    token_stream = CommonTokenStream(tokens)
    parser = SOKOParser(token_stream)
    tree = parser.program()

    if parser.getNumberOfSyntaxErrors() > 0:
        print("SYNTAX ERROR")
        return

    visitor = Visitor()
    visitor.visitProgram(tree)
    
    
if __name__ == "__main__":
    ejecutar()
    
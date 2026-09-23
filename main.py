from antlr4 import CommonTokenStream, InputStream
from SOKOLexer import SOKOLexer
from SOKOParser import SOKOParser
from Visitor import Visitor

def ejecutar():
    # codigo de prueba
    src_code = """
    # Configuración de pines
    CONFIG PIN 5 OUT
    CONFIG PIN 25 ANALOG_OUT
    CONFIG PIN 34 ANALOG_IN
    CONFIG PIN 4 IN
    """
    
    # 1. flujo de entrada
    
    input_stream = InputStream(src_code);
    # lexter y tokens
    tokens = SOKOLexer(input_stream)
    token_stream = CommonTokenStream(tokens)
    # parser y arbol
    parser = SOKOParser(token_stream)
    tree = parser.program()
    # verificacion sintaxis
    if parser.getNumberOfSyntaxErrors() > 0:
        print("SYNTAX ERROR")
        return
    # ejecutar visitor
    visitor = Visitor()
    visitor.visitProgram(tree)
    
    
if __name__ == "__main__":
    ejecutar()
    
from SOKOParser import SOKOParser
from SOKOVisitor import SOKOVisitor

class Visitor(SOKOVisitor):
    
    def visitProgram(self, ctx: SOKOParser.ProgramContext):
        
        for ctx_statement in ctx.statement():
            self.visit(ctx_statement)
        print(" Fin del recorrido, éxito")
        return None
    
    def visitConfigPin(self, ctx: SOKOParser.ConfigPinContext):
        pin = int(ctx.INT().getText())
        modo = self.visit(ctx.pinMode())


        print(f"CONFIG -> pin {pin} como {modo}")
        return None

    def visitPinMode(self, ctx: SOKOParser.PinModeContext):
        if ctx.OUT():
            return "OUT"
        elif ctx.IN():
            return "IN"
        elif ctx.ANALOG_IN():
            return "ANALOG_IN"
        elif ctx.ANALOG_OUT():
            return "ANALOG_OUT"
        raise ValueError("Modo de pin desconocido")
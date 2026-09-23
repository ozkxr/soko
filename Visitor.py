from SOKOParser import SOKOParser
from SOKOVisitor import SOKOVisitor

class Visitor(SOKOVisitor):
    
    def visitProgram(self, ctx: SOKOParser.ProgramContext):
        print("INICIO PROGRAMA")
        
        for ctx_statement in ctx.statement():
            self.visit(ctx_statement)
        print("FIN PROGRAMA")
        return None
    
    def visitConfigPin(self, ctx: SOKOParser.ConfigPinContext):
        pin = int(ctx.INT().getText())
        modo = self.visit(ctx.pinMode())


        print(f"CONFIG -> pin {pin} como {modo}")
        return None

    def visitSetPin(self, ctx: SOKOParser.SetPinContext):
        pin = ctx.INT().getText()
        value = self.visit(ctx.value())
        print(f"SET -> pin {pin} = {value}")
        return None

    def visitBucleWhile(self, ctx: SOKOParser.BucleWhileContext):
        condition = self.visit(ctx.condition())
        print(f"INICIO WHILE ({condition})")

        for ctx_statement in ctx.statement():
            self.visit(ctx_statement)

        print("FIN WHILE")
        return None

    def visitBucleRepeat(self, ctx: SOKOParser.BucleRepeatContext):
        repetitions = ctx.INT().getText()
        print(f"INICIO REPEAT ({repetitions} veces)")

        for ctx_statement in ctx.statement():
            self.visit(ctx_statement)

        print("FIN REPEAT")
        return None

    def visitCondicionalIf(self, ctx: SOKOParser.CondicionalIfContext):
        condition = self.visit(ctx.condition())
        print(f"INICIO IF ({condition})")

        else_token_index = ctx.ELSE().symbol.tokenIndex if ctx.ELSE() else None
        else_reported = False
        for statement in ctx.statement():
            if (else_token_index is not None
                    and not else_reported
                    and statement.start.tokenIndex > else_token_index):
                print("ELSE")
                else_reported = True
            self.visit(statement)

        print("FIN IF")
        return None

    def visitSleepCmd(self, ctx: SOKOParser.SleepCmdContext):
        print(f"SLEEP -> {ctx.INT().getText()} ms")
        return None

    def visitCondition(self, ctx: SOKOParser.ConditionContext):
        negation = "!" if ctx.getChild(0).getText() == "!" else ""
        pin = ctx.INT().getText()

        if ctx.comparador() and ctx.value():
            return f"{negation}PIN {pin} {ctx.comparador().getText()} {self.visit(ctx.value())}"
        return f"{negation}PIN {pin}"

    def visitValue(self, ctx: SOKOParser.ValueContext):
        if ctx.ON():
            return "ON"
        if ctx.OFF():
            return "OFF"
        return self.visit(ctx.numero())

    def visitNumero(self, ctx: SOKOParser.NumeroContext):
        return ctx.getText()

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
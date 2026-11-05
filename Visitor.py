from SOKOParser import SOKOParser
from SOKOVisitor import SOKOVisitor

class Visitor(SOKOVisitor):
    
    
    def __init__(self):
        super().__init__()
        # map si es salida o entrada
        self.pinTable = {}
        # tabla simbolos
        self.symbolTable = {}
        # log errores (linea, mensaje)
        self.errorsLog = []
        # validar pines
        self.VALID_PINS = set(range(40))

    def _report_error(self, ctx, message):
        self.errorsLog.append((ctx.start.line, message))
        print(f"ERROR SEMANTICO (linea {ctx.start.line}): {message}")

    def _pin_is_valid(self, pin, ctx):
        if pin not in self.VALID_PINS:
            self._report_error(ctx, f"el pin {pin} esta fuera de rango (0-39)")
            return False
        return True

    def _declared_mode(self, pin, ctx):
        if not self._pin_is_valid(pin, ctx):
            return None
        mode = self.pinTable.get(pin)
        if mode is None:
            self._report_error(ctx, f"el pin {pin} no fue declarado")
        return mode
    
    def visitProgram(self, ctx: SOKOParser.ProgramContext):
        print("INICIO PROGRAMA")
        
        for ctx_statement in ctx.statement():
            self.visit(ctx_statement)
        print("FIN PROGRAMA")
        return None
    
    def visitConfigPin(self, ctx: SOKOParser.ConfigPinContext):
        pin = int(ctx.INT().getText())
        modo = self.visit(ctx.pinMode())

        if not self._pin_is_valid(pin, ctx):
            return None
        if pin in self.pinTable:
            self._report_error(ctx, f"el pin {pin} ya fue declarado")
            return None

        self.pinTable[pin] = modo
        self.symbolTable[f"pin{pin}"] = modo

        print(f"CONFIG -> pin {pin} como {modo}")
        return None

    def visitSetPin(self, ctx: SOKOParser.SetPinContext):
        pin = int(ctx.INT().getText())
        value = self.visit(ctx.value())

        modo = self._declared_mode(pin, ctx)
        if modo is None:
            return None
        if modo not in {"OUT", "ANALOG_OUT"}:
            self._report_error(
                ctx,
                f"no se puede escribir el pin {pin}: fue declarado como {modo}",
            )
            return None

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
        # WHILE (TRUE): bucle infinito, no lee ningun pin
        if ctx.TRUE():
            return "TRUE"

        negation = "!" if ctx.getChild(0).getText() == "!" else ""
        pin = int(ctx.INT().getText())

        modo = self._declared_mode(pin, ctx)
        if modo is not None and modo not in {"IN", "ANALOG_IN"}:
            self._report_error(
                ctx,
                f"no se puede leer el pin {pin}: fue declarado como {modo}",
            )

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
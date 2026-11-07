from SOKOParser import SOKOParser
from SOKOVisitor import SOKOVisitor

class C3DVisitor(SOKOVisitor):
    def __init__(self):
        super().__init__()
        self.temp_count = 0
        self.label_count = 0
        self.codigo = []
        # modo de cada pin, para saber si se lee digital o analogico
        self.pinTable = {}
        # el WHILE (TRUE) que se vuelve el loop() de Arduino
        self.loop_principal = None

    def nuevo_temp(self) -> str:
        t = f"t{self.temp_count}"
        self.temp_count += 1
        return t

    def nueva_etiqueta(self, prefijo="L") -> str:
        lbl = f"{prefijo}{self.label_count}"
        self.label_count += 1
        return lbl

    def emitir(self, instruccion: str):
        self.codigo.append(instruccion)

    def _cerrar_etiqueta(self):
        # C++ no permite una etiqueta justo antes de la llave que cierra loop().
        if self.codigo and self.codigo[-1].startswith("LABEL"):
            self.emitir(f"{self.nuevo_temp()} = 0 == 0")

    def visitProgram(self, ctx: SOKOParser.ProgramContext):
        # el WHILE (TRUE) se vuelve loop() solo si es lo unico aparte de los CONFIG;
        # si no, las demas instrucciones se repetirian junto con el
        resto = [s for s in ctx.statement() if s.configPin() is None]
        if len(resto) == 1 and resto[0].bucleWhile() is not None:
            self.loop_principal = resto[0].bucleWhile()

        for statement in ctx.statement():
            self.visit(statement)
        self._cerrar_etiqueta()
        return self.codigo

    def visitConfigPin(self, ctx: SOKOParser.ConfigPinContext):
        pin = ctx.INT().getText()
        modo = ctx.pinMode().getText()
        self.pinTable[pin] = modo
        arduino = "OUTPUT" if modo in {"OUT", "ANALOG_OUT"} else "INPUT"
        self.emitir(f"CONFIG_PIN {pin}, {arduino}")
        return None

    def visitSetPin(self, ctx: SOKOParser.SetPinContext):
        pin = ctx.INT().getText()
        valor = self.visit(ctx.value())
        if ctx.value().numero() is None:
            self.emitir(f"SET_PIN {pin}, {valor}")
        else:
            self.emitir(f"ANALOG_WRITE {pin}, {valor}")
        return None

    def visitSleepCmd(self, ctx: SOKOParser.SleepCmdContext):
        self.emitir(f"SLEEP {ctx.INT().getText()}")
        return None

    def visitValue(self, ctx: SOKOParser.ValueContext):
        if ctx.ON():
            return "HIGH"
        if ctx.OFF():
            return "LOW"
        return ctx.numero().getText()

    def visitCondition(self, ctx: SOKOParser.ConditionContext):
        if ctx.TRUE():
            return "HIGH"

        pin = ctx.INT().getText()
        temp = self.nuevo_temp()
        if self.pinTable.get(pin) == "ANALOG_IN":
            self.emitir(f"{temp} = READ_ANALOG {pin}")
        else:
            self.emitir(f"{temp} = READ_DIGITAL {pin}")

        if ctx.comparador():
            lectura = temp
            temp = self.nuevo_temp()
            self.emitir(f"{temp} = {lectura} {ctx.comparador().getText()} {self.visit(ctx.value())}")

        if ctx.getChild(0).getText() == "!":
            negado = temp
            temp = self.nuevo_temp()
            self.emitir(f"{temp} = {negado} == LOW")
        return temp

    def visitCondicionalIf(self, ctx: SOKOParser.CondicionalIfContext):
        cond = self.visit(ctx.condition())

        lbl_sino = self.nueva_etiqueta("L_SINO_")
        lbl_fin = self.nueva_etiqueta("L_FIN_SI_")

        destino_falso = lbl_sino if ctx.ELSE() is not None else lbl_fin
        self.emitir(f"IF_FALSE {cond} GOTO {destino_falso}")

        # la gramatica junta THEN y ELSE en ctx.statement(): se separan por posicion
        else_index = ctx.ELSE().symbol.tokenIndex if ctx.ELSE() else None
        en_else = False
        for statement in ctx.statement():
            if else_index is not None and not en_else and statement.start.tokenIndex > else_index:
                en_else = True
                self.emitir(f"GOTO {lbl_fin}")
                self.emitir(f"LABEL {lbl_sino}:")
            self.visit(statement)

        # ELSE vacio: la etiqueta igual tiene que existir
        if ctx.ELSE() is not None and not en_else:
            self.emitir(f"GOTO {lbl_fin}")
            self.emitir(f"LABEL {lbl_sino}:")

        self.emitir(f"LABEL {lbl_fin}:")
        return None

    def visitBucleWhile(self, ctx: SOKOParser.BucleWhileContext):
        es_infinito = ctx.condition().TRUE() is not None
        if es_infinito and ctx is self.loop_principal:
            # GeneradorArduino omite las etiquetas L_LOOP_: loop() ya se repite solo
            lbl_inicio = self.nueva_etiqueta("L_LOOP_")
            self.emitir(f"LABEL {lbl_inicio}:")
            for statement in ctx.statement():
                self.visit(statement)
            self._cerrar_etiqueta()
            self.emitir(f"GOTO {lbl_inicio}")
            return None

        lbl_inicio = self.nueva_etiqueta("L_WHILE_")
        self.emitir(f"LABEL {lbl_inicio}:")
        if es_infinito:
            for statement in ctx.statement():
                self.visit(statement)
            self.emitir(f"GOTO {lbl_inicio}")
            return None

        lbl_fin = self.nueva_etiqueta("L_FIN_WHILE_")
        cond = self.visit(ctx.condition())
        self.emitir(f"IF_FALSE {cond} GOTO {lbl_fin}")
        for statement in ctx.statement():
            self.visit(statement)
        self.emitir(f"GOTO {lbl_inicio}")
        self.emitir(f"LABEL {lbl_fin}:")
        return None

    def visitBucleRepeat(self, ctx: SOKOParser.BucleRepeatContext):
        # GeneradorArduino declara cada temporal como bool nuevo, asi que no puede
        # llevar un contador: el cuerpo se copia tantas veces como indique REPEAT
        for _ in range(int(ctx.INT().getText())):
            for statement in ctx.statement():
                self.visit(statement)
        return None

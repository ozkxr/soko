class GeneradorArduino:
    def __init__(self, lista_c3d: list):
        self.c3d = lista_c3d
        self.setup_code = []
        self.loop_code = []

    def generar(self) -> str:
        for linea in self.c3d:
            linea = linea.strip()
            if not linea:
                continue

            partes = linea.split()
            instruccion = partes[0]

            if instruccion == "CONFIG_PIN":
                pin = partes[1].replace(",", "")
                modo = partes[2]
                self.setup_code.append(f"  pinMode({pin}, {modo});")

            elif instruccion == "SET_PIN":
                pin = partes[1].replace(",", "")
                estado = partes[2]
                self.loop_code.append(f"  digitalWrite({pin}, {estado});")

            elif instruccion == "ANALOG_WRITE":
                pin = partes[1].replace(",", "")
                valor = partes[2]
                self.loop_code.append(f"  analogWrite({pin}, {valor});")

            elif instruccion == "SLEEP":
                ms = partes[1]
                self.loop_code.append(f"  delay({ms});")

            elif len(partes) >= 4 and partes[2] == "READ_DIGITAL":
                temp = partes[0]
                pin = partes[3]
                self.loop_code.append(f"  {temp} = digitalRead({pin});")

            elif len(partes) >= 4 and partes[2] == "READ_ANALOG":
                temp = partes[0]
                pin = partes[3]
                self.loop_code.append(f"  {temp} = analogRead({pin});")

            elif len(partes) == 5 and partes[1] == "=":
                temp = partes[0]
                izq = partes[2]
                op = partes[3]
                der = partes[4]
                self.loop_code.append(f"  {temp} = ({izq} {op} {der});")

            elif instruccion == "IF_FALSE":
                cond = partes[1]
                label = partes[3]
                self.loop_code.append(f"  if (!{cond}) goto {label};")

            elif instruccion == "GOTO":
                label = partes[1]
                # Si es el salto del loop infinito principal, no necesitamos emitir goto en Arduino
                # porque void loop() ya se repite infinitamente por sí solo.
                if not label.startswith("L_LOOP_"):
                    self.loop_code.append(f"  goto {label};")

            elif instruccion == "LABEL":
                label = partes[1].replace(":", "")
                if not label.startswith("L_LOOP_"):
                    self.loop_code.append(f"{label}:")

        # los temporales se declaran al inicio de loop(): un goto no puede
        # saltar una declaracion con valor inicial
        temps = sorted({l.split()[0] for l in self.c3d if len(l.split()) > 1 and l.split()[1] == "="})
        if temps:
            self.loop_code.insert(0, "  int " + ", ".join(temps) + ";")

        plantilla = [
            "// ====================================================",
            "// Codigo generado automaticamente desde ArchLang (C3D)",
            "// ====================================================",
            "",
            "void setup() {",
            "\n".join(self.setup_code) if self.setup_code else "  // Sin configuraciones",
            "}",
            "",
            "void loop() {",
            "\n".join(self.loop_code) if self.loop_code else "  // Sin acciones",
            "}"
        ]

        return "\n".join(plantilla)
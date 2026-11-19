CANCELAR = "cancelar"
AYUDA_CANCELAR = "(escriba 'cancelar' para volver al menu)"

# ---------------------------------------------------------------- entrada de datos
def pedir_opcion():
    return input("Elige una opcion: ").strip()


def pedir_dato(mensaje, validar, permitir_vacio=False):
    """
    Pide un dato y REPITE la pregunta hasta que sea valido (bucle while).
    validar(valor) devuelve None si el dato es correcto o el texto del error.
    Retorna el dato, '' si esta permitido dejarlo vacio, o None si escribe 'cancelar'.
    """
    while True:
        valor = input(mensaje + " ").strip()
        if valor.lower() == CANCELAR:
            return None
        if valor == "" and permitir_vacio:
            return ""
        error = validar(valor)
        if error is None:
            return valor
        print(f"   Dato invalido: {error}")


def pedir_varios(preguntas):
    """
    preguntas: lista de (mensaje, regla, permitir_vacio).
    Retorna la lista de respuestas validas, o None si el usuario cancela.
    """
    print(AYUDA_CANCELAR)
    respuestas = []
    for mensaje, regla_dato, permitir_vacio in preguntas:
        valor = pedir_dato(mensaje, regla_dato, permitir_vacio)
        if valor is None:
            print("Operacion cancelada.")
            return None
        respuestas.append(valor)
    return respuestas


# ---------------------------------------------------------------- salida de datos
def mostrar_mensaje(texto):
    print(texto)


def mostrar_menu():
    print("\n===== SISTEMA DE ASISTENCIA - SG ARON'S EIRL =====")
    print("1. Registrar trabajador")
    print("2. Listar trabajadores")
    print("3. Buscar trabajador por codigo")
    print("4. Marcar entrada")
    print("5. Marcar salida")
    print("6. Ver asistencias de un trabajador")
    print("7. Ver todas las asistencias ordenadas por fecha")
    print("8. Contar tardanzas totales")
    print("9. Generar planilla mensual (pago por horas)")
    print("10. Exportar reporte completo a Excel")
    print("0. Salir")


def mostrar_trabajadores(empleados):
    if not empleados:
        print("No hay trabajadores registrados.")
    for e in empleados:
        print(
            f"{e['codigo']} - {e['nombres']} {e['apellidos']} - {e['cargo']} - "
            f"{e['turno']} - S/ {e['tarifa_hora']} por hora"
        )


def mostrar_trabajador_encontrado(e):
    print(
        f"Encontrado: {e['codigo']} - {e['nombres']} "
        f"{e['apellidos']} ({e['cargo']}, turno {e['turno']})"
    )


def mostrar_asistencia(r):
    """Imprime un registro de asistencia en una linea legible."""
    salida = r["hora_salida"] if r["hora_salida"] else "--:--"
    horas = r["horas_trabajadas"] if r["horas_trabajadas"] != "" else "-"
    print(
        f"{r['fecha']} | {r['codigo_empleado']} | {r['turno']:<6} | "
        f"{r['hora_entrada']} - {salida} | {horas} h | Tardanza: {r['tardanza']}"
    )


def mostrar_asistencias(registros, mensaje_vacio):
    if not registros:
        print(mensaje_vacio)
    for r in registros:
        mostrar_asistencia(r)


def mostrar_planilla(planilla, mes, total, avisos, meses_con_datos):
    """
    planilla: lista de dicts (uno por trabajador). avisos: {codigo: texto} que explican
    por que alguien sale en 0. meses_con_datos: lista de meses (vacia = no se muestra).
    """
    if not planilla:
        print("No hay trabajadores activos registrados.")
    for p in planilla:
        print(
            f"{p['codigo']} - {p['nombres']} {p['apellidos']}: "
            f"Mañana {p['horas_manana']} h + Tarde {p['horas_tarde']} h = "
            f"{p['horas_trabajadas']} h x S/ {p['tarifa_hora']} = S/ {p['pago_mensual']}"
        )
        if p["codigo"] in avisos:
            print(f"   Aviso: {avisos[p['codigo']]}")
    print(f"TOTAL PLANILLA {mes}: S/ {total}")
    if meses_con_datos:
        print("Meses con asistencias registradas: " + ", ".join(meses_con_datos))

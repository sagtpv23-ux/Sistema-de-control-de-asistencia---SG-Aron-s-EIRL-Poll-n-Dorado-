from modelos.empleado import (
    registrar_empleado,
    listar_empleados,
    ordenar_empleados_por_codigo,
    buscar_binario_recursivo,
)
from modelos.asistencia import (
    marcar_entrada,
    marcar_salida,
    buscar_asistencias_por_codigo,
    ordenar_asistencias_por_fecha,
    contar_tardanzas_recursivo,
    completar_turnos,
)
from modelos.base_datos import (
    guardar_empleados,
    cargar_empleados,
    guardar_asistencias,
    cargar_asistencias,
)
from modelos.planilla import (
    generar_planilla_mensual,
    total_planilla,
    contar_jornadas_mes,
    meses_con_datos,
)
from modelos.validaciones import (
    codigo_existe,
    normalizar_hora,
    validar_cargo,
    validar_codigo_formato,
    validar_dni,
    validar_formato_fecha,
    validar_formato_mes,
    validar_nombre,
    validar_tarifa_hora,
    validar_turno,
)
from vistas import consola as vista
from vistas.reporte_excel import exportar_a_excel


# ---------------------------------------------------------------- reglas de captura
def regla(condicion, error):
    """Crea una regla: devuelve None si el dato cumple la condicion o el mensaje de error."""
    return lambda valor: None if condicion(valor) else error


REGLA_CODIGO_FORMATO = regla(validar_codigo_formato, "use la letra E y 3 digitos (ej: E001).")
REGLA_NOMBRE = regla(validar_nombre, "solo letras y espacios (sin numeros ni simbolos como @).")
REGLA_DNI = regla(validar_dni, "el DNI debe tener exactamente 8 digitos.")
REGLA_CARGO = regla(validar_cargo, "use Parrillero, Mesero, Caja, Cocina o Administracion.")
REGLA_TURNO = regla(validar_turno, "use M (Mañana) o T (Tarde).")
REGLA_TARIFA = regla(validar_tarifa_hora, "debe ser un numero mayor que 0 (ej: 8.5).")
REGLA_FECHA = regla(validar_formato_fecha, "use AAAA-MM-DD con una fecha real (ej: 2026-09-01).")
REGLA_HORA = regla(lambda v: normalizar_hora(v) is not None, "use HH:MM en 24 horas (ej: 08:30).")
REGLA_MES = regla(validar_formato_mes, "use AAAA-MM (ej: 2026-09).")


def regla_codigo_nuevo(lista_empleados):
    """El codigo debe tener formato valido y no estar registrado."""
    def validar(valor):
        if not validar_codigo_formato(valor):
            return "use la letra E y 3 digitos (ej: E001)."
        if codigo_existe(valor, lista_empleados):
            return f"el codigo {valor.strip().upper()} ya esta registrado."
        return None
    return validar


def regla_codigo_existente(lista_empleados):
    """El codigo debe tener formato valido y pertenecer a un trabajador registrado."""
    def validar(valor):
        if not validar_codigo_formato(valor):
            return "use la letra E y 3 digitos (ej: E001)."
        if not codigo_existe(valor, lista_empleados):
            return f"no existe un trabajador con el codigo {valor.strip().upper()}."
        return None
    return validar


# ---------------------------------------------------------------- una funcion por opcion
def opcion_registrar(lista_empleados):
    datos = vista.pedir_varios([
        ("Codigo (ej: E001):", regla_codigo_nuevo(lista_empleados), False),
        ("Nombres:", REGLA_NOMBRE, False),
        ("Apellidos:", REGLA_NOMBRE, False),
        ("DNI (8 digitos):", REGLA_DNI, False),
        ("Cargo (Parrillero/Mesero/Caja/Cocina/Administracion):", REGLA_CARGO, False),
        ("Turno habitual (M=Mañana / T=Tarde):", REGLA_TURNO, False),
        ("Tarifa por hora en soles (ej: 8.5):", REGLA_TARIFA, False),
    ])
    if datos is None:
        return
    ok, mensaje = registrar_empleado(lista_empleados, *datos)
    vista.mostrar_mensaje(mensaje)
    if ok:
        guardar_empleados(lista_empleados)


def opcion_listar(lista_empleados):
    vista.mostrar_trabajadores(listar_empleados(lista_empleados))


def opcion_buscar(lista_empleados):
    datos = vista.pedir_varios([("Codigo a buscar (ej: E001):", REGLA_CODIGO_FORMATO, False)])
    if datos is None:
        return
    # La busqueda binaria requiere la lista ordenada por codigo
    ordenados = ordenar_empleados_por_codigo(lista_empleados)
    resultado = buscar_binario_recursivo(ordenados, datos[0])
    if resultado:
        vista.mostrar_trabajador_encontrado(resultado)
    else:
        vista.mostrar_mensaje("Trabajador no encontrado.")


def opcion_entrada(lista_empleados, lista_asistencias):
    datos = vista.pedir_varios([
        ("Codigo del trabajador:", regla_codigo_existente(lista_empleados), False),
        ("Fecha (AAAA-MM-DD):", REGLA_FECHA, False),
        ("Hora de entrada (HH:MM):", REGLA_HORA, False),
        ("Turno de la jornada (M/T, Enter = turno habitual):", REGLA_TURNO, True),
    ])
    if datos is None:
        return
    ok, mensaje = marcar_entrada(lista_asistencias, lista_empleados, *datos)
    vista.mostrar_mensaje(mensaje)
    if ok:
        guardar_asistencias(lista_asistencias)


def opcion_salida(lista_empleados, lista_asistencias):
    datos = vista.pedir_varios([
        ("Codigo del trabajador:", regla_codigo_existente(lista_empleados), False),
        ("Fecha (AAAA-MM-DD):", REGLA_FECHA, False),
        ("Hora de salida (HH:MM):", REGLA_HORA, False),
    ])
    if datos is None:
        return
    ok, mensaje = marcar_salida(lista_asistencias, *datos)
    vista.mostrar_mensaje(mensaje)
    if ok:
        guardar_asistencias(lista_asistencias)


def opcion_ver_asistencias(lista_empleados, lista_asistencias):
    datos = vista.pedir_varios([("Codigo del trabajador:", regla_codigo_existente(lista_empleados), False)])
    if datos is None:
        return
    registros = buscar_asistencias_por_codigo(lista_asistencias, datos[0])
    vista.mostrar_asistencias(registros, "No hay registros para ese trabajador.")


def opcion_ordenar(lista_asistencias):
    vista.mostrar_asistencias(ordenar_asistencias_por_fecha(lista_asistencias), "No hay asistencias registradas.")


def opcion_tardanzas(lista_asistencias):
    vista.mostrar_mensaje(f"Total de tardanzas registradas: {contar_tardanzas_recursivo(lista_asistencias)}")


def opcion_planilla(lista_empleados, lista_asistencias):
    datos = vista.pedir_varios([("Mes (AAAA-MM, ej: 2026-09):", REGLA_MES, False)])
    if datos is None:
        return
    mes = datos[0]
    planilla = generar_planilla_mensual(lista_empleados, lista_asistencias, mes)
    total = total_planilla(planilla)
    avisos = {}
    for p in planilla:
        if p["horas_trabajadas"] == 0:
            # Explicar por que sale en cero (no es un error del programa)
            cerradas, abiertas = contar_jornadas_mes(lista_asistencias, p["codigo"], mes)
            if abiertas:
                avisos[p["codigo"]] = f"{abiertas} jornada(s) sin hora de salida (use la opcion 5)."
            elif not cerradas:
                avisos[p["codigo"]] = f"este trabajador no tiene asistencias en {mes}."
    meses = meses_con_datos(lista_asistencias) if total == 0 and lista_asistencias else []
    vista.mostrar_planilla(planilla, mes, total, avisos, meses)


def opcion_exportar(lista_empleados, lista_asistencias):
    datos = vista.pedir_varios([("Mes de la planilla a incluir en el Excel (AAAA-MM):", REGLA_MES, False)])
    if datos is None:
        return
    planilla = generar_planilla_mensual(lista_empleados, lista_asistencias, datos[0])
    ruta = exportar_a_excel(lista_empleados, lista_asistencias, planilla=planilla)
    if ruta:
        vista.mostrar_mensaje(f"Reporte generado: {ruta}")


# ---------------------------------------------------------------- programa principal
def main():
    lista_empleados = cargar_empleados()
    lista_asistencias = cargar_asistencias()

    # Datos de versiones anteriores: asignar el turno habitual a jornadas sin turno
    antiguos = completar_turnos(lista_asistencias, lista_empleados)
    if antiguos:
        vista.mostrar_mensaje(f"Aviso: {antiguos} asistencia(s) de una version anterior no tenian turno;")
        vista.mostrar_mensaje("       se les asigno el turno habitual del trabajador.")

    acciones = {
        "1": lambda: opcion_registrar(lista_empleados),
        "2": lambda: opcion_listar(lista_empleados),
        "3": lambda: opcion_buscar(lista_empleados),
        "4": lambda: opcion_entrada(lista_empleados, lista_asistencias),
        "5": lambda: opcion_salida(lista_empleados, lista_asistencias),
        "6": lambda: opcion_ver_asistencias(lista_empleados, lista_asistencias),
        "7": lambda: opcion_ordenar(lista_asistencias),
        "8": lambda: opcion_tardanzas(lista_asistencias),
        "9": lambda: opcion_planilla(lista_empleados, lista_asistencias),
        "10": lambda: opcion_exportar(lista_empleados, lista_asistencias),
    }

    try:
        while True:
            vista.mostrar_menu()
            opcion = vista.pedir_opcion()
            if opcion == "0":
                vista.mostrar_mensaje("Hasta luego.")
                break
            accion = acciones.get(opcion)
            if accion is None:
                vista.mostrar_mensaje("Opcion invalida.")
                continue
            accion()
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C o fin de la entrada: se sale ordenadamente sin perder datos
        vista.mostrar_mensaje("\nPrograma interrumpido por el usuario.")
    finally:
        guardar_empleados(lista_empleados)
        guardar_asistencias(lista_asistencias)

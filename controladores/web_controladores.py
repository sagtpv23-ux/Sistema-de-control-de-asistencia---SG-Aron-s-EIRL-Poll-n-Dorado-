import os
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, send_file, url_for

from modelos.asistencia import (
    buscar_asistencias_por_codigo,
    completar_turnos,
    contar_tardanzas_recursivo,
    marcar_entrada,
    marcar_salida,
    ordenar_asistencias_por_fecha,
)
from modelos.base_datos import (
    cargar_asistencias,
    cargar_empleados,
    guardar_asistencias,
    guardar_empleados,
)
from modelos.empleado import (
    buscar_binario_recursivo,
    ordenar_empleados_por_codigo,
    registrar_empleado,
)
from modelos.planilla import contar_jornadas_mes, generar_planilla_mensual, total_planilla
from modelos.validaciones import CARGOS_VALIDOS, TURNOS_VALIDOS, validar_formato_mes
from vistas.reporte_excel import exportar_a_excel

# Las paginas (HTML) estan en views/templates
CARPETA_PLANTILLAS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "views", "templates"
)

app = Flask(__name__, template_folder=CARPETA_PLANTILLAS)
app.secret_key = "sg-arons-asistencia"  # solo para los mensajes flash

# Mismas listas en memoria que usa el controlador de consola (se guardan en SQLite tras cada cambio)
empleados = cargar_empleados()
asistencias = cargar_asistencias()
completar_turnos(asistencias, empleados)


# ------------------------------------------------------------------ rutas
@app.route("/")
def inicio():
    vista = request.args.get("vista", "trabajadores")
    ahora = datetime.now()

    # --- Trabajadores (con busqueda binaria opcional)
    lista_emp = empleados
    buscar = request.args.get("buscar", "").strip().upper()
    if buscar:
        encontrado = buscar_binario_recursivo(ordenar_empleados_por_codigo(empleados), buscar)
        lista_emp = [encontrado] if encontrado else []
        if not encontrado:
            flash("Trabajador no encontrado.", "error")

    # --- Asistencias (filtro por codigo / orden por fecha)
    lista_asis = asistencias
    codigo = request.args.get("codigo", "").strip().upper()
    if codigo:
        lista_asis = buscar_asistencias_por_codigo(asistencias, codigo)
    if request.args.get("orden") == "fecha":
        lista_asis = ordenar_asistencias_por_fecha(lista_asis)
    tardanzas = contar_tardanzas_recursivo(asistencias)

    # --- Planilla
    mes = request.args.get("mes", ahora.strftime("%Y-%m")).strip()
    planilla, total, avisos = [], 0, []
    if vista == "planilla":
        if validar_formato_mes(mes):
            planilla = generar_planilla_mensual(empleados, asistencias, mes)
            total = total_planilla(planilla)
            for p in planilla:
                if p["horas_trabajadas"] == 0:
                    _, abiertas = contar_jornadas_mes(asistencias, p["codigo"], mes)
                    if abiertas:
                        avisos.append(f"{p['codigo']}: {abiertas} jornada(s) sin hora de salida")
        else:
            flash("Mes inválido. Usa el formato AAAA-MM (ej: 2026-09).", "error")

    return render_template(
        "index.html", vista=vista, empleados=lista_emp, asistencias=lista_asis,
        cargos=CARGOS_VALIDOS, turnos=TURNOS_VALIDOS, tardanzas=tardanzas,
        hoy=ahora.strftime("%Y-%m-%d"), hora=ahora.strftime("%H:%M"),
        mes=mes, planilla=planilla, total=total, avisos=avisos, buscar=buscar, codigo=codigo,
    )


@app.post("/trabajadores")
def ruta_registrar():
    f = request.form
    ok, mensaje = registrar_empleado(
        empleados, f["codigo"], f["nombres"], f["apellidos"],
        f["dni"], f["cargo"], f["turno"], f["tarifa"],
    )
    if ok:
        guardar_empleados(empleados)
    flash(mensaje, "ok" if ok else "error")
    return redirect(url_for("inicio", vista="trabajadores"))


@app.post("/entrada")
def ruta_entrada():
    f = request.form
    ok, mensaje = marcar_entrada(asistencias, empleados, f["codigo"], f["fecha"], f["hora"], f.get("turno", ""))
    if ok:
        guardar_asistencias(asistencias)
    flash(mensaje, "ok" if ok else "error")
    return redirect(url_for("inicio", vista="asistencia"))


@app.post("/salida")
def ruta_salida():
    f = request.form
    ok, mensaje = marcar_salida(asistencias, f["codigo"], f["fecha"], f["hora"])
    if ok:
        guardar_asistencias(asistencias)
    flash(mensaje, "ok" if ok else "error")
    return redirect(url_for("inicio", vista="asistencia"))


@app.route("/exportar")
def ruta_exportar():
    mes = request.args.get("mes", "").strip()
    if not validar_formato_mes(mes):
        flash("Mes inválido. Usa el formato AAAA-MM.", "error")
        return redirect(url_for("inicio", vista="planilla"))
    planilla = generar_planilla_mensual(empleados, asistencias, mes)
    ruta = exportar_a_excel(empleados, asistencias, planilla=planilla)
    if not ruta:
        flash("No se pudo generar el Excel (¿está abierto en otro programa?).", "error")
        return redirect(url_for("inicio", vista="planilla", mes=mes))
    return send_file(ruta, as_attachment=True, download_name=f"reporte_asistencia_{mes}.xlsx")

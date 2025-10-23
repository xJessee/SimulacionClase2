import streamlit as st
import numpy as np
import pandas as pd
import math

# --- Función para convertir minutos a HH:MM:SS ---
def minutos_a_hms(minutos):
    total_segundos = int(round(minutos * 60))
    h = total_segundos // 3600
    m = (total_segundos % 3600) // 60
    s = total_segundos % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

# --- Función de simulación con colas y trabajadores ---
def simular_proceso(iteraciones, hora_inicio, media_llegada, media_corte, media_soldar, M_ver, raiz_ver):
    resultados = []

    hora_base = hora_inicio * 60  # convertir hora inicio a minutos
    # Relojes de disponibilidad de cada trabajador
    disponible_corte = hora_base
    disponible_soldar = hora_base
    disponible_verificar = hora_base
    hora_anterior_llegada = hora_base

    for i in range(1, iteraciones+1):
        # --- Llegada ---
        r_llegada = np.random.random()
        tiempo_llegada = -media_llegada * math.log(1 - r_llegada)
        hora_llegada = hora_anterior_llegada + tiempo_llegada

        # --- Corte ---
        r_corte = np.random.random()
        tiempo_corte = -media_corte * math.log(1 - r_corte)
        hora_inicio_corte = max(hora_llegada, disponible_corte)
        hora_fin_corte = hora_inicio_corte + tiempo_corte
        disponible_corte = hora_fin_corte

        # --- Soldar ---
        r_soldar = np.random.random()
        tiempo_soldar = -media_soldar * math.log(1 - r_soldar)
        hora_inicio_soldar = max(hora_fin_corte, disponible_soldar)
        hora_fin_soldar = hora_inicio_soldar + tiempo_soldar
        disponible_soldar = hora_fin_soldar

        # --- Verificación ---
        r12 = np.random.random(12)
        S = np.sum(r12)
        tiempo_verificar = (S - 6) * raiz_ver + M_ver
        hora_inicio_verificar = max(hora_fin_soldar, disponible_verificar)
        hora_fin_verificar = hora_inicio_verificar + tiempo_verificar
        disponible_verificar = hora_fin_verificar

        # Hora tarea finalizar
        hora_tarea_finalizar = hora_fin_verificar

        resultados.append({
            "#": i,
            "Tiempo Llegar": minutos_a_hms(tiempo_llegada),
            "Hora Llegada": minutos_a_hms(hora_llegada),
            "Hora Inicio Corte": minutos_a_hms(hora_inicio_corte),
            "Tiempo Corte": minutos_a_hms(tiempo_corte),
            "Hora Fin Corte": minutos_a_hms(hora_fin_corte),
            "Hora Inicio Soldar": minutos_a_hms(hora_inicio_soldar),
            "Tiempo Soldar": minutos_a_hms(tiempo_soldar),
            "Hora Fin Soldar": minutos_a_hms(hora_fin_soldar),
            "Hora Inicio Verificar": minutos_a_hms(hora_inicio_verificar),
            "Tiempo Verificar": minutos_a_hms(tiempo_verificar),
            "Hora Fin Verificar": minutos_a_hms(hora_fin_verificar),
            "Hora Tarea Finalizar": minutos_a_hms(hora_tarea_finalizar)
        })

        # Actualizamos hora anterior de llegada para la próxima barra
        hora_anterior_llegada = hora_llegada

    return pd.DataFrame(resultados)

# --- Streamlit Interface ---
st.title("Simulación de Línea de Producción de Barras")

st.sidebar.header("Parámetros de simulación")
hora_inicio = st.sidebar.number_input("Hora de inicio (24h)", value=8, min_value=0, max_value=23)
iteraciones = st.sidebar.number_input("Número de iteraciones", value=20, min_value=1)
media_llegada = st.sidebar.number_input("Media llegada barra (min)", value=3.0, min_value=0.1)
media_corte = st.sidebar.number_input("Media corte (min)", value=3.5, min_value=0.1)
media_soldar = st.sidebar.number_input("Media soldar (min)", value=4.8, min_value=0.1)
M_ver = st.sidebar.number_input("M Verificar (min)", value=3.2, min_value=0.1)
raiz_ver = st.sidebar.number_input("Raíz Verificar", value=1.1, min_value=0.01)

if st.button("Ejecutar simulación"):
    df = simular_proceso(iteraciones, hora_inicio, media_llegada, media_corte, media_soldar, M_ver, raiz_ver)
    st.dataframe(df)

    # Descargar CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(label="Descargar resultados CSV", data=csv, file_name="simulacion_barras.csv", mime="text/csv")

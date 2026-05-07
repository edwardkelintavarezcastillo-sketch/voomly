import streamlit as st
import datetime
import pandas as pd

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Voomly - Comparte tu ruta", page_icon="🚗")

# --- LÓGICA DEL NEGOCIO (Backend simplificado) ---
class CalculadoraPrecios:
    def calcular_costo_ruta(self, distancia_km, peajes=0):
        # Basado en tus cálculos previos para República Dominicana
        costo_gasolina = (distancia_km / 12 / 3.785) * 290 
        precio_sugerido = ((costo_gasolina + peajes) * 1.15) / 3
        return round(precio_sugerido, 2)

# Inicializar estados de la app (Simula una base de datos temporal)
if 'viajes' not in st.session_state:
    st.session_state.viajes = []
if 'ganancias' not in st.session_state:
    st.session_state.ganancias = 0.0

calc = CalculadoraPrecios()

# --- INTERFAZ DE USUARIO (Frontend) ---
st.title("🚗 Voomly")
st.markdown("### La red de movilidad compartida inteligente")

menu = st.sidebar.selectbox("Selecciona tu rol", ["Pasajero", "Conductor", "Panel de Control"])

# --- VISTA: CONDUCTOR ---
if menu == "Conductor":
    st.header("Publicar un viaje")
    with st.form("form_conductor"):
        nombre = st.text_input("Tu nombre")
        origen = st.selectbox("Origen", ["Santo Domingo", "Santiago", "Punta Cana", "La Romana"])
        destino = st.selectbox("Destino", ["Santiago", "Santo Domingo", "Punta Cana", "Puerto Plata"])
        distancia = st.number_input("Distancia estimada (KM)", min_value=1, value=155)
        peajes = st.number_input("Total peajes (RD$)", min_value=0, value=100)
        asientos = st.slider("Asientos disponibles", 1, 4, 3)
        
        btn_publicar = st.form_submit_button("Calcular y Publicar")
        
        if btn_publicar:
            precio = calc.calcular_costo_ruta(distancia, peajes)
            nuevo_viaje = {
                "id": len(st.session_state.viajes) + 1,
                "conductor": nombre,
                "ruta": f"{origen} -> {destino}",
                "asientos": asientos,
                "precio": precio,
                "origen_raw": origen.lower(),
                "destino_raw": destino.lower()
            }
            st.session_state.viajes.append(nuevo_viaje)
            st.success(f"¡Viaje publicado! Precio sugerido por asiento: RD${precio}")

# --- VISTA: PASAJERO ---
elif menu == "Pasajero":
    st.header("Busca tu aventón")
    col1, col2 = st.columns(2)
    with col1:
        busqueda_origen = st.text_input("Desde donde sales")
    with col2:
        busqueda_destino = st.text_input("A donde vas")

    if busqueda_origen and busqueda_destino:
        encontrados = [v for v in st.session_state.viajes if v['origen_raw'] == busqueda_origen.lower() and v['destino_raw'] == busqueda_destino.lower()]
        
        if encontrados:
            for v in encontrados:
                with st.expander(f"🚗 Con {v['conductor']} - RD${v['precio']}"):
                    st.write(f"Ruta: {v['ruta']}")
                    st.write(f"Asientos libres: {v['asientos']}")
                    if st.button(f"Reservar con {v['conductor']}", key=v['id']):
                        if v['asientos'] > 0:
                            v['asientos'] -= 1
                            st.session_state.ganancias += (v['precio'] * 0.15)
                            st.balloons()
                            st.success("¡Reserva confirmada!")
                        else:
                            st.error("Lo sentimos, ya no hay asientos.")
        else:
            st.warning("No hay viajes para esta ruta todavía.")

# --- VISTA: PANEL DE CONTROL ---
elif menu == "Panel de Control":
    st.header("Métricas del Negocio")
    kpi1, kpi2 = st.columns(2)
    kpi1.metric("Ingresos Voomly", f"RD${st.session_state.ganancias:.2f}")
    kpi2.metric("Viajes Activos", len(st.session_state.viajes))
    
    if st.session_state.viajes:
        df = pd.DataFrame(st.session_state.viajes)
        st.table(df[['conductor', 'ruta', 'precio', 'asientos']])

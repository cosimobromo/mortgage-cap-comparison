import io

import streamlit as st
import numpy as np
import pandas as pd
import numpy_financial as npf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. CONFIGURAZIONE PAGINA
st.set_page_config(
    page_title="Simulatore Mutuo vs PAC",
    page_icon="🏦",
    layout="wide"
)

pd.options.display.float_format = '€ {:,.2f}'.format

st.title("🏦 Simulatore: Estinzione Mutuo con apporto di capitale")
st.markdown("Analisi della convenienza nell'estenzione anticipata di un mutuo vs l'investimento del capitale extra in un PAC (Piano di Accumulo del Capitale).")

# 2. SIDEBAR - PARAMETRI DI INPUT
st.sidebar.header("1. Dati Mutuo Attuale")
capitale_residuo = st.sidebar.number_input("Capitale Residuo (€)", min_value=1000, value=150000, step=5000)
tasso_mutuo_annuo = st.sidebar.slider("Tasso Mutuo Annuo (%)", min_value=0.1, max_value=10.0, value=3.5, step=0.05) / 100
anni_residui = st.sidebar.slider("Anni Residui", min_value=1, max_value=40, value=30, step=1)

st.sidebar.header("2. Investimento Capitale Extra")
df = pd.DataFrame(
    [
        {"Capitale Extra Disponibile (€)": 10000, "Mesi dall'inizio del mutuo": 12},
    ]
)
capitale_extra_df = st.sidebar.data_editor(df, num_rows="dynamic", width = "stretch", column_config={
        # 1. Formato Mese: Intero puro
        "Mesi dall'inizio del mutuo": st.column_config.NumberColumn(
            "Mese di Versamento",
            help="Numero del mese progressivo (1-360)",
            min_value=1,
            max_value=anni_residui*12,
            step=1,
            format="%d",
            required=True
        ),
        "Capitale Extra Disponibile (€)": st.column_config.NumberColumn(
            "Capitale da investire",
            help="Capitale che si decide investire",
            min_value=1,
            max_value=capitale_residuo,
            step=1,
            format="€ %,d",
            required=True
        )})

simulato_rendimento_pac_annuo = st.sidebar.slider("Rendimento Annuo Atteso PAC (%)", min_value=0.0, max_value=12.0, value=5.0, step=0.5) / 100
reinvestimento_risparmio_rata = st.sidebar.checkbox("Reinvesti risparmio rata in PAC", value = False)

# 3. MOTORE DI CALCOLO
mesi_residui = anni_residui * 12
tasso_m = tasso_mutuo_annuo / 12
tasso_pac_m = simulato_rendimento_pac_annuo / 12
capitale_investito = 0

mesi = np.arange(1, mesi_residui + 1, 1)

rata_base = npf.pmt(tasso_m, mesi_residui, -capitale_residuo)
interessi_base = rata_base * mesi_residui - capitale_residuo
rata = rata_base  # Rata iniziale del mutuo
simulazione_mutuo = []
simulazione_pac = []

# Simulazione scenario 
for m in mesi:
    quota_interessi = capitale_residuo * tasso_m 
    quota_capitale = rata - quota_interessi
    capitale_residuo -= quota_capitale

    if reinvestimento_risparmio_rata: 
            capitale_investito += rata_base - rata 
    capitale_investito = capitale_investito * (1+tasso_pac_m) 

    simulazione_mutuo.append({"Mese": m, "Rata": rata, "Interessi Rata": quota_interessi, "Capitale Rata": quota_capitale, "Capitale Residuo": max(0, capitale_residuo)})
    simulazione_pac.append({"Mese": m, "Capitale PAC": capitale_investito})
    if m in capitale_extra_df["Mesi dall'inizio del mutuo"].values:
        capitale_extra = capitale_extra_df.loc[capitale_extra_df["Mesi dall'inizio del mutuo"] == m, "Capitale Extra Disponibile (€)"].values[0]
        capitale_residuo = max(0, capitale_residuo - capitale_extra)
        capitale_investito += capitale_extra
        mesi_residui -= m
        rata = npf.pmt(tasso_m, mesi_residui, -capitale_residuo)

    if capitale_residuo <= 0:
        break


simulazione_mutuo_df = pd.DataFrame(simulazione_mutuo)
simulazione_mutuo_df["Interessi Cumulati"] = simulazione_mutuo_df["Interessi Rata"].cumsum()
simulazione_pac_df = pd.DataFrame(simulazione_pac)

df_confronto = pd.merge(simulazione_mutuo_df, simulazione_pac_df, on="Mese")
df_confronto["Differenza (PAC - Interessi)"] = df_confronto["Capitale PAC"] - df_confronto["Interessi Cumulati"]

interessi_totali = simulazione_mutuo_df["Interessi Rata"].sum()
valore_finale_investimento = simulazione_pac_df.iloc[-1]["Capitale PAC"]

# 4. METRICHE PRINCIPALI
col1, col2, col3 = st.columns(3)

col1.metric("Interessi Totali", f"€ {interessi_totali:,.2f}", delta = f"- € {interessi_base-interessi_totali:,.2f}")
col2.metric("Mesi di estinzione mutuo", f"{m}", delta=f"{anni_residui*12-m}")
col3.metric("Patrimonio Finale PAC", f"€ {valore_finale_investimento:,.2f}", delta = f"€ {valore_finale_investimento-capitale_extra_df["Capitale Extra Disponibile (€)"].sum():,.2f}")


st.divider()

# 5. NUOVE TAB CON GRAFICI E TABELLE
tab_graf1, tab_graf2, tab_graf3, tab_dati = st.tabs([
    "📊 Capitale vs Interessi (Doppio Asse Y)", 
    "📈 Crescita PAC", 
    "⚖️ Differenza PAC vs Interessi",
    "📋 Tabelle Dati"
])

# --- TAB 1: Doppio Asse Y (Capitale Residuo e Interessi Cumulati) ---
with tab_graf1:
    st.subheader("Andamento del Capitale Residuo e degli Interessi Cumulati")
    
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig1.add_trace(
        go.Scatter(
            x=df_confronto["Mese"],
            y=df_confronto["Capitale Residuo"],
            name="Capitale Residuo (€)",
            line=dict(color="#1f77b4", width=3),
        )
    )

    fig1.add_trace(
        go.Scatter(
            x=df_confronto["Mese"],
            y=df_confronto["Interessi Cumulati"],
            name="Interessi Cumulati (€)",
            line=dict(color="#d62728", width=3, dash="dot"),
        )
    )

    fig1.update_layout(
        title="Evoluzione Mutuo: Capitale Residuo e Interessi",
        xaxis_title="Mese",
        yaxis_title="Importo (€)",
        hovermode="x unified",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
        ),
    )

    # Titoli Assi
    fig1.update_xaxes(title_text="Mese")
    fig1.update_yaxes(title_text="Capitale Residuo (€)", secondary_y=False, showgrid=True)
    fig1.update_yaxes(title_text="Interessi Cumulati (€)", secondary_y=True, showgrid=False)
    
    fig1.update_layout(hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig1, width="stretch")

# --- TAB 2: Andamento del PAC ---
with tab_graf2:
    st.subheader("Evoluzione del Patrimonio Accumulato nel PAC")
    
    fig2 = go.Figure()
    fig2.add_trace(
        go.Scatter(
            x=df_confronto["Mese"], 
            y=df_confronto["Capitale PAC"], 
            name="Valore PAC (€)",
            fill='tozeroy',
            line=dict(color="#2ca02c", width=3)
        )
    )
    
    fig2.update_layout(
        xaxis_title="Mese", 
        yaxis_title="Valore Accumulato (€)", 
        hovermode="x unified"
    )
    st.plotly_chart(fig2, width="stretch")

# --- TAB 3: Differenza PAC vs Interessi Cumulati ---
with tab_graf3:
    st.subheader("Differenza Netta: Capitale PAC - Interessi Cumulati Pagati")
    st.markdown("Guadagno/valore del PAC meno interessi cumulati del mutuo.")
    
    fig3 = go.Figure()
    
    # Traccia la linea differenziale
    fig3.add_trace(
        go.Scatter(
            x=df_confronto["Mese"], 
            y=df_confronto["Differenza (PAC - Interessi)"], 
            name="Differenza Netta (€)",
            line=dict(color="#ff7f0e", width=3)
        )
    )
    
    # Linea dello zero di riferimento
    fig3.add_hline(y=0, line_dash="dash", line_color="gray")
    
    fig3.update_layout(
        xaxis_title="Mese", 
        yaxis_title="Differenza (€)", 
        hovermode="x unified"
    )
    st.plotly_chart(fig3, width="stretch")

# --- TAB 4: Tabelle Dati Griglia ---
with tab_dati:
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown("### Piano Ammortamento Mutuo")
        
        buffer_mutuo = io.BytesIO()
        with pd.ExcelWriter(buffer_mutuo, engine='openpyxl') as writer:
            simulazione_mutuo_df.to_excel(writer, index=False, sheet_name='Piano Ammortamento')
        buffer_mutuo.seek(0)
        
        # Pulsante di Download Mutuo
        st.download_button(
            label="📥 Scarica Piano Ammortamento (Excel)",
            data=buffer_mutuo,
            file_name="piano_ammortamento_mutuo.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch"
        )

        st.dataframe(
            simulazione_mutuo_df, 
            hide_index=True,
            width="stretch",
            column_config={
                "Mese": st.column_config.NumberColumn("Mese", format="%d"),
                "Rata": st.column_config.NumberColumn("Rata", format="€ %,.2f"),
                "Interessi Rata": st.column_config.NumberColumn("Interessi", format="€ %,.2f"),
                "Capitale Rata": st.column_config.NumberColumn("Capitale", format="€ %,.2f"),
                "Capitale Residuo": st.column_config.NumberColumn("Residuo", format="€ %,.2f"),
                "Interessi Cumulati": st.column_config.NumberColumn("Interessi Cumulati", format="€ %,.2f"),
            }
        )
    with col_t2:
        st.markdown("### Simulazione PAC")

        buffer_pac = io.BytesIO()
        with pd.ExcelWriter(buffer_pac, engine='openpyxl') as writer:
            simulazione_pac_df.to_excel(writer, index=False, sheet_name='Piano PAC')
        buffer_pac.seek(0)
        
        # Pulsante di Download Mutuo
        st.download_button(
            label="📥 Scarica Piano PAC (Excel)",
            data=buffer_pac,
            file_name="piano_pac.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch"
        )

        st.dataframe(
            simulazione_pac_df, 
            hide_index=True,
            width="stretch",
            column_config={
                "Mese": st.column_config.NumberColumn("Mese", format="%d"),
                "Capitale PAC": st.column_config.NumberColumn("Valore PAC", format="€ %,.2f"),
            }
        )
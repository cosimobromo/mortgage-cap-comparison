import io

import streamlit as st
import numpy as np
import pandas as pd
import numpy_financial as npf
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="Mortgage vs CAP Simulator",
    page_icon="🏦",
    layout="wide"
)

pd.options.display.float_format = '€ {:,.2f}'.format

st.title("🏦 Simulator: Early Mortgage Prepayment with Extra Capital")
st.markdown("Analysis of the convenience of early mortgage prepayment vs investing extra capital in a CAP (Capital Accumulation Plan).")

# 2. SIDEBAR - INPUT PARAMETERS
st.sidebar.header("1. Current Mortgage Data")
capitale_residuo = st.sidebar.number_input("Remaining Capital (€)", min_value=1000, value=150000, step=5000)
tasso_mutuo_annuo = st.sidebar.slider("Annual Mortgage Rate (%)", min_value=0.1, max_value=10.0, value=3.5, step=0.05) / 100
anni_residui = st.sidebar.slider("Remaining Years", min_value=1, max_value=40, value=30, step=1)

st.sidebar.header("2. Extra Capital Investment")
df = pd.DataFrame(
    [
        {"Extra Available Capital (€)": 10000, "Months from start of mortgage": 12},
    ]
)
capitale_extra_df = st.sidebar.data_editor(df, num_rows="dynamic", width = "stretch", column_config={
        # 1. Month Format: Pure Integer
        "Months from start of mortgage": st.column_config.NumberColumn(
            "Payment Month",
            help="Progressive month number (1-360)",
            min_value=1,
            max_value=anni_residui*12,
            step=1,
            format="%d",
            required=True
        ),
        "Extra Available Capital (€)": st.column_config.NumberColumn(
            "Capital to invest",
            help="Capital you decide to invest",
            min_value=1,
            max_value=capitale_residuo,
            step=1,
            format="€ %,d",
            required=True
        )})

simulato_rendimento_pac_annuo = st.sidebar.slider("Expected Annual CAP Return (%)", min_value=0.0, max_value=12.0, value=5.0, step=0.5) / 100
reinvestimento_risparmio_rata = st.sidebar.checkbox("Reinvest payment savings in CAP", value = False)

# 3. CALCULATION ENGINE
mesi_residui = anni_residui * 12
tasso_m = tasso_mutuo_annuo / 12
tasso_pac_m = simulato_rendimento_pac_annuo / 12
capitale_investito = 0

mesi = np.arange(1, mesi_residui + 1, 1)

rata_base = npf.pmt(tasso_m, mesi_residui, -capitale_residuo)
interessi_base = rata_base * mesi_residui - capitale_residuo
rata = rata_base  # Initial mortgage payment
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

    simulazione_mutuo.append({"Month": m, "Payment": rata, "Interest Payment": quota_interessi, "Principal Payment": quota_capitale, "Remaining Capital": max(0, capitale_residuo)})
    simulazione_pac.append({"Month": m, "CAP Capital": capitale_investito})
    if m in capitale_extra_df["Months from start of mortgage"].values:
        capitale_extra = capitale_extra_df.loc[capitale_extra_df["Months from start of mortgage"] == m, "Extra Available Capital (€)"].values[0]
        capitale_residuo = max(0, capitale_residuo - capitale_extra)
        capitale_investito += capitale_extra
        mesi_residui -= m
        rata = npf.pmt(tasso_m, mesi_residui, -capitale_residuo)

    if capitale_residuo <= 0:
        break


simulazione_mutuo_df = pd.DataFrame(simulazione_mutuo)
simulazione_mutuo_df["Cumulative Interest"] = simulazione_mutuo_df["Interest Payment"].cumsum()
simulazione_pac_df = pd.DataFrame(simulazione_pac)

df_confronto = pd.merge(simulazione_mutuo_df, simulazione_pac_df, on="Month")
df_confronto["Difference (CAP - Interest)"] = df_confronto["CAP Capital"] - df_confronto["Cumulative Interest"]

interessi_totali = simulazione_mutuo_df["Interest Payment"].sum()
valore_finale_investimento = simulazione_pac_df.iloc[-1]["CAP Capital"]

# 4. KEY METRICS
col1, col2, col3 = st.columns(3)

col1.metric("Total Interest", f"€ {interessi_totali:,.2f}", delta = f"- € {interessi_base-interessi_totali:,.2f}")
col2.metric("Mortgage Payoff Months", f"{m}", delta=f"{anni_residui*12-m}")
col3.metric("Final CAP Assets", f"€ {valore_finale_investimento:,.2f}", delta = f"€ {valore_finale_investimento-capitale_extra_df["Extra Available Capital (€)"].sum():,.2f}")


st.divider()

# 5. TABS WITH CHARTS AND TABLES
tab_graf1, tab_graf2, tab_graf3, tab_dati = st.tabs([
    "📊 Capital vs Interest (Dual Y-Axis)", 
    "📈 CAP Growth", 
    "⚖️ CAP Difference vs Interest",
    "📋 Data Tables"
])

# --- TAB 1: Dual Y-Axis (Remaining Capital and Cumulative Interest) ---
with tab_graf1:
    st.subheader("Mortgage Trend: Remaining Capital and Cumulative Interest")
    
    fig1 = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig1.add_trace(
        go.Scatter(
            x=df_confronto["Month"],
            y=df_confronto["Remaining Capital"],
            name="Remaining Capital (€)",
            line=dict(color="#1f77b4", width=3),
        )
    )

    fig1.add_trace(
        go.Scatter(
            x=df_confronto["Month"],
            y=df_confronto["Cumulative Interest"],
            name="Cumulative Interest (€)",
            line=dict(color="#d62728", width=3, dash="dot"),
        )
    )

    fig1.update_layout(
        title="Mortgage Evolution: Remaining Capital and Interest",
        xaxis_title="Month",
        yaxis_title="Amount (€)",
        hovermode="x unified",
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1
        ),
    )

    # Axis Titles
    fig1.update_xaxes(title_text="Month")
    fig1.update_yaxes(title_text="Remaining Capital (€)", secondary_y=False, showgrid=True)
    fig1.update_yaxes(title_text="Cumulative Interest (€)", secondary_y=True, showgrid=False)
    
    fig1.update_layout(hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig1, width="stretch")

# --- TAB 2: CAP Portfolio Trend ---
with tab_graf2:
    st.subheader("Accumulated Asset Evolution in CAP")
    
    fig2 = go.Figure()
    fig2.add_trace(
        go.Scatter(
            x=df_confronto["Month"], 
            y=df_confronto["CAP Capital"], 
            name="CAP Value (€)",
            fill='tozeroy',
            line=dict(color="#2ca02c", width=3)
        )
    )
    
    fig2.update_layout(
        xaxis_title="Month", 
        yaxis_title="Accumulated Value (€)", 
        hovermode="x unified"
    )
    st.plotly_chart(fig2, width="stretch")

# --- TAB 3: CAP Difference vs Cumulative Interest ---
with tab_graf3:
    st.subheader("Net Difference: CAP Capital - Paid Cumulative Interest")
    st.markdown("Gain/value of the CAP minus cumulative mortgage interest.")
    
    fig3 = go.Figure()
    
    # Net difference line trace
    fig3.add_trace(
        go.Scatter(
            x=df_confronto["Month"], 
            y=df_confronto["Difference (CAP - Interest)"], 
            name="Net Difference (€)",
            line=dict(color="#ff7f0e", width=3)
        )
    )
    
    # Zero reference line
    fig3.add_hline(y=0, line_dash="dash", line_color="gray")
    
    fig3.update_layout(
        xaxis_title="Month", 
        yaxis_title="Difference (€)", 
        hovermode="x unified"
    )
    st.plotly_chart(fig3, width="stretch")

# --- TAB 4: Data Grid Tables ---
with tab_dati:
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown("### Mortgage Amortization Schedule")
        
        buffer_mutuo = io.BytesIO()
        with pd.ExcelWriter(buffer_mutuo, engine='openpyxl') as writer:
            simulazione_mutuo_df.to_excel(writer, index=False, sheet_name='Amortization')
        buffer_mutuo.seek(0)
        
        # Download Mortgage Button
        st.download_button(
            label="📥 Download Amortization Schedule (Excel)",
            data=buffer_mutuo,
            file_name="mortgage_amortization_schedule.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch"
        )

        st.dataframe(
            simulazione_mutuo_df, 
            hide_index=True,
            width="stretch",
            column_config={
                "Month": st.column_config.NumberColumn("Month", format="%d"),
                "Payment": st.column_config.NumberColumn("Payment", format="€ %,.2f"),
                "Interest Payment": st.column_config.NumberColumn("Interest", format="€ %,.2f"),
                "Principal Payment": st.column_config.NumberColumn("Principal", format="€ %,.2f"),
                "Remaining Capital": st.column_config.NumberColumn("Remaining", format="€ %,.2f"),
                "Cumulative Interest": st.column_config.NumberColumn("Cumulative Interest", format="€ %,.2f"),
            }
        )
    with col_t2:
        st.markdown("### CAP Simulation")

        buffer_pac = io.BytesIO()
        with pd.ExcelWriter(buffer_pac, engine='openpyxl') as writer:
            simulazione_pac_df.to_excel(writer, index=False, sheet_name='CAP')
        buffer_pac.seek(0)
        
        # Download CAP Button
        st.download_button(
            label="📥 Download CAP Plan (Excel)",
            data=buffer_pac,
            file_name="cap_plan.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width="stretch"
        )

        st.dataframe(
            simulazione_pac_df, 
            hide_index=True,
            width="stretch",
            column_config={
                "Month": st.column_config.NumberColumn("Month", format="%d"),
                "CAP Capital": st.column_config.NumberColumn("CAP Value", format="€ %,.2f"),
            }
        )
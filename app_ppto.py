import pandas as pd
import streamlit as st
from data_loading.odoo_data import leer_presupuesto
from plotnine import *
import plotly.graph_objects as go
from visualizations import create_monthly_plot, create_analyticgroup_plot,create_analyticaccount_plot
st.set_page_config (layout="wide",page_title="Ejecucion ppto",page_icon="..",menu_items={"About":"Aplicacion que busca analizar la ejecucion dle ppto"})
presupuesto = leer_presupuesto()


import datetime
# Create a slider to select date
localFormat = "%Y-%m-%d"
##this uses streamlit 'magic'!!!!
today = datetime.datetime.now()
start_date = today - datetime.timedelta(days=180)
start_date = start_date.replace(day=1)
# Calculate the first day of the current month
first_day = today.replace(day=1)
# Calculate the last day of the previous month
last_day = first_day - datetime.timedelta(days=1)
fecha_calculo = st.date_input('Periodo a considerar',value=[start_date,last_day])
fecha_inicio = fecha_calculo[0].strftime(localFormat) # type: ignore
fecha_fin    =fecha_calculo[1].strftime(localFormat) # type: ignore



presupuesto_filtered = presupuesto[(presupuesto["date_from"]>=fecha_inicio)
                                   &(presupuesto["date_to"]<=fecha_fin)]

presupuesto_filtered[["practical_amount","planned_amount","theoritical_amount"]] = presupuesto[["practical_amount","planned_amount","theoritical_amount"]].abs()


lineas_excluir = ['Ingresos','Costos de Ventas']
ppto_ingresos = presupuesto_filtered[presupuesto_filtered.general_budget_id.isin(lineas_excluir)]
ppto_gastos=presupuesto_filtered[~presupuesto_filtered.general_budget_id.isin(lineas_excluir)]
ejecucion_a_fecha = round(ppto_gastos.practical_amount.sum()/ppto_gastos.theoritical_amount.sum()*100,2)
ejecucion_planificada = round(ppto_gastos.practical_amount.sum()/ppto_gastos.planned_amount.sum()*100,2)

practical_amount_ingresos = ppto_ingresos[ppto_ingresos["general_budget_id"]=="Ingresos"].practical_amount.sum()
planned_amount_ingresos = ppto_ingresos[ppto_ingresos["general_budget_id"]=="Ingresos"].planned_amount.sum()
pct_ingresos = round((practical_amount_ingresos/planned_amount_ingresos-1)*100,2)
gap_amount_ingresos =round(practical_amount_ingresos-planned_amount_ingresos,0)

practical_amount_costo = ppto_ingresos[ppto_ingresos["general_budget_id"]=="Costos de Ventas"].practical_amount.sum()
planned_amount_costo = ppto_ingresos[ppto_ingresos["general_budget_id"]=="Costos de Ventas"].planned_amount.sum()
pct_costo= round((practical_amount_costo/planned_amount_costo-1)*100,2)

gap_amount_Costo =round((practical_amount_costo-planned_amount_costo)/planned_amount_costo,2)


practical_amount_gasto = ppto_gastos.practical_amount.sum()
planned_amount_gasto = ppto_gastos.planned_amount.sum()
pct_gasto= round((practical_amount_gasto/planned_amount_gasto-1)*100,2)

gap_amount_gasto =practical_amount_gasto-planned_amount_gasto
st.title("Control de ejecucion de presupuesto")
col1,col2,col3=st.columns(3)


with col1:
    st.markdown("### Ingreso")
    st.metric("Ingresos",f"L{practical_amount_ingresos:,.0f}",delta=pct_ingresos)
    st.metric("Ingresos planificado",f"L{planned_amount_ingresos:,.0f}")
    st.metric("Gap ingresos",f"L{gap_amount_ingresos:,.0f}")
with col2:
    st.markdown("### Costo")
    st.metric("Costo",f"L{practical_amount_costo:,.0f}", delta=pct_costo, delta_color="inverse")
    st.metric("Costo planificado",f"L{planned_amount_costo:,.0f}")
    st.metric("Gap costos",f"L{planned_amount_costo:,.0f}")
with col3:
    st.markdown("### Gasto")
    st.metric("Gasto",f"L{practical_amount_gasto:,.0f}", delta=pct_gasto, delta_color="inverse")
    st.metric("Gasto planificado",f"L{planned_amount_gasto:,.0f}")    
    st.metric("Gap",f"L{gap_amount_gasto:,.0f}")
if st.button("Actualizar valores en cache de `presupuesto`", on_click=leer_presupuesto.clear):
    leer_presupuesto.clear()
rounding_dict = {
    'practical_amount': 0,
    'planned_amount': 0,
    'Percentage': 2,
    "Ejecucion":2,
    'Gap':0
    }
def main():
    
    tab1,tab2=st.tabs(["Ejecucion ingreso/costo","Ejecucion gasto"])
    with tab1:
        st.info("Los apuntes analiticos a nivel de ingreso se empezaron a segmentar a nivel de ingresos y de costos a partir del 10 de junio 2024 en la mayoria de cuentas contables")
        ingresos_por_grupo=ppto_ingresos[ppto_ingresos["general_budget_id"]=="Ingresos"].groupby(["analytic_group_id"]).agg({'practical_amount':'sum', 'planned_amount':'sum'}).reset_index().sort_values('practical_amount',ascending=False)
        ingresos_por_grupo["Ejecucion"]=ingresos_por_grupo.practical_amount/ingresos_por_grupo.planned_amount*100
        ingresos_por_grupo["Gap"]=ingresos_por_grupo.planned_amount-ingresos_por_grupo.practical_amount
        st.dataframe(ingresos_por_grupo.round(rounding_dict))
        ingresos_por_cuenta=ppto_ingresos[ppto_ingresos["general_budget_id"]=="Ingresos"].groupby(["analytic_account_id"]).agg({'practical_amount':'sum', 'planned_amount':'sum'}).reset_index().sort_values('practical_amount',ascending=False)
        ingresos_por_cuenta["Ejecucion"]=ingresos_por_cuenta.practical_amount/ingresos_por_cuenta.planned_amount*100
        ingresos_por_cuenta["Gap"]=ingresos_por_cuenta.planned_amount-ingresos_por_cuenta.practical_amount
        st.dataframe(ingresos_por_cuenta.round(rounding_dict))



    with tab2:
        t2c1,t2c2 = st.columns([1, 1])  
        gastos_por_grupo=ppto_gastos.groupby(["analytic_group_id"]).agg({'practical_amount':'sum', 'planned_amount':'sum'}).reset_index().sort_values('practical_amount',ascending=False)
        gastos_por_grupo["Ejecucion"]=gastos_por_grupo.practical_amount/gastos_por_grupo.planned_amount*100
        gastos_por_grupo["Gap"]=gastos_por_grupo.planned_amount-gastos_por_grupo.practical_amount
        gastos_por_mes=ppto_gastos.groupby(["date_from"]).agg({'practical_amount':'sum', 'planned_amount':'sum'}).reset_index()
        gastos_por_mes["Ejecucion"]=gastos_por_mes.practical_amount/gastos_por_mes.planned_amount*100
        gastos_por_mes["Gap"]=gastos_por_mes.planned_amount-gastos_por_mes.practical_amount
        with t2c1:
            fig = create_monthly_plot(gastos_por_mes)
            st.plotly_chart(fig)
        with t2c2:
            fig_grupo = create_analyticgroup_plot(gastos_por_grupo)
            st.plotly_chart(fig_grupo)
        with t2c2:
            with st.popover ("Data por grupo analitico"):
                st.dataframe(gastos_por_grupo.round(rounding_dict),hide_index=True)
        with t2c1:
            with st.popover("Data mensual"):
                st.dataframe(gastos_por_mes.round(rounding_dict),hide_index=True)
        t1,t2 = st.tabs(["Cuenta analitica","Situacion presupuestaria"])

        # Get unique values for general_budget_id and analytic_account_id
        general_budget_ids = ppto_gastos["general_budget_id"].unique()
        analytic_account_ids = ppto_gastos["analytic_account_id"].unique()

        with t1:
            # Add a multiselect filter for situacion presupuestaria
            selected_general_budgets = st.multiselect("Filtrar por situacion presupuestaria", general_budget_ids)
            # Filter gastos_por_cuenta based on selected analytic accounts
            if (selected_general_budgets ):
                gastos_por_cuenta = ppto_gastos[ppto_gastos["general_budget_id"].isin(selected_general_budgets)].groupby(["analytic_account_id"]).agg({'practical_amount':'sum', 'planned_amount':'sum'}).reset_index().sort_values('practical_amount',ascending=False)
            else:
                gastos_por_cuenta = ppto_gastos.groupby(["analytic_account_id"]).agg({'practical_amount':'sum', 'planned_amount':'sum'}).reset_index().sort_values('practical_amount',ascending=True)

            gastos_por_cuenta["Percentage"] = (gastos_por_cuenta["practical_amount"] / gastos_por_cuenta["planned_amount"]) * 100
            gastos_por_cuenta["Gap"] = gastos_por_cuenta["planned_amount"] - gastos_por_cuenta["practical_amount"]

            fig_por_cuenta = create_analyticaccount_plot(gastos_por_cuenta)
            # Display the interactive chart using Streamlit
            st.plotly_chart(fig_por_cuenta)
            with st.popover("Mostrar detalle en tabla"):
             st.dataframe(gastos_por_cuenta.round(rounding_dict),hide_index=True)
        with t2:
            # Add a multiselect filter for analytic_account_id
            selected_analytic_accounts = st.multiselect("Filtrar por cuenta analitica", analytic_account_ids)

            # Filter gastos_por_situacion based on selected general budgets
            if selected_analytic_accounts:
                gastos_por_situacion = ppto_gastos[ppto_gastos["analytic_account_id"].isin(selected_analytic_accounts)].groupby(["general_budget_id"]).agg({'practical_amount':'sum', 'planned_amount':'sum'}).reset_index()
            else:
                gastos_por_situacion = ppto_gastos.groupby(["general_budget_id"]).agg({'practical_amount':'sum', 'planned_amount':'sum'}).reset_index()

            gastos_por_situacion["Percentage"] = (gastos_por_situacion["practical_amount"] / gastos_por_situacion["planned_amount"]) * 100
            gastos_por_situacion["Gap"] = gastos_por_situacion["planned_amount"] - gastos_por_situacion["practical_amount"]
            with st.popover("Mostrar detalle en tabla"):
                st.dataframe(gastos_por_situacion.round(rounding_dict),hide_index=True)
if __name__ == "__main__":
    main()

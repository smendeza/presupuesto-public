import plotly.graph_objects as go

def create_monthly_plot(gastos_por_mes):
    # Create the Plotly  chart
    fig = go.Figure()
    # Add the practical amount segments
    fig.add_trace(go.Bar(
        x=gastos_por_mes['date_from'],
        y=gastos_por_mes['practical_amount'],
        #orientation='h',
        marker=dict(color='blue'),
        name='Ejecutado',
        hoverinfo='text',
        hovertext=gastos_por_mes.apply(lambda row: f"Ejecutado: L{row['practical_amount']:,.0f}<br>Porcentaje: {row['Ejecucion']:.1f}%<br>Gap: {row['Gap']:,.0f}", axis=1)
    ))
    
    # Add the planned amount points
    fig.add_trace(go.Scatter(
        x=gastos_por_mes['date_from'],
        y=gastos_por_mes['planned_amount'],
        mode='lines+markers',
        marker=dict(color='gray', size=10),
        name='Planificado',
        hoverinfo='text',
        hovertext=gastos_por_mes.apply(lambda row: f"Planificado: L{row['planned_amount']:,.0f}", axis=1)
    ))

    # Customize the layout
    fig.update_layout(
        title='Ejecucion por mes',
        xaxis=dict(title='Mes'),
        yaxis=dict(title='Monto (L)'),
        barmode='overlay',
        height=400,
        width=500,
        hovermode='closest',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )                
    )
    return fig


def create_analyticgroup_plot(gastos_por_grupo):
    # Create the Plotly  chart
    fig = go.Figure()
    # Add the practical amount segments
    fig.add_trace(go.Bar(
        x=gastos_por_grupo['analytic_group_id'],
        y=gastos_por_grupo['practical_amount'],
        #orientation='h',
        marker=dict(color='blue'),
        name='Ejecutado',
        hoverinfo='text',
        hovertext=gastos_por_grupo.apply(lambda row: f"Ejecutado: L{row['practical_amount']:,.0f}<br>Porcentaje: {row['Ejecucion']:.1f}%<br>Gap: {row['Gap']:,.0f}", axis=1)
    ))
    
    # Add the planned amount points
    fig.add_trace(go.Scatter(
        x=gastos_por_grupo['analytic_group_id'],
        y=gastos_por_grupo['planned_amount'],
        mode='lines+markers',
        marker=dict(color='gray', size=10),
        name='Planificado',
        hoverinfo='text',
        hovertext=gastos_por_grupo.apply(lambda row: f"Planificado: L{row['planned_amount']:,.0f}", axis=1)
    ))

    # Customize the layout
    fig.update_layout(
        title='Ejecucion por grupo analitico',
        xaxis=dict(title='Grupo analitico'),
        yaxis=dict(title='Monto (L)'),
        barmode='overlay',
        height=400,
        width=500,
        hovermode='closest',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )                
    )
    return fig


def create_analyticaccount_plot(gastos_por_cuenta):
# Create the Plotly bullet chart
    fig = go.Figure()

    # Add the planned amount segments
    fig.add_trace(go.Bar(
        x=gastos_por_cuenta['planned_amount'],
        y=gastos_por_cuenta['analytic_account_id'],
        orientation='h',
        marker=dict(color='lightgray'),
        name='Planned Amount',
        hoverinfo='text',
        hovertext=gastos_por_cuenta['planned_amount'].apply(lambda x: f'Planned Amount: L{x:,.0f}')
    ))

    # Add the practical amount segments
    fig.add_trace(go.Bar(
        x=gastos_por_cuenta['practical_amount'],
        y=gastos_por_cuenta['analytic_account_id'],
        orientation='h',
        marker=dict(color='blue'),
        name='Practical Amount',
        hoverinfo='text',
        hovertext=gastos_por_cuenta.apply(lambda row: f"Practical Amount: L{row['practical_amount']:,.0f}<br>Percentage: {row['Percentage']:.1f}%", axis=1)
    ))

    # Add the planned amount points
    fig.add_trace(go.Scatter(
        x=gastos_por_cuenta['planned_amount'],
        y=gastos_por_cuenta['analytic_account_id'],
        mode='markers',
        marker=dict(color='grey', size=10, symbol='line-ns-open'),
        name='Planned Amount',
        hoverinfo='text',
        hovertext=gastos_por_cuenta['Gap'].apply(lambda x: f'Gap: L{x:,.0f}')
    ))

    # Customize the layout
    fig.update_layout(
        title='Ejecucion por cuenta analitica',
        xaxis=dict(title='Monto (L)'),
        yaxis=dict(title='Cuenta analitica'),
        barmode='overlay',
        height=600,
        width=800   ,
        hovermode='closest',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )                       
    )
    return fig
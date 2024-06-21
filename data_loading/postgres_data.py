import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use environment variables
dbname = os.environ.get('POSTGRES_DB')
user = os.environ.get('POSTGRES_USER')
password = os.environ.get('POSTGRES_PASSWORD')
host = os.environ.get('POSTGRES_HOST')
port = os.environ.get('POSTGRES_PORT')


import pandas as pd
import streamlit as st
# Initialize an empty list to store individual DataFrames
from sqlalchemy import create_engine

engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{dbname}')



#Venta historica segun BI
@st.cache_data
def leer_ventas():
    historico=pd.read_sql('historico_ventas_bi',engine) 
    location_map={'Tienda Ruben Dario':'RDA/Stock',
        'Contact Center':'RDA/Stock',
        'Tienda Choluteca Unimall':'CUM/Stock',
        'Tienda Las Acacias':'LAC/Stock',
        'Tienda Santa Rosa de Copán':'SRC/Stock',
        'Tienda Suyapa':'SUY/Stock',
        'Tienda Bermejo':'BER/Stock',
        'Tienda Comayagua':'COM/Stock',
        'Tienda La Ceiba':'LCB/Stock',
        'Tienda Choluteca Vicente Williams':'CVW/Stock',
        'Tienda Juticalpa':'JUT/Stock',
        'Tienda HMC':'HMC/Stock',
        'Tienda City Mall':'CTM/Stock',
        'Tienda La Granja':'LGJ/Stock',
        'Tienda Danlí':'DNL/Stock'
        }
    historico['location_id']= historico['name'].map(location_map)
    #historico = historico[historico['Date']>="2023-01-01"]
    return historico

@st.cache_data
def leer_ventas_consolidadas():
    sales = pd.read_sql("consolidado",engine)
    return sales

@st.cache_data
def leer_ventas_ir(historico):
    sales_summary = pd.read_sql('sales_summary',engine) 
    sales_summary = sales_summary.groupby(['product_id','Date']).agg({'Ventas':'sum','Unidades':'sum'}).reset_index()

    sales_summary['tipo']='IR'
    max_date=historico.Date.max()
    #sales_summary=sales_summary[sales_summary["Date"]>max_date]
    sales=historico.groupby(['product_id','Date']).agg({'Ventas':'sum','Unidades':'sum'}).reset_index()
    sales['tipo']='HI'
    sales_updated=pd.concat([sales,sales_summary])
    return(sales_updated)

import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

import xmlrpc
import pandas as pd
import streamlit as st
# Use environment variables
url = os.environ.get('ODOO_URL')
db = os.environ.get('ODOO_DB')
username = os.environ.get('ODOO_USERNAME')
password = os.environ.get('ODOO_PASSWORD')
import xmlrpc.client
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
from utils.timestamp_utils import adjust_timestamps

@st.cache_data()
def leer_presupuesto():

    domain = [
        
    ]
    fields = [
        'general_budget_id',
        "analytic_account_id",
        "analytic_group_id",
        'date_from',
        'date_to',
        "planned_amount",
        "practical_amount",
        'planned_amount',
        "theoritical_amount",
        "percentage"
    ]
    context = {"lang": "es_ES"}
    # Query the records that have been modified since the last refresh date
    lineas = models.execute_kw(db, uid, password, 'crossovered.budget.lines', 'search_read', [domain, fields], {'context': context})
    lineas = pd.DataFrame(lineas) # type: ignore
    lineas.general_budget_id = lineas.general_budget_id.str[1]
    lineas.analytic_account_id = lineas.analytic_account_id.str[1]
    lineas.analytic_group_id = lineas.analytic_group_id.str[1]
    lineas.date_from=pd.to_datetime(lineas.date_from)
    lineas["year"] = lineas.date_from.dt.year
    return(lineas)


@st.cache_data()
def leer_ingresos(product_ids):

    domain = [
        ["product_id","in",product_ids],
        ["location_id",'ilike','vendor'],
        ['state','=','done']
    ]
    fields = [
        'product_id',
        "qty_done",
        'date',
        'origin'
    ]
    context = {"lang": "es_ES"}
    # Query the records that have been modified since the last refresh date
    lineas = models.execute_kw(db, uid, password, 'stock.move.line', 'search_read', [domain, fields], {'context': context})
    lineas = pd.DataFrame(lineas) # type: ignore
    lineas.product_id=lineas.product_id.str[0]
    #lineas = lineas.groupby('product_id').last().reset_index()
    lineas = lineas.groupby(["product_id",'date','origin']).agg({'qty_done':'sum'}).reset_index()
    lineas.date = pd.to_datetime(lineas.date)
    lineas = adjust_timestamps(df=lineas, cols=["date"],hours=-6)
    return(lineas)
@st.cache_data()
def leer_venta_perdida():
    domain = [

    ]
    fields = [
        'create_uid',
        'pos_config_id',
        'product_id',
        "quantity",
        'notes',
        'create_date'
    ]
    context = {"lang": "es_ES"}
    # Query the records that have been modified since the last refresh date
    lineas = models.execute_kw(db, uid, password, 'pos.lost.sale', 'search_read', [domain, fields], {'context': context})
    lineas = pd.DataFrame(lineas)# type: ignore
    lineas.create_uid = lineas.create_uid.str[1]
    lineas.pos_config_id = lineas.pos_config_id.str[0]
    #lineas.register_partner_id=lineas.register_partner_id.str[1]
    lineas.product_id=lineas.product_id.str[0]
    # definir dominio y campos del modelo a ir a traer

    # Define the domain for the product model
    domain = [

    ]

    fields = [
        'id',
        'crm_team_id'
        ]
    context = {"lang": "es_ES"}

    cajas = models.execute_kw(db, uid, password, 'pos.config', 'search_read', [domain, fields], {'context': context})
    cajas = pd.DataFrame(cajas)# type: ignore
    cajas.crm_team_id=cajas.crm_team_id.str[1]
    lineas=lineas.merge(cajas, left_on='pos_config_id', right_on='id').drop(columns=['id_x','id_y','pos_config_id'])
    return(lineas)
@st.cache_data()
def leer_ubicaciones():

    ubicaciones = ['Stock','Inter-warehouse transit']
    #stock locations
    domain = [
       ["name","in",ubicaciones],
    #  ['name','=','Stock']
    ]
    
    fields = [
        "name",
        "complete_name",
    ]
    context = {"lang": "es_ES"}
    # Query the records that have been modified since the last refresh date
    stock_locations = models.execute_kw(db, uid, password, 'stock.location', 'search_read', [domain, fields], {'context': context})

    # Print the updated records
    stock_locations=pd.DataFrame(stock_locations)# type: ignore
    location_ids=stock_locations.id.to_list()
    return stock_locations,location_ids
@st.cache_data()
def leer_productos():
    # definir dominio y campos del modelo a ir a traer
    active=[True,False]
    # Define the domain for the product model
    domain = [
        ["active", "in", active],
        ["detailed_type", "=", "product"],
        ["default_code", "!=", False]
    ]

    fields = [
        'id',
        "default_code", 
        'name',
        'active',
        'product_tmpl_id'
        ]
    context = {"lang": "es_ES"}

    products = models.execute_kw(db, uid, password, 'product.product', 'search_read', [domain, fields], {'context': context})
    products = pd.DataFrame(products)# type: ignore
    products=products.rename(columns={'id':'product_id','name':'nombre'})
    products.product_tmpl_id = products.product_tmpl_id.str[0]

    return products
@st.cache_data()
def leer_existencias(product_ids,location_ids):

    locations=['Stock','Transit','Entrada']
    if isinstance(product_ids, list) and product_ids:
            #stock locations
        domain = [
        ["location_id","in",location_ids],
        ['product_id','in',product_ids]
        ]
    else:
        #stock locations
        domain = [
        ["location_id","in",location_ids]
        ]
    
    fields = [
        "location_id",
        "product_id",
        "quantity",
        "value"
    ]
    context = {"lang": "es_ES"}
    # Query the records that have been modified since the last refresh date
    stock_quant = models.execute_kw(db, uid, password, 'stock.quant', 'search_read', [domain, fields], {'context': context})

    # Print the updated records
    stock_quant=pd.DataFrame(stock_quant)# type: ignore
    stock_quant["product_id.id"]=stock_quant.product_id.str[0]
    stock_quant["product_id"]=stock_quant.product_id.str[1]
    stock_quant["location_id.id"]=stock_quant.location_id.str[0]
    stock_quant["location_id"]=stock_quant.location_id.str[1]
    return(stock_quant)

@st.cache_data
def leer_transitos(products):
    destinos = ["CDI/Entrada","BCC/Stock"]
    estados = ["assigned","waiting","confirmed"]
    #getting tansits from stock picking
    domain = [
        ["location_dest_id","in",destinos],
        ["state","in", estados],
        ['location_id','ilike','vendor']
    ]
    fields = [
        'name',
        "state",
        "scheduled_date",
        'income_state',
        'batch_id',
        'origin',
        'id'
    ]
    context = {"lang": "es_ES"}
    # Query the records that have been modified since the last refresh date
    picking = models.execute_kw(db, uid, password, 'stock.picking', 'search_read', [domain, fields], {'context': context})
    picking = pd.DataFrame(picking)# type: ignore
    pick_ids=picking.id.tolist()
    picking.batch_id = picking.batch_id.str[1]
    #getting transits from stock picking
    domain = [
        ["picking_id","in",pick_ids]
    ]
    fields = [
        'product_id',
        "qty_done",
        "product_qty",
        "picking_id"
    ]
    context = {"lang": "es_ES"}
    # Query the records that have been modified since the last refresh date
    lineas = models.execute_kw(db, uid, password, 'stock.move.line', 'search_read', [domain, fields], {'context': context})
    lineas = pd.DataFrame(lineas)# type: ignore
    lineas.picking_id=lineas.picking_id.str[0]
    lineas.product_id=lineas.product_id.str[0]
    transito=lineas.merge(picking, left_on="picking_id", right_on="id")
    transito=adjust_timestamps(transito,["scheduled_date"],-6)
    transito=transito.merge(products, left_on="product_id",right_on="product_id")
    import datetime 
    transito.scheduled_date=pd.to_datetime(transito.scheduled_date)
    transito["year"]=transito.scheduled_date.dt.year
    transito["month"]=transito.scheduled_date.dt.month
    transito["day"]=transito.scheduled_date.dt.day
    transito["year_month"]=pd.to_datetime(transito.year.astype(str) + '-' + transito.month.astype(str)) 
    # # format the year_month column to year-month
    transito['year_month'] = transito['year_month'].dt.strftime('%Y-%m')
    resumen=transito.groupby(["product_id",'default_code','nombre','year_month','batch_id']).agg({'product_qty':"sum"})
    transito = transito[['origin','name',"product_id",'default_code','nombre','product_qty','scheduled_date','income_state','batch_id']]
    transito = transito.groupby(['origin','name',"product_id",'default_code','nombre','scheduled_date','income_state']).agg({'product_qty':'sum'}).reset_index()

    return(transito,resumen)

@st.cache_data
def leer_proveedores():
    domain = [

    ]
    fields = [
        'name',
        'product_tmpl_id'

    ]
    context = {"lang": "es_ES"}
    # Query the records that have been modified since the last refresh date
    supplierinfo = models.execute_kw(db, uid, password, 'product.supplierinfo', 'search_read', [domain, fields], {'context': context})
    supplierinfo = pd.DataFrame(supplierinfo)# type: ignore
    supplierinfo.name=supplierinfo.name.str[1]
    supplierinfo.product_tmpl_id=supplierinfo.product_tmpl_id.str[0]
    return(supplierinfo)

@st.cache_data
def leer_compras():
    # domain = [
    #     ["product_id","in",prd_id],
    #     ['state','=','purchase']
    # ]
    # fields = [
    #     'product_id',
    #     'state',
        
    #     "product_uom_qty",
    #     "product_qty",
    #     "qty_invoiced",
    #     'qty_received',
    #     'order_id'
    # ]
    # context = {"lang": "es_ES"}
    # purchase_lines = models.execute_kw(db, uid, password, 'purchase.order.line', 'search_read', [domain, fields], {'context': context})
    # purchase_lines = pd.DataFrame(purchase_lines)# type: ignore
    # purchase_lines.product_id = purchase_lines.product_id.str[0]
    # purchase_lines.order_id = purchase_lines.order_id.str[0]
    # purchase_lines["uom_conv"] = purchase_lines.product_uom_qty/purchase_lines.product_qty
    # purchase_lines.qty_invoiced = purchase_lines.qty_invoiced*purchase_lines.uom_conv
    # purchase_lines.qty_received = purchase_lines.qty_received*purchase_lines.uom_conv
    # order_ids=purchase_lines.order_id.to_list()

    domain = [
        ["state","=",'purchase']
    ]
    fields = [
        'date_approve',
        'name',
        'partner_id',
        'effective_date',
        'payment_term_id',
        'amount_total',
        'amount_residual',
        'currency_id',
        'invoice_status',
        'account_payment_ids'
    ]
    context = {"lang": "es_ES"}
    purchases = models.execute_kw(db, uid, password, 'purchase.order', 'search_read', [domain, fields], {'context': context, 'limit':5})
    purchases = pd.DataFrame(purchases)# type: ignore
    purchases.payment_term_id = purchases.payment_term_id.str[1]
    purchases.partner_id = purchases.partner_id.str[1]
    purchases.currency_id = purchases.currency_id.str[1]

    return(purchases)

@st.cache_data
def leer_facturas_proveedor():
    tipos=['in_invoice','in_refund']
    domain = [
        ["payment_state","=",'not_paid'],
        ['state','=','posted'],
        ['move_type','in',tipos]
    ]
    fields = [
        'create_date',
        'invoice_date',
        'invoice_date_due',
        'name',
        'partner_id',
        'invoice_payment_term_id',
        'currency_id',  
        'amount_total',
        'amount_residual'  ]
    context = {"lang": "es_ES"}
    invoice = models.execute_kw(db, uid, password, 'account.move', 'search_read', [domain, fields], {'context': context})
    invoice = pd.DataFrame(invoice)
    invoice.partner_id  = invoice.partner_id.str[1]
    invoice.currency_id = invoice.currency_id.str[1]
    invoice.invoice_payment_term_id = invoice.invoice_payment_term_id.str[1]
    return invoice

@st.cache_data
def leer_pagos_pendientes():

    domain = [
        ['state','=','posted'],
        ['payment_type','=','outbound'],
        ['is_internal_transfer','=',False],
        ['date','>=','2024-01-01'],
        ['date','<=','2024-04-22']

    ]
    fields = [

        'amount_total', # monto total de la transaccion en moneda
        'amount_total_signed',# monto total de la transaccion en moneda local (L)
        'currency_id', 
        'reconciled_bill_ids', # facturas de proveedor coinciliadas
        'reconciled_bills_count',
        'name', # pago
        'is_an_advance_payment',
        'partner_id',
        'reconciled_statement_ids',
        'date',
        'ref'


    ]
    context = {"lang": "es_ES"}
    pagos = models.execute_kw(db, uid, password, 'account.payment', 'search_read', [domain, fields], {'context': context})

    pagos = pd.DataFrame(pagos)
    pagos.partner_id = pagos.partner_id.str[1]
    pagos.currency_id = pagos.currency_id.str[1]
    return(pagos)
import streamlit as st
import pandas as pd
import re
import datetime as dt
import sqlite3 as sqlite
from sqlite3 import Error

# Basic layout of the page
st.set_page_config(page_title='Exp Date Verification ✔️')
st.title('Expiration Date Validation ✔️')

st.write('Scan the barcode on the Case Label')

# ------------------------------------------------------------------
# Create the SQL connection to db
def create_connection(db_file):
    
    conn = None
    
    try:
        conn = sqlite.connect(db_file)

    except Error as e:
        print(e)
    return conn

conn = create_connection('first_label_scan.db')
cur = conn.cursor()
# cur.execute("DROP TABLE IF EXISTS scan_record")
# ------------------------------------------------------------------

def insertData(a, b, c, d, e):
    cur.execute("""CREATE TABLE IF NOT EXISTS scan_record (scan_time DATETIME, item_gtin nvarchar(14), lot nvarchar(4), exp_date nvarchar(6), if_pass nvarchar(3));""")
    cur.execute("""INSERT INTO scan_record VALUES(?, ?, ?, ?, ?)""", (a, b, c, d, e))
    conn.commit()
    
# ------------------------------------------------------------------

placeholder = st.empty()
barcode = placeholder.text_input('Barcode', key='Barcode')

# Define patterns for each number you want to extract
gtin_pattern = re.compile(r'\(01\)(\d+)')
exp_pattern = re.compile(r'\(17\)(\d+)')
lot_pattern = re.compile(r'\(10\)(\d+)')

# Use findall to extract the numbers
result_1 = re.findall(gtin_pattern, barcode)
result_2 = re.findall(exp_pattern, barcode)
result_3 = re.findall(lot_pattern, barcode)

# Convert the results to integers
gtin = int(result_1[0]) if result_1 else None
exp = int(result_2[0]) if result_2 else None
lot = int(result_3[0]) if result_3 else None

# Convert exp to text
exp = str(exp)

# Get today date
today = dt.date.today()

corr_exp = dt.date(today.year + 3, today.month, 1).strftime('%y%m%d')

scan_time = dt.datetime.today().strftime('%Y-%m-%d %H:%M:%S')

check_button = st.button('Check', help='Click to verify the expiration date')

if check_button:
    if exp == corr_exp:
        if_pass = "Yes"
        insertData(scan_time, gtin, lot, exp, if_pass)
        st.markdown(f'✅ Lot: {lot} has the correct expiration date on the label.')
        st.success(f"Validation successful!")
        
    else:
        if_pass = "No"
        insertData(scan_time, gtin, lot, exp, if_pass)
        st.warning('Double Check the Expiration Date', icon="⚠️")
        st.error(f"Expiration Date: {dt.date(today.year + 3, today.month, 1).strftime('%Y-%m-%d')}")

def clear_barcode():
    st.session_state['Barcode'] = ""

reset_button = st.button('Reset', type='primary', on_click=clear_barcode)

#if reset_button:
#    barcode = placeholder.text_input('Barcode', value='', key=2)
#    st.rerun()

st.write("Reach out to QA Dept for any needs to review the scanning records.")

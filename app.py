import streamlit as st
import pandas as pd
import re
import datetime as dt
import pyautogui

st.set_page_config(page_title='Exp Date Verification ✔️')
st.title('Expiration Date Velidation ✔️')

st.write('Scan the barcode on the Case Label')

realans = ['', 'abc', 'edf']

if  st.session_state['answer'] in realans:
    answerStat = "correct"
elif st.session_state['answer'] not in realans:
    answerStat = "incorrect"
    
st.write(st.session_state)
st.write(answerStat)

barcode = st.text_input('Barcode')

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

# Convert the Exp to time format
Exp = pd.to_datetime(exp, format='%y%m%d')
# Get today date
today = dt.date.today()

corr_exp = dt.date(today.year + 3, today.month, 1).strftime('%y%m%d')

check_button = st.button('Check', help='Click to verify the expiration date')

if check_button:
    if Exp == corr_exp:
        st.markdown(f'✅ Lot: {lot} has the correct expiration date on the label.')
        st.success(f"Validation successful!")
    else:
        st.warning('Double Check the Expiration Date', icon="⚠️")
        st.error(f"Expiration Date: {dt.date(today.year + 3, today.month, 1).strftime('%Y-%m-%d')}")

reset_button = st.button('Reset', type='primary')

if reset_button:
    pyautogui.hotkey('ctrl', 'F5')
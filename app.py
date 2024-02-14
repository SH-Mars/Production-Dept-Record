import streamlit as st
import re
import datetime as dt
import pyodbc
import smtplib as s
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# from keys import sql_user_name, email_sender, password, email_receiver

# Basic layout of the page
st.set_page_config(page_title='Exp Date Verification ✔️')
st.title('Expiration Date Validation ✔️')

st.write('Scan the barcode on the Case Label')

# ------------------------------------------------------------------

def insert_data_into_sql_server(a, b, c, d, e):
    
    try:
        # Create the SQL connection to db
        connection_string = 'DRIVER={SQL Server};SERVER=TEST-VM04;DATABASE=first_label_scan;UID=APLUS_NT\shihhsienma;Trusted_Connection=yes;'

        # Establish a connection to the database
        conn = pyodbc.connect(connection_string)

        # Create a cursor object
        cursor = conn.cursor()

        # cursor.execute("""CREATE TABLE IF NOT EXISTS scan_record (scan_time DATETIME, item_gtin nvarchar(14), lot nvarchar(4), exp_date nvarchar(6), if_pass nvarchar(3));""")
        cursor.execute("""INSERT INTO scan_record VALUES(?, ?, ?, ?, ?)""", (a, b, c, d, e))
    
        # Commit the query
        cursor.commit()
    
        # Close the cursor and connection
        cursor.close()
        conn.close()
    
        return True
    
    except pyodbc.Error as e:
        st.error(f"Error: {e}")
        return False
        
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

# ------------------------------------------------------------------

def email_notification(a, b, c, d, e):
    try:
        # Create the email message
        message = MIMEMultipart()
        message["From"] = a
        message["To"] = e
        message["Subject"] = c
        message.attach(MIMEText(d, "plain"))
        
        server = s.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(a, b)

        # Send the email
        server.sendmail(a, e, message.as_string())

        print("Email sent successfully!")

    except s.SMTPException as e:
        print(f"Error: {e}")

    finally:
        # Close the connection
        server.quit()
# ------------------------------------------------------------------

email_sender = st.secrets["email_sender"]
password = st.secrets["password"]
subject = 'Label Expiration Date Validation Failed'
body = f"""
    A First Piece Label Expiration Date Validation of Lot {lot} just failed. Please double check with the Production Dept to ensure the accuracy.
"""
email_receiver = st.secrets["email_receiver"]

# ------------------------------------------------------------------

if_pass = ""

if check_button:
    if exp == corr_exp:
        if_pass = "Yes"
        
        st.markdown(f'✅ Lot: {lot} has the correct expiration date on the label.')
        st.success(f"Validation successful!")
        
        if insert_data_into_sql_server(scan_time, gtin, lot, exp, if_pass):  
            st.success("Data inserted successfully!")
        else:
            st.error("Failed to insert data.")    
        
    else:
        if_pass = "No"
        
        st.warning('Double Check the Expiration Date', icon="⚠️")
        st.error(f"Expiration Date: {dt.date(today.year + 3, today.month, 1).strftime('%Y-%m-%d')}")
        
        email_notification(email_sender, password, subject, body, email_receiver)

        if insert_data_into_sql_server(scan_time, gtin, lot, exp, if_pass):  
            st.success("Data inserted successfully!")
        else:
            st.error("Failed to insert data.")
            
def clear_barcode():
    st.session_state['Barcode'] = ""

reset_button = st.button('Reset', type='primary', on_click=clear_barcode)

#if reset_button:
#    barcode = placeholder.text_input('Barcode', value='', key=2)
#    st.rerun()

st.write("Reach out to QA Dept for any needs to review the scanning records.")

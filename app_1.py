import streamlit as st
import pandas as pd
import re
import pytz
import datetime as dt
import smtplib as s
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sqlite3 as sqlite
# from keys import sql_user_name, email_sender, password, email_receiver

# -----------------------------------------------------------------
# Login
def login():
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("password", type='password')
    login_button = st.button("Login")
    
    if login_button:
        if username == st.secrets["login_username"] and password == st.secrets["login_password"]:
            st.session_state.logged_in = True
        else:
            st.error("Invalid credentials")
# ------------------------------------------------------------------
# SQLite connection
conn = sqlite.connect('first_label_scan.db')
cur = conn.cursor()
# cur.execute("DROP TABLE IF EXISTS scan_record")

def insertData(a, b, c, d, e):
    cur.execute("""CREATE TABLE IF NOT EXISTS scan_record (scan_time TEXT(50), item_gtin TEXT(14), lot TEXT(4), exp_date TEXT(6), if_pass TEXT);""")
    cur.execute("""INSERT INTO scan_record VALUES (?, ?, ?, ?, ?)""", (a, b, c, d, e))
    conn.commit()    

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
        
        
def clear_barcode():
        st.session_state['Barcode'] = ""

# ------------------------------------------------------------------

def main():
    # Basic layout of the page
    st.set_page_config(page_title='Exp Date Verification ✔️')
    st.title('Expiration Date Validation ✔️')
    
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        login()
    
    else:
        st.write('Scan the barcode on the Case Label')
        
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

        # Convert to text
        gtin = str(gtin)
        exp = str(exp)
        lot = str(lot)

        # Get today date
        today = dt.date.today()

        corr_exp = dt.date(today.year + 3, today.month, 1).strftime('%y%m%d')
        
        tzInfo = pytz.timezone('America/Los_Angeles')
        scan_time = dt.datetime.now(tz=tzInfo).strftime('%Y-%m-%d %H:%M:%S')

        check_button = st.button('Check', help='Click to verify the expiration date')

# ------------------------------------------------------------------
        email_sender = st.secrets["email_sender"]
        password = st.secrets["password"]
        subject = '❗Label Expiration Date Validation Failed⚠️'
        body = f"""
        A First Piece Label Expiration Date Validation of Lot {lot} just failed. 
        Please double check with the Production Dept to ensure the accuracy.
        """
        email_receiver = st.secrets["email_receiver"]
# ------------------------------------------------------------------
        if_pass = ""

        if check_button:
            if exp == corr_exp:
                if_pass = "Yes"
                st.markdown(f'✅ Lot: {lot} has the correct expiration date on the label.')
                st.success(f"Validation successful!")

                insertData(scan_time, gtin, lot, exp, if_pass)   
                
                st.success("Data inserted successfully!")
            else:
                if_pass = "No"
                st.warning('Double Check the Expiration Date', icon="⚠️")
                st.error(f"Expiration Date: {dt.date(today.year + 3, today.month, 1).strftime('%Y-%m-%d')}")
                
                for person in email_receiver:
                    receiver = person
                    email_notification(email_sender, password, subject, body, receiver)
                    
                insertData(scan_time, gtin, lot, exp, if_pass)
                
                st.success("Data inserted successfully!")

        st.button('Reset', type='primary', on_click=clear_barcode)

        st.write("Reach out to QA Dept for any needs to review the scanning records.")



        show_data = st.button('Previous Data')

        if show_data:
            db_table = pd.read_sql_query("SELECT * FROM scan_record ORDER BY scan_time", conn)
            st.dataframe(db_table)
# ------------------------------------------------------------------
if __name__ == "__main__":
    main()

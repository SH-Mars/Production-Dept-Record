import streamlit as st
import pandas as pd
import re
import pytz
import datetime as dt
import smtplib as s
import pymongo
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
# MongoDB connection
username = st.secrets["mongo_username"]
password = st.secrets["mongo_password"]
CONNECTION_STRING = f"mongodb+srv://{username}:{password}@cluster.89jetih.mongodb.net/"

client = pymongo.MongoClient(CONNECTION_STRING)
db = client["first_label_scan"]
collection = db['scan_record']

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
    st.title('Expiration Date Verification ✔️')
    st.write("")
    
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        login()
    
    else:
        st.write(r"$\textsf{\Large Scan the barcode on the Case Label}$")
        
        placeholder = st.empty()
        barcode = placeholder.text_input('Barcode', key='Barcode')

        # Define patterns for each number you want to extract
        gtin_pattern = re.compile(r'\(01\)(\d{14})')
        exp_pattern = re.compile(r'\(17\)(\d{6})')
        lot_pattern = re.compile(r'\(10\)([\d,\.]+)$')

        # Use findall to extract the numbers    
        result_1 = re.findall(gtin_pattern, barcode)
        result_2 = re.findall(exp_pattern, barcode)
        result_3 = re.findall(lot_pattern, barcode)

        # Convert the results to integers
        gtin = str(result_1[0]) if result_1 else None
        exp = str(result_2[0]) if result_2 else None
        lot = str(result_3[0]) if result_3 else None

        # Get today date
        today = dt.date.today()

        corr_exp = dt.date(today.year + 3, today.month, 1).strftime('%y%m%d')
        
        tzInfo = pytz.timezone('America/Los_Angeles')
        scan_time = dt.datetime.now(tz=tzInfo).strftime('%Y-%m-%d %H:%M:%S')

        check_button = st.button('Check', help='Click to verify the expiration date')

# ------------------------------------------------------------------
        email_sender = st.secrets["email_sender"]
        password = st.secrets["password"]
        subject = 'Label Expiration Date Verification Failed'
        body = f"""
        A First Piece Label Expiration Date Verification of Lot {lot} just failed. 
        Please double check with the Production Dept to ensure the accuracy.
        """
        email_receiver = st.secrets["email_receiver"]
# ------------------------------------------------------------------
        if_pass = ""

        if check_button:
            
            if barcode == "":
                st.warning('Please scan the barcode before clicking Check button.', icon="⚠️")
                
            elif gtin == "None" or lot == "None" or exp == "None":
                st.warning('Please clear out and make sure to scan the barcode properly then try again.', icon="⚠️")
            
            elif (lot.isdigit() == False) or (len(lot)!= 4):
                st.warning('Please check the Lot Number, if there is a typo or extra character.', icon="⚠️")
            
            elif barcode != "" and exp == corr_exp:
                if_pass = "Yes"
                st.markdown(f'✅ Lot: {lot} has the correct expiration date on the label.')
                st.success(f"Verification successful!")

                new_record = {'scan_time': scan_time, 'item_gtin': gtin, 'lot': lot, 'exp_date': exp, 'if_pass': if_pass}
                collection.insert_one(new_record)
                
                st.success("Data inserted successfully!")
            else:
                if_pass = "No"
                st.warning('Double Check the Expiration Date', icon="⚠️")
                st.error(f"Expiration Date: {dt.date(today.year + 3, today.month, 1).strftime('%Y-%m-%d')}")
                
                for person in email_receiver:
                    receiver = person
                    email_notification(email_sender, password, subject, body, receiver)
                    
                new_record = {'scan_time': scan_time, 'item_gtin': gtin, 'lot': lot, 'exp_date': exp, 'if_pass': if_pass}
                collection.insert_one(new_record)
                
                st.success("Data inserted successfully!")

        st.button('Reset', type='primary', on_click=clear_barcode)

        st.write("Reach out to QA Dept for any needs to review the scanning records.")

        show_data = st.button('Previous Data')

        if show_data:
            df = pd.DataFrame(list(collection.find()))
            st.dataframe(df)
                
        #for row in result:
            #st.write(f"ID: {row.id}, scan_time: {row.scan_time}, GTIN: {row.item_gtin}, Lot: {row.lot}, Exp Date: {row.exp_date}, if_pass: {row.if_pass}")
# ------------------------------------------------------------------
if __name__ == "__main__":
    main()

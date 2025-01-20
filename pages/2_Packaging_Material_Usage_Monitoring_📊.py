import streamlit as st
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Image, Table, TableStyle
import io
import pytz
import datetime as dt
import pymongo
import base64

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
collection = db['packaging_material']

# ------------------------------------------------------------------
# generate PDF file for label printint
def generate_pdf(image_path, user_data, image_width=135, image_height=115):
    
    buffer = io.BytesIO()
    
    # create a pdf document
    custom_page_size = (500, 500)
    doc = SimpleDocTemplate(buffer, pagesize=custom_page_size, topMargin=10, bottomMargin=0)
    
    # define the content
    content = []
    image = Image(image_path, width=image_width, height=image_height)
    image.rotate = 90
    content.append(image)
    
    # add data as a table
    data = []
    for key, value in user_data.items():
        data.append([key, value])
        
    table = Table(data, hAlign='CENTER')
    table_style = TableStyle([('BACKGROUND', (0,0), (-1,0), colors.grey),
                              ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
                              ('ALIGN', (0,0), (-1,-1), 'CENTER'),  # Alignment
                              ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),  # Vertical alignment
                              ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
                              ('FONTSIZE', (0,0), (-1,-1), 12),
                              ('FONTSIZE', (0,0), (-1,0), 16),
                              ('BACKGROUND', (0,1), (-1,-1), colors.beige),
                              ('GRID', (0,0), (-1,-1), 1, colors.black),
                              ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                              ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                              ('ROTATE', (0,0), (-1,-1), 90)])
    
    table.setStyle(table_style)
    content.append(table)
    
    doc.build(content)
    buffer.seek(0)
    return buffer
# ------------------------------------------------------------------

# Streamlit App
def main():
    
    # Basic layout of the page
    st.set_page_config(page_title='Packaging Roll Material Usage Monitoring 📊')
    st.title("Packaging Roll Material Usage Monitoring 📊")
    st.subheader("Production Order Record Attachment")
    st.write("")
    st.write("")
    
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        login()
    
    else:
        st.write(r"$\textsf{\Large Select the Material Type}$")
        options = ['Tyvek', 'Soft Pack', 'Rigid Tray']
        material_type = st.radio('Material Type', options)
        st.write("")
        data = {}

        # set timezone for scan time
        tzInfo = pytz.timezone('America/Los_Angeles')
        
        st.write(r"$\textsf{\Large Scan the Barcode on the Roll Packaging Label Accordingly}$")
    
        # Input fields
        if material_type == 'Tyvek':
            data["Part Number"] = st.text_input('Part Number')
        
            if data["Part Number"] == "RS-T440-1":
                image_path = "images/amcor.png"
                data["Scan Time"] = dt.datetime.now(tz=tzInfo).strftime('%Y-%m-%d %H:%M:%S')
                data["Roll No"] = st.text_input('Roll Number')
                data["Batch Number"] = st.text_input('Batch Number')
                data["MSI"] = st.text_input('MSI')
                # data["PO Number"] = st.text_input('PO No')
            
            else:
                image_path = "images/oliver.png"
                data["Scan Time"] = dt.datetime.now(tz=tzInfo).strftime('%Y-%m-%d %H:%M:%S')
                # data["PO Number"] = st.text_input('PO Number')
                data["Part Desc"] = 'APLS 440mm 0C SL 1059B/27HT-2C'
                # data["Sales Order"] = st.text_input('Sales Order')
                data["Material Number"] = st.text_input('Material #')
                data["Mfg Date"] = st.text_input('Mfg Date')
                data['Qty'] = st.text_input('Qty')
                id = st.text_input('HU ID')
                data["HU ID"] = id[10:]
        
            submit = st.button("Submit")
        
            if submit:
            
                st.info("Generating PDF...")
                pdf_buffer = generate_pdf(image_path, data, 135, 115)
            
                pdf_base64 = base64.b64encode(pdf_buffer.read()).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="700" height="700"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
                st.success('PDF generated successfully!')

                # insert record into db
                collection.insert_one(data)
                
        elif material_type == 'Soft Pack':
            image_path = "images/amcor.png"
            data["Item Number"] = st.text_input('Item No')
            data["Scan Time"] = dt.datetime.now(tz=tzInfo).strftime('%Y-%m-%d %H:%M:%S')
            data["Roll No"] = st.text_input('Roll Number')
            data["Batch Number"] = st.text_input('Batch Number')
            data["MSI"] = st.text_input('MSI')
            # data["PO Number"] = st.text_input('PO No')
        
            submit = st.button("Submit")
        
            if submit:
                st.info("Generating PDF...")
                pdf_buffer = generate_pdf(image_path, data)
            
                pdf_base64 = base64.b64encode(pdf_buffer.read()).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="700" height="700"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
                st.success('PDF generated successfully!')

                # insert record into db
                collection.insert_one(data)
        
        else:
            image_path = "images/primex.png"
            item_number = 'RS-H460-2'
            st.subheader(f"Part Number: {item_number}")
            data["Item Number"] = item_number
            data["Scan Time"] = dt.datetime.now(tz=tzInfo).strftime('%Y-%m-%d %H:%M:%S')
            info = st.text_input('Scan Barcode')
        
            if info != "":
                data["Order No"] = info.split(sep='  ')[0]
                data["Roll #"] = info.split(sep='  ')[1]
        
            submit = st.button("Submit")

            if submit:
                st.info("Generating PDF...")
                pdf_buffer = generate_pdf(image_path, data)
            
                pdf_base64 = base64.b64encode(pdf_buffer.read()).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{pdf_base64}" width="700" height="700"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
                st.success('PDF generated successfully!')

                # insert record into db
                collection.insert_one(data)
            
if __name__ == "__main__":
    table_data = []  # Initialize table data
    main()

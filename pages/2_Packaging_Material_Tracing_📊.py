import streamlit as st
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from PIL import Image
import tempfile
import base64


# generate PDF file for label printint
def generate_pdf(image_path, user_data, image_width, image_height):
  
    # create a temporary file in memory
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file_path = temp_file.name
    
    # create a pdf document
    custom_page_size = (500, 500)
    doc = SimpleDocTemplate(temp_file_path, pagesize=custom_page_size, topMargin=10, bottomMargin=0)
    styles = getSampleStyleSheet()
    
    # define the content
    content = []
    # Prepare the image for the table
    image = Image.open(image_path)
    image = image.resize((image_width, image_height))  # Resize the image if needed
    image_buffer = tempfile.NamedTemporaryFile(delete=False)
    image.save(image_buffer, format="PNG")
    image_buffer.close()
    image.rotate = 90
    content.append(image_buffer.name)
    
    # add data as a table
    data = []
    for key, value in user_data.items():
        data.append([key, value])
        
    table = Table(data)
    table_style = TableStyle([('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                              ('TEXTCOLOR', (0,0), (-1,0), colors.black),
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
    
    # build the PDF
    doc.build(content)
    
    return temp_file_path
    

# Streamlit App
def main():
    st.set_page_config(page_title='Packaging Roll Material Record Tracing 📊')
    st.title("Production Order Record Attachment")
    
    options = ['Tyvek', 'Soft Pack', 'Rigid Tray']
    material_type = st.radio('Material Type', options)
    
    data = {}
    
    # Input fields
    if material_type == 'Tyvek':
        data["Part Number"] = st.text_input('Part Number')
        
        if data["Part Number"] == "RS-T440-1":
            image_path = "images/amcor.png"
          
            data["Item Number"] = st.text_input('Item No')
            data["Roll No"] = st.text_input('Roll Number')
            data["Batch Number"] = st.text_input('Batch Number')
            data["MSI"] = st.text_input('MSI')
            data["PO Number"] = st.text_input('PO No')
            
        else:
            image_path = "images/oliver.png"
        
            data["PO Number"] = st.text_input('PO Number')
            data["Part Desc"] = 'APLS 440mm 0C SL 1059B/27HT-2C'
            data["Sales Order"] = st.text_input('Sales Order')
            data["Material Number"] = st.text_input('Material #')
            data["Mfg Date"] = st.text_input('Mfg Date')
            id = st.text_input('HU ID')
            data["HU ID"] = id[10:]
        
        submit = st.button("Submit")
      
        if submit:
            pdf_path = generate_pdf(image_path, data, 155, 130)
              
            st.success('Table printed successfully!')
                
    elif material_type == 'Soft Pack':
        image_path = "images/amcor.png"
        data["Item Number"] = st.text_input('Item No')
        data["Roll No"] = st.text_input('Roll Number')
        data["Batch Number"] = st.text_input('Batch Number')
        data["MSI"] = st.text_input('MSI')
        data["PO Number"] = st.text_input('PO No')
        
        submit = st.button("Submit")
        
        if submit:
            generate_pdf(image_path, data, 135, 95)
            st.success('Table printed successfully!')
        
    else:
        image_path = "images/primex.png"
        item_number = 'RS-H460-2'
        st.subheader(f"Part Number: {item_number}")
        data["Item Number"] = item_number
        info = st.text_input('Scan Barcode')
        
        if info != "":
            data["Order No"] = info.split(sep='  ')[0]
            data["Roll #"] = info.split(sep='  ')[1]
        
        submit = st.button("Submit")

        if submit:
            generate_pdf(image_path, data, 150, 120)
            st.success('Table printed successfully!')

if __name__ == "__main__":
    table_data = []  # Initialize table data
    main()

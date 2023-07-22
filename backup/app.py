from flask import Blueprint, Flask, request, jsonify,session,send_from_directory,redirect,abort, render_template, url_for
import sqlite3, datetime
import re
from datetime import date
import os
import pdfkit
from num2words import num2words
from auth import auth_bp
import json

import requests
from authlib.integrations.flask_client import OAuth

app = Flask(__name__)

app.register_blueprint(auth_bp, url_prefix='/')

meon_invoice = sqlite3.connect(
    'meon_invoice.db', detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)



meon_invoice.execute('''CREATE TABLE IF NOT EXISTS invoicefields
         (id INTEGER NOT NULL PRIMARY KEY,
         company TEXT,
         tax_invoice_type TEXT,
         invoice_no TEXT,
         invoice_company_name TEXT,
         invoice_company_address1 TEXT,
         invoice_company_address2 TEXT,
         invoice_company_address3 TEXT,

         invoice_company_address4 TEXT,
         invoice_date timestamp,
         hsn_code TEXT,
         item_description TEXT,
         quantity TEXT,
         rate_unit TEXT,

         amount TEXT,
         state TEXT,
         igst TEXT,
         bank_name TEXT,
         bank_address TEXT,
         account_no TEXT,

         Ifsc_code TEXT,
         cgst TEXT,
         igst_type,
         total_value_in_inr,
         sgst TEXT);''')

meon_invoice.execute('''CREATE TABLE IF NOT EXISTS addnewcustomer
(id INTEGER NOT NULL PRIMARY KEY,
customer_name TEXT,
gst_no TEXT,
invoice_company_address1 TEXT,
invoice_company_address2 TEXT,
invoice_company_address3 TEXT,
invoice_company_address4 TEXT,
state TEXT);''')

meon_invoice.execute('''CREATE TABLE IF NOT EXISTS hsn_no
         (id INTEGER NOT NULL PRIMARY KEY,
         hsn TEXT);''')

meon_invoice.execute('''CREATE TABLE IF NOT EXISTS login
         (id INTEGER NOT NULL PRIMARY KEY,
         username TEXT,
         password TEXT);''')
meon_invoice.commit()



meon_invoice.execute('''CREATE TABLE IF NOT EXISTS invoice
         (id INTEGER NOT NULL PRIMARY KEY,
         invoice TEXT);''')

meon_invoice.commit()

appConf = {
    "OAUTH2_CLIENT_ID": "24660824558-j1uj20ias0dsc3a6r436a770ge9adqdt.apps.googleusercontent.com",
    "OAUTH2_CLIENT_SECRET": "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",
    "OAUTH2_META_URL": "https://accounts.google.com/.well-known/openid-configuration",
    "FLASK_SECRET": "ALongRandomlyGeneratedString",
    "FLASK_PORT": 5000
}


app.secret_key = appConf.get("FLASK_SECRET")

oauth = OAuth(app)

oauth.register(
    "myApp",
    client_id=appConf.get("OAUTH2_CLIENT_ID"),
    client_secret=appConf.get("OAUTH2_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email https://www.googleapis.com/auth/user.birthday.read https://www.googleapis.com/auth/user.gender.read",
       
    },
    server_metadata_url=f'{appConf.get("OAUTH2_META_URL")}',
)






logos = {
        'Meon Tours and Travels':'https://meontoursandtravels.com/static/tour/img/travel1.png',
        'Meon Technologies pvt Ltd':'https://meon.co.in/static/meon/img/logo-new.png',
        'Meon Enterprises':'https://meon.co.in/static/meon/img/meon-enterprise.png',
        'Meon Financial Consultants Pvt Ltd':'https://meon.co.in/static/meon/img/meon-financial.png'
        }


@app.route('/invoice_form')
def index():
    return render_template('invoice_form.html')

@app.route('/submit_invoice/<inv>', methods=['POST'])
def submit_invoice(inv):
    state = meon_invoice.execute(" select state from invoicefields ORDER by id DESC LIMIT 1 ").fetchall()[0][0]

    data = request.form
    
    if request.method =="POST":

        company = request.form["company"]     
        item_description = request.form["item_description"]
        tax_invoice_type = request.form["tax_invoice_type"]
        quantity = request.form["quantity"]
        Rate_unit = request.form["Rate_unit"]
        terms = request.form["terms"]
        hsn = request.form["hsn"]

        #==========MULTIPLICATION==================

        if quantity.isdigit() and Rate_unit.isdigit():
   
            Amount = int(quantity) * int(Rate_unit)
    
        #=============STATE=========================

        if state == "Uttarpradesh":
            igst_type = "CGST@9% + SGST@9%"
            
        else:
           igst_type = "IGST@18%"

        #===========GST CALCULATION===============

        amount = int(Amount)
        igst = (amount * 9) / 100 
        total_value_in_inr = amount + igst + igst
        total_value_in_inr = round(total_value_in_inr, 2)

        #============TOTAL VALUE===================

          
          


        def convert_amount_to_text(amount):
            
                    # Convert the integer part of the amount to words
                    integer_part = int(amount)
                    integer_part_text = num2words(integer_part, lang='en_IN').title()

                    # Convert the decimal part of the amount to words
                    decimal_part = int(round((amount - integer_part) * 100))
                    decimal_part_text = num2words(decimal_part, lang='en_IN').title()

                    # Generate the complete Indian currency text
                    amount_text = integer_part_text + " Rupees"
                    if decimal_part > 0:
                        amount_text += " and " + decimal_part_text + " Paise"

                    return amount_text
            

                
        amount = total_value_in_inr
        amount_text = convert_amount_to_text(amount)

        #============MULTIPLE LOGOS=========================

        logo = logos[company]   

        #========= Acessing only date ==================

        invoice_date = datetime.datetime.now()
        current_date = invoice_date.date()
        formatted_date = current_date.strftime("%d/%m/%Y")
        
        #========= BANK DETAILS  ==================
        
        if company == "Meon Enterprises":
            gstin = "09CKAPA5543G1ZG"
            bank_name = "Central Bank of India"
            address = "31, Jail Chungi, P.o. Victoria Park Road, Meerut City"
            account_no = "3667793657"
            ifsc_code = "CBIN0282337" 
            pan = "CKAPA5543G"
            
        elif company == "Meon Financial Consultants Pvt Ltd":
            gstin = "09AAOCM8625J1ZS"
            bank_name = "HDFC BANK"
            address = "381, WESTERN KACHEHARI ROAD"
            account_no = "50200065427416"
            ifsc_code = "HDFC0000285" 
            pan = "AAOCM8625J"

        elif company == "Meon Tours and Travels":
            gstin = "09CPVPA1530F1Z0"
            bank_name = "ICICI Bank 4167"
            address = " Garh Road Meerut"
            account_no = "097505004167"
            ifsc_code = "ICIC0000975"
            pan = "CPVPA1530F"


        elif company == "Meon Technologies pvt Ltd":
            gstin = "09AANCM7861P1ZD"
            bank_name = "ICICI Bank"
            address = "Meerut Garh road"
            account_no = "097505003504"
            ifsc_code = "ICIC0000975"  
            pan = "AANCM7861P"
        else:
            pass

       
      
        financial_year = "23-24"

        invoice_no = None
        
        inv = meon_invoice.execute(" select invoice_no from invoicefields WHERE invoice_no = '"+inv+"' ").fetchall()[0][0]
       
        meon_invoice.execute("update invoicefields set invoice_date='"+str(invoice_date)+"',item_description='"+item_description+"',quantity='"+quantity+"',rate_unit='"+str(Rate_unit)+"',Amount='"+str(Amount)+"',igst='"+str(igst)+"',igst_type='"+str(igst_type)+"',total_value_in_inr='"+str(total_value_in_inr)+"',date='"+str(formatted_date)+"',amount_text='"+str(amount_text)+"',terms='"+str(terms)+"',logo='"+logo+"',bank_name='"+bank_name+"',bank_address='"+str(address)+"',account_no='"+str(account_no)+"',Ifsc_code='"+str(ifsc_code)+"',pan='"+str(pan)+"',hsn='"+str(hsn)+"',gstin='"+str(gstin)+"',financial_year='"+str(financial_year)+"' where invoice_no = '"+inv+"' ")
        meon_invoice.commit()

        data = meon_invoice.execute("SELECT * FROM invoicefields WHERE invoice_no= '"+inv+"' ").fetchall()
        
        id = data[0][0]
        company = data[0][1]
        tax_invoice_type = data[0][2]
        invoice_no = data[0][3]
        invoice_company_name = data[0][4]
        invoice_company_address1 = data[0][5]
        invoice_company_address2 = data[0][6]
        invoice_company_address3 =  data[0][7]
        invoice_company_address4 =  data[0][8]
        item_description = data[0][11]
        quantity = data[0][12]
        rate_unit = data[0][13]
        amount = data[0][14]
        igst = data[0][16]
        cgst = data[0][21]
        
        total_value_in_inr = data[0][23]
        sgst = data[0][24]
        date = data[0][25]
        amount_text = data[0][27]
        terms = data[0][28]

        bank_name = data[0][17]
        bank_address = data[0][18]
        account_no = data[0][19]
        Ifsc_code = data[0][20]

        pan = data[0][29]
        gstin = data[0][30]
        gstin_form = data[0][31]
        hsn = data[0][32]
        

        igst_type = data[0][22]
        if state == "Uttarpradesh":
            igst_type = "CGST@9% + SGST@9%"
            igst_type_1 = igst_type.split("+")[0]
            igst_type_2 = igst_type.split("+")[-1]

            html = '''<!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Tax-Invoice</title>
    <link
        href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap"
        rel="stylesheet"
    />
    <style>
        * {
        padding: 0px;
        margin: 0px;
        font-family: "Poppins", sans-serif !important;
        }
        .thirdSection table tr th {
        border: none;
        }
        .header {
        display: flex;
        justify-content: space-between;
        }
        .logo {
        width: 74%;
        }
        .header2 {
        width: 74%;
        margin-top: 10px;
        margin-left: 3em;
        }
        .pragraph p {
        display: -webkit-box;
        display: flex;
        -webkit-justify-content: space-between;
        justify-content: space-between;
        place-content: space-between;
        font-size: small;
        width: 100%;
        }

        .secondSection h4 {
        color: #1a5dba;
        margin: 20px 0 0 0;
        }
        .invoiced p {
        text-align: left;
        font-size: smaller;
        }
        .Consignee p {
        text-align: right;
        font-size: smaller;
        }
        .thirdSection td {
        font-size: x-small;
        text-align: center;
        }
        .thirdSection th {
        font-size: small;
        font-weight: 500;
        text-align: center;
        padding: 6px;
        }
        /*tr:nth-child(1) {
        background-image: linear-gradient(50deg, #1a5dba 50%, black 50%);
        color: white;
        border: none;
        outline: none;
        }*/
        .details {
        display: flex;
        justify-content: space-between;
        margin: 20px 0;
        }
        
        .totalDetail {
        text-align: right;
        }
        .totalDetail .total,
        .IGST,
        .subTotal {
        display: flex;
        justify-content: space-between;
        font-size: small;
        margin: 5px 0;
        }
        .total {
        background-color: #1a5dba;
        color: white;
        padding: 7px;
        }
        .bankarDetails p {
        font-size: small;
        }
        .footer {
        display: flex;
        justify-content: space-between;
        margin: 40px 0;
        }
        .footer p {
        font-size: small;
        }
        .footerSection p a {
        text-decoration: none;
        }

        .footerSection {
        font-size: 12px;
        background-image: -webkit-linear-gradient(50deg, #1a5dba 50%, black 50%);
        color: white;
        padding: 10px;
        }
    </style>
    </head>
    <body>
    <page class="frontpage-1">
        <div style="padding: 30px">
        
        <table class="secondSection" style="width:100%;">
            <tr>
            <td>
                <img width="175px" src='''+str(logo)+''' alt="logo"  />
                <div class="comAddress">
                    <p style="font-size: medium; margin-top: 5px">'''+str(company)+'''</p>
                    <p style="font-size: small">8/A Rana Pratap Enclave,Victoria Park, Meerut,</p>
                    <p style="font-size: small">UP-250001 INDIA</p>
                    <p style="font-size: small">
                    GSTIN : '''+str(gstin)+''' PAN No: '''+str(pan)+'''
                </p>
                <hr style="margin-top: 5px; background-color: black; height: 1px; width:65%" />
                </div>
                
            </td>
            <td>
                <div class="Consignee">
                <h1 style="color: #1a5dba; word-spacing: 10px; font-size: 40px; text-align:right;">
                    '''+str(tax_invoice_type)+'''
                </h1>
                <table style="width: 60%; margin-left: auto; text-align: right;">
                    <tr>
                        <td><p style="text-align:left;">Invoice No :</p></td>
                        <td ><p>'''+str(invoice_no).replace("_","/")+'''</p></td>
                    </tr>
                    <tr>
                        <td><p style="text-align:left;">Invoice Date :</p></td>
                        <td><p>'''+str(date)+'''</p></td>
                    </tr>
                </table>
                <hr style="margin-top: 10px; background-color: black; height: 0.9px; width:60%;margin-left: auto;"/>
                </div>
            </td>
            </tr>
        </table>

        <table class="secondSection" style="width:100%;margin-top:1em; margin-bottom:4em;">
            <tr>
            <td>
                <div class="invoiced">
                <h4>Invoiced To</h4>
                <div class="comAddress">
                    <p>'''+str(invoice_company_name)+'''</p>
                    <p>'''+str(invoice_company_address1)+'''</p>
                    <p>'''+str(invoice_company_address2)+'''</p>
                    <p>'''+str(invoice_company_address3)+'''</p>
                    <p>'''+str(invoice_company_address4)+'''</p>
                    <p>GSTIN : '''+str(gstin_form).upper()+'''</p>
                </div>
                </div>
            </td>
            <td>
                <div class="Consignee">
                <h4 style="text-align: right">Consignee</h4>
                <p>'''+str(invoice_company_name)+'''</p>
                <p>'''+str(invoice_company_address1)+'''</p>
                <p>'''+str(invoice_company_address2)+'''</p>
                <p>'''+str(invoice_company_address3)+'''</p>
                <p>'''+str(invoice_company_address4)+'''</p>
                <p>GSTIN : '''+str(gstin_form).upper()+'''</p>
                </div>
            </td>
            </tr>
        </table>

        <div class="thirdSection">
            <table style="width: 100%; margin: 20px 0;" cellspacing="0" cellpadding="0">
            <tr style="color:#fff;">
                <th style="background-image: -webkit-linear-gradient(50deg, #1a5dba 50%, #1a5dba 50%);">S.N</th>
                <th style="background-image: -webkit-linear-gradient(50deg, #1a5dba 50%, #1a5dba 50%);">HSN/SAC</th>
                <th style="background-image: -webkit-linear-gradient(50deg, #1a5dba 50%, #1a5dba 50%);">Item Description</th>
                <th style="background-image: -webkit-linear-gradient(50deg, #1a5dba 50%, black 50%);">Qty.</th>
                <th style="background-image: -webkit-linear-gradient(50deg, #000 50%, #000 50%);">U/M</th>
                <th style="background-image: -webkit-linear-gradient(50deg, #000 50%, #000 50%);">Rate/Unit</th>
                <th style="background-image: -webkit-linear-gradient(50deg, #000 50%, #000 50%);">Amount</th>
            </tr>
            <tr>
                <td>1</td>
                <td>'''+str(hsn)+'''</td>
                <td>'''+str(item_description)+''' </td>
                <td>'''+str(quantity)+'''</td>
                <td>AU</td>
                <td>'''+str(Rate_unit)+'''</td>
                <td>'''+str(Amount)+'''</td>
            </tr>
            </table>
            <hr />
        </div>
        <table class="fourthSection" style="width:100%; margin-top:10px; margin-bottom:10px;">
            <tr>
            <td>
                <div class="bankarDetails">
                <h5>Banker’s Details</h5>
                <p>Bank Name : '''+str(bank_name)+'''</p>
                <p>Address :   '''+str(bank_address)+'''</p>
                <p>Account No: '''+str(account_no)+'''</p>
                <p>IFSC Code : '''+str(Ifsc_code)+'''</p>
                </div>
            </td>
            <td>
                <table style="width: 70%; margin-left: auto; text-align: right;" cellspacing="0" cellpadding="0">
                    <tr>
                        <td><p style="font-size: 15px; font-weight: 500; text-align:left; padding-left: 2em;">Subtotal</p></td>
                        <td ><p style="text-align:left;">'''+str(Amount)+'''</p></td>
                    </tr>
                    <tr>
                        <td><p style="font-size: 15px; font-weight: 500; text-align:left; padding-left: 2em;"> '''+str(igst_type_1)+'''</p></td>
                        <td ><p style="text-align:left;">'''+str(igst)+'''</p></td>
                    </tr>
                    <tr>
                        <td><p style="font-size: 15px; font-weight: 500; text-align:left; padding-left: 2em;"> '''+str(igst_type_2)+'''</p></td>
                        <td ><p style="text-align:left;">'''+str(igst)+'''</p></td>
                    </tr>
            
                  
                   
                    <tr style="background-color: #1a5dba; color: white;">
                        <td><p style="font-size: 15px; font-weight: 500; width:300px; text-align:left; padding-left: 2em;">Total Value in INR</p></td>
                        <td ><p style="text-align:left;">'''+str(total_value_in_inr)+'''</p></td>
                    </tr>
                </table>
            </td>
            </tr>
            <tr>
            <td colspan="2">
                <h5 style="text-align: center; font-size:15px; padding-top:2em;">INVOICE VALUE: '''+str(amount_text).upper()+'''</h5>
            </td>
            </tr>
        </table>

            <table class="secondSection" style="width:100%;margin-bottom:4em;">
                <tr>
                    <td>
                        <div class="invoiced">
                            <h4>Contact Details</h4>
                            <div class="comAddress">
                                <p>Name : Mr. Shyam Arora</p>
                                <p>Ref E-mail : <a style="text-decoration: none; color: black"
                                    href="mailto:shyam@meon.co.in">shyam@meon.co.in</a></p>
                                <p>Place of Supply: INDIA</p>
                                <p>Terms of Payment: '''+str(terms)+'''</p>
                            </div>
                        </div>
                    </td>
                    <td>
                        <div class="Consignee">
                            <h4 style="text-align: right; margin-bottom: 60px;">For '''+str(company)+'''</h4>
                            <p style="font-weight: 700; color: #1a5dba; font-size: 1rem; font-family: Verdana, Geneva, Tahoma, sans-serif;">Authorised Signatory</p>
                        </div>
                    </td>
                </tr>
            </table>

        <table class="footerSection" style="width:100%; margin-top:5em; margin-bottom:10px;">
            <tr>
            <td>
                <p>B 902-905, 9th floor, B- Tower, Noida One, Sector-62, Noida Uttar Pradesh (201301)</p>
            </td>
            <td>
                <p style="text-align:right;">email: <a style="text-decoration: none; color: white" href="mailto:info@meon.co.in">info@meon.co.in</a></p>
            </td>
            </tr>
        </table>

        
        </div>
    </page>
    </body>
    </html>

    '''

        else:
            igst_type = igst_type
            print("igst type:- ",igst_type)
            if igst is not None:
                igst = float(igst) + float(igst)
                print("igst :- ",igst)
            html = '''<!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Tax-Invoice</title>
    <link
        href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap"
        rel="stylesheet"
    />
    <style>
        * {
        padding: 0px;
        margin: 0px;
        font-family: "Poppins", sans-serif !important;
        }
        .thirdSection table tr th {
        border: none;
        }
        .header {
        display: flex;
        justify-content: space-between;
        }
        .logo {
        width: 74%;
        }
        .header2 {
        width: 74%;
        margin-top: 10px;
        margin-left: 3em;
        }
        .pragraph p {
        display: -webkit-box;
        display: flex;
        -webkit-justify-content: space-between;
        justify-content: space-between;
        place-content: space-between;
        font-size: small;
        width: 100%;
        }

        .secondSection h4 {
        color: #1a5dba;
        margin: 20px 0 0 0;
        }
        .invoiced p {
        text-align: left;
        font-size: smaller;
        }
        .Consignee p {
        text-align: right;
        font-size: smaller;
        }
        .thirdSection td {
        font-size: x-small;
        text-align: center;
        }
        .thirdSection th {
        font-size: small;
        font-weight: 500;
        text-align: center;
        padding: 6px;
        }
        /*tr:nth-child(1) {
        background-image: linear-gradient(50deg, #1a5dba 50%, black 50%);
        color: white;
        border: none;
        outline: none;
        }*/
        .details {
        display: flex;
        justify-content: space-between;
        margin: 20px 0;
        }
        
        .totalDetail {
        text-align: right;
        }
        .totalDetail .total,
        .IGST,
        .subTotal {
        display: flex;
        justify-content: space-between;
        font-size: small;
        margin: 5px 0;
        }
        .total {
        background-color: #1a5dba;
        color: white;
        padding: 7px;
        }
        .bankarDetails p {
        font-size: small;
        }
        .footer {
        display: flex;
        justify-content: space-between;
        margin: 40px 0;
        }
        .footer p {
        font-size: small;
        }
        .footerSection p a {
        text-decoration: none;
        }

        .footerSection {
        font-size: 12px;
        background-image: -webkit-linear-gradient(50deg, #1a5dba 50%, black 50%);
        color: white;
        padding: 10px;
        }
    </style>
    </head>
    <body>
    <page class="frontpage-1">
        <div style="padding: 30px">
        
        <table class="secondSection" style="width:100%;">
            <tr>
            <td>
                <img width="175px" src='''+str(logo)+''' alt="logo"  />
                <div class="comAddress">
                    <p style="font-size: medium; margin-top: 5px">'''+str(company)+'''</p>
                    <p style="font-size: small">8/A Rana Pratap Enclave,Victoria Park, Meerut,</p>
                    <p style="font-size: small">UP-250001 INDIA</p>
                    <p style="font-size: small">
                    GSTIN : '''+str(gstin)+''' PAN No: '''+str(pan)+'''
                </p>
                <hr style="margin-top: 5px; background-color: black; height: 1px; width:65%" />
                </div>
                
            </td>
            <td>
                <div class="Consignee">
                <h1 style="color: #1a5dba; word-spacing: 10px; font-size: 40px; text-align:right;">
                    '''+str(tax_invoice_type)+'''
                </h1>
                <table style="width: 60%; margin-left: auto; text-align: right;">
                    <tr>
                        <td><p style="text-align:left;">Invoice No :</p></td>
                        <td ><p>'''+str(invoice_no).replace("_","/")+'''</p></td>
                    </tr>
                    <tr>
                        <td><p style="text-align:left;">Invoice Date :</p></td>
                        <td><p>'''+str(date)+'''</p></td>
                    </tr>
                </table>
                <hr style="margin-top: 10px; background-color: black; height: 0.9px; width:60%;margin-left: auto;"/>
                </div>
            </td>
            </tr>
        </table>

        <table class="secondSection" style="width:100%;margin-top:1em; margin-bottom:4em;">
            <tr>
            <td>
                <div class="invoiced">
                <h4>Invoiced To</h4>
                <div class="comAddress">
                    <p>'''+str(invoice_company_name)+'''</p>
                    <p>'''+str(invoice_company_address1)+'''</p>
                    <p>'''+str(invoice_company_address2)+'''</p>
                    <p>'''+str(invoice_company_address3)+'''</p>
                    <p>'''+str(invoice_company_address4)+'''</p>
                    <p>GSTIN : '''+str(gstin_form).upper()+'''</p>
                </div>
                </div>
            </td>
            <td>
                <div class="Consignee">
                <h4 style="text-align: right">Consignee</h4>
                <p>'''+str(invoice_company_name)+'''</p>
                <p>'''+str(invoice_company_address1)+'''</p>
                <p>'''+str(invoice_company_address2)+'''</p>
                <p>'''+str(invoice_company_address3)+'''</p>
                <p>'''+str(invoice_company_address4)+'''</p>
                <p>GSTIN : '''+str(gstin_form).upper()+'''</p>
                </div>
            </td>
            </tr>
        </table>

        <div class="thirdSection">
            <table style="width: 100%; margin: 20px 0;" cellspacing="0" cellpadding="0">
            <tr style="color:#fff;">
                <th style="background-image: -webkit-linear-gradient(50deg, #1a5dba 50%, #1a5dba 50%);">S.N</th>
                <th style="background-image: -webkit-linear-gradient(50deg, #1a5dba 50%, #1a5dba 50%);">HSN/SAC</th>
                <th style="background-image: -webkit-linear-gradient(50deg, #1a5dba 50%, #1a5dba 50%);">Item Description</th>
                <th style="background-image: -webkit-linear-gradient(50deg, #1a5dba 50%, black 50%);">Qty.</th>
                <th style="background-image: -webkit-linear-gradient(50deg, #000 50%, #000 50%);">U/M</th>
                <th style="background-image: -webkit-linear-gradient(50deg, #000 50%, #000 50%);">Rate/Unit</th>
                <th style="background-image: -webkit-linear-gradient(50deg, #000 50%, #000 50%);">Amount</th>
            </tr>
            <tr>
                <td>1</td>
                <td>'''+str(hsn)+'''</td>
                <td>'''+str(item_description)+''' </td>
                <td>'''+str(quantity)+'''</td>
                <td>AU</td>
                <td>'''+str(Rate_unit)+'''</td>
                <td>'''+str(Amount)+'''</td>
            </tr>
            </table>
            <hr />
        </div>
        <table class="fourthSection" style="width:100%; margin-top:10px; margin-bottom:10px;">
            <tr>
            <td>
                <div class="bankarDetails">
                <h5>Banker’s Details</h5>
                <p>Bank Name : '''+str(bank_name)+'''</p>
                <p>Address :   '''+str(bank_address)+'''</p>
                <p>Account No: '''+str(account_no)+'''</p>
                <p>IFSC Code : '''+str(Ifsc_code)+'''</p>
                </div>
            </td>
            <td>
                <table style="width: 70%; margin-left: auto; text-align: right;" cellspacing="0" cellpadding="0">
                    <tr>
                        <td><p style="font-size: 15px; font-weight: 500; text-align:left; padding-left: 2em;">Subtotal</p></td>
                        <td ><p style="text-align:left;">'''+str(Amount)+'''</p></td>
                    </tr>
                    <tr>
                        <td><p style="font-size: 15px; font-weight: 500; text-align:left; padding-left: 2em;"> '''+str(igst_type)+'''</p></td>
                        <td ><p style="text-align:left;">'''+str(igst)+'''</p></td>
                    </tr>
                    
            
                  
                   
                    <tr style="background-color: #1a5dba; color: white;">
                        <td><p style="font-size: 15px; font-weight: 500; width:300px; text-align:left; padding-left: 2em;">Total Value in INR</p></td>
                        <td ><p style="text-align:left;">'''+str(total_value_in_inr)+'''</p></td>
                    </tr>
                </table>
            </td>
            </tr>
            <tr>
            <td colspan="2">
                <h5 style="text-align: center; font-size:15px; padding-top:2em;">INVOICE VALUE: '''+str(amount_text).upper()+'''</h5>
            </td>
            </tr>
        </table>

        <table class="secondSection" style="width:100%; margin-bottom:4em;">
                <table class="secondSection" style="width:100%;margin-top:1em; margin-bottom:4em;">
                <tr>
                    <td>
                        <div class="invoiced">
                            <h4>Contact Details</h4>
                            <div class="comAddress">
                                <p>Name : Mr. Shyam Arora</p>
                                <p>Ref E-mail : <a style="text-decoration: none; color: black"
                                    href="mailto:shyam@meon.co.in">shyam@meon.co.in</a></p>
                                <p>Place of Supply: INDIA</p>
                                <p>Terms of Payment: '''+str(terms)+'''</p>
                            </div>
                        </div>
                    </td>
                    <td>
                        <div class="Consignee">
                            <h4 style="text-align: right; margin-bottom: 60px;">For '''+str(company)+'''</h4>
                            <p style="font-weight: 700; color: #1a5dba; font-size: 1rem; font-family: Verdana, Geneva, Tahoma, sans-serif;">Authorised Signatory</p>
                        </div>
                    </td>
                </tr>
                </table>
            </table>

        <table class="footerSection" style="width:100%; margin-top:5em; margin-bottom:10px;">
            <tr>
            <td>
                <p>B 902-905, 9th floor, B- Tower, Noida One, Sector-62, Noida Uttar Pradesh (201301)</p>
            </td>
            <td>
                <p style="text-align:right;">email: <a style="text-decoration: none; color: white" href="mailto:info@meon.co.in">info@meon.co.in</a></p>
            </td>
            </tr>
        </table>

        
        </div>
    </page>
    </body>
    </html>

    '''
    
    options = {'enable-local-file-access': None, '--page-size': 'A4'}
    path = 'static/invoice'
    if os.path.exists(path):
        pass
    else:
        os.mkdir("static/invoice")
    pdfkit.from_string(html, "static/invoice/"+invoice_no+"_.pdf", options=options)



    return jsonify({'pdf':"static/invoice/"+invoice_no+"_.pdf"})



@app.route('/fetch_invoice_no', methods=['POST','GET'])
def fetch_invoice_no():

    data = request.form
    if request.method =="POST":

        company = request.form["company"]     
        tax_invoice_type = request.form["tax_invoice_type"]
        # plus = request.form["plus"]
        # minus = request.form["minus"]

        try:
            
            # if plus == "plus":    
                if tax_invoice_type == "Proforma Invoice" and company == 'Meon Technologies pvt Ltd' :
                    data = meon_invoice.execute("SELECT invoice_no,rate_unit,quantity FROM invoicefields WHERE tax_invoice_type = '"+tax_invoice_type+"' AND company =  '"+company+"' ORDER by id DESC LIMIT 1").fetchall()
                    
                    if data != []:
                        invoice_no =  data[0][0]
                        rate_unit = data[0][1]
                        quantity = data[0][2]

                         
                        if (rate_unit == '' or rate_unit == None) and (quantity == '' or quantity == None):
                            return jsonify({'invoice_no':invoice_no,'status':True})

                        
                        
                        elif data is not None and  data !='' and  len(data)!=0:
                            string_f = invoice_no
                            new_s = string_f.split("00")[0]         #getting only string

                            num = string_f.split("MT")[1]           #getting digits only
                            count = 1
                            digit = int(num)
                            a = count + digit                       #increment digit
                            invoice_no = new_s + "00" + str(a)     #merge string with increment digit
                            meon_invoice.execute('INSERT INTO invoicefields  (company,tax_invoice_type,invoice_no) VALUES(?,?,?)',(company,tax_invoice_type,invoice_no))
                            meon_invoice.commit()
                            
                            return jsonify({'invoice_no':invoice_no,'status':True})
                        
                    else:
                        count =82
                        invoice_no = 'MT00'+str(count)
                        
                        meon_invoice.execute('INSERT INTO invoicefields  (company,tax_invoice_type,invoice_no) VALUES(?,?,?)',(company,tax_invoice_type,invoice_no))
                        meon_invoice.commit()
                        return jsonify({'invoice_no':invoice_no,'status':True})
                        
                if tax_invoice_type == "Proforma Invoice" and company == 'Meon Enterprises' :
                    data = meon_invoice.execute("SELECT invoice_no,rate_unit,quantity FROM invoicefields WHERE tax_invoice_type = '"+tax_invoice_type+"' AND company =  '"+company+"' ORDER by id DESC LIMIT 1").fetchall()                    
                    if data != []:
                        invoice_no =  data[0][0]
                        rate_unit = data[0][1]
                        quantity = data[0][2]

                        if (rate_unit == '' or rate_unit == None) and (quantity == '' or quantity == None):
                            return jsonify({'invoice_no':invoice_no,'status':True})

                        

                        elif data is not None and  data !='' and  len(data)!=0:
                            string_f = invoice_no
                            new_s = string_f.split("00")[0]         #getting only string

                            num = string_f.split("ME")[1]           #getting digits only
                            count = 1
                            digit = int(num)
                            a = count + digit                       #increment digit
                            invoice_no = new_s + "00" + str(a)     #merge string with increment digit
                            
                            meon_invoice.execute('INSERT INTO invoicefields  (company,tax_invoice_type,invoice_no) VALUES(?,?,?)',(company,tax_invoice_type,invoice_no))
                            meon_invoice.commit()
                            
                            return jsonify({'invoice_no':invoice_no,'status':True})        
                    
                    
                    else:
                        count =19
                        invoice_no = 'ME00'+str(count)
                        
                        meon_invoice.execute('INSERT INTO invoicefields  (company,tax_invoice_type,invoice_no) VALUES(?,?,?)',(company,tax_invoice_type,invoice_no))
                        meon_invoice.commit()
                        return jsonify({'invoice_no':invoice_no,'status':True})
               
                if tax_invoice_type == "Proforma Invoice" and company == 'Meon Financial Consultants Pvt Ltd' :                    
                    data = meon_invoice.execute("SELECT invoice_no,rate_unit,quantity FROM invoicefields WHERE tax_invoice_type = '"+tax_invoice_type+"' AND company =  '"+company+"' ORDER by id DESC LIMIT 1").fetchall()
                    if data != []:
                        invoice_no =  data[0][0]
                        rate_unit = data[0][1]
                        quantity = data[0][2]

                        if (rate_unit == '' or rate_unit == None) and (quantity == '' or quantity == None):
                            return jsonify({'invoice_no':invoice_no,'status':True})

                        

                        elif data is not None and  data !='' and  len(data)!=0:
                            string_f = invoice_no
                            new_s = string_f.split("00")[0]         #getting only string

                            num = string_f.split("MF")[1]           #getting digits only
                            count = 1
                            digit = int(num)
                            a = count + digit                       #increment digit
                            invoice_no = new_s + "00" + str(a)     #merge string with increment digit
                            
                            meon_invoice.execute('INSERT INTO invoicefields  (company,tax_invoice_type,invoice_no) VALUES(?,?,?)',(company,tax_invoice_type,invoice_no))
                            meon_invoice.commit()
                            
                            return jsonify({'invoice_no':invoice_no,'status':True})        
                    
                    
                    else:
                        count =19
                        invoice_no = 'MF00'+str(count)
                        
                        meon_invoice.execute('INSERT INTO invoicefields  (company,tax_invoice_type,invoice_no) VALUES(?,?,?)',(company,tax_invoice_type,invoice_no))
                        meon_invoice.commit()
                        return jsonify({'invoice_no':invoice_no,'status':True})

                if tax_invoice_type == "Proforma Invoice" and company == 'Meon Tours and Travels':
                    data = meon_invoice.execute("SELECT invoice_no,rate_unit,quantity FROM invoicefields WHERE tax_invoice_type = '"+tax_invoice_type+"' AND company =  '"+company+"' ORDER by id DESC LIMIT 1").fetchall()
                    if data != []:
                        invoice_no =  data[0][0]
                        rate_unit = data[0][1]
                        quantity = data[0][2]

                        if (rate_unit == '' or rate_unit == None) and (quantity == '' or quantity == None):
                            return jsonify({'invoice_no':invoice_no,'status':True})

                        

                        elif data is not None and  data !='' and  len(data)!=0:
                            string_f = invoice_no
                            new_s = string_f.split("00")[0]         #getting only string

                            num = string_f.split("MTO")[1]           #getting digits only
                            count = 1
                            digit = int(num)
                            a = count + digit                       #increment digit
                            invoice_no = new_s + "000" + str(a)     #merge string with increment digit
                            meon_invoice.execute('INSERT INTO invoicefields  (company,tax_invoice_type,invoice_no) VALUES(?,?,?)',(company,tax_invoice_type,invoice_no))
                            meon_invoice.commit()
                            
                            return jsonify({'invoice_no':invoice_no,'status':True})        
                    
                    
                    else:
                        count =1
                        invoice_no = 'MTO000'+str(count)   

                        meon_invoice.execute('INSERT INTO invoicefields  (company,tax_invoice_type,invoice_no) VALUES(?,?,?)',(company,tax_invoice_type,invoice_no))
                        meon_invoice.commit()
                        return jsonify({'invoice_no':invoice_no,'status':True})



                if tax_invoice_type == "Tax Invoice" and company == "Meon Technologies pvt Ltd":
                    data = meon_invoice.execute("SELECT invoice_no,rate_unit,quantity FROM invoicefields WHERE company = '"+company+"' AND tax_invoice_type = '"+tax_invoice_type+"' ORDER by id DESC LIMIT 1").fetchall()
                    if data != []:
                        invoice_no =  data[0][0]
                        rate_unit = data[0][1]
                        quantity = data[0][2]

                        if (rate_unit == '' or rate_unit == None) and (quantity == '' or quantity == None):
                            return jsonify({'invoice_no':invoice_no,'status':True})

                        

                        elif data is not None and  data !='' and  len(data)!=0:
                            string_f = invoice_no
                            new_s = string_f.split("_")[0]           #getting only string
                            num = string_f.split("_")[1]             #getting digits only
                            count = 1
                            digit = int(num)
                            a = count + digit                        #increment digit
                            invoice_no = new_s +"_"+ str(a)          #merge string with increment digit
                            meon_invoice.execute('INSERT INTO invoicefields  (company,tax_invoice_type,invoice_no) VALUES(?,?,?)',(company,tax_invoice_type,invoice_no))
                            meon_invoice.commit()
                            return jsonify({'invoice_no':invoice_no,'status':True}) 
                
                
                    else:
                        count =53
                        invoice_no = 'MTECH23-24_'+str(count)
                        meon_invoice.execute('INSERT INTO invoicefields  (company,tax_invoice_type,invoice_no) VALUES(?,?,?)',(company,tax_invoice_type,invoice_no))
                        meon_invoice.commit()
                    
                        
                        return jsonify({'invoice_no':invoice_no,'status':True})        

                if tax_invoice_type == "Tax Invoice" and company == "Meon Enterprises":            
                    data = meon_invoice.execute(" select invoice_no,rate_unit,quantity from invoicefields WHERE company = '"+company+"' AND tax_invoice_type = '"+tax_invoice_type+"' ORDER by id DESC LIMIT 1 ").fetchall()
                    if data != []:
                        invoice_no =  data[0][0]
                        rate_unit = data[0][1]
                        quantity = data[0][2]

                        if (rate_unit == '' or rate_unit == None) and (quantity == '' or quantity == None):
                            return jsonify({'invoice_no':invoice_no,'status':True})

                    
                        elif data is not None and  data !='' and  len(data)!=0:
                            string_f = invoice_no
                            new_s = string_f.split("_")[0]                #getting only string
                            num = string_f.split("_")[1]                  #getting digits only
                            count = 1
                            digit = int(num)
                            a = count + digit                             #increment digit
                            invoice_no = new_s +"_"+ str(a)               #merge string with increment digit
                            meon_invoice.execute('INSERT INTO invoicefields  (company,tax_invoice_type,invoice_no) VALUES(?,?,?)',(company,tax_invoice_type,invoice_no))
                            meon_invoice.commit()
                        
                            
                            return jsonify({'invoice_no':invoice_no,'status':True})
                     
            
                
                    else:
                        count =13
                        invoice_no = 'MEON23-24_'+str(count)
                        meon_invoice.execute('INSERT INTO invoicefields  (company,tax_invoice_type,invoice_no) VALUES(?,?,?)',(company,tax_invoice_type,invoice_no))
                        meon_invoice.commit()
                    
                        
                        return jsonify({'invoice_no':invoice_no,'status':True})


                if tax_invoice_type == "Tax Invoice" and company == "Meon Financial Consultants Pvt Ltd":
            
                    data = meon_invoice.execute(" select invoice_no,rate_unit,quantity from invoicefields WHERE company = '"+company+"' AND tax_invoice_type = '"+tax_invoice_type+"' ORDER by id DESC LIMIT 1 ").fetchall()

                    if data != []:
                        invoice_no =  data[0][0]
                        rate_unit = data[0][1]
                        quantity = data[0][2]

                        if (rate_unit == '' or rate_unit == None) and (quantity == '' or quantity == None):
                            return jsonify({'invoice_no':invoice_no,'status':True})
                        
                        elif data is not None and  data !='' and  len(data)!=0:
                            string_f = invoice_no                  #getting data from list
                            new_s = string_f.split("_")[0]           #getting only string
                            num = string_f.split("_")[1]             #getting digits only
                            count = 1
                            digit = int(num)
                            a = count + digit                        #increment digit
                            invoice_no = new_s +"_"+ str(a)          #merge string with increment digit
                            meon_invoice.execute('INSERT INTO invoicefields  (company,tax_invoice_type,invoice_no) VALUES(?,?,?)',(company,tax_invoice_type,invoice_no))
                            meon_invoice.commit()
                        
                            
                            return jsonify({'invoice_no':invoice_no,'status':True})
                        
            
                
                    else:
                        count =7
                        invoice_no = 'MFIN23-24_'+str(count)

                        meon_invoice.execute('INSERT INTO invoicefields  (company,tax_invoice_type,invoice_no) VALUES(?,?,?)',(company,tax_invoice_type,invoice_no))
                        meon_invoice.commit()
                    
                        
                        return jsonify({'invoice_no':invoice_no,'status':True})


                if tax_invoice_type == "Tax Invoice" and company == "Meon Tours and Travels":            
                    data = meon_invoice.execute(" select invoice_no,rate_unit,quantity from invoicefields WHERE company = '"+company+"' AND tax_invoice_type = '"+tax_invoice_type+"' ORDER by id DESC LIMIT 1 ").fetchall()

                    if data != []:
                        invoice_no =  data[0][0]
                        rate_unit = data[0][1]
                        quantity = data[0][2]

                        if (rate_unit == '' or rate_unit == None) and (quantity == '' or quantity == None):
                            return jsonify({'invoice_no':invoice_no,'status':True})
                        
                        elif data is not None and  data !='' and  len(data)!=0:
                            string_f = invoice_no                   #getting data from list
                            new_s = string_f.split("_")[0]              #getting only string
                            num = string_f.split("_")[1]                #getting digits only
                            count = 1
                            digit = int(num)
                            a = count + digit                           #increment digit
                            invoice_no = new_s +"_"+ str(a)             #merge string with increment digit
                            meon_invoice.execute('INSERT INTO invoicefields  (company,tax_invoice_type,invoice_no) VALUES(?,?,?)',(company,tax_invoice_type,invoice_no))
                            meon_invoice.commit()
                        
                            
                            return jsonify({'invoice_no':invoice_no,'status':True})
            
                
                    else:
                        count =4
                        invoice_no = 'MTOUR23-24_'+str(count)  

                        meon_invoice.execute('INSERT INTO invoicefields  (company,tax_invoice_type,invoice_no) VALUES(?,?,?)',(company,tax_invoice_type,invoice_no))
                        meon_invoice.commit()
                    
                        
                        return jsonify({'invoice_no':invoice_no,'status':True})
        
        except:
            return jsonify({'msg':'No invoice number available'})     



@app.route("/find_invoicelink",methods=['GET','POST'])
def find_invoicelink():
    return render_template('preinvoice.html')

@app.route("/find_invoice",methods=['GET','POST'])
def find_invoice():
    data = request.form    
    if request.method =="POST":

        financial_year =    request.form["financial_year"]
        customer = request.form["customer"]
        meon_company = request.form["meon_company"]
        invoice_type = request.form["invoice_type"]
        

        data = meon_invoice.execute(" SELECT company, tax_invoice_type, invoice_company_name, financial_year, invoice_no FROM invoicefields WHERE company = '"+meon_company+"' AND financial_year = '"+financial_year+"' AND tax_invoice_type = '"+invoice_type+"' ").fetchall()

        if data == [] or data[0][0] != meon_company or data[0][1] != invoice_type or data[0][3] != financial_year :
            return({'msg':'Data Not Found'})
        
        else:
            data_list = []
            print("aaa",data)
            for inv in data:
                invoice = inv[4]
                data_list.append(invoice)
                
                

    return jsonify({'data':data_list})
           

            
           






@app.route("/generate_invoice/<invoice_no>",methods=['GET','POST'])
def generate_invoice(invoice_no):


    data = meon_invoice.execute(" SELECT * FROM invoicefields WHERE invoice_no= '"+invoice_no+"' ").fetchall() 

    id                                  = data[0][0]
    company                         	= data[0][1]
    tax_invoice_type                    = data[0][2]	
    invoice_no	                        = data[0][3]
    invoice_company_name                = data[0][4]	
    invoice_company_address1	        = data[0][5]
    invoice_company_address2	        = data[0][6]
    invoice_company_address3	        = data[0][7]
    invoice_company_address4	        = data[0][8]
    invoice_date	                    = data[0][9]
    hsn_code	                        = data[0][10]
    item_description	                = data[0][11]
    quantity	                        = data[0][12]
    rate_unit	                        = data[0][13]
    amount	                            = data[0][14]
    state	                            = data[0][15]
    igst	                            = data[0][16]
    bank_name	                        = data[0][17]
    bank_address	                    = data[0][18]
    account_no	                        = data[0][19]
    Ifsc_code	                        = data[0][20]
    cgst	                            = data[0][21]
    igst_type                           = data[0][22]
    total_value_in_inr	                = data[0][23]
    sgst	                            = data[0][24]
    date	                            = data[0][25]
    logo	                            = data[0][26]
    amount_text	                        = data[0][27]
    terms	                            = data[0][28]
    pan	                                = data[0][29]
    gstin	                            = data[0][30]
    gstin_form	                        = data[0][31]
    hsn	                                = data[0][32]
    
    if state == "Uttarpradesh":
        igst_type = "CGST@9% + SGST@9%"
        igst_type_1 = igst_type.split("+")[0]
        igst_type_2 = igst_type.split("+")[-1]

        html = '''<!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Tax-Invoice</title>
    <link
        href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap"
        rel="stylesheet"
    />
    <style>
        * {
        padding: 0px;
        margin: 0px;
        font-family: "Poppins", sans-serif !important;
        }
        .thirdSection table tr th {
        border: none;
        }
        .header {
        display: flex;
        justify-content: space-between;
        }
        .logo {
        width: 74%;
        }
        .header2 {
        width: 74%;
        margin-top: 10px;
        margin-left: 3em;
        }
        .pragraph p {
        display: -webkit-box;
        display: flex;
        -webkit-justify-content: space-between;
        justify-content: space-between;
        place-content: space-between;
        font-size: small;
        width: 100%;
        }

        .secondSection h4 {
        color: #1a5dba;
        margin: 20px 0 0 0;
        }
        .invoiced p {
        text-align: left;
        font-size: smaller;
        }
        .Consignee p {
        text-align: right;
        font-size: smaller;
        }
        .thirdSection td {
        font-size: x-small;
        text-align: center;
        }
        .thirdSection th {
        font-size: small;
        font-weight: 500;
        text-align: center;
        padding: 6px;
        }
        /*tr:nth-child(1) {
        background-image: linear-gradient(50deg, #1a5dba 50%, black 50%);
        color: white;
        border: none;
        outline: none;
        }*/
        .details {
        display: flex;
        justify-content: space-between;
        margin: 20px 0;
        }
        
        .totalDetail {
        text-align: right;
        }
        .totalDetail .total,
        .IGST,
        .subTotal {
        display: flex;
        justify-content: space-between;
        font-size: small;
        margin: 5px 0;
        }
        .total {
        background-color: #1a5dba;
        color: white;
        padding: 7px;
        }
        .bankarDetails p {
        font-size: small;
        }
        .footer {
        display: flex;
        justify-content: space-between;
        margin: 40px 0;
        }
        .footer p {
        font-size: small;
        }
        .footerSection p a {
        text-decoration: none;
        }

        .footerSection {
        font-size: 12px;
        background-image: -webkit-linear-gradient(50deg, #1a5dba 50%, black 50%);
        color: white;
        padding: 10px;
        }
    </style>
    </head>
    <body>
    <page class="frontpage-1">
        <div style="padding: 30px">
        
        <table class="secondSection" style="width:100%;">
            <tr>
            <td>
                <img width="175px" src='''+str(logo)+''' alt="logo"  />
                <div class="comAddress">
                    <p style="font-size: medium; margin-top: 5px">'''+str(company)+'''</p>
                    <p style="font-size: small">8/A Rana Pratap Enclave,Victoria Park, Meerut,</p>
                    <p style="font-size: small">UP-250001 INDIA</p>
                    <p style="font-size: small">
                    GSTIN : '''+str(gstin)+''' PAN No: '''+str(pan)+'''
                </p>
                <hr style="margin-top: 5px; background-color: black; height: 1px; width:65%" />
                </div>
                
            </td>
            <td>
                <div class="Consignee">
                <h1 style="color: #1a5dba; word-spacing: 10px; font-size: 40px; text-align:right;">
                    '''+str(tax_invoice_type)+'''
                </h1>
                <table style="width: 60%; margin-left: auto; text-align: right;">
                    <tr>
                        <td><p style="text-align:left;">Invoice No :</p></td>
                        <td ><p>'''+str(invoice_no).replace("_","/")+'''</p></td>
                    </tr>
                    <tr>
                        <td><p style="text-align:left;">Invoice Date :</p></td>
                        <td><p>'''+str(date)+'''</p></td>
                    </tr>
                </table>
                <hr style="margin-top: 10px; background-color: black; height: 0.9px; width:60%;margin-left: auto;"/>
                </div>
            </td>
            </tr>
        </table>

        <table class="secondSection" style="width:100%;margin-top:1em; margin-bottom:4em;">
            <tr>
            <td>
                <div class="invoiced">
                <h4>Invoiced To</h4>
                <div class="comAddress">
                    <p>'''+str(invoice_company_name)+'''</p>
                    <p>'''+str(invoice_company_address1)+'''</p>
                    <p>'''+str(invoice_company_address2)+'''</p>
                    <p>'''+str(invoice_company_address3)+'''</p>
                    <p>'''+str(invoice_company_address4)+'''</p>
                    <p>GSTIN : '''+str(gstin_form).upper()+'''</p>
                </div>
                </div>
            </td>
            <td>
                <div class="Consignee">
                <h4 style="text-align: right">Consignee</h4>
                <p>'''+str(invoice_company_name)+'''</p>
                <p>'''+str(invoice_company_address1)+'''</p>
                <p>'''+str(invoice_company_address2)+'''</p>
                <p>'''+str(invoice_company_address3)+'''</p>
                <p>'''+str(invoice_company_address4)+'''</p>
                <p>GSTIN : '''+str(gstin_form).upper()+'''</p>
                </div>
            </td>
            </tr>
        </table>

        <div class="thirdSection">
            <table style="width: 100%; margin: 20px 0;" cellspacing="0" cellpadding="0">
            <tr style="color:#fff;">
                <th style="background-image: -webkit-linear-gradient(50deg, #1a5dba 50%, #1a5dba 50%);">S.N</th>
                <th style="background-image: -webkit-linear-gradient(50deg, #1a5dba 50%, #1a5dba 50%);">HSN/SAC</th>
                <th style="background-image: -webkit-linear-gradient(50deg, #1a5dba 50%, #1a5dba 50%);">Item Description</th>
                <th style="background-image: -webkit-linear-gradient(50deg, #1a5dba 50%, black 50%);">Qty.</th>
                <th style="background-image: -webkit-linear-gradient(50deg, #000 50%, #000 50%);">U/M</th>
                <th style="background-image: -webkit-linear-gradient(50deg, #000 50%, #000 50%);">Rate/Unit</th>
                <th style="background-image: -webkit-linear-gradient(50deg, #000 50%, #000 50%);">Amount</th>
            </tr>
            <tr>
                <td>1</td>
                <td>'''+str(hsn)+'''</td>
                <td>'''+str(item_description)+''' </td>
                <td>'''+str(quantity)+'''</td>
                <td>AU</td>
                <td>'''+str(rate_unit)+'''</td>
                <td>'''+str(amount)+'''</td>
            </tr>
            </table>
            <hr />
        </div>
        <table class="fourthSection" style="width:100%; margin-top:10px; margin-bottom:10px;">
            <tr>
            <td>
                <div class="bankarDetails">
                <h5>Banker’s Details</h5>
                <p>Bank Name : '''+str(bank_name)+'''</p>
                <p>Address :   '''+str(bank_address)+'''</p>
                <p>Account No: '''+str(account_no)+'''</p>
                <p>IFSC Code : '''+str(Ifsc_code)+'''</p>
                </div>
            </td>
            <td>
                <table style="width: 70%; margin-left: auto; text-align: right;" cellspacing="0" cellpadding="0">
                    <tr>
                        <td><p style="font-size: 15px; font-weight: 500; text-align:left; padding-left: 2em;">Subtotal</p></td>
                        <td ><p style="text-align:left;">'''+str(amount)+'''</p></td>
                    </tr>
                    <tr>
                        <td><p style="font-size: 15px; font-weight: 500; text-align:left; padding-left: 2em;"> '''+str(igst_type_1)+'''</p></td>
                        <td ><p style="text-align:left;">'''+str(igst)+'''</p></td>
                    </tr>
                    <tr>
                        <td><p style="font-size: 15px; font-weight: 500; text-align:left; padding-left: 2em;"> '''+str(igst_type_2)+'''</p></td>
                        <td ><p style="text-align:left;">'''+str(igst)+'''</p></td>
                    </tr>
            
                  
                   
                    <tr style="background-color: #1a5dba; color: white;">
                        <td><p style="font-size: 15px; font-weight: 500; width:300px; text-align:left; padding-left: 2em;">Total Value in INR</p></td>
                        <td ><p style="text-align:left;">'''+str(total_value_in_inr)+'''</p></td>
                    </tr>
                </table>
            </td>
            </tr>
            <tr>
            <td colspan="2">
                <h5 style="text-align: center; font-size:15px; padding-top:2em;">INVOICE VALUE: '''+str(amount_text).upper()+'''</h5>
            </td>
            </tr>
        </table>

            <table class="secondSection" style="width:100%; margin-bottom:4em;">
                <tr>
                    <td>
                        <div class="invoiced">
                            <h4>Contact Details</h4>
                            <div class="comAddress">
                                <p>Name : Mr. Shyam Arora</p>
                                <p>Ref E-mail : <a style="text-decoration: none; color: black"
                                    href="mailto:shyam@meon.co.in">shyam@meon.co.in</a></p>
                                <p>Place of Supply: INDIA</p>
                                <p>Terms of Payment: '''+str(terms)+'''</p>
                            </div>
                        </div>
                    </td>
                    <td>
                        <div class="Consignee">
                            <h4 style="text-align: right; margin-bottom: 60px;">For '''+str(company)+'''</h4>
                            <p style="font-weight: 700; color: #1a5dba; font-size: 1rem; font-family: Verdana, Geneva, Tahoma, sans-serif;">Authorised Signatory</p>
                        </div>
                    </td>
                </tr>
            </table>

        <table class="footerSection" style="width:100%; margin-top:5em; margin-bottom:10px;">
            <tr>
            <td>
                <p>B 902-905, 9th floor, B- Tower, Noida One, Sector-62, Noida Uttar Pradesh (201301)</p>
            </td>
            <td>
                <p style="text-align:right;">email: <a style="text-decoration: none; color: white" href="mailto:info@meon.co.in">info@meon.co.in</a></p>
            </td>
            </tr>
        </table>

        
        </div>
    </page>
    </body>
    </html>

    '''

    else:
        igst_type = igst_type
        print("igst type:- ",igst_type)
        if igst is not None:
            igst = float(igst) + float(igst)
            print("igst :- ",igst)
            html = '''<!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Tax-Invoice</title>
    <link
        href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap"
        rel="stylesheet"
    />
    <style>
        * {
        padding: 0px;
        margin: 0px;
        font-family: "Poppins", sans-serif !important;
        }
        .thirdSection table tr th {
        border: none;
        }
        .header {
        display: flex;
        justify-content: space-between;
        }
        .logo {
        width: 74%;
        }
        .header2 {
        width: 74%;
        margin-top: 10px;
        margin-left: 3em;
        }
        .pragraph p {
        display: -webkit-box;
        display: flex;
        -webkit-justify-content: space-between;
        justify-content: space-between;
        place-content: space-between;
        font-size: small;
        width: 100%;
        }

        .secondSection h4 {
        color: #1a5dba;
        margin: 20px 0 0 0;
        }
        .invoiced p {
        text-align: left;
        font-size: smaller;
        }
        .Consignee p {
        text-align: right;
        font-size: smaller;
        }
        .thirdSection td {
        font-size: x-small;
        text-align: center;
        }
        .thirdSection th {
        font-size: small;
        font-weight: 500;
        text-align: center;
        padding: 6px;
        }
        /*tr:nth-child(1) {
        background-image: linear-gradient(50deg, #1a5dba 50%, black 50%);
        color: white;
        border: none;
        outline: none;
        }*/
        .details {
        display: flex;
        justify-content: space-between;
        margin: 20px 0;
        }
        
        .totalDetail {
        text-align: right;
        }
        .totalDetail .total,
        .IGST,
        .subTotal {
        display: flex;
        justify-content: space-between;
        font-size: small;
        margin: 5px 0;
        }
        .total {
        background-color: #1a5dba;
        color: white;
        padding: 7px;
        }
        .bankarDetails p {
        font-size: small;
        }
        .footer {
        display: flex;
        justify-content: space-between;
        margin: 40px 0;
        }
        .footer p {
        font-size: small;
        }
        .footerSection p a {
        text-decoration: none;
        }

        .footerSection {
        font-size: 12px;
        background-image: -webkit-linear-gradient(50deg, #1a5dba 50%, black 50%);
        color: white;
        padding: 10px;
        }
    </style>
    </head>
    <body>
    <page class="frontpage-1">
        <div style="padding: 30px">
        
        <table class="secondSection" style="width:100%;">
            <tr>
            <td>
                <img width="175px" src='''+str(logo)+''' alt="logo"  />
                <div class="comAddress">
                    <p style="font-size: medium; margin-top: 5px">'''+str(company)+'''</p>
                    <p style="font-size: small">8/A Rana Pratap Enclave,Victoria Park, Meerut,</p>
                    <p style="font-size: small">UP-250001 INDIA</p>
                    <p style="font-size: small">
                    GSTIN : '''+str(gstin)+''' PAN No: '''+str(pan)+'''
                </p>
                <hr style="margin-top: 5px; background-color: black; height: 1px; width:65%" />
                </div>
                
            </td>
            <td>
                <div class="Consignee">
                <h1 style="color: #1a5dba; word-spacing: 10px; font-size: 40px; text-align:right;">
                    '''+str(tax_invoice_type)+'''
                </h1>
                <table style="width: 60%; margin-left: auto; text-align: right;">
                    <tr>
                        <td><p style="text-align:left;">Invoice No :</p></td>
                        <td ><p>'''+str(invoice_no).replace("_","/")+'''</p></td>
                    </tr>
                    <tr>
                        <td><p style="text-align:left;">Invoice Date :</p></td>
                        <td><p>'''+str(date)+'''</p></td>
                    </tr>
                </table>
                <hr style="margin-top: 10px; background-color: black; height: 0.9px; width:60%;margin-left: auto;"/>
                </div>
            </td>
            </tr>
        </table>

        <table class="secondSection" style="width:100%;margin-top:1em; margin-bottom:4em;">
            <tr>
            <td>
                <div class="invoiced">
                <h4>Invoiced To</h4>
                <div class="comAddress">
                    <p>'''+str(invoice_company_name)+'''</p>
                    <p>'''+str(invoice_company_address1)+'''</p>
                    <p>'''+str(invoice_company_address2)+'''</p>
                    <p>'''+str(invoice_company_address3)+'''</p>
                    <p>'''+str(invoice_company_address4)+'''</p>
                    <p>GSTIN : '''+str(gstin_form).upper()+'''</p>
                </div>
                </div>
            </td>
            <td>
                <div class="Consignee">
                <h4 style="text-align: right">Consignee</h4>
                <p>'''+str(invoice_company_name)+'''</p>
                <p>'''+str(invoice_company_address1)+'''</p>
                <p>'''+str(invoice_company_address2)+'''</p>
                <p>'''+str(invoice_company_address3)+'''</p>
                <p>'''+str(invoice_company_address4)+'''</p>
                <p>GSTIN : '''+str(gstin_form).upper()+'''</p>
                </div>
            </td>
            </tr>
        </table>

        <div class="thirdSection">
            <table style="width: 100%; margin: 20px 0;" cellspacing="0" cellpadding="0">
            <tr style="color:#fff;">
                <th style="background-image: -webkit-linear-gradient(50deg, #1a5dba 50%, #1a5dba 50%);">S.N</th>
                <th style="background-image: -webkit-linear-gradient(50deg, #1a5dba 50%, #1a5dba 50%);">HSN/SAC</th>
                <th style="background-image: -webkit-linear-gradient(50deg, #1a5dba 50%, #1a5dba 50%);">Item Description</th>
                <th style="background-image: -webkit-linear-gradient(50deg, #1a5dba 50%, black 50%);">Qty.</th>
                <th style="background-image: -webkit-linear-gradient(50deg, #000 50%, #000 50%);">U/M</th>
                <th style="background-image: -webkit-linear-gradient(50deg, #000 50%, #000 50%);">Rate/Unit</th>
                <th style="background-image: -webkit-linear-gradient(50deg, #000 50%, #000 50%);">Amount</th>
            </tr>
            <tr>
                <td>1</td>
                <td>'''+str(hsn)+'''</td>
                <td>'''+str(item_description)+''' </td>
                <td>'''+str(quantity)+'''</td>
                <td>AU</td>
                <td>'''+str(rate_unit)+'''</td>
                <td>'''+str(amount)+'''</td>
            </tr>
            </table>
            <hr />
        </div>
        <table class="fourthSection" style="width:100%; margin-top:10px; margin-bottom:10px;">
            <tr>
            <td>
                <div class="bankarDetails">
                <h5>Banker’s Details</h5>
                <p>Bank Name : '''+str(bank_name)+'''</p>
                <p>Address :   '''+str(bank_address)+'''</p>
                <p>Account No: '''+str(account_no)+'''</p>
                <p>IFSC Code : '''+str(Ifsc_code)+'''</p>
                </div>
            </td>
            <td>
                <table style="width: 70%; margin-left: auto; text-align: right;" cellspacing="0" cellpadding="0">
                    <tr>
                        <td><p style="font-size: 15px; font-weight: 500; text-align:left; padding-left: 2em;">Subtotal</p></td>
                        <td ><p style="text-align:left;">'''+str(amount)+'''</p></td>
                    </tr>
                    <tr>
                        <td><p style="font-size: 15px; font-weight: 500; text-align:left; padding-left: 2em;"> '''+str(igst_type)+'''</p></td>
                        <td ><p style="text-align:left;">'''+str(igst)+'''</p></td>
                    </tr>
                    
            
                  
                   
                    <tr style="background-color: #1a5dba; color: white;">
                        <td><p style="font-size: 15px; font-weight: 500; width:300px; text-align:left; padding-left: 2em;">Total Value in INR</p></td>
                        <td ><p style="text-align:left;">'''+str(total_value_in_inr)+'''</p></td>
                    </tr>
                </table>
            </td>
            </tr>
            <tr>
            <td colspan="2">
                <h5 style="text-align: center; font-size:15px; padding-top:2em;">INVOICE VALUE: '''+str(amount_text).upper()+'''</h5>
            </td>
            </tr>
        </table>

        <table class="secondSection" style="width:100%; margin-bottom:4em;">
                <table class="secondSection" style="width:100%;margin-top:1em; margin-bottom:4em;">
                <tr>
                    <td>
                        <div class="invoiced">
                            <h4>Contact Details</h4>
                            <div class="comAddress">
                                <p>Name : Mr. Shyam Arora</p>
                                <p>Ref E-mail : <a style="text-decoration: none; color: black"
                                    href="mailto:shyam@meon.co.in">shyam@meon.co.in</a></p>
                                <p>Place of Supply: INDIA</p>
                                <p>Terms of Payment: '''+str(terms)+'''</p>
                            </div>
                        </div>
                    </td>
                    <td>
                        <div class="Consignee">
                            <h4 style="text-align: right; margin-bottom: 60px;">For '''+str(company)+'''</h4>
                            <p style="font-weight: 700; color: #1a5dba; font-size: 1rem; font-family: Verdana, Geneva, Tahoma, sans-serif;">Authorised Signatory</p>
                        </div>
                    </td>
                </tr>
                </table>
            </table>

        <table class="footerSection" style="width:100%; margin-top:5em; margin-bottom:10px;">
            <tr>
            <td>
                <p>B 902-905, 9th floor, B- Tower, Noida One, Sector-62, Noida Uttar Pradesh (201301)</p>
            </td>
            <td>
                <p style="text-align:right;">email: <a style="text-decoration: none; color: white" href="mailto:info@meon.co.in">info@meon.co.in</a></p>
            </td>
            </tr>
        </table>

        
        </div>
    </page>
    </body>
    </html>

    '''
            


        

    
    options = {'enable-local-file-access': None, '--page-size': 'A4'}
    path = 'static/invoice'
    if os.path.exists(path):
        pass
    else:
        os.mkdir("static/invoice")
    pdfkit.from_string(html, "static/invoice/"+invoice_no+"_.pdf", options=options)



    return jsonify({'pdf':"static/invoice/"+invoice_no+"_.pdf"})


@app.route('/addcompany', methods=['POST'])
def addcompany():
    data = request.form
    if request.method =="POST":
        customer_name = request.form["customer_name"]
        g = request.form["gstno"]
        add1 = request.form["add1"]
        add2 = request.form["add2"]
        add3 = request.form["add3"]
        add4 = request.form["add4"]
        state = request.form["state"]
        
        cn = customer_name
        

        gstn = len(g)
        gstno = int(gstn)

        if gstno>15:
            return jsonify({'msg':'Lengh of GST number should be 15','status':False})
        else:
            pass


        data = meon_invoice.execute(" select customer_name from addnewcustomer WHERE customer_name = '"+cn+"' ").fetchall()
        if data == [] or data[0][0]!=  cn:
            meon_invoice.execute('INSERT INTO addnewcustomer  (customer_name,gst_no,invoice_company_address1,invoice_company_address2,invoice_company_address3,invoice_company_address4,state) VALUES(?,?,?,?,?,?,?)',(customer_name,g,add1,add2,add3,add4,state))

            meon_invoice.commit()
            return jsonify({'msg':'success','status':True})
        else:
            return jsonify({'msg':'Customer Name Exists','status':False})




@app.route('/searchcompany/<invoice>', methods=['POST','GET'])
def searchcompany(invoice):
    inv = meon_invoice.execute("select invoice_no from invoicefields WHERE invoice_no = '"+invoice+"' ").fetchall()[0][0]
    data = request.get_json()

    customer_name = data['customer_name']

    all_data = meon_invoice.execute(" SELECT customer_name,gst_no,invoice_company_address1,invoice_company_address2,invoice_company_address3,invoice_company_address4,state FROM addnewcustomer WHERE customer_name = '"+customer_name+"' ").fetchall()
    d = len(all_data)
    if all_data == None or all_data == '' or d == 0:
        return jsonify({'msg':'Name not found...'})
    
    else:
        customer_name = all_data[0][0]
        gstno = str(all_data[0][1])
        add1 = str(all_data[0][2])
        add2 = str(all_data[0][3])
        add3 = str(all_data[0][4])
        add4 = str(all_data[0][5])
        state = str(all_data[0][6])
    
    
    
        print(" UPDATE invoicefields SET invoice_company_name = '"+str(customer_name)+"',gstin_form = '"+str(gstno)+"',invoice_company_address1='"+str(add1)+"',invoice_company_address2='"+str(add2)+"',invoice_company_address3='"+str(add3)+"',invoice_company_address4='"+str(add4)+"',state='"+str(state)+"' WHERE invoice_no = '"+inv+"'")
        meon_invoice.execute(" UPDATE invoicefields SET invoice_company_name = '"+str(customer_name)+"',gstin_form = '"+str(gstno)+"',invoice_company_address1='"+str(add1)+"',invoice_company_address2='"+str(add2)+"',invoice_company_address3='"+str(add3)+"',invoice_company_address4='"+str(add4)+"',state='"+str(state)+"' WHERE invoice_no = '"+inv+"'")
        meon_invoice.commit()

        return jsonify({'msg':'Data fetch successfully...','data':all_data}) 
    

        



@app.route("/")
def home():
    return render_template("home.html", session=session.get("user"),
                           pretty=json.dumps(session.get("user"), indent=4))


@app.route("/signin-google")
def googleCallback():
    token = oauth.myApp.authorize_access_token()

    personDataUrl = "https://people.googleapis.com/v1/people/me?personFields=emailAddresses,clientData"
    personData = requests.get(personDataUrl, headers={
        "Authorization": f"Bearer {token['access_token']}"
    }).json()

    token["personData"] = personData
    session["user"] = token
    return redirect(url_for("index"))


@app.route("/google-login")
def googleLogin():
    print(url_for("googleCallback", _external=True))
    if "user" in session:
        abort(404)
    return oauth.myApp.authorize_redirect(redirect_uri=url_for("googleCallback", _external=True, _scheme='https'))


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=appConf.get(
        "FLASK_PORT"), debug=True)       

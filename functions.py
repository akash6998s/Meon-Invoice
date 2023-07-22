from num2words import num2words
import random, string, os, json
import datetime

current_year = datetime.date.today().year
financial_year_current = str(current_year)[-2:] + '-' + str(current_year+1)[-2:]
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
        amount_text += " and " + decimal_part_text + " Paisa"

    return amount_text
            

def generateCompanyId(company_name):
    return str(company_name).split(' ',1)[0]+'_'+''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def InvoicePDFUP(data, logo, pan, signature_path):
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
    # quantity = data[0][12]
    # Rate_unit = data[0][13]
    rate_distribution = json.loads(data[0][35])
    Amount = data[0][14]
    igst = data[0][16]
    cgst = data[0][21]

    total_value_in_inr = data[0][23]
    sgst = data[0][24]
    date = data[0][25]
    amount_text = data[0][26]
    terms = data[0][27]

    bank_name = data[0][17]
    bank_address = data[0][18]
    account_no = data[0][19]
    Ifsc_code = data[0][20]

    # pan = data[0][29]
    gstin = data[0][31]
    gstin_form = data[0][34]
    hsn = data[0][30]


    igst_type = data[0][22]
    igst_type = "CGST@9% + SGST@9%"
    igst_type_1 = igst_type.split("+")[0]
    igst_type_2 = igst_type.split("+")[-1]

    table_rate_data = ''
    for i, x in enumerate(rate_distribution):
        table_rate_data += '''<tr>
                <td>'''+str(i+1)+'''</td>
                <td>'''+str(x['hsn'])+'''</td>
                <td>'''+str(x['item_description'])+''' </td>
                <td>'''+str(x['quantity'])+'''</td>
                <td>AU</td>
                <td>'''+str(x['Rate_unit'])+'''</td>
                <td>'''+str(round(int(x['quantity'])*float(x['Rate_unit']), 2))+'''</td>
            </tr>'''

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
        <br><br>
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
            '''+table_rate_data+'''
            </table>
            <hr />
        </div>
        <table class="fourthSection" style="width:100%; margin-top:10px; margin-bottom:10px;">
            <tr>
            <td>
                <div class="bankarDetails">
                <h5>Banker’s Details</h5>
                <p>Bank Name : '''+str(bank_name)+'''</p>
                <p>Branch Address :   '''+str(bank_address)+'''</p>
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
                            <h4 style="text-align: right;">For '''+str(company)+'''</h4>
                            <img src="'''+os.path.join(os.getcwd(),str(signature_path))+'''" style="width: 150px; margin-left:auto; display:block; margin-right:18px">
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
    return html


def InvoicePDFOthers(data, logo, pan,signature_path):
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
    # quantity = data[0][12]
    # Rate_unit = data[0][13]
    rate_distribution = json.loads(data[0][35])
    Amount = data[0][14]
    igst = data[0][16]
    cgst = data[0][21]

    total_value_in_inr = data[0][23]
    sgst = data[0][24]
    date = data[0][25]
    amount_text = data[0][26]
    terms = data[0][27]

    bank_name = data[0][17]
    bank_address = data[0][18]
    account_no = data[0][19]
    Ifsc_code = data[0][20]

    # pan = data[0][28]
    gstin = data[0][31]
    gstin_form = data[0][34]
    hsn = data[0][30]
    # print(gstin_form, hsn)

    igst_type = data[0][22]
    igst_type = igst_type
    if igst is not None:
        igst = float(igst) + float(igst)
    else:
    	igst = ''

    table_rate_data = ''
    for i, x in enumerate(rate_distribution):
        table_rate_data += '''<tr>
                <td>'''+str(i+1)+'''</td>
                <td>'''+str(x['hsn'])+'''</td>
                <td>'''+str(x['item_description'])+''' </td>
                <td>'''+str(x['quantity'])+'''</td>
                <td>AU</td>
                <td>'''+str(x['Rate_unit'])+'''</td>
                <td>'''+str(round(int(x['quantity'])*float(x['Rate_unit']), 2))+'''</td>
            </tr>'''

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
        <br><br>
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
            '''+table_rate_data+'''
            </table>
            <hr />
        </div>
        <table class="fourthSection" style="width:100%; margin-top:10px; margin-bottom:10px;">
            <tr>
            <td>
                <div class="bankarDetails">
                <h5>Banker’s Details</h5>
                <p>Bank Name : '''+str(bank_name)+'''</p>
                <p>Branch Address :   '''+str(bank_address)+'''</p>
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
                            <h4 style="text-align: right; ">For '''+str(company)+'''</h4>
                            <img src="'''+os.path.join(os.getcwd(),str(signature_path))+'''" style="width: 150px; margin-left:auto; display:block; margin-right:18px">
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

    return html
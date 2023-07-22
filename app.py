from flask import Blueprint, Flask, request, jsonify,session,send_from_directory,redirect,abort, render_template, url_for
import sqlite3, datetime
import re
from datetime import date
import os
import pdfkit
from auth import auth_bp
import json
from decorator import *
import requests
from authlib.integrations.flask_client import OAuth
from functions import *

app = Flask(__name__)

app.register_blueprint(auth_bp)

meon_invoice = sqlite3.connect('database/meon_invoice.db', detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)

company_details = sqlite3.connect('database/company_details.db', detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)

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
         bank_address TEXT,ddcustomer
         account_no TEXT,

         Ifsc_code TEXT,
         cgst TEXT,
         igst_type,
         total_value_in_inr,
         sgst TEXT,
         date TEXT,
         amount_text TEXT,
        terms TEXT,
        logo TEXT,
        pan TEXT,
        hsn TEXT,
        gstin TEXT,
        financial_year TEXT,
        invoice_path TEXT,
        customer_gstin TEXT,
        rate_distribution TEXT
    );''')
meon_invoice.commit()

meon_invoice.execute('''CREATE TABLE IF NOT EXISTS addnewcustomer
    (id INTEGER NOT NULL PRIMARY KEY,
    customer_name TEXT,
    gst_no TEXT,
    invoice_company_address1 TEXT,
    invoice_company_address2 TEXT,
    invoice_company_address3 TEXT,
    invoice_company_address4 TEXT,
    state TEXT);''')
meon_invoice.commit()

meon_invoice.execute('''CREATE TABLE IF NOT EXISTS SeriesCount
    (id INTEGER NOT NULL PRIMARY KEY,
    company TEXT,
    count TEXT,
    tax_invoice_type TEXT,
    pattern TEXT);''')
meon_invoice.commit()

meon_invoice.execute('''CREATE TABLE IF NOT EXISTS hsn_no
         (id INTEGER NOT NULL PRIMARY KEY,
         hsn TEXT);''')
meon_invoice.commit()

meon_invoice.execute('''CREATE TABLE IF NOT EXISTS login
         (id INTEGER NOT NULL PRIMARY KEY,
         username TEXT,
         password TEXT);''')
meon_invoice.commit()



meon_invoice.execute('''CREATE TABLE IF NOT EXISTS invoice
         (id INTEGER NOT NULL PRIMARY KEY,
         invoice TEXT);''')
meon_invoice.commit()


company_details.execute('''CREATE TABLE IF NOT EXISTS users
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    email TEXT,
    company INTEGER
    );'''
)
company_details.commit()

company_details.execute('''CREATE TABLE IF NOT EXISTS directors
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    director_name TEXT,
    director_email TEXT,
    company INTEGER
    );'''
)
company_details.commit()

company_details.execute('''CREATE TABLE IF NOT EXISTS companyinfo
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    company_name TEXT,
    company_logo TEXT,
    gstin TEXT,
    bank_name TEXT,
    address TEXT,
    account_no TEXT,
    ifsc_code TEXT,
    pan TEXT,
    FOREIGN KEY(directors) REFERENCES directors(id)
    );'''
)
company_details.commit()

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
@authenticate_user
def index():
    return render_template('invoice_form.html')

@app.route('/submit_invoice/<inv>', methods=['POST'])
@authenticate_user
def submit_invoice(inv):
    company = request.form["company"]
    id = request.form["id"]  
    if company == None or company == '':
        return jsonify({"pdf":"", "message":"company name is blank", "status":False})
    data = meon_invoice.execute(f"SELECT customer_name from addnewcustomer where id = {id}").fetchall()
    if data == []:
        print("data not found")
        return jsonify({"pdf":"", "message":"data not found", "status":False})
    customer_name = data[0][0]
    if customer_name == None or customer_name == '':
        return jsonify({"pdf":"", "message":"customer name is blank", "status":False})    
    tax_invoice_type = request.form["tax_invoice_type"]
    rate_distribution = request.form["rate_distribution"]
    try:
        json.loads(rate_distribution.replace("'",'"'))
    except:
        return jsonify({"pdf":"", "message":"Invalid request", "status":False})
    quantity, Rate_unit, Amount = 0, 0, 0
    for x in json.loads(rate_distribution.replace("'",'"')):
        quantity += int(x["quantity"])
        Rate_unit += float(x["Rate_unit"])
        Amount += int(x["quantity"])*float(x["Rate_unit"])
    terms = request.form["terms"]

    company_data = company_details.execute(f"select signature_path from companyinfo where company_name='{company}'").fetchone()
    if company_data is None:
        return jsonify({"pdf":"", "message":"Invalid company name", "status":False})
    signature_path = company_data[0]
    customer_data = meon_invoice.execute(f"select state, customer_name, invoice_company_address1, invoice_company_address2, invoice_company_address3, invoice_company_address4, gst_no from addnewcustomer where id='{id}'").fetchall()
    if customer_data == []:
        return jsonify({"pdf":"", "message":"customer name is blank", "status":False})  
    state = customer_data[0][0]
    customer_name = str(customer_data[0][1])
    add1 = str(customer_data[0][2])
    add2 = str(customer_data[0][3])
    add3 = str(customer_data[0][4])
    add4 = str(customer_data[0][5])
    gst_no = str(customer_data[0][6])

    
    meon_invoice.execute("INSERT into invoicefields(invoice_company_name, customer_gstin, invoice_company_address1,invoice_company_address2,invoice_company_address3,invoice_company_address4,state, invoice_no, tax_invoice_type, company) Values(?,?,?,?,?,?,?,?,?,?)",(customer_name, gst_no, add1, add2, add3, add4, state, inv, tax_invoice_type, company))
    meon_invoice.commit()

    if state == "Uttarpradesh":
        igst_type = "CGST@9% + SGST@9%"
    else:
       igst_type = "IGST@18%"

    #===========GST CALCULATION===============

    amount = float(Amount)
    igst = (amount * 9) / 100 
    total_value_in_inr = amount + igst + igst
    total_value_in_inr = round(total_value_in_inr, 2)

    #============TOTAL VALUE===================  
    amount = total_value_in_inr
    try:
        amount_text = convert_amount_to_text(amount)
    except OverflowError:
        return jsonify({'pdf':"", "message":f"{quantity}*{Rate_unit} must be less than 10000000000", "status":False})

    #============MULTIPLE LOGOS=========================

    logo = logos[company]   

    #========= Acessing only date ==================

    invoice_date = datetime.datetime.now()
    current_date = invoice_date.date()
    formatted_date = current_date.strftime("%d/%m/%Y")

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
    
    inv = meon_invoice.execute("select invoice_no from invoicefields WHERE invoice_no = '"+inv+"' ").fetchall()[0][0]
    financial_year = financial_year_current
    meon_invoice.execute("update invoicefields set invoice_date='"+str(invoice_date)+"',quantity='"+str(quantity)+"',rate_unit='"+str(Rate_unit)+"',Amount='"+str(Amount)+"',igst='"+str(igst)+"',igst_type='"+str(igst_type)+"',total_value_in_inr='"+str(total_value_in_inr)+"',date='"+str(formatted_date)+"',amount_text='"+str(amount_text)+"',terms='"+str(terms)+"',logo='"+logo+"',bank_name='"+bank_name+"',bank_address='"+str(address)+"',account_no='"+str(account_no)+"',Ifsc_code='"+str(ifsc_code)+"',pan='"+str(pan)+"',gstin='"+str(gstin)+"',financial_year='"+str(financial_year)+"', rate_distribution='"+rate_distribution.replace("'",'"')+"' where invoice_no = '"+inv+"' ")
    meon_invoice.commit()

    data = meon_invoice.execute("SELECT * FROM invoicefields WHERE invoice_no= '"+inv+"' ").fetchall()
    invoice_no = data[0][3]
    try:
        if state == "Uttarpradesh":
            html = InvoicePDFUP(data, logo, pan, signature_path)
        else:
            html = InvoicePDFOthers(data, logo, pan, signature_path)
    except Exception as e:
        print(e)
        return jsonify({'pdf':"", "message":"pdf generation failed", "status":True})
    
    options = {'enable-local-file-access': None, '--page-size': 'A4'}
    path = 'static/invoice/'
    if not os.path.exists(path):
        os.mkdir("static/invoice/")

    invoice_path = "static/invoice/"+invoice_no+".pdf"
    meon_invoice.execute("update invoicefields set invoice_path='"+str(invoice_path)+"' where invoice_no = '"+inv+"' ")
    meon_invoice.commit()
    pdfkit.from_string(html, invoice_path, options=options)
    count_data = meon_invoice.execute("SELECT count, pattern FROM SeriesCount WHERE tax_invoice_type = '"+tax_invoice_type+"' AND company =  '"+company+"'").fetchall()
    meon_invoice.execute("UPDATE SeriesCount set count = '"+str(int(count_data[0][0])+1)+"' WHERE tax_invoice_type = '"+tax_invoice_type+"' AND company =  '"+company+"'")
    meon_invoice.commit()
    return jsonify({'pdf':invoice_path, "message":"invoice generated", "status":True})


@app.route('/fetch_invoice_no', methods=['POST'])
@authenticate_user
def fetch_invoice_no():
    data = request.form
    company = request.form["company"]     
    tax_invoice_type = request.form["tax_invoice_type"]
    count_data = meon_invoice.execute("SELECT count, pattern FROM SeriesCount WHERE tax_invoice_type = '"+tax_invoice_type+"' AND company =  '"+company+"'").fetchall()
    print(count_data)
    if count_data == []:
        return jsonify({'invoice_no':'','status':False})
    if tax_invoice_type == "Proforma Invoice" :
        invoice_no = count_data[0][1] + count_data[0][0].zfill(4)
    else:
        invoice_no = count_data[0][1]+financial_year_current+'_'+count_data[0][0]
    return jsonify({'invoice_no':invoice_no,'status':False})     


@app.route("/find_invoicelink",methods=['GET','POST'])
@authenticate_user
def find_invoicelink():
    return render_template('preinvoice.html')

@app.route("/find_invoice",methods=['POST'])
@authenticate_user
def find_invoice():
    data = request.form    

    financial_year =    request.form["financial_year"]
    id = request.form["id"]
    meon_company = request.form["meon_company"]
    invoice_type = request.form["invoice_type"]

    data = meon_invoice.execute(" SELECT company, tax_invoice_type, invoice_company_name, date, invoice_no, quantity, rate_unit FROM invoicefields WHERE company = '"+meon_company+"' AND financial_year = '"+financial_year+"' AND tax_invoice_type = '"+invoice_type+"' order by invoice_no DESC").fetchall()

    if data == []:
        return({'msg':'Data Not Found'})
    
    data_list = []
    for inv in data:
        invoice = str(inv[4])+', '+str(inv[3])+', '+str(inv[5])
        data_list.append(invoice)

    return jsonify({'data':data_list})

@app.route("/generate_invoice/<invoice_no>",methods=['GET','POST'])
@authenticate_user
def generate_invoice(invoice_no):
    data = meon_invoice.execute(" SELECT invoice_path FROM invoicefields WHERE invoice_no= '"+invoice_no+"' ").fetchall() 
    if data != []:
        return jsonify({'pdf':data[0][0]})


@app.route("/delete_invoice/<invoice_no>",methods=['GET','POST'])
@authenticate_user
def delete_invoice(invoice_no):
    chk = meon_invoice.execute(" SELECT company, financial_year, tax_invoice_type FROM invoicefields WHERE invoice_no= '"+invoice_no+"' ").fetchall()

    data = meon_invoice.execute(" SELECT invoice_no FROM invoicefields WHERE company = '"+chk[0][0]+"' AND financial_year = '"+chk[0][1]+"' AND tax_invoice_type = '"+chk[0][2]+"' ").fetchall()
    if data[-1][0] != invoice_no:
        return jsonify({"status":False})

    count_data = meon_invoice.execute("SELECT count FROM SeriesCount WHERE tax_invoice_type = '"+chk[0][2]+"' AND company =  '"+chk[0][0]+"'").fetchall()
    if count_data==[]:
        return jsonify({"status":False})

    meon_invoice.execute("UPDATE SeriesCount set count = '"+str(int(count_data[0][0])-1)+"' WHERE tax_invoice_type = '"+chk[0][1]+"' AND company =  '"+chk[0][0]+"'")
    meon_invoice.commit()
    meon_invoice.execute(" DELETE FROM invoicefields WHERE invoice_no= '"+invoice_no+"' ")
    meon_invoice.commit()
    return jsonify({"status":True})

@app.route('/addcompany', methods=['POST', 'GET'])
@authenticate_user
def addcompany():
    if request.method == 'GET':
        return render_template('addcustomer.html')
    else:
        data = request.form
        customer_name = str(request.form["customer_name"]  ).strip().upper()
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


        data = meon_invoice.execute(" select customer_name from addnewcustomer WHERE customer_name = '"+customer_name+"' ").fetchall()
        if data == []:
            # customer_id = generateCompanyId(customer_name)
            meon_invoice.execute('INSERT INTO addnewcustomer(customer_name,gst_no,invoice_company_address1,invoice_company_address2,invoice_company_address3,invoice_company_address4,state) VALUES(?,?,?,?,?,?,?)',(customer_name,g,add1,add2,add3,add4,state))

            meon_invoice.commit()
            return jsonify({'msg':'success','status':True})
        else:
            return jsonify({'msg':'Customer Name Exists','status':False})



@app.route('/searchcompany/<invoice>', methods=['POST','GET'])
@authenticate_user
def searchcompany(invoice):
    inv = meon_invoice.execute("select invoice_no from invoicefields WHERE invoice_no = '"+invoice+"' ").fetchall()[0][0]
    data = request.get_json()

    id = data['id']
    customer_data = meon_invoice.execute(f"SELECT customer_name from addnewcustomer where id = {id}").fetchall()
    if customer_data == []:
        return jsonify({"msg":"Invalid"})
    customer_name = data[0][0]
    all_data = meon_invoice.execute(" SELECT customer_name,gst_no,invoice_company_address1,invoice_company_address2,invoice_company_address3,invoice_company_address4,state FROM addnewcustomer WHERE id = '"+id+"' ").fetchall()
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
    return render_template("home.html")


@app.route("/signin-google")
def googleCallback():
    token = oauth.myApp.authorize_access_token()

    personDataUrl = "https://people.googleapis.com/v1/people/me?personFields=emailAddresses,clientData"
    personData = requests.get(personDataUrl, headers={"Authorization": f"Bearer {token['access_token']}"}).json()

    if 'emailAddresses' in personData:
        for x in personData['emailAddresses']:
            if 'metadata' in x:
                if 'primary' in x['metadata'] and x['metadata']:
                    email = str(x['value']).lower()
                    data = company_details.execute(f"select * from users where email = '{email}' union select * from directors where director_email = '{email}'").fetchall()
                    if data != []:
                        session["user"] = email
                        return redirect(url_for("index", success="yes"))

    return redirect(url_for("home", success="no"))

@app.route("/google-login")
def googleLogin():
    return oauth.myApp.authorize_redirect(redirect_uri=url_for("googleCallback", _external=True, _scheme='http'))

@app.route("/logout")
@authenticate_user
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

@app.route("/set_user", methods=['POST'])
def set_user():
    data = request.get_json()
    email = data['user_email']
    session["user"] = email
    return jsonify({"message":"user is set", "success":True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=appConf.get("FLASK_PORT"))       

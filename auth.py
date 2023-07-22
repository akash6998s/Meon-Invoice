from flask import Blueprint, Flask, request, jsonify, render_template,session,send_from_directory,redirect,url_for
import sqlite3, datetime, jwt, requests, json, base64
import re
from datetime import date
import os
import pdfkit
from num2words import num2words
from decorator import *
from functions import generateCompanyId


auth_bp = Blueprint('auth', __name__)


meon_invoice = sqlite3.connect(
    'database/meon_invoice.db', detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)

company_details = sqlite3.connect('database/company_details.db', detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)

company_details.execute('''CREATE TABLE IF NOT EXISTS API_Details
    (id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    user_email TEXT,
    password TEXT,
    api_type TEXT
    );'''
)

@auth_bp.route('/hsn', methods=['POST','GET'])
@authenticate_user
def hsn():
    return render_template("hsnpage.html")


@auth_bp.route('/fetch_customer/<id>', methods=['POST','GET'])
@authenticate_user
def fetch_details(id):
    data = meon_invoice.execute("SELECT id,customer_name, gst_no, invoice_company_address1, invoice_company_address2,invoice_company_address3, invoice_company_address4, state  FROM addnewcustomer WHERE id = '"+id+"' ").fetchall()
    d = len(data)
    if data == None or data == '' or d == 0:
        return jsonify({'msg':'data not found'})
    else:
        id = data[0][0]
        customer_name = data[0][1]
        gst_no = data[0][2]
        invoice_company_address1 = data[0][3]
        invoice_company_address2 = data[0][4]
        invoice_company_address3 = data[0][5]
        invoice_company_address4 = data[0][6]
        state = data[0][7]

        

        return jsonify(
            {
                'id':id,
                'customer_name':customer_name,
                'gst_no':gst_no,
                'invoice_company_address1':invoice_company_address1,
                'invoice_company_address2':invoice_company_address2,
                'invoice_company_address3':invoice_company_address3,
                'invoice_company_address4':invoice_company_address4,
                'state':state


            }
        )
    
@auth_bp.route('/editcustomer')
@authenticate_user
def editcustomer():
        return render_template("editcustomer.html")
    
@auth_bp.route('/editcompany/<id>', methods=['POST'])
@authenticate_user
def editcompany(id):
    data = request.form
    l = len(data)
    if data == None or data == '' or l == 0:
        return jsonify({'msg':'data not found', 'status':False})
    else:
        customer_data = meon_invoice.execute(f"SELECT customer_name from addnewcustomer where id = {id}").fetchall()
        if customer_data == []:
            return jsonify({"msg":"Invalid"})
        customer_name = request.form["customer_name"]
        gstno = request.form["gstno"]
        add1 = request.form["add1"]
        add2 = request.form["add2"]
        add3 = request.form["add3"]
        add4 = request.form["add4"]
        state = request.form["state"]


        meon_invoice.execute(" UPDATE addnewcustomer SET customer_name = '"+customer_name+"',gst_no = '"+gstno+"',invoice_company_address1 = '"+add1+"',invoice_company_address2 = '"+add2+"',invoice_company_address3 = '"+add3+"',invoice_company_address4 = '"+add4+"',state = '"+state+"' WHERE id = '"+id+"' ")
        meon_invoice.commit()
                        
        return jsonify({'msg':'success','status':True})  

    

@auth_bp.route('/addhsn', methods=['POST'])
@authenticate_user
def addhsn():
    data = request.form
    hsn = request.form["hsn_no"]
    meon_invoice.execute('INSERT INTO hsn_no (hsn) VALUES(?)',(hsn,))
    meon_invoice.commit()             
    return jsonify({'msg':'success','status':True})    
    

@auth_bp.route('/displayhsn', methods=['POST','GET'])
@authenticate_user
def displayhsn():
    data = meon_invoice.execute(" SELECT hsn FROM hsn_no ").fetchall()
    data_list = []
    data_list.append(data)
    for data_dict in data_list:
        print(data_dict)
    return jsonify({'msg':data_dict})    


@auth_bp.route('/searchcompany/<invoice>', methods=['POST','GET'])
@authenticate_user
def searchcompany(invoice):
    inv = meon_invoice.execute(" select invoice_no from invoicefields WHERE invoice_no = '"+invoice+"' ").fetchall()[0][0]
    data = request.get_json()

    id = data['id']

    all_data = meon_invoice.execute("SELECT customer_name, gst_no, invoice_company_address1, invoice_company_address2, invoice_company_address3, invoice_company_address4, state FROM addnewcustomer WHERE id = ?", (id,)).fetchall()

    d = len(all_data)

    if all_data == None or all_data == '' or d == 0:
        return jsonify({'msg':'Name not found...'})

    return jsonify({'msg':'Data fetch successfully...','data':all_data})
    


@auth_bp.route("/listdetailslink",methods=['GET','POST'])
@authenticate_user
def listdetailslink():
    return render_template('allcustomers.html')

@auth_bp.route("/listdetails",methods=['GET'])
@authenticate_user
def listdetails():
    data = meon_invoice.execute(" SELECT * FROM addnewcustomer ").fetchall()    
    data_list = []

    for i in data:
        x = {
            'id':i[0],
            'customer_name':i[1],
            'gst_no':i[2],
            'invoice_company_address1':i[3],
            'invoice_company_address2':i[4],
            'invoice_company_address3':i[5],
            'invoice_company_address4':i[6],
            'state':i[7]}
        data_list.append(x)
        
        
    return jsonify({"data":data_list})



@auth_bp.route('/search_company', methods=['POST','GET'])
@authenticate_user
def search_company():
    data = request.get_json()

    customer_name = data['customer_name']

    all_data = meon_invoice.execute("SELECT DISTINCT invoice_company_name FROM invoicefields WHERE invoice_company_name LIKE ? || '%' ", (customer_name,)).fetchall()
    
    d = len(all_data)
   
    if all_data == None or all_data == '' or d == 0:
        return jsonify({'msg':'Name not found'})
    
    else:
        customer_name = all_data[0][0]

        return jsonify({'msg':'Data fetch successfully...','data':all_data})
    



@auth_bp.route('/listcustomer', methods=['POST','GET'])
@authenticate_user
def listcustomer():
    all_data = meon_invoice.execute(" SELECT id, customer_name FROM addnewcustomer ").fetchall()
    return jsonify({'msg':'Data fetch successfully...','data':all_data})
    

@auth_bp.route('/auth', methods=['POST'])
def auth():
    data = request.get_json()
    user_email = str(data['user_email']).strip()
    password = data['password']
    chk = company_details.execute(f"SELECT * FROM API_Details where user_email = '{user_email}' and password = '{password}' and api_type='user'").fetchone()
    if chk is None:
        return jsonify({"signature":"", "message":"invalid", "status":False})

    payload = {
        "user_email": user_email,
        "password": password,
        "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=180)
    }
    return jsonify({"signature":jwt.encode(payload, 'IAMTHEBOSS', algorithm='HS256'), "message":"signature generated. will be valid for 180 seconds", "status":True})


@auth_bp.route('/get_customer_details', methods=['POST'])
def get_customer_details():
    if "signature" in request.headers:
        jwt_token = request.headers.get('signature')
    else:
        return jsonify({"data":"", "success":False,"message":"Header Missing"})
    try:
        data = jwt.decode(jwt_token, 'IAMTHEBOSS', leeway=datetime.timedelta(seconds=3), algorithms=["HS256"])
    except jwt.ExpiredSignatureError as e:
        return jsonify({"data":"", "success":False,"message":str(e)})
    except jwt.exceptions.DecodeError as e:
        return jsonify({"data":"", "success":False,"message":str(e)})
    if 'user_email' in data and 'password' in data:
        user_email = data['user_email']
        password = data['password']
        chk = company_details.execute(f"SELECT * FROM API_Details where user_email = '{user_email}' and password = '{password}' and api_type='user'").fetchone()
        if chk is None:
            return jsonify({"data":"", "message":"invalid", "status":False})

        host = 'http://localhost:5000/'
        headers = {
            "Content-Type":"application/json"
        }
        response = requests.post(host+'set_user', json={"user_email":user_email}, headers = headers)
        response = requests.post(host+f'listcustomer', cookies = response.cookies)
        # print(response.text)
        if response.status_code == 200:
            return jsonify({"data":response.json().get('data'), "success":True, "message":"success"})
    return jsonify({"data":"", "success":False, "message":"failed"})


     

@auth_bp.route('/get_invoice_pdf', methods=['POST'])
def invoice_pdf():
    if "signature" in request.headers:
        jwt_token = request.headers.get('signature')
    else:
        return jsonify({"document":"", "success":False,"message":"Header Missing"})
    try:
        data = jwt.decode(jwt_token, 'IAMTHEBOSS', leeway=datetime.timedelta(seconds=3), algorithms=["HS256"])
    except jwt.ExpiredSignatureError as e:
        return jsonify({"document":"", "success":False,"message":str(e)})
    except jwt.exceptions.DecodeError as e:
        return jsonify({"document":"", "success":False,"message":str(e)})
    if 'user_email' in data and 'password' in data:
        user_email = data['user_email']
        password = data['password']
        chk = company_details.execute(f"SELECT * FROM API_Details where user_email = '{user_email}' and password = '{password}' and api_type='user'").fetchone()
        if chk is None:
            return jsonify({"document":"", "message":"invalid", "status":False})


        data = request.get_json()
        company = data['company']
        tax_invoice_type = data['tax_invoice_type']

        # invoice generation logic
        host = 'http://localhost:5000/'
        headers = {
            "Content-Type":"application/json"
        }
        response = requests.post(host+'set_user', json={"user_email":user_email}, headers = headers)
        responseInv = requests.post(host+'fetch_invoice_no', data={"company":company, "tax_invoice_type":tax_invoice_type}, cookies = response.cookies)
        print(responseInv.text)
        if responseInv.status_code == 200 and json.loads(responseInv.text)['status']:
            invoice_id = responseInv.json()['invoice_no']
        else:
            return jsonify({"document":"", "success":False,"message":"Invoice No generation failed"})

        print(data['rate_distribution'])
        data['rate_distribution'] = str(data['rate_distribution'])
        response = requests.post(host+f'submit_invoice/{invoice_id}', data=data, cookies = response.cookies)
        print(response.text)
        if response.status_code == 200 and json.loads(response.text)['status']:
            document_path = json.loads(response.text)['pdf']
        else:
            return jsonify({"document":"", "success":False, "message":"Invoice generation failed"})

        with open(document_path, "rb") as f:
            document = base64.b64encode(f.read()).decode()
        return jsonify({"document":document, "success":True, "message":"Invoice generated"})

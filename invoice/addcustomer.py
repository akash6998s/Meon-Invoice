from flask import Blueprint, Flask, request, jsonify, render_template,session,send_from_directory,redirect,url_for
import sqlite3, datetime
import re
from datetime import date
import os
import pdfkit
from num2words import num2words
meon = Flask(__name__)
# from invoice import invoice
# from invoice.addcustomer import addcustomer

meon_invoice = sqlite3.connect(
    'meon_invoice.db', detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)

# invoice = Blueprint('invoice', __name__, url_prefix='/invoice')
# invoice.register_blueprint(addcustomer)
@meon.route('/addcompany', methods=['POST'])
def addcompany():
    data = request.form
    print("===========GETTING DATA FROM FORM===========",data)
    if request.method =="POST":
        customer_name = request.form["customer_name"]
        gstno = request.form["gstno"]
        add1 = request.form["add1"]
        add2 = request.form["add2"]
        add3 = request.form["add3"]
        add4 = request.form["add4"]
        state = request.form["state"]

        meon_invoice.execute('INSERT INTO addnewcustomer  (customer_name,gst_no,invoice_company_address1,invoice_company_address2,invoice_company_address3,invoice_company_address4,state) VALUES(?,?,?,?,?,?,?)',(customer_name,gstno,add1,add2,add3,add4,state))

        meon_invoice.commit()
                        
        return jsonify({'msg':'success','status':True})
    

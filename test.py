from flask import Blueprint, Flask, request, jsonify, render_template,session,send_from_directory,redirect,url_for
import sqlite3, datetime
import re
from datetime import date
import os
import pdfkit
test = Flask(__name__)
meon_invoice = sqlite3.connect(
    'database/meon_invoice.db', detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)

company = "Performa"
tax_invoice_type = "Meontech"
plus="plus"
minus ="minus"



if plus == "plus":
    data = meon_invoice.execute("SELECT company,tax_invoice_type,invoice_no FROM invoicefields WHERE company= '"+company+"' AND tax_invoice_type = '"+tax_invoice_type+"' ORDER by id DESC LIMIT 1").fetchall()

    company = data[0][0]
    tax_invoice_type = data[0][1]
    invoice_no = data[0][2]

    if tax_invoice_type == "Performa":
        print("====== Found Performa ========")
        data = meon_invoice.execute(" select invoice_no from invoicefields WHERE tax_invoice_type = '"+tax_invoice_type+"' ORDER by id DESC LIMIT 1 ").fetchall()
        print(data,len(data),"===================== data")

        if data is not None and  data !='' and  len(data)!=0:
            string_f = data[0][0]
            print(string_f,"====")                  #getting data from list
            new_s = string_f.split("00")[0]         #getting only string
            print(new_s,"====")   

            num = string_f.split("ME")[1]           #getting digits only
            print(num,"====") 
            count = 1
            digit = int(num)
            a = count + digit                       #increment digit
            print(a)     
            invoice_no = new_s + "000" + str(a)     #merge string with increment digit
            print(invoice_no)
            ("UPDATE invoicefields SET invoice_no = ? WHERE company = ?",
        (invoice_no,company))
    
        
        else:
            print("inside else")
            count =1
            invoice_no = 'ME000'+str(count)
            print(invoice_no,"----")
            print(company,"====")     
            meon_invoice.execute(f"UPDATE invoicefields SET invoice_no = '{invoice_no}' where company = '{company}'")
            meon_invoice.commit()


    if tax_invoice_type == "Tax" and company == "Meontech":
        print("============== Found Tax ===========")          
        data = meon_invoice.execute(" select invoice_no from invoicefields WHERE company = '"+company+"' AND tax_invoice_type = '"+tax_invoice_type+"' ORDER by id DESC LIMIT 1 ").fetchall()
        print(data,len(data),"===================== data")
        if data is not None and  data !='' and  len(data)!=0:
            string_f = data[0][0]
            print(string_f,"====")                   #getting data from list
            new_s = string_f.split("_")[0]           #getting only string
            print(new_s,"====")    
            num = string_f.split("_")[1]             #getting digits only
            print(num,"====")  
            count = 1
            digit = int(num)
            a = count + digit                        #increment digit
            print(a)    
            invoice_no = new_s +"_"+ str(a)          #merge string with increment digit
            print(invoice_no)
            ("UPDATE invoicefields SET invoice_no = ? WHERE company = ?",
            (invoice_no,company))
    
    
        else:
            print("inside else of tax")
            count =1
            invoice_no = 'MTECH23-24_'+str(count)
            print(invoice_no,"----")
            print(company,"====")
        
            meon_invoice.execute(f"UPDATE invoicefields SET invoice_no = '{invoice_no}' where company = '{company}'")
            meon_invoice.commit()        

    if tax_invoice_type == "Tax" and company == "MeonEnterprise":
        print("==============Found Tax===========")

        data = meon_invoice.execute(" select invoice_no from invoicefields WHERE company = '"+company+"' AND tax_invoice_type = '"+tax_invoice_type+"' ORDER by id DESC LIMIT 1 ").fetchall()
        print(data,len(data),"===================== data")
        if data is not None and  data !='' and  len(data)!=0:
            string_f = data[0][0]
            print(string_f,"====")                        #getting data from list
            new_s = string_f.split("_")[0]                #getting only string
            print(new_s,"====")   

            num = string_f.split("_")[1]                  #getting digits only
            print(num,"====")  
            count = 1
            digit = int(num)
            a = count + digit                             #increment digit
            print(a)     
            invoice_no = new_s +"_"+ str(a)               #merge string with increment digit
            print(invoice_no)
            ("UPDATE invoicefields SET invoice_no = ? WHERE company = ?",
        (invoice_no,company))

    
        else:
            print("inside else")
            count =1
            invoice_no = 'MEON23-24_'+str(count)
            print(invoice_no,"----")
            print(company,"====")


    if tax_invoice_type == "Tax" and company == "MeonFinancial":
        print("==============Found Tax===========")

        data = meon_invoice.execute(" select invoice_no from invoicefields WHERE company = '"+company+"' AND tax_invoice_type = '"+tax_invoice_type+"' ORDER by id DESC LIMIT 1 ").fetchall()
        print(data,len(data),"===================== data")
        if data is not None and  data !='' and  len(data)!=0:
            string_f = data[0][0]                    #getting data from list
            print(string_f,"====")  
            new_s = string_f.split("_")[0]           #getting only string
            print(new_s,"====")   
            num = string_f.split("_")[1]             #getting digits only
            print(num,"====")  
            count = 1
            digit = int(num)
            a = count + digit                        #increment digit
            print(a)     
            invoice_no = new_s +"_"+ str(a)          #merge string with increment digit
            print(invoice_no)
            ("UPDATE invoicefields SET invoice_no = ? WHERE company = ?",
        (invoice_no,company))

    
        else:
            print("inside else")
            count =1
            invoice_no = 'MFIN23-24_'+str(count)
            print(invoice_no,"----")
            print(company,"====")


    if tax_invoice_type == "Tax" and company == "Meontours":
        print("==============Found Tax Meontours===========")

        data = meon_invoice.execute(" select invoice_no from invoicefields WHERE company = '"+company+"' AND tax_invoice_type = '"+tax_invoice_type+"' ORDER by id DESC LIMIT 1 ").fetchall()
        print(data,len(data),"===================== data")
        if data is not None and  data !='' and  len(data)!=0:
            string_f = data[0][0]                       #getting data from list
            print(string_f,"====")  
            new_s = string_f.split("_")[0]              #getting only string
            print(new_s,"====")   
            num = string_f.split("_")[1]                #getting digits only
            print(num,"====")  
            count = 1
            digit = int(num)
            a = count + digit                           #increment digit
            print(a)     
            invoice_no = new_s +"_"+ str(a)             #merge string with increment digit
            print(invoice_no)
            ("UPDATE invoicefields SET invoice_no = ? WHERE company = ?",
        (invoice_no,company))

    
        else:
            print("inside else")
            count =1
            invoice_no = 'MTOUR23-24_'+str(count)
            print(invoice_no,"----")
            print(company,"====")    

            meon_invoice.execute(f"UPDATE invoicefields SET invoice_no = '{invoice_no}' where company = '{company}'")
            meon_invoice.commit()

elif minus == "minus":
    data = meon_invoice.execute("SELECT company,tax_invoice_type,invoice_no FROM invoicefields WHERE company= '"+company+"' AND tax_invoice_type = '"+tax_invoice_type+"' ORDER by id DESC LIMIT 1").fetchall()

    company = data[0][0]
    tax_invoice_type = data[0][1]
    invoice_no = data[0][2]

    if tax_invoice_type == "Performa":
        print("====== Found Performa ========")
        data = meon_invoice.execute(" select invoice_no from invoicefields WHERE tax_invoice_type = '"+tax_invoice_type+"' ORDER by id DESC LIMIT 1 ").fetchall()
        print(data,len(data),"===================== data")

        if data is not None and  data !='' and  len(data)!=0:
            string_f = data[0][0]
            print(string_f,"====")                  #getting data from list
            new_s = string_f.split("00")[0]         #getting only string
            print(new_s,"====")   

            num = string_f.split("ME")[1]           #getting digits only
            print(num,"====") 
            count = 1
            digit = int(num)
            a = count - digit                       #increment digit
            print(a)     
            invoice_no = new_s + "000" + str(a)     #merge string with increment digit
            print(invoice_no)
            data =  meon_invoice.execute("SELECT invoice_no,igst from invoicefields").fetchall()
            inv = data[0][0]
            igst= data[0][1]
            print("inv:",inv,"===","igst:",igst)

            if inv == invoice_no and (igst == None or igst == ''):
                ("UPDATE invoicefields SET invoice_no = ? WHERE company = ?",
            (invoice_no,company))
                
            else:
                print("invoice number already register")
                # return jsonify({'msg':'invoice number already register'})
        
        else:
            print("No Invoice No Found")
            # return jsonify({'msg':'No Invoice No Found'})
            # print("inside else")
            # count =1
            # invoice_no = 'ME000'+str(count)
            # print(invoice_no,"----")
            # print(company,"====")     
            # meon_invoice.execute(f"UPDATE invoicefields SET invoice_no = '{invoice_no}' where company = '{company}'")
            # meon_invoice.commit()


from datetime import datetime

datetime_str = "2023-06-21 16:07:41.559914"
datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S.%f")
year = datetime_obj.year

print(year)

d = year + 1
print(d)

print(str(year) + "-" + str(d))



if __name__ == '__main__':
    test.run(debug=True)                

        


import sqlite3
import pandas as pd

meon_invoice = sqlite3.connect(
    'database/meon_invoice.db', detect_types=sqlite3.PARSE_DECLTYPES, check_same_thread=False)


wb=pd.ExcelFile('data 1.xlsx')
for sheet3 in wb.sheet_names:
        df=pd.read_excel('data 1.xlsx',sheet_name=sheet3)
        df.to_sql(sheet3,meon_invoice, index=False,if_exists="replace")
        
        
meon_invoice.commit()
meon_invoice.close()
#@author: diego
import creds
import requests
from bs4 import BeautifulSoup
import pandas as pd

date_out = input('Enter a date formatted as YYYY-MM-DD: ')     ## Variable global para la fecha que quieras ver o exportar

def GetResponseUrl():                                          ## esta funcion te da el url de response damageid cuando pones la fecha y all cases

    date_components =  date_out.split("-")

    year, month, day = [int(item) for item in date_components]
    
    f_url = 'https://app.damageid.com/case/list?searchUnit=&inoutKey=dateOut&inoutValue='

    date = f'{month}%2F{day}%2F{year}'

    c_url = '&statusFilter=-1&templateFilter=7&searchCaseNumber=&searchUser=&searchLicensePlate=&searchVin='

    response_url = f_url + date + c_url

    return response_url


request_url = ('https://app.damageid.com/authenticate')

response_url = (GetResponseUrl()) 

payload = {                                                      ## tienes que tener el archivo creds.py en el mismo folder que este notebook
    
    'username':creds.username,
    'password':creds.password    
    }

case_list = []                                                   ## Inicias listas vacias para dumpear la data
status_list = []
van_list = []
username = []

print("Scraping DamageID...")
with requests.session() as s:                                    ## aqui es donde se hace el scraping con Beautiful Soup
        s.post(request_url, data = payload)
        r = s.get(response_url)
        soup = BeautifulSoup(r.content, 'html.parser')
        
        cases = soup.find_all('td', {'class':'damage-td-first'})
        statuses = soup.find_all('td', {'class':'damage-td-last'})
        table = soup.find('table', {"class":"table table-hover"})

        for case in cases:
            case_list.append(case.text.replace("\t","").replace("\n","").strip())
        
        
        for status in statuses:
                status_list.append(status.text.strip())
        
        for driver in table.find_all("tbody"):
            rows = driver.find_all("tr")
            for row in rows:
                values = row.find("td")
                    
                values1 = values.find_next("td")
                van_list.append(values1.text.strip())
                   
                values2 = values1.find_next("td")
                values2 = values2.text.split(" ")[0].strip()             ## agarra solo el primer id de cada row de la tabla en  damageid
                username.append(values2)

        
        df = pd.DataFrame({"Cases ID":case_list, "Van Unit":van_list, "Username":username, "Status":status_list, "Date_Out":date_out})   ### sale el df con la data
print("Complete")

a = input("export? y/n")

if a.lower() == "y":    #### por si lo quieres guardar como csv o solo ver
    file = "DamageID_" + date_out + ".csv"
    df.to_csv(file)
    print(f"File {file} saved")
else:
    print(df)

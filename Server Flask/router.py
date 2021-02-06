import threading
import nmap
import requests  
import pythoncom
import who_is_on_my_wifi

my_position = "(1654,3648)"
def index():
    threading.Timer(300.0, index).start()
    pythoncom.CoInitialize()
    connected_list = who_is_on_my_wifi.who() #Get users who use my network
    users_mac = [i[3] for i in connected_list] #Take their Mac ADD
    for i in range(len(users_mac)):
        for j in range(i+1,len(users_mac)):
            #Create users if first time
            requests.get("http://127.0.0.1:5000/create_user/"+str(users_mac[i]))
            requests.get("http://127.0.0.1:5000/create_user/"+str(users_mac[j]))
            #Create contact
            lien = "http://127.0.0.1:5000/contact/"+str(users_mac[i])+"/"+str(users_mac[j])+"/"+my_position
            requests.get(lien)
    return render_template('index.html')
    

index()

# schedule.every(5).minutes.do(index)
# schedule.every().hour.do(index)
# schedule.every().day.at("10:30").do(index)

# while 1:
#     schedule.run_pending()
#     time.sleep(1)

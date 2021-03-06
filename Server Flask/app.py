#Importation Libraries
from flask import Flask , render_template,url_for,request,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from sqlalchemy import exc
from flask_migrate import Migrate, MigrateCommand
from datetime import datetime,timedelta
import who_is_on_my_wifi
import pythoncom
from apscheduler.schedulers.background import BackgroundScheduler
import itertools
import atexit

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' #Initialize our database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'True' #To track updates in our databases
db = SQLAlchemy(app) #Define the database

#To keep the database updated
migrate =  Migrate(app,db) 
manager = Manager(app)
manager.add_command('db', MigrateCommand)


class User(db.Model):
    uid = db.Column(db.String(255),primary_key=True) #For privacy reason we won't take any informations about the user this is mac add
    CovidPositive = db.Column(db.Boolean, default=False, nullable=False) # Status of user
    warning = db.Column(db.Boolean, default=False, nullable=False) # if he was near to someone who tested positive
    positive_date = db.Column(db.DateTime)
    warning_date = db.Column(db.DateTime) #Last time was near to someone who tested positive
    def __repr__(self):
        return "<User : %r>" %self.uid


class Router(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    position = db.Column(db.String(255), nullable=False) 


class Contact(db.Model):
    id_contact = db.Column(db.Integer, primary_key=True, autoincrement=True)
    origin_user = db.Column(db.Integer, db.ForeignKey('user.uid')) # the current user
    other_user = db.Column(db.Integer, db.ForeignKey('user.uid')) # Users who was in contact with the current user (near to him)
    position = db.Column(db.String(255), nullable=False)
    date = db.Column(db.DateTime) #Date of contact 
    
# class Track_movement(db.Model):
#     user_uid = db.Column(db.Integer, db.ForeignKey('user.uid'), primary_key=True) #The current user
#     position = db.Column(db.String(255), nullable=False) #Type of position (X,Y)
#     date =  db.Column(db.DateTime) #Date of this position

@app.route('/',methods=['POST','GET'])
def index():
    notify_users()
    return render_template('index.html')

@app.route('/create_user/<uid>',methods=['POST','GET'])
def create_user(uid):
    new_user = User(uid=uid,CovidPositive=False)
    try:
        db.session.add(new_user)
        db.session.commit()
        return "The user : %r is created with success" %uid
    except :
        return "ERROR ! : User id : %r already exist" %uid
        
@app.route('/create_router/<id>/<position>/',methods=['POST','GET'])
def create_router(id,position):
    new_router=Router(id=id,position=position)
    try:
        db.session.add(new_router)
        db.session.commit()
        return "The router : %r is successfully created" %id
    except :
        return "ERROR ! :  id router : %r already exist" %id


@app.route('/contact/<main_uid>/<second_uid>/<router_position>',methods=['POST','GET'])
def in_contact(main_uid,second_uid,router_position):
    yesterday = datetime.now() - timedelta(days=1) #Check if we already have a contact in this day no need to create a new one
    if Contact.query.filter_by(origin_user=main_uid).filter_by(other_user=second_uid).first() != None:
        if Contact.query.filter_by(origin_user=main_uid).filter_by(other_user=second_uid).first().date >= yesterday and Contact.query.filter_by(origin_user=main_uid).filter_by(other_user=second_uid).first().position == router_position:
            return "Contact already exist for today"
    new_contact = Contact(origin_user=main_uid,other_user=second_uid,date=datetime.now(),position=router_position) #If not we create a new one for today
    try:
        db.session.add(new_contact)
        db.session.commit()
        return "The contact between user : %r and the user : %r is saved !" %(main_uid,second_uid)
    except exc.SQLAlchemyError as e:
        return e

@app.route('/all_users',methods=['POST','GET'])
def all_users():
    all_users =  User.query.all()
    for user in all_users :
        print(user)
    return "CHeck "

@app.route('/all_contact',methods=['POST','GET'])
def all_contact():
    all_contact = Contact.query.all()
    for contact in all_contact:
        print(contact.origin_user)
        print("In contactt with :")
        print(contact.other_user)
    return "Check Cmd"

def fetch_contact(uid,date):
     #Get the users that were in contact with the current one who tested positive in the last 5 days
    last_5days = date - timedelta(days=5)
    #users_contact = Contact.query.filter_by(origin_user=uid).filter(date >= last_5days).all() #To verify if the date condition work fine
    users_contact = Contact.query.filter((Contact.origin_user==uid) | (Contact.other_user==uid) & (Contact.date >= last_5days)).all()
    return users_contact

@app.route('/covid/<uid>',methods=['POST','GET'])
def covid_pos(uid):
  
    current_user = User.query.filter_by(uid=uid).first() #Get the current user
    if current_user is None:
        create_user(uid)
        current_user = User.query.filter_by(uid=uid).first()
    current_user.CovidPositive = True #Change status to positive
    current_user.positive_date = datetime.now() #Date of test
    db.session.commit() #Update database
    notify_users()
    return {"data" : True } #Return the uid as a list 

@app.route('/covid-neg/<uid>',methods=['POST','GET'])
def covid_neg(uid):
    # !!! You need to check if the used exist cz it throws an error if user not found
    current_user = User.query.filter_by(uid=uid).first() #Get the current user
    if current_user is None:
        create_user(uid)
        current_user = User.query.filter_by(uid=uid).first()
    current_user.CovidPositive = False #Change status to positive
    db.session.commit() #Update database
    return {"data" : True } #Return the uid as a list 


def notify_users():
    #We need to loop over users who have state positive then get the id store it in uid
    positive_users = User.query.filter_by(CovidPositive=True).all()
    for pos_user in positive_users :  
        fetched_contact = fetch_contact(pos_user.uid,datetime.now()) #Get the users who were in contact with the positive one
        for in_contact in fetched_contact: #In this loop we notify
            wanted_user = User.query.filter((User.uid==in_contact.origin_user)).first() #Two time because he may be the origin user or the other one and even if u do or inside one query won't work because she will always get the same users and ignore some
            wanted_user.warning = True
            wanted_user.warning_date = datetime.now()
            db.session.commit()
            wanted_user = User.query.filter(User.uid == in_contact.other_user).first()
            wanted_user.warning = True
            db.session.commit()
            wanted_user.warning_date = datetime.now()
            

@app.route('/warning/<uid>',methods=['POST','GET'])
def warning_pos(uid):
    warning_user = User.query.filter_by(uid=uid).first()
    if warning_user is None:
        return {"data":False}
    if warning_user.CovidPositive :
        return {"data":"Positive"}
    elif warning_user.warning or warning_user.CovidPositive :
        return {"data":True}
    else :
        return {"data":False}

def reset_warnings():
    print("Start reseting warnings")
    time_reset = datetime.now() - timedelta(days=15)
    all_users = User.query.filter_by(warning=True).all()
    for user in all_users :      
        if user.warning_date <= time_reset :
            print(user)
            user.warning = False
            db.session.commit() #Update database

def reset_contact(): #Delete contact every 15days
    print("Start reseting Contact")
    time_reset = datetime.now() - timedelta(days=15)
    all_contacts = Contact.query.all()
    for contact in all_contacts:
        if contact.date <= time_reset:
            db.session.delete(contact)
            print(str(contact)+" Has been deleted")
            db.session.commit()


scheduler = BackgroundScheduler()
scheduler.add_job(func=reset_warnings, trigger="interval", seconds=86400) #Execute the function every 24h to reset the warning for users who were near to someone positive the last 15days
scheduler.add_job(func=reset_contact, trigger="interval", seconds=86400)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown()) 


if __name__ == "__main__":
    app.run(debug=True)
    manager.run() #For migrations

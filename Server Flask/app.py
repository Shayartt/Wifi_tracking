#Importation Libraries
from flask import Flask , render_template,url_for,request,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from sqlalchemy import exc
from flask_migrate import Migrate, MigrateCommand
from datetime import datetime,timedelta
import who_is_on_my_wifi
import pythoncom
import itertools

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
    def __repr__(self):
        return "<User : %r>" %self.uid


class Router(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    position = db.Column(db.String(255), nullable=False) #Khalid try to do something for this position we don't wanna to do it manually with random data


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
    users_contact = Contact.query.filter_by(origin_user=uid).filter(date >= last_5days).all() #To verify if the date condition work fine
    return users_contact

@app.route('/covid/<uid>',methods=['POST','GET'])
def covid_pos(uid):
    current_user = User.query.filter_by(uid=uid).first() #Get the current user
    current_user.CovidPositive = True #Change status to positive
    db.session.commit() #Update database
    users_contact = fetch_contact(uid,datetime.now()) #Look for users who were in contact for the last 5 days
    result_users = []
    for user in users_contact: #Store the uid of fetched users
        result_users.append(user.other_user)
    return str(result_users) #Return the uid as a list 


def notify_users():
    #We need to loop over users who have state positive then get the id store it in uid
    positive_users = User.query.filter_by(covid_pos=True).all()
    for pos_user in positive_users :  
        fetched_contact = fetch_contact(pos_user.uid,datetime.now()) #Get the users who were in contact with the positive one
        for in_contact in fetch_contact: #In this loop we notify
            wanted_user = User.query.filter_by(uid=in_contact.other_user).first()
            wanted_user.warning = True
            db.session.commit()

@app.route('/warning/<uid>',methods=['POST','GET'])
def warning_pos(uid):
    warning_user = User.query.filter_by(uid=uid).first()
    if warning_user.warning :
        return "Be carefull you were near to someone who tested positive stay quarantine !"
    else :
        return "You're safe the last 5 days"


if __name__ == "__main__":
    app.run(debug=True)
    manager.run() #For migrations
    

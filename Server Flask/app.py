#Importation Libraries
from flask import Flask , render_template,url_for,request,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from sqlalchemy import exc
from flask_migrate import Migrate, MigrateCommand
from datetime import datetime,timedelta


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' #Initialize our database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'True' #To track updates in our databases
db = SQLAlchemy(app) #Define the database

#To keep the database updated
migrate =  Migrate(app,db) 
manager = Manager(app)
manager.add_command('db', MigrateCommand)

class User(db.Model):
    uid = db.Column(db.Integer,primary_key=True) #For privacy reason we won't take any informations about the user
    CovidPositive = db.Column(db.Boolean, default=False, nullable=False) #Status of user
    def __repr__(self):
        return "<User : %r>" %self.uid

class Contact(db.Model):
    id_contact = db.Column(db.Integer, primary_key=True, autoincrement=True)
    origin_user = db.Column(db.Integer, db.ForeignKey('user.uid')) # the current user
    other_user = db.Column(db.Integer, db.ForeignKey('user.uid')) # Users who was in contact with the current user (near to him)
    date = db.Column(db.DateTime) #Date of contact 
    
class Track_movement(db.Model):
    user_uid = db.Column(db.Integer, db.ForeignKey('user.uid'), primary_key=True) #The current user
    position = db.Column(db.String(255), nullable=False) #Type of position (X,Y)
    date =  db.Column(db.DateTime) #Date of this position

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

@app.route('/track/<uid>/<pos>',methods=['POST','GET'])
def track_user(uid,pos):
    new_tracked = Track_movement(user_uid=uid,position=str(pos),date=datetime.now())
    try:
        db.session.add(new_tracked)
        db.session.commit()
        return "Movement of user : %r is tracked with success" %uid
    except exc.SQLAlchemyError as e:
        return e

@app.route('/contact/<main_uid>/<second_uid>',methods=['POST','GET'])
def in_contact(main_uid,second_uid):
    new_contact = Contact(origin_user=main_uid,other_user=second_uid,date=datetime.now())
    try:
        db.session.add(new_contact)
        db.session.commit()
        return "The contact between user : %r and the user : %r is saved !" %(main_uid,second_uid)
    except exc.SQLAlchemyError as e:
        return e

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




if __name__ == "__main__":
    app.run(debug=True)
    manager.run() #For migrations
    

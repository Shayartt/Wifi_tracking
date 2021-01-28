#Importation Libraries
from flask import Flask , render_template,url_for,request,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_script import Manager
from sqlalchemy import exc
from flask_migrate import Migrate, MigrateCommand
from datetime import datetime


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///wifitracker.db' #Initialize our database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = 'True' #To track updates in our databases
db = SQLAlchemy(app) #Define the database

#To keep the database updated
migrate =  Migrate(app,db) 
manager = Manager(app)
manager.add_command('db', MigrateCommand)

class User(db.Model):
    uid = db.Column(db.Integer,primary_key=True) #For privacy reason we won't take any informations about the user
    def __repr__(self):
        return "<User : %r>" %self.uid

class Contact(db.Model):
    origin_user = db.Column(db.Integer, db.ForeignKey('user.uid'), primary_key=True) # the current user
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
    new_user = User(uid=uid)
    try:
        db.session.add(new_user)
        db.session.commit()
        return "The user : %r is created with success" %uid
    except :
        return "ERROR ! : User id : %r already exist" %uir

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


if __name__ == "__main__":
    app.run(debug=True)
    manager.run() #For migrations
    

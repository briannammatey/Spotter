from flask import Flask, render_template, request
app = Flask(__name__)

@app.route("/")

def index():
    return render_template("index.html")
@app.route("/create_challenge", methods= ["POST"])
def create_challenge():
    title = request.form.get("title")
    goal = request.form.get("goal")
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")
    description = request.form.get("description")
    privacy = request.form.get("privacy")



    ## okay

    # check if challenge title is a good size
    

    # check if goal str is a good size


    # convert start date and end date to normal format, and check if start date 
    # is less than end date


    #check if description is right size

    # check if all inputs are correct if not, print error message 

    #if all inputs aren't correct print message saying this is all correct
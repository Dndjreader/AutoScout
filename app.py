from cs50 import SQL
from flask import Flask, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
import sys


# Configure application
app = Flask(__name__)


# login in fucntion to ensure session is valid and keeps person logged in until clicks log out
def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/getstarted")
        return f(*args, **kwargs)
    return decorated_function

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = "filesystem"
app.config['SESSION_COOKIE_NAME'] = "currentSession"
# Set the secret key to some random bytes
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
Session(app)

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Database
db = SQL("sqlite:///Players.db")

# error Page
def error(message, code=400):
    """Render message as an error to user."""
    return render_template("error.html", code=code, message=message)

# Formats to Euros
def euro(value):
    """Format value as USD."""
    return f"€{int(float(value)):,}"

# Change figures for value, wage and release clause to Euros
def currency(players):
    for player in players:

        if player['value_eur']:
            value = euro(player['value_eur'])
            player['value'] = value
        else:
            player['value'] = "Unknown"

        try:
            if player['wage_eur']:
                wage = euro(player['wage_eur'])
                player['wage'] = wage
            else:
                player['wage'] = "Unknown"
        except (KeyError):
            pass


        try:
            if player['release_clause_eur']:
                releaseClause = euro(player['release_clause_eur'])
                player['release_clause'] = releaseClause
            else:
                player['release_clause'] = "Unknown"
        except (KeyError):
            pass
    return players

@app.route("/getstarted", methods=["GET", "POST"])
def getStarted():
    """ Getting tarted Page"""
    return render_template("getstarted.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        username = request.form.get("username")
        password = request.form.get("password")

        if not username or not password:
            return error("Please input username and password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return error("Invalid username or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["person_id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting the form correctly)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        team = request.form.get("team-name")

        if not username:
            return error("Please input username", 400)

        # Confirm username not in use
        if db.execute("SELECT username FROM users WHERE username == ?", username):
            return error("Username already in use", 403)

        # Ensure both password fields match
        elif password != confirmation:
            return error("Passwords do not match", 403)

        # Adds information to database
        else:
            hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            db.execute("INSERT INTO users (username, hash, team) VALUES(:username, :hash, :team)", username=username, hash=hash, team=team)
            return render_template("login.html")

    # reached form by GET load page
    else:
        teams = db.execute("SELECT DISTINCT club_name FROM Players ORDER BY league_name DESC, club_name ASC;")
        return render_template("register.html", teams=teams)

@app.route("/", methods=['GET', 'POST'])
@login_required
def index():
    players = db.execute("SELECT sofifa_id, short_name, age, player_positions, player_face_url, nationality_name, nation_flag_url, club_name, club_logo_url, league_name, overall, potential, wage_eur, value_eur FROM Players LIMIT 250;" )
    leagues = db.execute("SELECT DISTINCT league_name FROM Players ORDER BY league_name, league_level DESC;")
    players = currency(players)
    return render_template("index.html", players=players, leagues=leagues)

@app.route("/myteam", methods=['GET', 'POST'])
@login_required
def myteam():
    team = db.execute("SELECT team FROM users WHERE person_id = :person_id;", person_id=session["user_id"])
    teamName = team[0]['team']
    players = db.execute("SELECT sofifa_id, short_name, age, player_positions, player_face_url, nationality_name, nation_flag_url, club_name, club_logo_url, league_name, overall, potential, wage_eur, value_eur FROM Players WHERE club_name = ? LIMIT 250;", teamName )
    players = currency(players)
    clubLogo = players[0]['club_logo_url']
    return render_template("myteam.html", players=players, teamName = teamName, clubLogo = clubLogo)

@app.route("/playerdatabase", methods=['GET', 'POST'])
@login_required
def playerdatabase():  
    sort_by = request.args.get('sort_by')
    asc = request.args.get('asc')
    league = request.args.get('league')
    playerName = request.args.get('player')
    if not sort_by:
        if not league:
            players = db.execute("SELECT sofifa_id, short_name, age, player_positions, player_face_url, nationality_name, nation_flag_url, club_name, club_logo_url, league_name, overall, potential, wage_eur, value_eur FROM Players WHERE value_eur <> '' AND long_name LIKE '%{}%' LIMIT 250;".format(playerName))
        else:
            players = db.execute("SELECT sofifa_id, short_name, age, player_positions, player_face_url, nationality_name, nation_flag_url, club_name, club_logo_url, league_name, overall, potential, wage_eur, value_eur FROM Players WHERE value_eur <> '' AND league_name LIKE '%{}%' AND long_name LIKE '%{}%' LIMIT 250;".format(league, playerName))
    elif sort_by == "name":
        players = db.execute("SELECT sofifa_id, short_name, age, player_positions, player_face_url, nationality_name, nation_flag_url, club_name, club_logo_url, league_name, overall, potential, wage_eur, value_eur FROM Players WHERE value_eur <> '' AND league_name LIKE '%{}%' AND long_name LIKE '%{}%' ORDER BY short_name {} LIMIT 250;".format(league, playerName, asc))
    else:
        players = db.execute("SELECT sofifa_id, short_name, age, player_positions, player_face_url, nationality_name, nation_flag_url, club_name, club_logo_url, league_name, overall, potential, wage_eur, value_eur FROM Players WHERE value_eur <> '' AND league_name LIKE '%{}%' AND long_name LIKE '%{}%' ORDER BY CAST({} AS INTEGER)= 0, CAST({} AS INTEGER) {} LIMIT 250;".format(league, playerName, sort_by, sort_by, asc))
    players = currency(players)
    return jsonify({'players': players})

@app.route("/playerinfo/<player_id>", methods=['GET', 'POST'])
@login_required
def playerinfo(player_id):
    playerInfo = db.execute("SELECT * FROM Players WHERE sofifa_id = ? ;", player_id)
    rating = playerInfo[0]['overall']
    age = playerInfo[0]['age']
    potential = playerInfo[0]['potential']

    if age > 36:
        playerValues = db.execute("SELECT * FROM playerValues WHERE overall = ? AND age = ?", rating, age)
        playerPotential = db.execute("SELECT * FROM playerValues WHERE overall = ? AND age = ?", potential, age)
    else:
        playerValues = db.execute("SELECT * FROM playerValues WHERE overall = ? AND age > ? AND age < 38;", rating, age)
        playerPotential = db.execute("SELECT * FROM playerValues WHERE overall = ? AND age > ? AND age < 38;", potential, age)

    valueChange = []

    for i in range(len(playerValues)):
        current = int(float(playerValues[i]['value_eur']))
        potential = int(float(playerPotential[i]['value_eur']))
        valueChange.append(euro(potential-current))

    playerInfo = currency(playerInfo)
    playerValues = currency(playerValues)
    playerPotential = currency(playerPotential)

    return render_template("playerinfo.html", playerInfo=playerInfo, playerValues=playerValues, playerPotential=playerPotential, valueChange=valueChange, valueLength=range(len(valueChange)))

@app.route("/usercheck", methods=['GET', 'POST'])
def usercheck():  
    username = request.args.get('username')
    if db.execute("SELECT username FROM users WHERE username == ?;", username):
        return "true"
    else:
        return "false"

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/myteamdata", methods=['GET', 'POST'])
@login_required
def myteamdata():  
    team = request.args.get('team')
    sort_by = request.args.get('sort_by')
    asc = request.args.get('asc')
    playerName = request.args.get('player')
    if not sort_by:
        players = db.execute("SELECT sofifa_id, short_name, age, player_positions, player_face_url, nationality_name, nation_flag_url, club_name, club_logo_url, league_name, overall, potential, wage_eur, value_eur FROM Players WHERE value_eur <> '' AND club_name = '{}' AND long_name LIKE '%{}%' LIMIT 250;".format(team, playerName))
    elif sort_by == "name":
        players = db.execute("SELECT sofifa_id, short_name, age, player_positions, player_face_url, nationality_name, nation_flag_url, club_name, club_logo_url, league_name, overall, potential, wage_eur, value_eur FROM Players WHERE value_eur <> '' AND club_name = '{}' AND long_name LIKE '%{}%' ORDER BY short_name {} LIMIT 250;".format(team, playerName, asc))
    else:
        players = db.execute("SELECT sofifa_id, short_name, age, player_positions, player_face_url, nationality_name, nation_flag_url, club_name, club_logo_url, league_name, overall, potential, wage_eur, value_eur FROM Players WHERE value_eur <> '' AND club_name = '{}' AND long_name LIKE '%{}%' ORDER BY CAST({} AS INTEGER)= 0, CAST({} AS INTEGER) {} LIMIT 250;".format(team, playerName, sort_by, sort_by, asc))
    players = currency(players)
    return jsonify({'players': players})

@app.route("/watchlist", methods=['GET', 'POST'])
@login_required
def watchlist():
    players = db.execute("SELECT Players.sofifa_id, Players.short_name, Players.age, Players.player_positions, Players.player_face_url, Players.nationality_name, Players.nation_flag_url, Players.club_name, Players.club_logo_url, Players.league_name, Players.overall, Players.potential, Players.wage_eur, Players.value_eur FROM Players INNER JOIN Watchlist ON Players.sofifa_id = Watchlist.sofifa_id WHERE Watchlist.userid = :person_id;", person_id=session["user_id"])
    leagues = db.execute("SELECT DISTINCT league_name FROM Players ORDER BY league_name, league_level DESC;")
    players = currency(players)
    return render_template("watchlist.html", players=players, leagues=leagues)

@app.route("/addwatchlist", methods=['GET', 'POST'])
@login_required
def addwatchlist():
    playerId = request.args.get('player')
    checkId = db.execute("SELECT sofifa_id FROM Watchlist WHERE sofifa_id = :id AND userid = :userid;", id=playerId, userid=session["user_id"])
    if checkId:
        return "Already In Watchlist"
    else:
        db.execute("INSERT INTO Watchlist (sofifa_id, userid) VALUES(:sofifa_id, :userid);", sofifa_id=playerId, userid=session["user_id"])
        return "Added"

@app.route("/removewatchlist", methods=['GET', 'POST'])
@login_required
def removewatchlist():
    playerId = request.args.get('player')
    db.execute("DELETE FROM Watchlist WHERE sofifa_id = :id AND userid = :person_id;", id=playerId, person_id=session["user_id"])
    players = db.execute("SELECT Players.sofifa_id, Players.short_name, Players.age, Players.player_positions, Players.player_face_url, Players.nationality_name, Players.nation_flag_url, Players.club_name, Players.club_logo_url, Players.league_name, Players.overall, Players.potential, Players.wage_eur, Players.value_eur FROM Players INNER JOIN Watchlist ON Players.sofifa_id = Watchlist.sofifa_id WHERE Watchlist.userid = :person_id;", person_id=session["user_id"])
    players = currency(players)
    return jsonify({'players': players})

@app.route("/watchlistData", methods=['GET', 'POST'])
@login_required
def watchlistData():  
    sort_by = request.args.get('sort_by')
    asc = request.args.get('asc')
    league = request.args.get('league')
    playerName = request.args.get('player')
    if not sort_by:
        if not league:
            players = db.execute("SELECT Players.sofifa_id, Players.short_name, Players.age, Players.player_positions, Players.player_face_url, Players.nationality_name, Players.nation_flag_url, Players.club_name, Players.club_logo_url, Players.league_name, Players.overall, Players.potential, Players.wage_eur, Players.value_eur FROM Players INNER JOIN Watchlist ON Players.sofifa_id = Watchlist.sofifa_id WHERE Watchlist.userid = {} AND Players.value_eur <> '' AND Players.long_name LIKE '%{}%' LIMIT 250;".format(session["user_id"], playerName))
        else:
            players = db.execute("SELECT Players.sofifa_id, Players.short_name, Players.age, Players.player_positions, Players.player_face_url, Players.nationality_name, Players.nation_flag_url, Players.club_name, Players.club_logo_url, Players.league_name, Players.overall, Players.potential, Players.wage_eur, Players.value_eur FROM Players INNER JOIN Watchlist ON Players.sofifa_id = Watchlist.sofifa_id WHERE Watchlist.userid = {} AND Players.value_eur <> '' AND Players.league_name LIKE '%{}%' AND Players.long_name LIKE '%{}%' LIMIT 250;".format(session["user_id"], league, playerName))
    elif sort_by == "name":
        players = db.execute("SELECT Players.sofifa_id, Players.short_name, Players.age, Players.player_positions, Players.player_face_url, Players.nationality_name, Players.nation_flag_url, Players.club_name, Players.club_logo_url, Players.league_name, Players.overall, Players.potential, Players.wage_eur, Players.value_eur FROM Players INNER JOIN Watchlist ON Players.sofifa_id = Watchlist.sofifa_id WHERE Watchlist.userid = {} AND Players.value_eur <> '' AND Players.league_name LIKE '%{}%' AND Players.long_name LIKE '%{}%' ORDER BY Players.short_name {} LIMIT 250;".format(session["user_id"], league, playerName, asc))
    else:
        players = db.execute("SELECT Players.sofifa_id, Players.short_name, Players.age, Players.player_positions, Players.player_face_url, Players.nationality_name, Players.nation_flag_url, Players.club_name, Players.club_logo_url, Players.league_name, Players.overall, Players.potential, Players.wage_eur, Players.value_eur FROM Players INNER JOIN Watchlist ON Players.sofifa_id = Watchlist.sofifa_id WHERE Watchlist.userid = {} AND Players.value_eur <> '' AND Players.league_name LIKE '%{}%' AND Players.long_name LIKE '%{}%' ORDER BY CAST(Players.{} AS INTEGER)= 0, CAST(Players.{} AS INTEGER) {} LIMIT 250;".format(session["user_id"], league, playerName, sort_by, sort_by, asc))
    players = currency(players)
    return jsonify({'players': players})
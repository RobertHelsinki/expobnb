from flask import Flask, render_template, session, url_for,flash, redirect, request
from flask_sqlalchemy import SQLAlchemy
from coincap import coin_price


app = Flask(__name__)
SQLALCHEMY_DATABASE_URI = "mysql://udxc36kd9rouf413:4z7DNLHn2TFZeviMGYDQ@bnd37cggl1pw4zgweiph-mysql.services.clever-cloud.com:3306/bnd37cggl1pw4zgweiph"
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI
app.secret_key = '7311920049'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    inviter = db.Column(db.String(100))
    wallet_config = db.Column(db.String(80), server_default="no")

    def __init__(self, username, password, inviter, wallet_config):

        self.username = username
        self.password = password
        self.inviter = inviter
        self.wallet_config = wallet_config


class Wallets(db.Model):
    id_user = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(100))
    token = db.Column(db.String(100))
    address = db.Column(db.String(120))
    balance = db.Column(db.String(70), server_default='0')
    staked = db.Column(db.String(70), server_default='0')
    reward = db.Column(db.String(70), server_default='0')

    def __init__(self, username, token, address, balance,staked,reward):

        self.username = username
        self.token = token
        self.address = address
        self.balance = balance
        self.staked = staked
        self.reward = reward


class Withdrawals(db.Model):
    id = db.Column(db.Integer, autoincrement=True)
    username = db.Column(db.String(100), unique=True, primary_key=True)
    token = db.Column(db.String(100))
    amount = id = db.Column(db.String(100))

    def __init__(self, username, token, amount):

        self.username = username
        self.token = token
        self.amount = amount


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/profit')
def profits():
    return render_template('profit.html')


@app.route('/join')
def join():
    return render_template('join.html')


@app.route('/no_wallet')
def nowallet():
    return render_template('no_wallet.html')


@app.route('/wallet_add', methods=['GET','POST'])
def wallet_add():
    if 'USER' in session:
        if request.method == "POST":
            wallet_address = request.form['address']
            token = request.form['token']
            username = session.get('USER')

            ch_user = User.query.filter_by(username=username).first()
            ch_data = Wallets.query.filter_by(username=username).first()
            if ch_data and ch_data.token == token:
                ch_data.address = wallet_address
                ch_user.wallet_config = "yes"
                db.session.commit()

            else:
                new_data = Wallets(username, token, wallet_address, '0', '0', '0')
                db.session.add(new_data)
                ch_user.wallet_config = "yes"
                db.session.commit()
            token=token.upper()
            flash("{} Address set successfully".format(token))
            return redirect(url_for('wallet_add'))


        else:
            return render_template('wallet_add.html')
    else:
        flash("Login to continue")
        return redirect(url_for('join'))


@app.route('/dashboard')
def dashboard():
    if 'USER' in session:
        username = session.get('USER')
        ch_user = User.query.filter_by(username=username).first()
        wallet_status = ch_user.wallet_config
        if wallet_status == "no":
            return redirect(url_for('nowallet'))
        else:
            bnb_balance = Wallets.query.filter_by(username=username, token='bnb').first()
            doge_balance = Wallets.query.filter_by(username=username, token='doge').first()
            trx_balance = Wallets.query.filter_by(username=username, token='trx').first()
            bnb_amnt = float(bnb_balance.balance)*coin_price('binance-coin')
            doge_amnt = float(doge_balance.balance) * coin_price('dogecoin')
            trx_amnt = float(trx_balance.balance) * coin_price('tron')

            total_amnt = bnb_amnt + doge_amnt + trx_amnt
            total_amnt = round(total_amnt,2)
            token_balance = [bnb_balance.balance,doge_balance.balance,trx_balance.balance]
            print(token_balance)
            return render_template('dashboard.html', data_dict=token_balance,usd_balance=total_amnt)
    else:
        flash("Login to continue")
        return redirect(url_for('join'))

@app.route('/deposit')
def deposit():
    if 'USER' in session:
        return render_template('deposit.html')
    else:
        flash("Login to continue")
        return redirect(url_for('join'))


@app.route('/stake', methods=['GET','POST'])
def stake():
    if 'USER' in session:
        username = session.get('USER')
        if request.method == 'POST':
            token = request.form['token']
            stake_amount = request.form['amount']

            ch_wallets = Wallets.query.filter_by(username=username, token=token).first()

            stake_init = eval(ch_wallets.staked)
            balance_init = eval(ch_wallets.balance)
            if balance_init < eval(stake_amount):
                flash("Insufficient Balance")
                return redirect(url_for('stake'))
            else:
                stake_init += eval(stake_amount)
                balance_init -= eval(stake_amount)

                stake_init = str(stake_init)
                balance_init = str(balance_init)

                ch_wallets.staked = stake_init
                ch_wallets.balance = balance_init
                db.session.commit()
                flash("{} {} staked successfully.Reward after 24Hrs".format(stake_amount,token))
                return redirect(url_for('stake'))
        else:
            bnb_balance = Wallets.query.filter_by(username=username, token='bnb').first()
            doge_balance = Wallets.query.filter_by(username=username, token='doge').first()
            trx_balance = Wallets.query.filter_by(username=username, token='trx').first()

            bnblist = [eval(bnb_balance.balance),eval(bnb_balance.staked),eval(bnb_balance.reward),round((eval(bnb_balance.staked)*0.062),5)]
            dogelist = [eval(doge_balance.balance), eval(doge_balance.staked), eval(doge_balance.reward),round((eval(doge_balance.staked)*0.0745),5)]
            trxlist = [eval(trx_balance.balance), eval(trx_balance.staked), eval(trx_balance.reward),round((eval(bnb_balance.staked)*0.0826),5)]

            return render_template('stake.html',bnblist=bnblist,dogelist=dogelist,trxlist=trxlist)
    else:
        flash("Login to continue")
        return redirect(url_for('join'))


@app.route('/withdraw',methods=['GET','POST'])
def withdraw():
    if 'USER' in session:

        if request.method == 'POST':
            username = session.get("USER")
            token = request.form['token']
            amount = request.form['amount']

            ch_wallets = Wallets.query.filter_by(username=username, token=token).first()
            max_amt = eval(ch_wallets.reward)

            if eval(amount)>max_amt:
                flash("Insufficient earnings.")
                return redirect(url_for('withdraw'))
            else:
                new_data = Withdrawals(username, token, amount)
                db.session.add(new_data)
                db.session.commit()
                flash("Withdrawal request processed")
                return redirect(url_for('withdraw'))
        else:
            return render_template('withdrawal.html')
    else:
        flash("Login to continue")
        return redirect(url_for('join'))

@app.route('/register', methods=["POST"])
def register():

    username = request.form["username"]
    password = request.form["password"]
    inviter = request.form["inviter"]

    ch_user = User.query.filter_by(username=username).first()
    ch_inviter = User.query.filter_by(username=inviter).first()

    if ch_user:
        flash("Username Already exists.")
    else:
        if ch_inviter:
            new_data = User(username, password, inviter, "no")
            db.session.add(new_data)
            db.session.commit()

            flash("Account Created Successful")
            return redirect(url_for('join'))

        elif not ch_inviter:
            flash("Invite does not exist")
            return redirect(url_for('join'))

        else:
            flash("Contact Admin")
            return redirect(url_for('join'))
@app.route('/login',methods=["POST"])
def login():
    username = request.form['username']
    password = request.form['password']

    ch_user = User.query.filter_by(username=username).first()

    if ch_user:
        username = ch_user.username
        passwd = ch_user.password
        wallet_config = ch_user.wallet_config
        if passwd == password:
            session['USER'] = username
            if wallet_config == "no":
                return redirect(url_for('nowallet'))
            else:
                return redirect(url_for('dashboard'))
        else:
            flash("Wrong Username or password")
            return redirect(url_for('join'))
    else:
        flash("Wrong Username or password")
        return redirect(url_for('join'))

@app.route('/logout')
def logout():
    session.pop('USER', None)
    return redirect(url_for('join'))


if __name__ == '__main__':
    app.run(debug=True,host='192.168.1.8')

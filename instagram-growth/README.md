# Instagram Growth (Flask + MySQL)

Order-management website for follower growth plans: public plans/order/tracking pages and a protected admin panel.
It does **not** collect Instagram passwords, take payments, or deliver followers. Fulfilment and payment
verification are done by you, and the admin panel records them (Completed / Paid are set manually).

## 1. Install Python
Install Python 3.10+ from https://www.python.org/downloads/ (tick "Add Python to PATH" on Windows). Check: `python --version`.

## 2. Install and configure MySQL
Install MySQL Community Server 8+ (https://dev.mysql.com/downloads/mysql/), set a root password, and make sure the service is running.

## 3. Create the database
```
mysql -u root -p < database/schema.sql
```
or inside the MySQL shell: `CREATE DATABASE instagram_growth_db CHARACTER SET utf8mb4;`
(The app creates the tables and default plans automatically on first start.)

## 4. Configure `.env`
Edit `.env` (a random `SECRET_KEY` is already set) and fill in `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`,
plus `CONTACT_EMAIL` / `CONTACT_PHONE`. Use `.env.example` as the reference. Set `FLASK_DEBUG=0` and
`SESSION_COOKIE_SECURE=1` (HTTPS) in production.

## 5. Install dependencies and run
```
python -m venv venv
venv\Scripts\activate          # Windows   (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
flask --app app run            # or: python app.py
```
(Direct install: `pip install flask flask-sqlalchemy flask-login pymysql python-dotenv flask-wtf cryptography`)

## 6. Open the site
http://127.0.0.1:5000 - admin at http://127.0.0.1:5000/admin/login

## 7. Create the first admin
```
flask --app app create-admin
```
Enter a username and a password (8+ characters). Running it again for the same username resets that password.

## Production notes
Serve with gunicorn/waitress behind HTTPS, keep `.env` out of version control, and add rate limiting
(e.g. Flask-Limiter with Redis) - the built-in login throttle is per-process only. Add a payment gateway
(e.g. Razorpay) if you want automatic payment verification; today "Paid" is set manually by an admin.
Review Instagram's/Meta's Terms of Use for how growth services may be offered.

# Deploying Instagram Growth on Render

This guide walks you through deploying the Instagram Growth application to [Render](https://render.com).

The project is preconfigured with:
- `render.yaml` for 1-click Blueprint deployment (provisions web app + PostgreSQL database automatically)
- `gunicorn` production WSGI server
- Support for PostgreSQL (native to Render), MySQL, and SQLite
- Automatic database table creation and plan seeding on first startup
- Automatic initial admin user creation via `ADMIN_USERNAME` and `ADMIN_PASSWORD` environment variables

---

## Method 1: Deploy with Render Blueprint (Recommended - 1 Click)

1. **Sign up or log in** to [dashboard.render.com](https://dashboard.render.com).
2. Click the **New +** button in the top navigation bar and select **Blueprint**.
3. Connect your GitHub repository:
   `https://github.com/rustammansuri1117/instagram-follower-tool`
4. Render will detect `render.yaml` and show:
   - **instagram-growth** (Web Service, Python, Gunicorn)
   - **instagram-growth-db** (Free PostgreSQL Database)
5. Under Environment Variables:
   - Enter your desired **`ADMIN_USERNAME`** (e.g., `admin`).
   - Enter your desired **`ADMIN_PASSWORD`** (at least 8 characters).
   - Enter **`CONTACT_EMAIL`** and **`CONTACT_PHONE`**.
   - `SECRET_KEY` and `DATABASE_URL` are generated and linked automatically.
6. Click **Apply**.
7. Render will build the web service and provision the database. In 2-3 minutes, your application will be live at `https://<service-name>.onrender.com`.

---

## Method 2: Manual Setup on Render Dashboard

If you prefer to configure the Web Service and Database manually:

### Step 1: Create the Database
1. Go to [dashboard.render.com](https://dashboard.render.com).
2. Click **New +** -> **PostgreSQL**.
3. Fill in:
   - **Name**: `instagram-growth-db`
   - **Database**: `instagram_growth`
   - **User**: `ig_user`
   - **Plan**: `Free`
4. Click **Create Database**.
5. Once created, scroll down to **Connections** and copy the **Internal Database URL** (`postgres://...`).

### Step 2: Create the Web Service
1. In Render Dashboard, click **New +** -> **Web Service**.
2. Select your repository: `instagram-follower-tool`.
3. Configure settings:
   - **Name**: `instagram-growth`
   - **Root Directory**: `instagram-growth`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: `Free`
4. Scroll down to **Environment Variables** and add:
   - `DATABASE_URL`: (Paste the **Internal Database URL** from Step 1)
   - `SECRET_KEY`: (Click *Generate* or enter a random string)
   - `ADMIN_USERNAME`: `admin`
   - `ADMIN_PASSWORD`: (Your secure admin password - minimum 8 characters)
   - `FLASK_DEBUG`: `0`
   - `SESSION_COOKIE_SECURE`: `1`
   - `CONTACT_EMAIL`: `support@example.com`
   - `CONTACT_PHONE`: `+91 00000 00000`
5. Click **Create Web Service**.

---

## Accessing Your Application

- **Public Website**: `https://<your-service-name>.onrender.com`
- **Admin Dashboard**: `https://<your-service-name>.onrender.com/admin/login`
  - Log in with the credentials set in `ADMIN_USERNAME` and `ADMIN_PASSWORD`.

---

## Creating / Resetting Admin from Render Shell (Alternative)

If you did not set `ADMIN_USERNAME` and `ADMIN_PASSWORD` in the environment variables, you can create or reset the admin anytime:
1. In the Render Dashboard, open your `instagram-growth` web service.
2. Click the **Shell** tab on the left.
3. Run:
   ```bash
   flask --app app create-admin
   ```
4. Enter the username and password when prompted.

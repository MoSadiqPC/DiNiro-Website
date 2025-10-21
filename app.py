from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from functools import wraps # Required for decorators
# from flask_cors import CORS # Keep commented out
import sqlite3
import os
import json
import datetime # لإضافة الوقت والتاريخ
from datetime import timezone # Required for timezone-aware comparison

# --- Absolute Path Settings ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.path.join(BASE_DIR, 'database.db')
UPLOAD_FOLDER_PATH = os.path.join(BASE_DIR, 'static')
SETTINGS_FILE_PATH = os.path.join(BASE_DIR, 'settings.json')

app = Flask(__name__)
# CORS(app, supports_credentials=True) # Not needed now
app.secret_key = os.urandom(24) # Required for sessions & Flask-Login
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER_PATH
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=7) # Keep session for 7 days
IQD_RATE = 1460 # (You can adjust this later)

# --- Flask-Login Setup for Regular Users ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login_selection" # Redirect page if user isn't logged in
login_manager.login_message = "login_required_message" # Key for translation
login_manager.login_message_category = "info"

# --- User Model for Flask-Login ---
class User(UserMixin):
    def __init__(self, id, username, email=None): # Made email optional here too
        self.id = id
        self.username = username
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    user_data = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    if user_data:
        # Use direct indexing for email
        return User(id=user_data['id'], username=user_data['username'], email=user_data['email'])
    return None

# --- Translation System ---
TRANSLATIONS = {
    'en': { 'home': 'Home', 'shop': 'Shop', 'free_games': 'Free Games', 'contact_us': 'Contact Us', 'sign_in': 'SIGN IN', 'dashboard': 'Dashboard', 'manage_admins': 'Manage Admins', 'logout': 'Logout', 'welcome': 'Welcome', 'add_new_game': 'Add New Game', 'shop_games': 'Shop Games', 'new_orders': 'New Purchase Orders', 'free_games_title': 'Free Games', 'customer_name': 'Customer Name', 'phone': 'Phone', 'game': 'Game', 'date': 'Date', 'actions': 'Actions', 'price': 'Price', 'edit': 'Edit', 'delete': 'Delete', 'order_form': 'Order Form', 'your_name': 'Your Full Name', 'your_phone': 'Your Phone Number', 'order_notice': 'We will contact you via phone to complete the purchase process.', 'place_order': 'Confirm Order', 'order_success_title': 'Order Received', 'order_success_msg': 'Thank you! Your order has been received successfully. We will contact you soon.', 'back_to_shop': 'Back to Shop', 'buy_now': 'Buy Now', 'get_now': 'Get Now', 'admin_login': 'Admin Login', 'no_new_orders': 'There are no new orders.', 'no_paid_games': 'No games have been added to the shop yet.', 'edit_index': 'Edit Home Page', 'view_messages': 'View Messages', 'no_free_games': 'No free games have been added yet.', 'admin_profile': 'Admin Profile', 'update_profile': 'Update Profile', 'change_password': 'Change Password', 'new_password': 'New Password', 'current_password': 'Current Password', 'admin_logs': 'Admin Activity Logs', 'username': 'Username', 'password': 'Password', 'is_free_game': 'Is Free Game?', 'game_name': 'Game Name', 'description': 'Description', 'category': 'Category', 'game_image': 'Game Image', 'game_username': 'Game Username (Optional)', 'game_password': 'Game Password (Optional)', 'add_game_btn': 'Add Game', 'back_to_dashboard': 'Back to Dashboard', 'update_game_btn': 'Update Game', 'send_message': 'Send Message', 'get_in': 'Get In', 'touch': 'Touch', 'your_email': 'Your Email', 'message': 'Message', 'all_rights_reserved': 'All Rights Reserved.', 'change_your_password': 'Change Your Password', 'update_password': 'Update Password', 'add_new_admin': 'Add New Admin', 'add_admin_btn': 'Add Admin', 'current_admins': 'Current Admins', 'you': 'You', 'login': 'Login', 'our': 'Our', 'games': 'Games', 'your_next': 'Your Next', 'adventure': 'Adventure', 'awaits': 'Awaits', 'premium_hub': 'The premium hub for exclusive game accounts.', 'login_options': 'Login', 'login_admin': 'Admin Login', 'logout_user': 'Logout', 'register': 'Register', 'user_login_title': 'User Login', 'user_register_title': 'Create New Account', 'username_or_email': 'Username or Email', 'confirm_password': 'Confirm Password', 'account_exists': 'Already have an account?', 'no_account': "Don't have an account?", 'passwords_no_match': 'Passwords do not match!', 'registration_success': 'Account created successfully! Please log in.', 'login_failed': 'Incorrect username or password.', 'login_required_message': 'Please log in to access this page.', 'back_to_options': 'Back to Login Options', 'registered_users': 'Registered Users', 'registration_date': 'Registration Date', 'admins_list': 'Admins List', 'role': 'Role', 'status': 'Status', 'online': 'Online', 'offline': 'Offline', 'last_seen': 'Last Seen', 'login_success': 'Logged in successfully!', 'send_us_message': 'Send us your message below.', 'login_to_contact': 'Please log in or register to send us a message.', 'optional': 'Optional', 'phone_whatsapp_note': 'Please ensure this number is reachable via call or WhatsApp.', 'password_security_note': 'Use a strong password different from your Google account.', 'phone_required': 'Phone number is required.', 'search': 'Search', 'sort_by': 'Sort By', 'name_asc': 'Name (A-Z)', 'name_desc': 'Name (Z-A)', 'price_asc': 'Price (Low to High)', 'price_desc': 'Price (High to Low)', 'default': 'Default', 'game_type': 'Product Type', 'platform': 'Platform', 'account': 'Account', 'game_code': 'Game/Code', 'steam': 'Steam', 'epic': 'Epic Games', 'xbox': 'Xbox', 'playstation': 'PlayStation', 'other': 'Other' },
    'ar': { 'home': 'الرئيسية', 'shop': 'المتجر', 'free_games': 'ألعاب مجانية', 'contact_us': 'تواصل معنا', 'sign_in': 'تسجيل الدخول', 'dashboard': 'لوحة التحكم', 'manage_admins': 'إدارة المشرفين', 'logout': 'تسجيل الخروج', 'welcome': 'أهلاً بك', 'add_new_game': 'إضافة لعبة جديدة', 'shop_games': 'ألعاب المتجر', 'new_orders': 'طلبات الشراء الجديدة', 'free_games_title': 'الألعاب المجانية', 'customer_name': 'اسم الزبون', 'phone': 'رقم الهاتف', 'game': 'اللعبة', 'date': 'التاريخ', 'actions': 'الإجراءات', 'price': 'السعر', 'edit': 'تعديل', 'delete': 'حذف', 'order_form': 'نموذج الطلب', 'your_name': 'اسمك الكامل', 'your_phone': 'رقم هاتفك', 'order_notice': 'سنتواصل معك عبر الهاتف لإكمال عملية الشراء.', 'place_order': 'تأكيد الطلب', 'order_success_title': 'تم استلام الطلب', 'order_success_msg': 'شكراً لك! لقد تم استلام طلبك بنجاح. سنتواصل معك قريباً.', 'back_to_shop': 'العودة للمتجر', 'buy_now': 'شراء الآن', 'get_now': 'احصل عليها الآن', 'admin_login': 'دخول المشرفين', 'no_new_orders': 'لا توجد طلبات شراء جديدة.', 'no_paid_games': 'لم تتم إضافة أي ألعاب للمتجر بعد.', 'edit_index': 'تعديل الصفحة الرئيسية', 'view_messages': 'عرض الرسائل', 'no_free_games': 'لم تتم إضافة أي ألعاب مجانية بعد.', 'admin_profile': 'الملف الشخصي للمشرف', 'update_profile': 'تحديث الملف الشخصي', 'change_password': 'تغيير كلمة المرور', 'new_password': 'كلمة المرور الجديدة', 'current_password': 'كلمة المرور الحالية', 'admin_logs': 'سجل نشاط المشرفين', 'username': 'اسم المستخدم', 'password': 'كلمة المرور', 'is_free_game': 'هل اللعبة مجانية؟', 'game_name': 'اسم اللعبة', 'description': 'الوصف', 'category': 'الفئة', 'game_image': 'صورة اللعبة', 'game_username': 'اسم مستخدم اللعبة (اختياري)', 'game_password': 'كلمة مرور اللعبة (اختياري)', 'add_game_btn': 'إضافة لعبة', 'back_to_dashboard': 'العودة للوحة التحكم', 'update_game_btn': 'تحديث اللعبة', 'send_message': 'إرسال الرسالة', 'get_in': 'ابقى على', 'touch': 'تواصل', 'your_email': 'بريدك الإلكتروني', 'message': 'الرسالة', 'all_rights_reserved': 'كل الحقوق محفوظة.', 'change_your_password': 'تغيير كلمة المرور الخاصة بك', 'update_password': 'تحديث كلمة المرور', 'add_new_admin': 'إضافة مشرف جديد', 'add_admin_btn': 'إضافة مشرف', 'current_admins': 'المشرفون الحاليون', 'you': 'أنت', 'login': 'دخول', 'our': 'ألعابنا', 'games': 'الرئيسية', 'your_next': 'مغامرتك', 'adventure': 'القادمة', 'awaits': 'بانتظارك', 'premium_hub': 'المركز المميز لحسابات الألعاب الحصرية.', 'login_options': 'دخول', 'login_admin': 'دخول المشرف', 'logout_user': 'تسجيل الخروج', 'register': 'تسجيل', 'user_login_title': 'دخول المستخدم', 'user_register_title': 'إنشاء حساب جديد', 'username_or_email': 'اسم المستخدم أو البريد', 'confirm_password': 'تأكيد كلمة المرور', 'account_exists': 'لديك حساب بالفعل؟', 'no_account': 'ليس لديك حساب؟', 'passwords_no_match': 'كلمتا المرور غير متطابقتين!', 'registration_success': 'تم إنشاء الحساب بنجاح! يرجى تسجيل الدخول.', 'login_failed': 'اسم المستخدم أو كلمة المرور غير صحيحة.', 'login_required_message': 'يرجى تسجيل الدخول للوصول لهذه الصفحة.', 'back_to_options': 'العودة لخيارات الدخول', 'registered_users': 'المستخدمون المسجلون', 'registration_date': 'تاريخ التسجيل', 'admins_list': 'قائمة المشرفين', 'role': 'الدور', 'status': 'الحالة', 'online': 'متصل', 'offline': 'غير متصل', 'last_seen': 'آخر ظهور', 'login_success': 'تم تسجيل الدخول بنجاح!', 'send_us_message': 'أرسل لنا رسالتك أدناه.', 'login_to_contact': 'يرجى تسجيل الدخول أو إنشاء حساب لإرسال رسالة.', 'optional': 'اختياري', 'phone_whatsapp_note': 'يرجى التأكد من أن هذا الرقم متاح للمكالمات أو واتساب.', 'password_security_note': 'استخدم كلمة مرور قوية مختلفة عن حسابك في جوجل.', 'phone_required': 'رقم الهاتف مطلوب.', 'search': 'بحث', 'sort_by': 'ترتيب حسب', 'name_asc': 'الاسم (أ-ي)', 'name_desc': 'الاسم (ي-أ)', 'price_asc': 'السعر (منخفض للأعلى)', 'price_desc': 'السعر (مرتفع للأقل)', 'default': 'افتراضي', 'game_type': 'نوع المنتج', 'platform': 'المنصة', 'account': 'حساب', 'game_code': 'لعبة/كود', 'steam': 'ستيم', 'epic': 'إبيك غيمز', 'xbox': 'إكس بوكس', 'playstation': 'بلايستيشن', 'other': 'أخرى' }
}

# --- Helper Functions ---
@app.context_processor
def inject_global_vars():
    lang = session.get('language', 'en')
    unread_count = 0
    is_super_admin = False
    if 'admin_id' in session:
        try:
            conn = get_db_connection()
            count_cursor = conn.execute("SELECT COUNT(id) FROM messages WHERE is_read = 0")
            result = count_cursor.fetchone()
            if result: unread_count = result[0]
            admin_cursor = conn.execute("SELECT role FROM admins WHERE id = ?", (session['admin_id'],))
            admin_role = admin_cursor.fetchone()
            if admin_role and admin_role['role'] == 'super_admin':
                is_super_admin = True
            conn.close()
        except Exception as e:
            print(f"Error in context processor: {e}")
            unread_count = 0
            is_super_admin = False

    def get_text(key):
        return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)

    return dict(get_text=get_text, currency=session.get('currency', 'USD'), IQD_RATE=IQD_RATE, endpoint=request.endpoint, unread_count=unread_count, is_super_admin=is_super_admin, current_user=current_user)

def get_db_connection():
    conn = sqlite3.connect(DATABASE_PATH, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    conn.row_factory = sqlite3.Row
    return conn

def get_index_settings():
    try:
        with open(SETTINGS_FILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {'title_part1': 'YOUR NEXT', 'title_part2': 'ADVENTURE', 'title_part3': 'AWAITS', 'subtitle': 'The premium hub...', 'discount': '70'}

# --- Database Initialization ---
def init_db():
    with get_db_connection() as conn:
        # --- Games Table ---
        conn.execute('''CREATE TABLE IF NOT EXISTS games (
                            id INTEGER PRIMARY KEY,
                            name TEXT NOT NULL,
                            description TEXT,
                            price REAL NOT NULL,
                            category TEXT,
                            image_filename TEXT,
                            is_free BOOLEAN NOT NULL DEFAULT 0,
                            game_username TEXT,
                            game_password TEXT,
                            game_type TEXT DEFAULT 'game_code', -- Added
                            platform TEXT DEFAULT 'other'     -- Added
                        );''')
        # Add columns if they don't exist (for existing databases)
        try: conn.execute('ALTER TABLE games ADD COLUMN game_type TEXT DEFAULT "game_code"')
        except: pass
        try: conn.execute('ALTER TABLE games ADD COLUMN platform TEXT DEFAULT "other"')
        except: pass

        # --- Admins Table ---
        try: conn.execute('ALTER TABLE admins ADD COLUMN role TEXT NOT NULL DEFAULT "admin"')
        except: pass
        try: conn.execute('ALTER TABLE admins ADD COLUMN last_seen TIMESTAMP')
        except: pass
        conn.execute('CREATE TABLE IF NOT EXISTS admins (id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, password TEXT NOT NULL, role TEXT NOT NULL DEFAULT "admin", last_seen TIMESTAMP);')

        # --- Orders Table ---
        conn.execute('CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT NOT NULL, customer_phone TEXT NOT NULL, game_id INTEGER NOT NULL, game_name TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);')

        # --- Messages Table ---
        conn.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL, message TEXT NOT NULL, is_read BOOLEAN NOT NULL DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);')

        # --- Admin Logs Table ---
        conn.execute('CREATE TABLE IF NOT EXISTS admin_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, admin_id INTEGER NOT NULL, admin_username TEXT NOT NULL, action TEXT NOT NULL, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (admin_id) REFERENCES admins (id));')

        # --- Users Table ---
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                email TEXT UNIQUE,
                phone TEXT, -- Added phone field
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        try: conn.execute('ALTER TABLE users ADD COLUMN phone TEXT')
        except: pass

        # --- Create Super Admin if not exists ---
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE username = ?", ('admin',))
        if not cursor.fetchone():
            hashed_password = generate_password_hash('admin123', method='pbkdf2:sha256')
            conn.execute("INSERT INTO admins (username, password, role) VALUES (?, ?, ?)", ('admin', hashed_password, 'super_admin'))
            conn.commit()
init_db()

# --- Admin Activity Logging ---
def log_admin_activity(admin_id, admin_username, action):
    try:
        with get_db_connection() as conn:
            conn.execute("INSERT INTO admin_logs (admin_id, admin_username, action) VALUES (?, ?, ?)",
                         (admin_id, admin_username, action))
            conn.commit()
    except Exception as e:
        print(f"Error logging activity: {e}")

# --- Update Admin Last Seen Timestamp ---
@app.before_request
def update_last_seen():
    if 'admin_id' in session:
        admin_id = session['admin_id']
        now = datetime.datetime.now(timezone.utc)
        try:
            with get_db_connection() as conn:
                conn.execute("UPDATE admins SET last_seen = ? WHERE id = ?", (now, admin_id))
                conn.commit()
        except Exception as e:
            print(f"Error updating last_seen for admin {admin_id}: {e}")

# --- Decorators for access control ---
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session:
            lang = session.get('language', 'en')
            login_message = TRANSLATIONS.get(lang, TRANSLATIONS['en']).get('login_required_message', 'Please log in to access this page.')
            flash(login_message, 'info')
            return redirect(url_for('login_selection'))
        return f(*args, **kwargs)
    return decorated_function

def super_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session or session.get('role') != 'super_admin':
            flash("You do not have permission to access this page.", "error")
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

# --- Public Routes ---
@app.route('/')
def index():
    settings = get_index_settings()
    return render_template('index.html', settings=settings)

@app.route('/shop')
def shop():
    search_query = request.args.get('search', '')
    sort_option = request.args.get('sort', 'default')
    query = "SELECT * FROM games WHERE is_free = 0"
    params = []
    if search_query:
        query += " AND name LIKE ?"
        params.append(f'%{search_query}%')
    if sort_option == 'price_asc': query += " ORDER BY price ASC"
    elif sort_option == 'price_desc': query += " ORDER BY price DESC"
    elif sort_option == 'name_asc': query += " ORDER BY name ASC"
    elif sort_option == 'name_desc': query += " ORDER BY name DESC"
    else: query += " ORDER BY id DESC"
    conn = get_db_connection()
    games = conn.execute(query, params).fetchall()
    conn.close()
    return render_template('shop.html', games=games, search_query=search_query, sort_option=sort_option)

@app.route('/free-games')
def free_games():
    search_query = request.args.get('search', '')
    sort_option = request.args.get('sort', 'default')
    query = "SELECT * FROM games WHERE is_free = 1"
    params = []
    if search_query:
        query += " AND name LIKE ?"
        params.append(f'%{search_query}%')
    if sort_option == 'name_asc': query += " ORDER BY name ASC"
    elif sort_option == 'name_desc': query += " ORDER BY name DESC"
    else: query += " ORDER BY id DESC"
    conn = get_db_connection()
    games = conn.execute(query, params).fetchall()
    conn.close()
    return render_template('free-games.html', games=games, search_query=search_query, sort_option=sort_option)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash(get_text('login_required_message'), 'info')
            return redirect(url_for('login_selection'))
        message_content = request.form['message']
        user_name = current_user.username
        user_email = current_user.email
        if not user_email: user_email = "Not Provided"
        with get_db_connection() as conn:
            conn.execute("INSERT INTO messages (name, email, message) VALUES (?, ?, ?)", (user_name, user_email, message_content))
            conn.commit()
        flash("Your message has been sent successfully!", "success")
        return redirect(url_for('contact'))
    return render_template('contact.html')

@app.route('/order/<int:game_id>', methods=['GET', 'POST'])
@login_required # <-- Require user login
def order_form(game_id):
    conn = get_db_connection()
    game = conn.execute("SELECT * FROM games WHERE id = ? AND is_free = 0", (game_id,)).fetchone()
    if game is None:
        conn.close()
        flash("This game is not available for purchase.", "error")
        return redirect(url_for('shop'))
    if request.method == 'POST':
        customer_name = request.form['customer_name']
        customer_phone = request.form['customer_phone']
        with get_db_connection() as conn_post:
            conn_post.execute("INSERT INTO orders (customer_name, customer_phone, game_id, game_name) VALUES (?, ?, ?, ?)", (customer_name, customer_phone, game_id, game['name']))
            conn_post.commit()
        return redirect(url_for('order_success'))
    conn.close()
    return render_template('order-form.html', game=game)

@app.route('/order-success')
def order_success():
    return render_template('order-success.html')

@app.route('/reveal/<int:game_id>')
def reveal_credentials(game_id):
    conn = get_db_connection()
    game = conn.execute("SELECT * FROM games WHERE id = ? AND is_free = 1", (game_id,)).fetchone()
    conn.close()
    if game is None:
        flash("Sorry, this free game is not available.", "error")
        return redirect(url_for('free_games'))
    return render_template('reveal-credentials.html', game=game)

# --- Login Selection Page ---
@app.route('/login-selection')
def login_selection():
    if current_user.is_authenticated: return redirect(url_for('index'))
    if 'admin_id' in session: return redirect(url_for('dashboard'))
    return render_template('login_selection.html')

# --- User Login and Registration Routes ---
@app.route('/user-login', methods=['GET', 'POST'])
def user_login_route():
    if current_user.is_authenticated: return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username_or_email']
        password = request.form['password']
        conn = get_db_connection()
        user_data = conn.execute('SELECT * FROM users WHERE username = ? OR email = ?', (username, username)).fetchone()
        conn.close()
        if user_data and check_password_hash(user_data['password'], password):
            user_obj = User(id=user_data['id'], username=user_data['username'], email=user_data['email'])
            login_user(user_obj)
            flash(TRANSLATIONS.get(session.get('language', 'en'), TRANSLATIONS['en']).get('login_success', 'Logged in successfully!'), 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('index'))
        else:
            flash(TRANSLATIONS.get(session.get('language', 'en'), TRANSLATIONS['en']).get('login_failed', 'Incorrect username or password.'), 'error')
            return render_template('user_login.html')
    return render_template('user_login.html')

@app.route('/user-register', methods=['GET', 'POST'])
def user_register_route():
    if current_user.is_authenticated: return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        email = request.form.get('email') or None
        phone = request.form.get('phone')

        lang = session.get('language', 'en')

        if password != confirm_password:
            flash(TRANSLATIONS.get(lang, TRANSLATIONS['en']).get('passwords_no_match', 'Passwords do not match!'), 'error')
            return render_template('user_register.html')
        
        if not phone:
             flash(get_text('phone_required'), 'error')
             return render_template('user_register.html')

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password, email, phone) VALUES (?, ?, ?, ?)',
                         (username, hashed_password, email, phone))
            conn.commit()
            conn.close()
            flash(TRANSLATIONS.get(lang, TRANSLATIONS['en']).get('registration_success', 'Account created successfully! Please log in.'), 'success')
            return redirect(url_for('user_login_route'))
        except sqlite3.IntegrityError as e:
            conn.close()
            if 'username' in str(e).lower():
                flash('اسم المستخدم هذا موجود بالفعل.', 'error')
            elif email and 'email' in str(e).lower():
                 flash('هذا البريد الإلكتروني مسجل بالفعل.', 'error')
            else:
                 flash('حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى.', 'error')
            return render_template('user_register.html')

    return render_template('user_register.html')

# --- User Logout Route ---
@app.route("/logout-user")
@login_required
def logout_user_route():
    logout_user()
    flash("تم تسجيل الخروج.", "info")
    return redirect(url_for("index"))

# --- Admin Routes ---
@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if 'admin_id' in session: return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        admin = conn.execute("SELECT * FROM admins WHERE username = ?", (username,)).fetchone()
        conn.close()
        if admin and check_password_hash(admin['password'], password):
            session['admin_id'] = admin['id']
            session['username'] = admin['username']
            session['role'] = admin['role']
            log_admin_activity(admin['id'], admin['username'], 'Logged In')
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username or password", "error")
            return redirect(url_for('admin_login'))
    return render_template('admin-login.html')

@app.route('/dashboard')
@admin_required
def dashboard():
    conn = get_db_connection()
    shop_games = conn.execute("SELECT * FROM games WHERE is_free = 0 ORDER BY id DESC").fetchall()
    free_games = conn.execute("SELECT * FROM games WHERE is_free = 1 ORDER BY id DESC").fetchall()
    orders = conn.execute("SELECT * FROM orders ORDER BY id DESC").fetchall()
    users_list = conn.execute("SELECT id, username, created_at FROM users ORDER BY created_at DESC").fetchall()
    admins_cursor = conn.execute("SELECT id, username, role, last_seen FROM admins").fetchall()
    admins_list = []
    now = datetime.datetime.now(timezone.utc)
    online_threshold = datetime.timedelta(minutes=5)

    for admin in admins_cursor:
        admin_dict = dict(admin)
        last_seen = admin_dict.get('last_seen')
        status_key = 'offline'
        if last_seen:
            if isinstance(last_seen, str):
                try:
                    last_seen_dt = datetime.datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
                    if last_seen_dt.tzinfo is None: last_seen = last_seen_dt.replace(tzinfo=timezone.utc)
                    else: last_seen = last_seen_dt
                except ValueError:
                    try:
                        naive_dt = datetime.datetime.strptime(last_seen.split('.')[0], '%Y-%m-%d %H:%M:%S')
                        last_seen = naive_dt.replace(tzinfo=timezone.utc)
                    except ValueError: last_seen = None
            elif last_seen.tzinfo is None: last_seen = last_seen.replace(tzinfo=timezone.utc)

            if last_seen and isinstance(last_seen, datetime.datetime):
                time_diff = now - last_seen
                if time_diff >= datetime.timedelta(0) and time_diff < online_threshold: status_key = 'online'
            else: status_key = 'offline'
        admin_dict['status_key'] = status_key
        admins_list.append(admin_dict)
    conn.close()
    return render_template('dashboard.html', shop_games=shop_games, free_games=free_games, orders=orders, users_list=users_list, admins_list=admins_list)

@app.route('/add-game', methods=['POST'])
@admin_required
def add_game():
    file = request.files.get('image')
    if file and file.filename != '':
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO games (name, price, description, category, image_filename,
                                   is_free, game_username, game_password, game_type, platform)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (request.form['name'],
                  float(request.form['price']),
                  request.form['description'],
                  request.form['category'],
                  filename,
                  1 if 'is_free' in request.form else 0,
                  request.form.get('game_username'),
                  request.form.get('game_password'),
                  request.form.get('game_type', 'game_code'), # Get type
                  request.form.get('platform', 'other')      # Get platform
                 ))
            conn.commit()
        log_admin_activity(session['admin_id'], session['username'], f"Added game: {request.form['name']}")
        flash(f"Game '{request.form['name']}' added successfully!", "success")
    else:
        flash("Image is a required field.", "error")
    return redirect(url_for('dashboard'))

@app.route('/edit-game/<int:game_id>', methods=['GET', 'POST'])
@admin_required
def edit_game(game_id):
    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name']; price = request.form['price']; description = request.form['description']
        category = request.form['category']; is_free = 1 if 'is_free' in request.form else 0
        game_username = request.form['game_username']; game_password = request.form['game_password']
        game_type = request.form.get('game_type', 'game_code') # Get type
        platform = request.form.get('platform', 'other')     # Get platform
        price_val = 0.0 if is_free else float(price)
        original_game = conn.execute("SELECT image_filename FROM games WHERE id = ?", (game_id,)).fetchone()

        filename = original_game['image_filename'] if original_game else None
        if 'image' in request.files and request.files['image'].filename != '':
            file = request.files['image']
            new_filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
            if original_game and original_game['image_filename'] and original_game['image_filename'] != new_filename:
                 old_path = os.path.join(app.config['UPLOAD_FOLDER'], original_game['image_filename'])
                 if os.path.exists(old_path):
                     try: os.remove(old_path)
                     except OSError as e: print(f"Error deleting old file {old_path}: {e}")
            filename = new_filename # Update filename only if new one was uploaded
            conn.execute("UPDATE games SET image_filename = ? WHERE id = ?", (filename, game_id))


        conn.execute("""UPDATE games SET
                        name=?, price=?, description=?, category=?, is_free=?,
                        game_username=?, game_password=?, game_type=?, platform=?
                        WHERE id=?""",
                     (name, price_val, description, category, is_free,
                      game_username, game_password, game_type, platform, game_id))
        conn.commit()
        conn.close()
        log_admin_activity(session['admin_id'], session['username'], f"Edited game: {name} (ID: {game_id})")
        flash(f"Game '{name}' updated successfully!", "success")
        return redirect(url_for('dashboard'))

    game = conn.execute("SELECT * FROM games WHERE id = ?", (game_id,)).fetchone()
    conn.close()
    if game is None:
        flash("Game not found!", "error")
        return redirect(url_for('dashboard'))
    return render_template('edit-game.html', game=game)

@app.route('/delete-game/<int:game_id>', methods=['POST'])
@admin_required
def delete_game(game_id):
    with get_db_connection() as conn:
        game = conn.execute("SELECT name, image_filename FROM games WHERE id = ?", (game_id,)).fetchone()
        conn.execute("DELETE FROM games WHERE id = ?", (game_id,))
        conn.commit()
        if game:
            log_admin_activity(session['admin_id'], session['username'], f"Deleted game: {game['name']} (ID: {game_id})")
            if game['image_filename']:
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], game['image_filename'])
                if os.path.exists(image_path):
                    try: os.remove(image_path)
                    except OSError as e: print(f"Error deleting image file {image_path}: {e}")
    flash("Game deleted successfully.", "success")
    return redirect(url_for('dashboard'))

@app.route('/manage-admins', methods=['GET', 'POST'])
@super_admin_required # Only super admins
def manage_admins():
    conn = get_db_connection()
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add_admin':
            username = request.form['username']
            password = request.form['password']
            role = request.form.get('role', 'admin')
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            try:
                conn.execute("INSERT INTO admins (username, password, role) VALUES (?, ?, ?)", (username, hashed_password, role))
                conn.commit()
                log_admin_activity(session['admin_id'], session['username'], f'Added admin: {username} with role: {role}')
                flash(f"Admin '{username}' added successfully.", "success")
            except sqlite3.IntegrityError:
                flash(f"Username '{username}' already exists.", "error")

        elif action == 'delete_admin':
            admin_id_to_delete = request.form['admin_id']
            admin_to_delete = conn.execute("SELECT username, role FROM admins WHERE id = ?", (admin_id_to_delete,)).fetchone()
            
            if admin_to_delete and admin_to_delete['role'] != 'super_admin' and int(admin_id_to_delete) != session['admin_id']:
                conn.execute("DELETE FROM admins WHERE id = ?", (admin_id_to_delete,))
                conn.commit()
                log_admin_activity(session['admin_id'], session['username'], f'Deleted admin: {admin_to_delete["username"]}')
                flash("Admin deleted successfully.", "success")
            elif int(admin_id_to_delete) == session['admin_id']:
                 flash("You cannot delete your own account.", "error")
            else:
                flash("Super admins cannot be deleted.", "error")

        conn.close()
        return redirect(url_for('manage_admins'))
        
    admins = conn.execute("SELECT id, username, role FROM admins").fetchall()
    conn.close()
    return render_template('manage-admins.html', admins=admins)

@app.route('/admin/profile', methods=['GET', 'POST'])
@admin_required # Any admin can edit their own profile
def admin_profile():
    admin_id = session['admin_id']
    conn = get_db_connection()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update_profile':
            new_username = request.form['username']
            current_admin = conn.execute("SELECT username FROM admins WHERE id = ?", (admin_id,)).fetchone()
            
            if new_username == current_admin['username']:
                flash("Username is already set to this value.", "info")
            else:
                 existing_admin = conn.execute("SELECT id FROM admins WHERE username = ? AND id != ?", (new_username, admin_id)).fetchone()
                 if existing_admin:
                     flash("Username already exists.", "error")
                 else:
                     conn.execute("UPDATE admins SET username = ? WHERE id = ?", (new_username, admin_id))
                     conn.commit()
                     session['username'] = new_username
                     log_admin_activity(admin_id, new_username, 'Updated own profile username')
                     flash("Username updated successfully.", "success")

        elif action == 'change_password':
            current_password = request.form['current_password']
            new_password = request.form['new_password']
            
            admin = conn.execute("SELECT password FROM admins WHERE id = ?", (admin_id,)).fetchone()
            
            if admin and check_password_hash(admin['password'], current_password):
                hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
                conn.execute("UPDATE admins SET password = ? WHERE id = ?", (hashed_password, admin_id))
                conn.commit()
                log_admin_activity(admin_id, session['username'], 'Changed own password')
                flash("Password updated successfully.", "success")
            else:
                flash("Incorrect current password.", "error")
                
        conn.close()
        return redirect(url_for('admin_profile'))

    admin = conn.execute("SELECT username FROM admins WHERE id = ?", (admin_id,)).fetchone()
    conn.close()
    return render_template('admin-profile.html', admin=admin if admin else {'username': 'Unknown'})


@app.route('/admin/logs')
@super_admin_required # Only super admins
def admin_logs():
    conn = get_db_connection()
    logs = conn.execute("SELECT * FROM admin_logs ORDER BY timestamp DESC LIMIT 50").fetchall()
    conn.close()
    return render_template('admin-logs.html', logs=logs)

@app.route('/edit-index', methods=['GET', 'POST'])
@admin_required # Any admin can edit index
def edit_index():
    if request.method == 'POST':
        settings = {'title_part1': request.form['title_part1'], 'title_part2': request.form['title_part2'], 'title_part3': request.form['title_part3'], 'subtitle': request.form['subtitle'], 'discount': request.form['discount']}
        with open(SETTINGS_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        file = request.files.get('home_image')
        if file and file.filename != '':
            filename = "home_image.png"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
        log_admin_activity(session['admin_id'], session['username'], 'Edited home page content')
        flash('Home page content updated successfully!', 'success')
        return redirect(url_for('edit_index'))
    settings = get_index_settings()
    return render_template('index-editor.html', settings=settings)
    
@app.route('/view-messages')
@admin_required # Any admin can view messages
def view_messages():
    conn = get_db_connection()
    messages = conn.execute("SELECT * FROM messages ORDER BY created_at DESC").fetchall()
    # Mark messages as read only when viewed
    conn.execute("UPDATE messages SET is_read = 1 WHERE is_read = 0")
    conn.commit()
    conn.close()
    log_admin_activity(session['admin_id'], session['username'], 'Viewed contact messages')
    return render_template('view-messages.html', messages=messages)

@app.route('/logout') # Admin logout
def logout():
    if 'admin_id' in session:
        log_admin_activity(session['admin_id'], session['username'], 'Logged Out')
    session.clear() # Clear admin session
    return redirect(url_for('index'))

# --- Language and Currency Settings ---
@app.route('/set-currency/<currency>')
def set_currency(currency):
    session['currency'] = currency
    return redirect(request.referrer or url_for('index'))
    
@app.route('/language/<lang>')
def set_language(lang):
    session['language'] = lang
    return redirect(request.referrer or url_for('index'))

# --- Serve Static Files (Important for Images) ---
@app.route('/static/<path:filename>')
def serve_static(filename):
    if '..' in filename or filename.startswith('/'): return "Invalid path", 404
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

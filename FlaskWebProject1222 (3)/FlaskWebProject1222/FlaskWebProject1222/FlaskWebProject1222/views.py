from asyncio.windows_events import NULL
from datetime import datetime
from math import nan
from flask import render_template, request, redirect, url_for, session, jsonify
from FlaskWebProject1222 import app
import sqlite3 
import os
from werkzeug.security import generate_password_hash, check_password_hash
app.secret_key = 'your_secret_key_here'

def is_logged_in():
    return 'email' in session

conn = None
try:
    conn = sqlite3.connect('APIshowcase.db', isolation_level='DEFERRED', check_same_thread= False)
    db = conn.cursor()
    db.execute('''
    CREATE TABLE IF NOT EXISTS USERS(
        USER_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        EMAIL CHAR(320) NOT NULL UNIQUE,
        PASSWORD CHAR(600) NOT NULL,
        ACCESS CHAR(200) DEFAULT NULL,
        SUPERUSER BOOLEAN DEFAULT FALSE
        )''')
    conn.commit()
    db.execute('''CREATE TABLE IF NOT EXISTS PRODUCTS(
        PRODUCT_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        PRODUCT_NAME VARCHAR(100) NOT NULL DEFAULT '',
        PICTURE BLOB,
        API_DESCRIPTION VARCHAR(1500),
        RATE INTEGER DEFAULT 1,
        RATE_DESCRIPTION VARCHAR(500),
        PRICE INTEGER NOT NULL DEFAULT 0,
        REQUESTS INTEGER NOT NULL DEFAULT 0,
        LINK VARCHAR(100) NOT NULL
        )''')
    conn.commit()
    db.execute('''CREATE TABLE IF NOT EXISTS OPERATIONS(
        OPERATION_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        USER INTEGER,
        PRODUCT INTEGER,
        FOREIGN KEY (USER) REFERENCES USERS(USER_ID) ON DELETE NO ACTION ON UPDATE NO ACTION,
        FOREIGN KEY (PRODUCT) REFERENCES PRODUCTS(PRODUCT_ID) ON DELETE NO ACTION ON UPDATE NO ACTION
        )''')
    conn.commit()
    print("sucsess!")
        
except:
    print("conect fail")

class User:

    def __init__(self, user_id, email, password, access, superuser):
        self.user_id = user_id
        self.email = email
        self.password = password
        self.access = access
        self.superuser = superuser

    
    def totuple(self):
        list_of_att = []
        list_of_att.append(self.user_id)
        list_of_att.append(self.email)
        list_of_att.append(self.password)
        list_of_att.append(self.access)
        list_of_att.append(self.superuser)
        return tuple(list_of_att)

    @staticmethod
    def find_user_by_email(email):
        db.execute("SELECT * FROM USERS WHERE EMAIL = ?", (email,))
        user_data = db.fetchone()
        if user_data:
            return User(*user_data) 
        return None


user_list = []

#Добавление суперюзера в БД
superuser = User(user_id=None, email = 'qwerty12345@mail.ru', password = generate_password_hash("123456789"), access=None, superuser=True)
db.execute('INSERT OR IGNORE INTO USERS(USER_ID, EMAIL, PASSWORD, ACCESS, SUPERUSER) VALUES (?, ?, ?, ?, ?)', superuser.totuple())
conn.commit()

def picture_to_binlist(pic_path):
    with open(pic_path, 'rb') as file:
        image_data = file.read()
    return sqlite3.Binary(image_data)

class Product:

    def __init__(self, product_id, product_name, picture, API_description, rate, rate_description, price, requests, link):
        self.product_id = product_id
        self.product_name = product_name
        self.picture = picture
        self.API_description = API_description
        self.rate = rate
        self.rate_description = rate_description
        self.price = price
        self.requests = requests
        self.link = link

    def get_atts_list(self):
        list_of_atts = ['product_id', 'product_name', 'picture', 'API_description', 'rate', 'rate_description', 'price', 'requests','link']
        return list_of_atts

def add_API():
    product_name = ''
    pic_path = '/'
    API_description = ''
    num_of_rates = 1 #default
    requests = 0
   
    for rate in range(1,num_of_rates+1):
        price = 0
        rate_description = ''
        API_vals = (None, product_name, picture_to_binlist(pic_path=pic_path), API_description, rate, rate_description, price, requests)
        db.execute('''INSERT INTO PRODUCTS VALUES (?,?,?,?,?,?,?,?)''', API_vals)

    conn.commit()

def delete_API():
    API_id = None
    db.execute('''DELETE PRODUCTS WHERE PRODUCT_ID = (?)''', API_id)
    conn.commit()

def edit_API():
    API_id = None
    db.execute('''SELECT PRODUCTS WHERE PRODUCT_ID = (?)''', API_id)
    editing_choice = None

    if editing_choice <= 3:
        
        editted_att = ''
        db.execute('''UPDATE PRODUCTS
                        SET (?) = (?)''', (Product.get_atts_list[editing_choice].upper, editted_att))
        
 
    else:
        choosen_rate = None
        db.execute('SELECT * FROM PRODUCTS WHERE RATE = (?)', choosen_rate)

        editted_att = ''
        db.execute('''UPDATE PRODUCTS
                        SET (?) = (?)''', (Product.get_atts_list[editing_choice].upper, editted_att))

    conn.commit()


@app.route('/')
def index():
    is_superuser = session.get('superuser', False)  # Get superuser status from session
    return render_template('index.html', is_superuser=is_superuser)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.find_user_by_email(email=email)
        if user and check_password_hash(user.password, password):
            session['email'] = user.email  # Store user ID in session
            session['superuser'] = user.superuser
            print(session)
            return redirect(url_for('index')) 
        else:
            return "Wrong E-mail or password"

    return render_template('login.html')

@app.route('/logout')
def logout():
    print("Session before logout:", session)  # Debugging line
    session.pop('email', None)  # Remove email from session
    print("Session after logout:", session)  # Debugging line
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password == confirm_password:
            try:
                user = User.find_user_by_email(email=email)
                if user is None: 
                    password_hash = generate_password_hash(password)
                    db.execute('''
                        INSERT INTO USERS(USER_ID, EMAIL, PASSWORD, ACCESS, SUPERUSER) VALUES (?, ?, ?, ?, ?)''', 
                        (None, email, password_hash, None, False))
                    conn.commit()
                else:
                    print('User already exists')
                    return 'User with this email already exists'  

            except Exception as e:
                print(f"Error saving user: {e}")
                return 'Error saving user to database'
            return redirect(url_for('index'))
        else:
            return 'Passwords do not match'

    return render_template('register.html')

@app.route('/api_card_1')
def api_card_1():
    return render_template('api_card_1.html')

@app.route('/api_card_2')
def api_card_2():
    return render_template('api_card_2.html')

@app.route('/api_card_3')
def api_card_3():
    return render_template('api_card_3.html')

@app.route('/api_card_4')
def api_card_4():
    return render_template('api_card_4.html')

@app.route('/api_card_5')
def api_card_5():
    return render_template('api_card_5.html')

@app.route('/sandbox')
def sandbox():
    return render_template('sandbox.html')

@app.route('/account')
def account():
    return render_template('account.html')

@app.route('/monitoring')
def monitoring():
    db.execute('INSERT INTO OPERATIONS VALUES (?,?,?,?)', (None,1,1,'success'))
    db.execute('SELECT * FROM OPERATIONS')    
    operations = db.fetchall()
    return render_template('monitoring.html', operations=operations)

@app.route('/payment')
def initiate_payment():
    product_description = 'Купи API-мужика'
    price = 1000000
    payment_url = quickpay.payment_url(price, product_description, 'http://названиесайта.com/payment_callback')
    return redirect(payment_url)

@app.route('/payment_callback', methods=['POST'])
def payment_callback():
    payment_data = request.get_json()
    if payment_data['status'] == 'success':
        return redirect(url_for('index'))
    else:
        return redirect(url_for('paiment_failed'))
    
@app.route('/paiment_failed', methods=['POST'])
def paiment_failed():
    #Оплата не прошла, кнопка "Ок"
    return redirect(url_for('index'))

@app.route('/add-api', methods=['POST'])
def add_api():
    api_name = request.form['api-name']
    api_description = request.form['api-description']
    api_image = request.files['api-image']
    api_basic_price = request.form['api-basic-price']
    api_advanced_price = request.form['api-advanced-price']
    api_enterprise_price = request.form['api-enterprise-price']
    api_documentation = request.files['api-documentation']
    api_prices = [api_basic_price, api_advanced_price, api_enterprise_price]
    #api_requests = request.form['api-requests']
    api_requests = 10

    api_id = None
    api_name = api_name.replace(" ", "_").lower()
    api_link = f"api_card_{api_name}"
    img_dir = os.path.join('FlaskWebProject1222', 'static', 'img')
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    image_filename = f"{api_name}.png"
    image_path = os.path.join(img_dir, image_filename)

    api_image.save(image_path)

    docs_dir = os.path.join('FlaskWebProject1222', 'static', 'docs')
    if not os.path.exists(docs_dir):
        os.makedirs(docs_dir)

    documentation_filename = f"{api_name}_documentation.pdf"
    documentation_path = os.path.join(docs_dir, documentation_filename)
    api_documentation.save(documentation_path)
       
    rate_desciptions = ['basic','advanced','enterprise']
    for i in range(3):
        db.execute('INSERT INTO PRODUCTS VALUES (?,?,?,?,?,?,?,?,?)', (api_id, 
                                                                        api_name, 
                                                                        picture_to_binlist(image_path),
                                                                        api_description,
                                                                        i+1,
                                                                        rate_desciptions[i],
                                                                        api_prices[i],
                                                                        api_requests,
                                                                        api_link))
    conn.commit()

    create_api_page(api_id, api_name, api_description, api_basic_price, api_advanced_price, api_enterprise_price, documentation_filename)
    return redirect(url_for('view_api_card', title=api_name))

def create_api_page(api_id, title, description, basic_price, advanced_price, enterprise_price, documentation_filename):
    output_dir = 'FlaskWebProject1222/templates'
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    html_content = render_template('api_card_template.html', title=title, description=description,
                                   basic_price=basic_price, advanced_price=advanced_price, enterprise_price=enterprise_price,
                                   documentation_filename=documentation_filename)
    
    html_file_path = os.path.join(output_dir, f'api_card_{title}.html')
    
    with open(html_file_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

if __name__ == '__main__':
    app.run(debug=True)

@app.route('/api_card_<title>', methods=['GET'])
def view_api_card(title):
    # This function will render the API card page
    return render_template(f'api_card_{title}.html')

@app.route('/api/products', methods=['GET'])
def get_products(): 
    db.execute('''SELECT PRODUCT_ID, 
       PRODUCT_NAME, 
       API_DESCRIPTION, 
       LINK, 
       GROUP_CONCAT(RATE, ", ") 
    FROM PRODUCTS 
    GROUP BY PRODUCT_NAME''')
    products = db.fetchall()

    product_list = [
        {
            'id': 1,
            'title': "Agreement management",
            'description': "API соглашений предоставляет стандартизированный механизм управления соглашениями, особенно в контексте партнерских отношений между партнерами. API позволяет создавать, обновлять и запрашивать экземпляры соглашения, а также создавать, обновлять и запрашивать спецификации соглашения, служащие шаблонами для экземпляров соглашения.",
            'image': url_for('static', filename='img/agreement.png'),
            'link': "api_card_1"
        },
        {
            'id': 2,
            'title': "Customer management",
            'description': "API управления клиентами предоставляет стандартизированный механизм для управления клиентами и учетными записями клиентов, например, создание, обновление, извлечение, удаление и уведомление о событиях. Клиентом может быть человек, организация или другой поставщик услуг, который покупает продукты у предприятия. API управления клиентами позволяет управлять идентификационной и финансовой информацией о нем.",
            'image': url_for('static', filename='img/cust.png'),
            'link': "api_card_2"
        },
        {
            'id': 3,
            'title': "Document management",
            'description': "Основная цель API программного обеспечения системы управления документами Folderit или API облачного хранилища — позволить компании-партнеру создать гибкое функциональное приложение. API позволяет легко и быстро получить все функции, которые включает в себя Folderit DMS.",
            'image': url_for('static', filename='img/document.png'),
            'link': "api_card_3"
        },
        {
            'id': 4,
            'title': "Payment management",
            'description': "API управления платежами включает определение модели, а также все доступные операции для платежей и возвратов. Этот API позволяет выполнять следующие операции: уведомление о выполненном платеже, получение списка платежей, отфильтрованных по заданным критериям, получение отдельного выполненного платежа, уведомление о выполненном возврате, получение списка возвратов, отфильтрованных по заданным критериям, получение отдельного выполненного возврата.",
            'image': url_for('static', filename='img/paymant.png'),
            'link': "api_card_4"
        },
        {
            'id': 5,
            'title': "Product catalog management",
            'description': "API управления каталогом продуктов позволяет управлять всем жизненным циклом элементов каталога, консультироваться с элементами каталога во время нескольких процессов, таких как процесс заказа, управление кампанией, управление продажами. Эта версия спецификации API управления каталогом продуктов Rest включает функционал Engage Party Migration.",
            'image': url_for('static', filename='img/catalog.png'),
            'link': "api_card_5"
        }
    ]
    for product in products:
        product_dict = {
            'id': product[0],
            'title': product[1],
            'description': product[2],
            'link': url_for('view_api_card', title=product[1].replace(" ", "_").lower()),
            'image': url_for('static', filename=f'img/{product[1]}.png')
        }

        product_list.append(product_dict)

    conn.commit()
    return jsonify(product_list)


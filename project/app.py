import sqlite3
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect('mcdonalds.db')
    c = conn.cursor()

    # Tạo bảng menu
    c.execute('''
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category TEXT NOT NULL
        )
    ''')

    # Tạo bảng đơn hàng
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT,
            total_price REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tạo bảng chi tiết đơn hàng
    c.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER,
            item_id INTEGER,
            quantity INTEGER,
            FOREIGN KEY (order_id) REFERENCES orders(id),
            FOREIGN KEY (item_id) REFERENCES menu(id)
        )
    ''')

    # Thêm dữ liệu mẫu
    c.execute("SELECT COUNT(*) FROM menu")
    if c.fetchone()[0] == 0:
        c.executemany("INSERT INTO menu (name, price, category) VALUES (?, ?, ?)", [
            ('Big Mac', 35, 'Main'),
            ('Fries', 12, 'Side'),
            ('Coke', 10, 'Drink')
        ])

    conn.commit()
    conn.close()

# Khởi tạo database
init_db()


from flask import Flask, jsonify, request, render_template
import sqlite3

app = Flask(__name__)

# Lấy danh sách menu
@app.route('/api/menu', methods=['GET'])
def get_menu():
    conn = sqlite3.connect('mcdonalds.db')
    c = conn.cursor()
    c.execute("SELECT * FROM menu")
    menu = [{'id': row[0], 'name': row[1], 'price': row[2], 'category': row[3]} for row in c.fetchall()]
    conn.close()
    return jsonify(menu)

# Tạo đơn hàng
@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    customer_name = data.get('customer_name')
    items = data.get('items')

    if not customer_name or not items:
        return jsonify({'error': 'Missing parameters'}), 400

    total_price = sum(item['price'] * item['quantity'] for item in items)

    conn = sqlite3.connect('mcdonalds.db')
    c = conn.cursor()
    c.execute("INSERT INTO orders (customer_name, total_price) VALUES (?, ?)", (customer_name, total_price))
    order_id = c.lastrowid

    for item in items:
        c.execute("INSERT INTO order_items (order_id, item_id, quantity) VALUES (?, ?, ?)",
                  (order_id, item['id'], item['quantity']))

    conn.commit()
    conn.close()
    return jsonify({'order_id': order_id, 'total_price': total_price}), 201

# Hiển thị giao diện web
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

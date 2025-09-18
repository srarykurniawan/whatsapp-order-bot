import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from models.order_model import Order

class DatabaseManager:
    def __init__(self, db_path='data/orders.db'):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Buat tabel orders jika belum ada
        c.execute('''CREATE TABLE IF NOT EXISTS orders
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      customer_name TEXT,
                      customer_wa TEXT,
                      customer_address TEXT,
                      items TEXT,
                      total REAL,
                      status TEXT,
                      created_at TIMESTAMP)''')
        
        conn.commit()
        conn.close()
    
    def init_sample_data(self):
        """Inisialisasi data contoh untuk testing"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Hapus tabel jika sudah ada (hati-hati di production)
        c.execute('''DROP TABLE IF EXISTS orders''')
        
        # Buat tabel baru
        c.execute('''CREATE TABLE orders
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      customer_name TEXT,
                      customer_wa TEXT,
                      customer_address TEXT,
                      items TEXT,
                      total REAL,
                      status TEXT,
                      created_at TIMESTAMP)''')
        
        # Data contoh
        sample_orders = [
            ('Budi Santoso', '+628123456789', 'Jl. Merdeka No. 123', '2 Nasi Goreng, 1 Es Teh', 55000, 'completed', '2024-01-15 10:30:00'),
            ('Siti Rahayu', '+628987654321', 'Jl. Sudirman No. 45', '1 Ayam Bakar, 2 Es Jeruk', 47000, 'processing', '2024-01-15 11:15:00'),
            ('Ahmad Wijaya', '+628112233445', 'Jl. Gatot Subroto No. 67', '3 Mie Goreng, 1 Es Teh', 65000, 'confirmed', '2024-01-15 12:00:00'),
            ('Dewi Lestari', '+628556677889', 'Jl. Thamrin No. 89', '1 Nasi Goreng, 1 Ayam Bakar', 60000, 'pending', '2024-01-15 09:45:00'),
        ]
        
        # Insert data contoh
        c.executemany('''INSERT INTO orders 
                         (customer_name, customer_wa, customer_address, items, total, status, created_at)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''', sample_orders)
        
        conn.commit()
        conn.close()
        print("Data contoh berhasil diinisialisasi")
    
    def add_order(self, order):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''INSERT INTO orders 
                     (customer_name, customer_wa, customer_address, items, total, status, created_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                 (order.customer_name, order.customer_wa, order.customer_address, 
                  order.items, order.total, order.status, order.created_at))
        
        order_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return order_id
    
    def get_all_orders(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''SELECT * FROM orders ORDER BY created_at DESC''')
        rows = c.fetchall()
        
        orders = []
        for row in rows:
            orders.append(Order(
                id=row[0],
                customer_name=row[1],
                customer_wa=row[2],
                customer_address=row[3],
                items=row[4],
                total=row[5],
                status=row[6],
                created_at=datetime.strptime(row[7], '%Y-%m-%d %H:%M:%S') if isinstance(row[7], str) else row[7]
            ))
        
        conn.close()
        return orders
    
    def get_order(self, order_id):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''SELECT * FROM orders WHERE id = ?''', (order_id,))
        row = c.fetchone()
        
        if row:
            order = Order(
                id=row[0],
                customer_name=row[1],
                customer_wa=row[2],
                customer_address=row[3],
                items=row[4],
                total=row[5],
                status=row[6],
                created_at=datetime.strptime(row[7], '%Y-%m-%d %H:%M:%S') if isinstance(row[7], str) else row[7]
            )
            conn.close()
            return order
        else:
            conn.close()
            return None
    
    def update_order_status(self, order_id, new_status):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''UPDATE orders SET status = ? WHERE id = ?''', (new_status, order_id))
        conn.commit()
        conn.close()
    
    def get_today_orders(self):
        today = datetime.now().date()
        all_orders = self.get_all_orders()
        
        return [order for order in all_orders if order.created_at.date() == today]
    
    def get_weekly_orders(self):
        week_ago = datetime.now() - timedelta(days=7)
        all_orders = self.get_all_orders()
        
        return [order for order in all_orders if order.created_at >= week_ago]
    
    def get_monthly_orders(self):
        month_ago = datetime.now() - timedelta(days=30)
        all_orders = self.get_all_orders()
        
        return [order for order in all_orders if order.created_at >= month_ago]
    
    def get_pending_orders(self):
        all_orders = self.get_all_orders()
        return [order for order in all_orders if order.status in ['pending', 'confirmed', 'processing']]
    
    def get_orders_by_status(self, status):
        all_orders = self.get_all_orders()
        return [order for order in all_orders if order.status == status]
    
    def get_orders_by_status_count(self):
        all_orders = self.get_all_orders()
        status_count = {}
        
        for order in all_orders:
            status_count[order.status] = status_count.get(order.status, 0) + 1
        
        return status_count
    
    def get_top_customers(self):
        all_orders = self.get_all_orders()
        customer_orders = {}
        
        for order in all_orders:
            if order.customer_wa in customer_orders:
                customer_orders[order.customer_wa]['count'] += 1
                customer_orders[order.customer_wa]['total'] += order.total
            else:
                customer_orders[order.customer_wa] = {
                    'name': order.customer_name,
                    'count': 1,
                    'total': order.total
                }
        
        # Konversi ke dataframe untuk tampilan yang lebih baik
        top_customers = []
        for wa, data in customer_orders.items():
            top_customers.append({
                'WhatsApp': wa,
                'Nama': data['name'],
                'Jumlah Pesanan': data['count'],
                'Total Pembelian': data['total']
            })
        
        # Perbaikan: Pastikan DataFrame tidak kosong sebelum sorting
        if not top_customers:
            # Return DataFrame dengan kolom yang diharapkan meski kosong
            return pd.DataFrame(columns=['WhatsApp', 'Nama', 'Jumlah Pesanan', 'Total Pembelian'])
        
        df = pd.DataFrame(top_customers)
        
        # Perbaikan: Pastikan kolom 'Total Pembelian' ada sebelum sorting
        if 'Total Pembelian' in df.columns:
            return df.sort_values('Total Pembelian', ascending=False)
        else:
            # Jika kolom tidak ada, return DataFrame tanpa sorting
            return df
    
    def export_orders_to_csv(self):
        orders = self.get_all_orders()
        
        orders_data = []
        for order in orders:
            orders_data.append({
                'ID': order.id,
                'Nama Pelanggan': order.customer_name,
                'WhatsApp': order.customer_wa,
                'Alamat': order.customer_address,
                'Items': order.items,
                'Total': order.total,
                'Status': order.status,
                'Tanggal': order.created_at
            })
        
        df = pd.DataFrame(orders_data)
        df.to_csv('data/orders_export.csv', index=False)
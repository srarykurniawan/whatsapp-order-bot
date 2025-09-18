import streamlit as st
import sqlite3
import json
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
from utils.message_processor import MessageProcessor
from utils.whatsapp_integration import WhatsAppIntegration
from utils.database import DatabaseManager
from models.order_model import Order

# Konfigurasi halaman Streamlit
st.set_page_config(
    page_title="WhatsApp Order Bot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inisialisasi komponen
db_manager = DatabaseManager()
message_processor = MessageProcessor()
whatsapp = WhatsAppIntegration()

# Judul aplikasi
st.title("🤖 Agentic AI Chatbot untuk Otomatisasi Pesanan WhatsApp")
st.markdown("""
Bot ini akan membantu mengotomatiskan proses pemesanan melalui WhatsApp tanpa perlu menjawab manual.
""")

# Sidebar untuk konfigurasi
with st.sidebar:
    st.header("Konfigurasi")
    
    # Input Twilio credentials (jika menggunakan Twilio API)
    st.subheader("Konfigurasi WhatsApp API")
    account_sid = st.text_input("Account SID", type="password")
    auth_token = st.text_input("Auth Token", type="password")
    whatsapp_number = st.text_input("Nomor WhatsApp Bot")
    
    # Simpan konfigurasi
    if st.button("Simpan Konfigurasi"):
        whatsapp.set_credentials(account_sid, auth_token, whatsapp_number)
        st.success("Konfigurasi disimpan!")
    
    # Status bot
    st.subheader("Status Bot")
    st.info("Bot aktif dan siap menerima pesanan")
    
    # Statistik
    st.subheader("Statistik Hari Ini")
    today_orders = db_manager.get_today_orders()
    pending_orders = db_manager.get_pending_orders()
    st.metric("Pesanan Hari Ini", len(today_orders))
    st.metric("Pesanan Tertunda", len(pending_orders))

# Tab utama
tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Pesanan", "Pesan Masuk", "Analytics"])

with tab1:
    st.header("Dashboard Pesanan")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Pesanan Hari Ini")
        today_orders = db_manager.get_today_orders()
        st.metric("Jumlah Pesanan", len(today_orders))
        
    with col2:
        st.subheader("Pesanan Bulan Ini")
        monthly_orders = db_manager.get_monthly_orders()
        st.metric("Jumlah Pesanan", len(monthly_orders))
        
    with col3:
        st.subheader("Total Pendapatan")
        revenue = sum(order.total for order in monthly_orders if order.status == "completed")
        st.metric("Pendapatan", f"Rp {revenue:,.0f}")
    
    # Grafik pesanan
    st.subheader("Grafik Pesanan 7 Hari Terakhir")
    weekly_orders = db_manager.get_weekly_orders()
    
    if weekly_orders:
        dates = [order.created_at.strftime("%Y-%m-%d") for order in weekly_orders]
        order_counts = {}
        
        for date in dates:
            order_counts[date] = order_counts.get(date, 0) + 1
        
        st.bar_chart(order_counts)
    else:
        st.info("Belum ada pesanan dalam 7 hari terakhir")

with tab2:
    st.header("Manajemen Pesanan")
    
    # Filter pesanan
    status_filter = st.selectbox("Filter Status", ["Semua", "pending", "confirmed", "processing", "completed", "cancelled"])
    
    if status_filter == "Semua":
        orders = db_manager.get_all_orders()
    else:
        orders = db_manager.get_orders_by_status(status_filter)
    
    # Tampilkan pesanan
    for order in orders:
        with st.expander(f"Pesanan #{order.id} - {order.customer_name} - {order.status}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Pelanggan:** {order.customer_name}")
                st.write(f"**WhatsApp:** {order.customer_wa}")
                st.write(f"**Alamat:** {order.customer_address}")
                st.write(f"**Tanggal:** {order.created_at.strftime('%d/%m/%Y %H:%M')}")
            
            with col2:
                st.write(f"**Items:** {order.items}")
                st.write(f"**Total:** Rp {order.total:,.0f}")
                st.write(f"**Status:** {order.status}")
                
                # Ubah status
                new_status = st.selectbox(
                    "Ubah Status",
                    ["pending", "confirmed", "processing", "completed", "cancelled"],
                    index=["pending", "confirmed", "processing", "completed", "cancelled"].index(order.status),
                    key=f"status_{order.id}"
                )
                
                if st.button("Perbarui Status", key=f"update_{order.id}"):
                    db_manager.update_order_status(order.id, new_status)
                    st.success("Status diperbarui!")
                    time.sleep(1)
                    st.rerun()

with tab3:
    st.header("Pesan Masuk Terbaru")
    
    # Simulasi pesan masuk (dalam implementasi nyata, ini akan terhubung ke API WhatsApp)
    st.info("Fitur ini memerlukan integrasi dengan API WhatsApp seperti Twilio")
    
    # Demo dengan data contoh
    sample_messages = [
        {"from": "+628123456789", "body": "Halo, saya ingin memesan nasi goreng", "timestamp": "2023-10-15 10:30:15"},
        {"from": "+628987654321", "body": "Apakah masih buka? Saya mau pesan ayam bakar", "timestamp": "2023-10-15 10:25:42"},
        {"from": "+628112233445", "body": "Pesanan saya kapan sampai?", "timestamp": "2023-10-15 09:45:18"},
    ]
    
    for msg in sample_messages:
        with st.chat_message("user"):
            st.write(f"**{msg['from']}** ({msg['timestamp']})")
            st.write(msg['body'])
            
            # Tombol untuk membalas otomatis
            if st.button("Proses Pesan", key=f"process_{msg['from']}"):
                response = message_processor.process_message(msg['body'], msg['from'])
                st.success(f"Respon: {response}")

with tab4:
    st.header("📊 Analytics & Laporan")
    
    # Tambahkan tombol untuk inisialisasi data contoh
    col_init, col_export = st.columns(2)
    with col_init:
        if st.button("🗃️ Initialize Sample Data", key="init_sample_data", use_container_width=True):
            db_manager.init_sample_data()
            st.success("Data contoh berhasil diinisialisasi!")
            time.sleep(1)
            st.rerun()
    
    with col_export:
        if st.button("📤 Ekspor Data ke CSV", key="export_data", use_container_width=True):
            db_manager.export_orders_to_csv()
            st.success("Data berhasil diekspor!")
    
    # --- SECTION 1: SUMMARY CARDS ---
    st.subheader("📈 Summary Overview")
    
    # Data untuk summary cards
    all_orders = db_manager.get_all_orders()
    today_orders = db_manager.get_today_orders()
    monthly_orders = db_manager.get_monthly_orders()
    completed_orders = [o for o in monthly_orders if o.status == "completed"]
    revenue = sum(order.total for order in completed_orders)
    avg_order_value = revenue / len(completed_orders) if completed_orders else 0
    
    # Tampilkan metrics dalam columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Pesanan", len(all_orders))
    
    with col2:
        st.metric("Pesanan Hari Ini", len(today_orders))
    
    with col3:
        st.metric("Pendapatan Bulan Ini", f"Rp {revenue:,.0f}")
    
    with col4:
        st.metric("Rata-Rata Nilai Pesanan", f"Rp {avg_order_value:,.0f}")
    
    # --- SECTION 2: REVENUE CHART ---
    st.subheader("💰 Trend Pendapatan")
    
    # Siapkan data untuk chart pendapatan
    daily_revenue = {}
    for order in completed_orders:
        date_str = order.created_at.strftime("%Y-%m-%d")
        if date_str in daily_revenue:
            daily_revenue[date_str] += order.total
        else:
            daily_revenue[date_str] = order.total
    
    if daily_revenue:
        # Buat chart pendapatan
        revenue_dates = list(daily_revenue.keys())
        revenue_values = list(daily_revenue.values())
        
        fig_revenue = go.Figure()
        fig_revenue.add_trace(go.Scatter(
            x=revenue_dates, 
            y=revenue_values,
            mode='lines+markers',
            name='Pendapatan',
            line=dict(color='#FF4B4B', width=3),
            marker=dict(size=8)
        ))
        
        fig_revenue.update_layout(
            title="Trend Pendapatan Harian",
            xaxis_title="Tanggal",
            yaxis_title="Pendapatan (Rp)",
            template="plotly_white",
            height=400
        )
        
        st.plotly_chart(fig_revenue, use_container_width=True)
    else:
        st.info("Belum ada data pendapatan untuk ditampilkan")
    
    # --- SECTION 3: ORDER STATUS DISTRIBUTION ---
    st.subheader("📋 Distribusi Status Pesanan")
    
    col5, col6 = st.columns(2)
    
    with col5:
        # Pie chart status pesanan
        status_counts = db_manager.get_orders_by_status_count()
        if status_counts:
            status_df = pd.DataFrame.from_dict(status_counts, orient='index', columns=['Jumlah'])
            status_df = status_df.reset_index()
            status_df.columns = ['Status', 'Jumlah']
            
            fig_pie = px.pie(
                status_df, 
                values='Jumlah', 
                names='Status',
                title='Distribusi Status Pesanan',
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("Belum ada data status pesanan")
    
    with col6:
        # Bar chart status pesanan
        if status_counts:
            fig_bar = px.bar(
                status_df, 
                x='Status', 
                y='Jumlah',
                title='Jumlah Pesanan per Status',
                color='Status',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_bar.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Belum ada data status pesanan")
    
    # --- SECTION 4: TOP CUSTOMERS AND PRODUCTS ---
    st.subheader("🏆 Top Performers")
    
    col7, col8 = st.columns(2)
    
    with col7:
        # Top customers
        st.markdown("**👥 Pelanggan Teratas**")
        top_customers = db_manager.get_top_customers()
        if not top_customers.empty:
            # Batasi hanya top 5
            top_5_customers = top_customers.head(5)
            
            fig_customers = px.bar(
                top_5_customers,
                x='Nama',
                y='Total Pembelian',
                title='Top 5 Pelanggan by Spending',
                color='Nama',
                color_discrete_sequence=px.colors.sequential.Blues
            )
            fig_customers.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_customers, use_container_width=True)
        else:
            st.info("Belum ada data pelanggan")
    
    with col8:
        # Top products (analisis dari items)
        st.markdown("**🍽️ Menu Populer**")
        if all_orders:
            # Ekstrak data menu dari items
            menu_items = {}
            for order in all_orders:
                items = order.items.split(',')
                for item in items:
                    item_clean = item.strip().lower()
                    if item_clean in menu_items:
                        menu_items[item_clean] += 1
                    else:
                        menu_items[item_clean] = 1
            
            if menu_items:
                menu_df = pd.DataFrame(list(menu_items.items()), columns=['Menu', 'Jumlah'])
                menu_df = menu_df.sort_values('Jumlah', ascending=False).head(5)
                
                fig_menu = px.bar(
                    menu_df,
                    x='Menu',
                    y='Jumlah',
                    title='Top 5 Menu Paling Populer',
                    color='Menu',
                    color_discrete_sequence=px.colors.sequential.Greens
                )
                fig_menu.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig_menu, use_container_width=True)
            else:
                st.info("Belum ada data menu")
        else:
            st.info("Belum ada data pesanan untuk analisis menu")
    
    # --- SECTION 5: ORDER TIMELINE ANALYSIS ---
    st.subheader("⏰ Analisis Waktu Pesanan")
    
    if all_orders:
        # Ekstrak jam dari timestamp
        order_hours = [order.created_at.hour for order in all_orders]
        
        # Hitung pesanan per jam
        hour_counts = {}
        for hour in range(24):
            hour_counts[hour] = order_hours.count(hour)
        
        # Buat dataframe
        hour_df = pd.DataFrame(list(hour_counts.items()), columns=['Jam', 'Jumlah Pesanan'])
        
        fig_hour = px.line(
            hour_df,
            x='Jam',
            y='Jumlah Pesanan',
            title='Distribusi Pesanan per Jam',
            markers=True
        )
        fig_hour.update_layout(xaxis=dict(tickmode='linear', dtick=1))
        st.plotly_chart(fig_hour, use_container_width=True)
    else:
        st.info("Belum ada data untuk analisis waktu")
    
    # --- SECTION 6: DETAILED DATA TABLES ---
    st.subheader("📋 Data Detail")
    
    tab_detail1, tab_detail2, tab_detail3 = st.tabs(["Pesanan per Status", "Pelanggan Teratas", "Data Mentah"])
    
    with tab_detail1:
        status_counts = db_manager.get_orders_by_status_count()
        if status_counts:
            st.dataframe(pd.DataFrame.from_dict(status_counts, orient='index', columns=['Jumlah']))
        else:
            st.info("Belum ada data pesanan")
    
    with tab_detail2:
        top_customers = db_manager.get_top_customers()
        if not top_customers.empty:
            st.dataframe(top_customers)
        else:
            st.info("Belum ada data pelanggan")
    
    with tab_detail3:
        if all_orders:
            # Siapkan data untuk tabel
            orders_data = []
            for order in all_orders:
                orders_data.append({
                    'ID': order.id,
                    'Pelanggan': order.customer_name,
                    'WhatsApp': order.customer_wa,
                    'Items': order.items,
                    'Total': order.total,
                    'Status': order.status,
                    'Tanggal': order.created_at.strftime('%Y-%m-%d %H:%M')
                })
            
            orders_df = pd.DataFrame(orders_data)
            st.dataframe(orders_df, height=300)
        else:
            st.info("Belum ada data pesanan")
    
    # --- SECTION 7: EXPORT OPTIONS ---
    st.subheader("💾 Opsi Ekspor Data")
    
    export_col1, export_col2, export_col3 = st.columns(3)
    
    with export_col1:
        if st.button("📊 Ekspor Laporan Bulanan", use_container_width=True):
            db_manager.export_orders_to_csv()
            st.success("Laporan bulanan berhasil diekspor!")
    
    with export_col2:
        if st.button("👥 Ekspor Data Pelanggan", use_container_width=True):
            st.info("Fitur ekspor data pelanggan akan segera tersedia")
    
    with export_col3:
        if st.button("📈 Ekspor Analytics", use_container_width=True):
            st.info("Fitur ekspor analytics akan segera tersedia")

# Footer
st.markdown("---")
st.markdown("**Agentic AI Chatbot** © 2023 - Otomatiskan pesanan WhatsApp tanpa repot")
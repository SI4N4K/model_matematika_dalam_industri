import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pulp
from math import sqrt

st.set_page_config(page_title="Industrial Math Models", layout="wide")

# Sidebar Dokumentasi
st.sidebar.header("Panduan Aplikasi")
st.sidebar.markdown("""
**1. Optimasi Produksi**:
- Masukkan koefisien fungsi tujuan dan kendala
- Sistem akan menampilkan solusi optimal

**2. Model Persediaan**:
- Input parameter permintaan dan biaya
- Hitung EOQ dan biaya total optimal

**3. Model Antrian**:
- Simulasikan sistem antrian M/M/1
- Visualisasi panjang antrian over time

**4. Model Industri Lain**:
- Break-even point analysis
- Analisis sensitivitas parameter
""")

# Inisialisasi Tab
tab1, tab2, tab3, tab4 = st.tabs(["Optimasi Produksi", "Model Persediaan", "Model Antrian", "Model Lain"])

with tab1:  # Linear Programming
    st.header("Optimasi Produksi Linear Programming")
    
    # Input Fungsi Tujuan
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Fungsi Tujuan")
        c1 = st.number_input("Koefisien X1 (Profit)", value=3)
        c2 = st.number_input("Koefisien X2 (Profit)", value=2)
    
    # Input Kendala
    with col2:
        st.subheader("Kendala Produksi")
        a1 = st.number_input("Koefisien X1 (Kendala 1)", value=1)
        a2 = st.number_input("Koefisien X2 (Kendala 1)", value=1)
        b = st.number_input("Kapasitas Maksimum", value=100)
    
    # Solve LP Problem
    prob = pulp.LpProblem("Max_Profit", pulp.LpMaximize)
    x1 = pulp.LpVariable("x1", lowBound=0)
    x2 = pulp.LpVariable("x2", lowBound=0)
    prob += c1*x1 + c2*x2, "Profit"
    prob += a1*x1 + a2*x2 <= b, "Kendala Kapasitas"
    
    prob.solve()
    
    # Visualisasi Hasil
    fig, ax = plt.subplots()
    x = np.linspace(0, b/a1, 100)
    y = (b - a1*x)/a2
    ax.plot(x, y, label='Kendala Produksi')
    ax.fill_between(x, 0, y, alpha=0.1)
    ax.scatter(x1.value(), x2.value(), color='red', label='Solusi Optimal')
    ax.set_xlabel("X1")
    ax.set_ylabel("X2")
    ax.legend()
    
    st.subheader("Solusi Optimal")
    st.write(f"X1 = {x1.value():.2f}, X2 = {x2.value():.2f}")
    st.write(f"Profit Maksimum: ${pulp.value(prob.objective):.2f}")
    st.pyplot(fig)

with tab2:  # EOQ Model
    st.header("Economic Order Quantity (EOQ)")
    
    D = st.number_input("Permintaan Tahunan (unit)", value=1000)
    S = st.number_input("Biaya Pemesanan ($/pesan)", value=10)
    H = st.number_input("Biaya Penyimpanan ($/unit/tahun)", value=0.5)
    
    Q = sqrt((2*D*S)/H)
    TC = (D/Q)*S + (Q/2)*H
    
    # Visualisasi Grafik
    q_values = np.linspace(Q*0.5, Q*1.5, 100)
    tc_values = (D/q_values)*S + (q_values/2)*H
    
    fig, ax = plt.subplots()
    ax.plot(q_values, tc_values, label='Total Biaya')
    ax.axvline(Q, color='r', linestyle='--', label='EOQ')
    ax.set_xlabel("Jumlah Pesanan")
    ax.set_ylabel("Biaya Total ($)")
    ax.legend()
    
    st.subheader("Hasil Perhitungan")
    st.write(f"EOQ: {Q:.2f} unit")
    st.write(f"Biaya Total Minimum: ${TC:.2f}")
    st.pyplot(fig)

with tab3:  # M/M/1 Queue
    st.header("Model Antrian M/M/1")
    
    lambda_ = st.number_input("Tingkat Kedatangan (λ)", value=0.5)
    mu = st.number_input("Tingkat Pelayanan (μ)", value=0.6)
    
    # Simulasi Antrian
    np.random.seed(42)
    num_customers = 100
    inter_arrivals = np.random.exponential(1/lambda_, num_customers)
    service_times = np.random.exponential(1/mu, num_customers)
    
    # Visualisasi Panjang Antrian
    times = np.cumsum(inter_arrivals)
    queue_length = np.zeros_like(times)
    
    for i in range(1, num_customers):
        queue_length[i] = max(queue_length[i-1] + 1 - (times[i] - times[i-1])*mu, 0)
    
    fig, ax = plt.subplots()
    ax.plot(times, queue_length, drawstyle='steps-post')
    ax.set_xlabel("Waktu")
    ax.set_ylabel("Panjang Antrian")
    ax.set_title("Dinamika Panjang Antrian")
    st.pyplot(fig)
    
    # Performance Metrics
    rho = lambda_/mu
    Lq = rho**2/(1 - rho)
    Wq = Lq/lambda_
    
    st.subheader("Metrik Kinerja")
    st.write(f"Utilization (ρ): {rho:.2f}")
    st.write(f"Rata-rata Pelanggan dalam Antrian (Lq): {Lq:.2f}")
    st.write(f"Rata-rata Waktu Tunggu (Wq): {Wq:.2f} menit")

with tab4:  # Other Models
    st.header("Break-even Point Analysis")
    
    fixed_cost = st.number_input("Biaya Tetap ($)", value=5000)
    variable_cost = st.number_input("Biaya Variabel per Unit ($)", value=10)
    price = st.number_input("Harga Jual per Unit ($)", value=25)
    
    break_even = fixed_cost/(price - variable_cost)
    
    x = np.linspace(0, 1000, 100)
    revenue = price * x
    total_cost = fixed_cost + variable_cost * x
    
    fig, ax = plt.subplots()
    ax.plot(x, revenue, label='Pendapatan')
    ax.plot(x, total_cost, label='Biaya Total')
    ax.axvline(break_even, color='r', linestyle='--', label='Break-even')
    ax.set_xlabel("Jumlah Unit")
    ax.set_ylabel("Dolar ($)")
    ax.legend()
    
    st.subheader("Hasil Analisis")
    st.write(f"Break-even Point: {break_even:.2f} unit")
    st.pyplot(fig)

if __name__ == "__main__":
    st.write("Aplikasi Model Matematika Industri")

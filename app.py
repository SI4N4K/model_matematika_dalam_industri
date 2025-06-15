import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pulp
from math import sqrt
from scipy.optimize import linprog
import sympy as sp

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

tab1, tab2, tab3, tab4 = st.tabs(["Optimasi Produksi", "Model Persediaan", "Model Antrian", "Model Lain"])

with tab1:
    st.title("🏭 Optimasi Produksi - PT. Sinar Terang")
  
st.markdown("""
Aplikasi ini membantu PT. Sinar Terang menentukan jumlah produksi optimal untuk dua produk:
- Produk A: Blender
- Produk B: Pemanggang Roti

Tujuannya adalah untuk memaksimalkan keuntungan, dengan batasan waktu mesin yang tersedia per minggu.
""")

with st.form("input_form"):
    st.subheader("🔧 Masukkan Parameter Produksi")

    col1, col2 = st.columns(2)

    with col1:
        profit_A = st.number_input("Keuntungan per unit Blender (Rp)", value=40000, step=1000, min_value=0)
        time_A = st.number_input("Jam mesin per unit Blender", value=2.0, step=0.1, min_value=0.1)
    
    with col2:
        profit_B = st.number_input("Keuntungan per unit Pemanggang Roti (Rp)", value=60000, step=1000, min_value=0)
        time_B = st.number_input("Jam mesin per unit Pemanggang Roti", value=3.0, step=0.1, min_value=0.1)
    
    total_time = st.number_input("Total jam mesin tersedia per minggu", value=100.0, step=1.0, min_value=1.0)

    submitted = st.form_submit_button("🔍 Hitung Produksi Optimal")

if submitted:
    c = [-profit_A, -profit_B]
    A = [[time_A, time_B]]
    b = [total_time]
    bounds = [(0, None), (0, None)]

    result = linprog(c, A_ub=A, b_ub=b, bounds=bounds, method='highs')

    st.subheader("📊 Hasil Optimasi")

    if result.success:
        x = result.x[0]
        y = result.x[1]
        max_profit = -result.fun

        st.success("Solusi optimal ditemukan ✅")
        st.write(f"🔹 Jumlah Blender (Produk A): **{x:.2f} unit")
        st.write(f"🔹 Jumlah Pemanggang Roti (Produk B): **{y:.2f} unit")
        st.write(f"💰 Total keuntungan maksimal: Rp {max_profit:,.0f}")

        # ===== VISUALISASI =====
        st.subheader("📉 Visualisasi Daerah Solusi & Titik Optimal")

        fig, ax = plt.subplots(figsize=(7, 5))

        x_vals = np.linspace(0, total_time / time_A + 5, 400)
        y_vals = (total_time - time_A * x_vals) / time_B
        y_vals = np.maximum(0, y_vals)

        ax.plot(x_vals, y_vals, label="Batas Waktu Mesin", color="blue")
        ax.fill_between(x_vals, 0, y_vals, alpha=0.2, color="blue", label="Daerah Feasible")

        ax.scatter(x, y, color="red", zorder=5, label="Solusi Optimal")
        ax.set_xlim(left=0)
        ax.set_ylim(bottom=0)
        ax.set_xlabel("Unit Blender (Produk A)")
        ax.set_ylabel("Unit Pemanggang Roti (Produk B)")
        ax.set_title("Visualisasi Optimasi Produksi")
        ax.legend()
        ax.grid(True)

        st.pyplot(fig)

    else:
        st.error("❌ Gagal menemukan solusi optimal.")
with tab2:
        st.header("📦 Kalkulator EOQ", divider="rainbow")
    with st.expander("ℹ️ Tentang Aplikasi"):
        st.write("""
        Aplikasi ini menghitung Economic Order Quantity (EOQ) dan visualisasi biaya total
        menggunakan rumus:  
        **EOQ** = √(2DS/H)  
        **Total Cost** = (D/Q)S + (Q/2)H
        """)

    # ================== INPUT SECTION ==================
    col1, col2, col3 = st.columns(3)
    with col1:
        D = st.number_input("Permintaan Tahunan (unit)", 
                          value=1000, 
                          step=100,
                          format="%d",
                          help="Jumlah total unit yang dibutuhkan per tahun")
    with col2:
        S = st.number_input("Biaya Pemesanan (Rp./pesan)", 
                          value=10.0, 
                          step=1.0,
                          format="%.2f",
                          help="Biaya tetap per pesanan")
    with col3:
        H = st.number_input("Biaya Penyimpanan (Rp./unit/tahun)", 
                          value=0.5, 
                          step=0.1,
                          format="%.2f",
                          help="Biaya penyimpanan per unit per tahun")

    # ================== CALCULATION SECTION ==================
    Q = sqrt((2*D*S)/H)
    TC = (D/Q)*S + (Q/2)*H

    # ================== VISUALIZATION SECTION ==================
    q_values = np.linspace(Q*0.5, Q*1.5, 100)
    tc_values = (D/q_values)*S + (q_values/2)*H

    fig, ax = plt.subplots(figsize=(8,5))
    ax.plot(q_values, tc_values, label='Total Biaya', color='#1f77b4', linewidth=2)
    ax.axvline(Q, color='#ff7f0e', linestyle='--', linewidth=2, label='EOQ')
    ax.set_xlabel("Jumlah Pesanan", fontsize=10)
    ax.set_ylabel("Biaya Total (Rp.)", fontsize=10)
    ax.set_title("Optimasi Biaya Inventory", fontsize=12, pad=20)
    ax.legend(frameon=True, facecolor='#f0f0f0')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.set_facecolor('#f5f5f5')

    # ================== RESULT SECTION ==================
    st.subheader("📊 Hasil Perhitungan", divider="gray")
    result_col1, result_col2 = st.columns(2)
    with result_col1:
        st.metric(label="**EOQ Optimal**", value=f"{Q:.2f} unit")
    with result_col2:
        st.metric(label="**Biaya Total Minimum**", value=f"Rp.{TC:.2f}")

    st.pyplot(fig)
with tab3:
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


with tab4:
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
if __name__ == "__main__":
    st.write("Aplikasi Model Matematika Industri")

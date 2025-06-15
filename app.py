import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from math import sqrt
from scipy.optimize import linprog

st.set_page_config(
    page_title="Industrial Math Models",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar Dokumentasi
with st.sidebar:
    st.header("📖 Panduan Aplikasi")
    st.markdown("""
    **1. Optimasi Produksi**  
    &nbsp;&nbsp;• Masukkan koefisien fungsi tujuan dan kendala  
    &nbsp;&nbsp;• Sistem akan menampilkan solusi optimal

    **2. Model Persediaan**  
    &nbsp;&nbsp;• Input parameter permintaan dan biaya  
    &nbsp;&nbsp;• Hitung EOQ dan biaya total optimal

    **3. Model Antrian**  
    &nbsp;&nbsp;• Simulasikan sistem antrian M/M/1  
    &nbsp;&nbsp;• Visualisasi panjang antrian selama waktu

    **4. Model Industri Lain**  
    &nbsp;&nbsp;• Analisa Break-even point  
    &nbsp;&nbsp;• Analisis sensitivitas parameter
    """)

    st.markdown("---")
    st.caption("Dibuat oleh PT. Sinar Terang © 2025")

tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🏭 Optimasi Produksi",
        "📦 Model Persediaan",
        "⏳ Model Antrian",
        "💡 Model Lain"
    ]
)

with tab1:
    st.title("🏭 Optimasi Produksi - PT. Sinar Terang")
    st.markdown("""
    Tentukan jumlah produksi **optimal** untuk dua produk:
    - **Produk A:** Blender
    - **Produk B:** Pemanggang Roti

    <span style='color:#4e79a7; font-weight:bold;'>Maksimalkan keuntungan dengan batasan waktu mesin per minggu.</span>
    """, unsafe_allow_html=True)

    with st.form("input_form_prod"):
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
            st.write(f"🔹 Jumlah **Blender** (Produk A): <b>{x:.2f} unit</b>", unsafe_allow_html=True)
            st.write(f"🔹 Jumlah <b>Pemanggang Roti</b> (Produk B): <b>{y:.2f} unit</b>", unsafe_allow_html=True)
            st.write(f"💰 <b>Total keuntungan maksimal:</b> <span style='color:#43aa8b; font-size:1.2em;'>Rp {max_profit:,.0f}</span>", unsafe_allow_html=True)

            # Visualisasi
            fig, ax = plt.subplots(figsize=(7, 5))
            x_vals = np.linspace(0, total_time / time_A + 5, 400)
            y_vals = (total_time - time_A * x_vals) / time_B
            y_vals = np.maximum(0, y_vals)

            ax.plot(x_vals, y_vals, label="Batas Waktu Mesin", color="#4e79a7", linewidth=2)
            ax.fill_between(x_vals, 0, y_vals, alpha=0.15, color="#4e79a7", label="Daerah Feasible")
            ax.scatter(x, y, color="#e15759", zorder=5, s=80, label="Solusi Optimal")
            ax.set_xlim(left=0)
            ax.set_ylim(bottom=0)
            ax.set_xlabel("Unit Blender (Produk A)")
            ax.set_ylabel("Unit Pemanggang Roti (Produk B)")
            ax.set_title("Visualisasi Optimasi Produksi")
            ax.legend()
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.set_facecolor('#f7f7f7')
            st.pyplot(fig)
        else:
            st.error("❌ Gagal menemukan solusi optimal. Cek parameter input.")

with tab2:
    st.header("📦 Kalkulator EOQ (Economic Order Quantity)")
    st.markdown("""
    Hitung **EOQ** dan lihat visualisasi biaya total:  

    <span style='font-size:1.1em;'>EOQ = √(2DS/H)</span>  
    <span style='font-size:1.1em;'>Total Cost = (D/Q)S + (Q/2)H</span>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        D = st.number_input("Permintaan Tahunan (unit)", value=1000, step=100, format="%d",
                            help="Jumlah total unit yang dibutuhkan per tahun")
    with col2:
        S = st.number_input("Biaya Pemesanan (Rp./pesan)", value=10.0, step=1.0, format="%.2f",
                            help="Biaya tetap per pesanan")
    with col3:
        H = st.number_input("Biaya Penyimpanan (Rp./unit/tahun)", value=0.5, step=0.1, format="%.2f",
                            help="Biaya penyimpanan per unit per tahun")

    if H > 0:
        Q = sqrt((2*D*S)/H)
        TC = (D/Q)*S + (Q/2)*H

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

        st.subheader("📊 Hasil Perhitungan")
        result_col1, result_col2 = st.columns(2)
        with result_col1:
            st.metric(label="EOQ Optimal", value=f"{Q:.2f} unit")
        with result_col2:
            st.metric(label="Biaya Total Minimum", value=f"Rp {TC:,.2f}")

        st.pyplot(fig)
    else:
        st.error("Biaya penyimpanan (H) harus lebih besar dari 0.")

with tab3:
    st.header("⏳ Model Antrian M/M/1")
    st.markdown("""
    Simulasikan sistem antrian **M/M/1** dan lihat dinamika panjang antrian seiring waktu.
    """)

    lambda_ = st.number_input("Tingkat Kedatangan (λ)", value=0.5, min_value=0.01, step=0.01)
    mu = st.number_input("Tingkat Pelayanan (μ)", value=0.6, min_value=0.01, step=0.01)

    if mu > 0 and lambda_ > 0:
        np.random.seed(42)
        num_customers = 100
        inter_arrivals = np.random.exponential(1/lambda_, num_customers)
        service_times = np.random.exponential(1/mu, num_customers)

        arrival_times = np.cumsum(inter_arrivals)
        queue_length = np.zeros_like(arrival_times)

        for i in range(1, num_customers):
            queue_length[i] = max(queue_length[i-1] + 1 - (arrival_times[i] - arrival_times[i-1])*mu, 0)

        fig, ax = plt.subplots()
        ax.plot(arrival_times, queue_length, drawstyle='steps-post', color='#4e79a7')
        ax.set_xlabel("Waktu")
        ax.set_ylabel("Panjang Antrian")
        ax.set_title("Dinamika Panjang Antrian")
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.set_facecolor('#f7f7f7')
        st.pyplot(fig)

        rho = lambda_/mu
        if rho < 1:
            Lq = rho**2 / (1 - rho)
            Wq = Lq / lambda_
        else:
            Lq = float('inf')
            Wq = float('inf')

        st.subheader("📈 Metrik Kinerja")
        st.markdown(f"""
        - Utilization (ρ): <span style='color:#e15759'><b>{rho:.2f}</b></span>
        - Rata-rata Pelanggan dalam Antrian (Lq): <b>{Lq:.2f}</b>
        - Rata-rata Waktu Tunggu (Wq): <b>{Wq:.2f} satuan waktu</b>
        """, unsafe_allow_html=True)

        if rho >= 1:
            st.warning("Sistem tidak stabil (ρ ≥ 1). Tingkat pelayanan harus lebih besar dari tingkat kedatangan.")
    else:
        st.error("λ dan μ harus lebih besar dari 0.")

with tab4:
    st.header("💡 Analisis Break-even Point")
    st.markdown("""
    Hitung titik **Break-even** serta visualisasi pendapatan dan biaya total terhadap jumlah unit.
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        fixed_cost = st.number_input("Biaya Tetap ($)", value=5000.0, min_value=0.0)
    with col2:
        variable_cost = st.number_input("Biaya Variabel per Unit ($)", value=10.0, min_value=0.0)
    with col3:
        price = st.number_input("Harga Jual per Unit ($)", value=25.0, min_value=0.0)

    if price > variable_cost:
        break_even = fixed_cost / (price - variable_cost)
        x = np.linspace(0, max(break_even * 1.5, 1000), 300)
        revenue = price * x
        total_cost = fixed_cost + variable_cost * x

        fig, ax = plt.subplots(figsize=(8,5))
        ax.plot(x, revenue, label='Pendapatan', color='#43aa8b', linewidth=2)
        ax.plot(x, total_cost, label='Biaya Total', color='#f8961e', linewidth=2)
        ax.axvline(break_even, color='#e15759', linestyle='--', label='Break-even', linewidth=2)
        ax.set_xlabel("Jumlah Unit")
        ax.set_ylabel("Dolar ($)")
        ax.set_title("Break-even Point Analysis")
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.set_facecolor('#f7f7f7')

        st.subheader("📊 Hasil Analisis")
        st.write(f"Break-even Point: <b>{break_even:.2f} unit</b>", unsafe_allow_html=True)
        st.pyplot(fig)
    else:
        st.error("Harga jual per unit harus lebih besar dari biaya variabel per unit.")

st.markdown(
    "<hr style='margin-top:40px; margin-bottom:10px; border:1px solid #e0e0e0;'>",
    unsafe_allow_html=True
)
st.caption("Aplikasi Model Matematika Industri | PT. Sinar Terang — Versi 2025")

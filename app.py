# ========================================
# Author    : Ahmad Sanusi
# Instagram : @a.saan_
# ========================================


from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime
from flask import jsonify

app = Flask(__name__)
DB = 'database.db'

# ================= STATE PANGGILAN TERAKHIR =================
last_called = {
    "nomor": None,
    "poli": None,
    "recall": False
}

# ================= DATABASE =================
def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return render_template("index.html")
@app.route("/about")
def about():
    return render_template("about.html")
# ================= HALAMAN USER =================
@app.route('/user')
def user():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, nama FROM services")
    services = cur.fetchall()
    conn.close()
    return render_template('user.html', services=services)

# ================= AMBIL ANTRIAN (RESET HARIAN) =================
@app.route('/ambil', methods=['POST'])
def ambil_antrian():
    service_id = request.form['service_id']
    today = datetime.now().strftime('%Y-%m-%d')

    conn = get_db()
    cur = conn.cursor()

    # Ambil nama poli
    cur.execute("SELECT nama FROM services WHERE id=?", (service_id,))
    poli = cur.fetchone()['nama']

    # 🔥 NOMOR GLOBAL (SEMUA POLI)
    cur.execute("""
        SELECT MAX(nomor)
        FROM queues
        WHERE DATE(waktu_ambil)=?
    """, (today,))

    last = cur.fetchone()[0]
    nomor_baru = 1 if last is None else last + 1

    waktu = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cur.execute("""
        INSERT INTO queues (nomor, service_id, status, waktu_ambil)
        VALUES (?, ?, 'menunggu', ?)
    """, (nomor_baru, service_id, waktu))

    conn.commit()
    conn.close()

    return render_template(
        'struk.html',
        nomor=nomor_baru,
        poli=poli,
        waktu=datetime.now().strftime('%d-%m-%Y %H:%M')
    )

# ================= ADMIN DASHBOARD =================
@app.route('/admin')
def admin():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT id, nama FROM services")
    services = cur.fetchall()

    data = {}

    for s in services:
        cur.execute("""
            SELECT q.id, q.nomor, q.status, q.waktu_ambil
            FROM queues q
            WHERE q.service_id=?
            AND q.status != 'selesai'
            ORDER BY q.nomor
        """, (s['id'],))
        data[s['nama']] = cur.fetchall()

    conn.close()
    return render_template('admin.html', data=data)

# ================= PANGGIL =================
@app.route('/admin/panggil/<int:id>')
def panggil(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE queues
        SET status='dipanggil'
        WHERE id=?
    """, (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

# ================= SELESAI =================
@app.route('/admin/selesai/<int:id>')
def selesai(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE queues
        SET status='selesai', waktu_selesai=?
        WHERE id=?
    """, (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))
# ================= HALAMAN POLI =================
@app.route('/admin/poli')
def manage_poli():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT id, nama FROM services ORDER BY id ASC")
    polies = cur.fetchall()
    conn.close()
    return render_template('admin_poli.html', polies=polies)

# ================= TAMBAH POLI =================
@app.route('/admin/poli/add', methods=['POST'])
def poli_add():
    nama = request.form.get('nama', '').strip()
    if not nama:
        return jsonify({'success': False, 'error': 'Nama poli harus diisi'})

    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO services (nama) VALUES (?)", (nama,))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    return jsonify({'success': True, 'id': new_id, 'nama': nama})

# ================= EDIT POLI =================
@app.route('/admin/poli/edit/<int:id>', methods=['POST'])
def edit_poli(id):
    nama = request.form.get('nama', '').strip()
    if not nama:
        return jsonify({'success': False, 'error': 'Nama tidak boleh kosong'})

    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE services SET nama=? WHERE id=?", (nama, id))
    conn.commit()
    conn.close()

    return jsonify({'success': True, 'id': id, 'nama': nama})

# ================= HAPUS POLI =================
@app.route('/admin/poli/delete/<int:id>', methods=['DELETE'])
def poli_delete(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM services WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return jsonify({'success': True})



# ================= GRAFIK + TOTAL =================
@app.route('/grafik')
def grafik():
    conn = get_db()
    cur = conn.cursor()

    mode  = request.args.get('mode', 'harian')
    bulan = request.args.get('bulan', datetime.now().strftime('%m'))
    tahun = request.args.get('tahun', datetime.now().strftime('%Y'))

    # ================= TENTUKAN FORMAT GROUP =================
    if mode == 'harian':
        group_fmt = '%d'
    elif mode == 'bulanan':
        group_fmt = '%m'
    else:
        group_fmt = '%Y'

    # ================= AMBIL SEMUA POLI =================
    cur.execute("SELECT id, nama FROM services")
    polis = cur.fetchall()

    labels = []
    datasets = []

    # ================= LABEL (X AXIS) =================
    if mode == 'harian':
        cur.execute("""
            SELECT strftime('%d', waktu_ambil) grp, COUNT(*) total
            FROM queues
            WHERE waktu_ambil IS NOT NULL
            AND strftime('%m', waktu_ambil)=?
            AND strftime('%Y', waktu_ambil)=?
            GROUP BY grp
            ORDER BY grp
        """, (bulan, tahun))
    elif mode == 'bulanan':
        cur.execute("""
            SELECT strftime('%m', waktu_ambil) grp, COUNT(*) total
            FROM queues
            WHERE waktu_ambil IS NOT NULL
            AND strftime('%Y', waktu_ambil)=?
            GROUP BY grp
            ORDER BY grp
        """, (tahun,))
    else:  # tahunan
        cur.execute("""
            SELECT strftime('%Y', waktu_ambil) grp, COUNT(*) total
            FROM queues
            WHERE waktu_ambil IS NOT NULL
            GROUP BY grp
            ORDER BY grp
        """)

    rows = cur.fetchall()
    label_map = {r['grp'].lstrip('0'): r['total'] for r in rows if r['grp']}
    labels = list(label_map.keys())

    # ================= DATASET PER POLI =================
    for poli in polis:
        data_map = {l: 0 for l in labels}

        if mode == 'harian':
            query = """
                SELECT strftime('%d', waktu_ambil) grp, COUNT(*)
                FROM queues
                WHERE service_id=? AND strftime('%m', waktu_ambil)=? AND strftime('%Y', waktu_ambil)=?
                GROUP BY grp ORDER BY grp
            """
            params = (poli['id'], bulan, tahun)
        elif mode == 'bulanan':
            query = """
                SELECT strftime('%m', waktu_ambil) grp, COUNT(*)
                FROM queues
                WHERE service_id=? AND strftime('%Y', waktu_ambil)=?
                GROUP BY grp ORDER BY grp
            """
            params = (poli['id'], tahun)
        else:  # tahunan
            query = """
                SELECT strftime('%Y', waktu_ambil) grp, COUNT(*)
                FROM queues
                WHERE service_id=? GROUP BY grp ORDER BY grp
            """
            params = (poli['id'],)

        cur.execute(query, params)
        for r in cur.fetchall():
            if r['grp']:
                key = r['grp'].lstrip('0')
                if key in data_map:
                    data_map[key] = r[1]

        datasets.append({
            "label": poli['nama'],
            "data": list(data_map.values())
        })

    # ================= TOTAL HARIN, BULAN, TAHUN =================
    # Total Harian
    cur.execute("""
        SELECT COUNT(*) as total_harian
        FROM queues
        WHERE DATE(waktu_ambil) = ?
    """, (datetime.now().strftime('%Y-%m-%d'),))
    total_harian = cur.fetchone()['total_harian']

    # Total Bulanan
    cur.execute("""
        SELECT COUNT(*) as total_bulanan
        FROM queues
        WHERE strftime('%m', waktu_ambil) = ?
        AND strftime('%Y', waktu_ambil) = ?
    """, (bulan, tahun))
    total_bulanan = cur.fetchone()['total_bulanan']

    # Total Tahunan
    cur.execute("""
        SELECT COUNT(*) as total_tahunan
        FROM queues
        WHERE strftime('%Y', waktu_ambil) = ?
    """, (tahun,))
    total_tahunan = cur.fetchone()['total_tahunan']

    conn.close()

    return render_template(
        'grafik.html',
        labels=labels,
        datasets=datasets,
        bulan=bulan,
        tahun=tahun,
        mode=mode,
        total_harian=total_harian,
        total_bulanan=total_bulanan,
        total_tahunan=total_tahunan
    )

# ================= PANGGIL ULANG =================

@app.route('/display')
def display():
    conn = get_db()
    cur = conn.cursor()

    today = datetime.now().strftime('%Y-%m-%d')
    tahun = datetime.now().year

    # Ambil antrian TERAKHIR yang DIPANGGIL (global)
    # Perhatikan: Pastikan kolom 'waktu_panggil' ada di tabel queues Anda
    cur.execute("""
        SELECT q.nomor, s.nama AS poli
        FROM queues q
        JOIN services s ON q.service_id = s.id
        WHERE q.status = 'dipanggil'
        AND DATE(q.waktu_ambil) = ?
        ORDER BY q.id DESC 
        LIMIT 1
    """, (today,))
    dipanggil = cur.fetchone()

    # Ambil BERIKUTNYA (global)
    cur.execute("""
        SELECT q.nomor
        FROM queues q
        WHERE q.status = 'menunggu'
        AND DATE(q.waktu_ambil) = ?
        ORDER BY q.nomor ASC
        LIMIT 1
    """, (today,))
    berikutnya = cur.fetchone()
    conn.close()

    data = {
        "poli": dipanggil["poli"] if dipanggil else "Silakan Antri",
        "dipanggil": dipanggil["nomor"] if dipanggil else "-",
        "berikutnya": berikutnya["nomor"] if berikutnya else "-"
    }

    # 🔥 LOGIKA KRUSIAL: Jika permintaan datang dari JS (Fetch), balas dengan JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(data)

    # Jika dibuka biasa lewat browser, balas dengan HTML
    return render_template("display.html", data=data, tahun=tahun)

# ================= RUN =================
if __name__ == '__main__':
    app.run(debug=True)

# Sistem Pengaduan Masyarakat dengan Flask dan MySQL (XAMPP)
# Fitur:
# - User bisa tambah pengaduan dan melihat pengaduan + tanggapan tanpa login
# - Admin bisa login, logout, melihat, menghapus, dan memberi tanggapan pada pengaduan

from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'secret_key_anda'  # Digunakan untuk session admin

# Koneksi ke database MySQL (XAMPP)
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",  # Kosongkan jika default XAMPP
    database="pengaduan_masyarakat1"
)
cursor = db.cursor()

# Halaman utama: tampilkan semua pengaduan dan tanggapan
@app.route('/')
def index():
    cursor.execute("""
        SELECT pengaduan.pengaduan_id,pengaduan.nama, pengaduan.isi, pengaduan.tanggal, tanggapan.id, tanggapan.tanggapan, tanggapan.tanggal
        FROM pengaduan
        LEFT JOIN tanggapan ON pengaduan.pengaduan_id = tanggapan.pengaduan_id
        ORDER BY pengaduan.tanggal DESC;
    """)
    data = cursor.fetchall()
    return render_template('index.html', data=data)

# Form tambah pengaduan oleh user
@app.route('/tambah', methods=['GET', 'POST'])
def tambah():
    if request.method == 'POST':
        nama = request.form['nama']
        isi = request.form['isi']
        no_telp = request.form['no_telp']
        cursor.execute("INSERT INTO pengaduan (nama, isi, no_telp) VALUES (%s, %s, %s )", (nama, isi, no_telp))
        db.commit()
        return redirect(url_for('index'))
    return render_template('tambah.html')

# Halaman login admin
@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (username, password))
        admin = cursor.fetchone()
        if admin:
            session['admin'] = username
            return redirect(url_for('dashboard'))
    return render_template('login.html')

# Logout admin
@app.route('/admin/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

# Halaman dashboard admin
@app.route('/admin/dashboard')
def dashboard():
    if 'admin' not in session:
        return redirect(url_for('login'))
    cursor.execute("SELECT * FROM pengaduan LEFT JOIN tanggapan ON pengaduan.pengaduan_id = tanggapan.pengaduan_id")
    data = cursor.fetchall()
    return render_template('dashboard.html', data=data)

@app.route('/admin/user')
def user():
    if 'admin' not in session:
        return redirect(url_for('login'))
    cursor.execute("SELECT * FROM pengaduan")
    data = cursor.fetchall()
    return render_template('user.html', data=data)

@app.route('/admin/tanggapan')
def tanggapan():
    if 'admin' not in session:
        return redirect(url_for('login'))
    cursor.execute("SELECT pengaduan.tanggal, pengaduan.isi, tanggapan.tanggapan FROM pengaduan LEFT JOIN tanggapan ON pengaduan.pengaduan_id = tanggapan.pengaduan_id")
    data = cursor.fetchall()
    return render_template('tanggapan.html', data=data)


# Fitur hapus pengaduan oleh admin
@app.route('/admin/delete/<int:pengaduan_id>')
def delete(pengaduan_id):
    if 'admin' not in session:
        return redirect(url_for('login'))
    
    # Hapus semua tanggapan yang terkait terlebih dahulu
    cursor.execute("DELETE FROM tanggapan WHERE pengaduan_id=%s", (pengaduan_id,))
    db.commit()

    # Baru hapus pengaduan
    cursor.execute("DELETE FROM pengaduan WHERE pengaduan_id=%s", (pengaduan_id,))
    db.commit()

    return redirect(url_for('dashboard'))

# Admin memberi tanggapan terhadap pengaduan
@app.route('/admin/tanggapi/<int:pengaduan_id>', methods=['GET', 'POST'])
def tanggapi(pengaduan_id):
    if 'admin' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        tanggapan = request.form['tanggapan']
        cursor.execute("INSERT INTO tanggapan (pengaduan_id, tanggapan) VALUES (%s, %s)", (pengaduan_id, tanggapan))
        db.commit()
        return redirect(url_for('dashboard'))
    cursor.execute("SELECT * FROM pengaduan WHERE pengaduan_id=%s", (pengaduan_id,))
    pengaduan = cursor.fetchone()
    return render_template('tanggapi.html', pengaduan=pengaduan)

if __name__ == '__main__':
    app.run(debug=True)

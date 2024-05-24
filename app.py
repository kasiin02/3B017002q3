from flask import Flask, session, render_template, request, redirect, url_for, g
from flask_session import Session
import sqlite3

app = Flask(__name__)  # __name__ 代表目前執行的模組

app.secret_key = 'mysecretkey'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


def error_log(error: str):
    with open('error.log', 'a', encoding='UTF-8') as f:
        f.write(f"error: {error}\n")


# 在每次請求之前運行的函數
@app.before_request
def before_request():
    g.db = sqlite3.connect('mydb.db')
    g.db.row_factory = sqlite3.Row  # 設置 row_factory，幫助取值方便


@app.route('/')
def index():
    '''
    若不存在使用者的 session 時，需導向至【登入路由 /login】
    若存在使用者的 session 時，則依據 session 取得資料表該使用者之資料，一併傳送給 index.html 網頁樣板
    若發生例外時，將詳細的錯誤訊息寫入 error.log 檔，並呼叫 error.html 網頁樣板，簡單地告知使用者發生了例外
    '''
    try:
        if 'nm' not in session:
            return redirect(url_for('login'))
        else:
            cur = g.db.cursor()
            cur.execute("SELECT * FROM member WHERE nm = ?", (session['nm'],))
            user_data = cur.fetchone()
            if user_data:
                return render_template('index.html', user=user_data)
            else:
                session.pop('nm', None)
                return redirect(url_for('login'))  # 使用者資料不存在，重新導向至登入頁面
    except Exception as e:
        error_log(str(e))
        return render_template('error.html', error=str(e))


# 定義登入頁面路由
@app.route('/login', methods=['GET', 'POST'])
def login():
    '''
    若收到 GET 請求時，呼叫 login.html 網頁樣板
    若收到 POST 請求時，接收 username 與 password，以之查詢資料表
    若找到該使用者則重新導向至首頁路由 /
    若找不到該使用者則呼叫 login.html 網頁樣板，並傳送【請輸入正確的帳號密碼】訊息
    若發生例外時，將詳細的錯誤訊息寫入 error.log 檔，並呼叫 error.html 網頁樣板，簡單地告知使用者發生了例外
    '''
    try:
        # 如果是 GET 請求，顯示登入頁面
        if request.method == 'GET':
            return render_template('login.html')
        elif request.method == 'POST':
            useridno = request.form.get('idno')
            password = request.form.get('pwd')

            cur = g.db.cursor()
            cur.execute("SELECT * FROM member WHERE idno = ? AND pwd = ?", (useridno, password))
            user = cur.fetchone()
            if user:
                session['iid'] = user[0]
                session['nm'] = user[1]
                return redirect(url_for('index'))
            else:
                return render_template('login.html', message='請輸入正確的帳號密碼')
    except Exception as e:
        error_log(str(e))
        return render_template('error.html', error=str(e))


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    '''
    內含表單，表單各欄位即個人的基本資料，下方包含 2 個按鈕或連結
    送出
    登出
    '''
    try:
        if 'nm' not in session:
            return redirect(url_for('login'))
        else:
            if request.method == 'GET':
                cur = g.db.cursor()
                cur.execute("SELECT * FROM member WHERE nm = ?", (session['nm'],))
                user_data = cur.fetchone()
                if user_data:
                    return render_template('edit.html', user=user_data)
            elif request.method == 'POST':
                session['nm'] = request.form['nm']
                session['birth'] = request.form['birth']
                session['blood'] = request.form['blood']
                session['phone'] = request.form['phone']
                session['email'] = request.form['email']
                session['idno'] = request.form['idno']
                session['pwd'] = request.form['pwd']
                cur = g.db.cursor()
                cur.execute("UPDATE member SET nm = ?, \
                    birth = ?, \
                    blood = ?, \
                    phone = ?, \
                    email = ?, \
                    idno = ?, \
                    pwd = ? \
                    WHERE iid = ?", (session['nm'],
                                     session['birth'],
                                     session['blood'],
                                     session['phone'],
                                     session['email'],
                                     session['idno'],
                                     session['pwd'],
                                     session['iid']))
                # 提交更改
                g.db.commit()
                cur.execute("SELECT * FROM member WHERE nm = ?", (session['nm'],))
                user_data = cur.fetchone()
                return render_template('index.html', user=user_data)
    except Exception as e:
        error_log(str(e))
        return render_template('error.html', error=str(e))


@app.route('/logout', methods=['GET'])
def logout():
    session.clear()  # 清除所有数據
    return redirect('/')


# 在請求結束後自動關閉資料庫連接
@app.teardown_appcontext
def teardown(exception):
    if hasattr(g, 'db'):
        g.db.close()

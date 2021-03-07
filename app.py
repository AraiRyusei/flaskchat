from flask import *   # Flaskのなかみを全部持ってくる
import sqlite3
app = Flask(__name__)  # アプリの設定

app.secret_key = 'sunabakoza'


@app.route("/")
def jump():
    # ここにチャットルーム一覧をDBからとって、表示するプログラム
    return redirect("/login")


@app.route("/chatroom")
def chatroom_get():
    if "user_id" in session:
        my_id = session["user_id"]
        # ここにチャットルーム一覧をDBからとって、表示するプログラム
        conn = sqlite3.connect('chattest.db')
        c = conn.cursor()
        c.execute(
            "select id, room from chat where user_id1 = ? or user_id2 = ?", (my_id, my_id))
        chat_list = c.fetchall()

        return render_template("/chatroom.html", tpl_chat_list=chat_list)
    else:
        return redirect("/login")


@app.route("/chatroom/<int:other_id>", methods=["POST"])
def chatroom_post(other_id):
    if "user_id" in session:
        # まずはチャットルームがあるかchatidをとってくる
        my_id = session["user_id"]
        print(my_id)
        conn = sqlite3.connect('chattest.db')
        c = conn.cursor()
        c.execute(
            "select id from chat where (user_id1 = ? and user_id2 = ?) or (user_id1 = ? and user_id2 = ?)", (my_id, other_id, other_id, my_id))
        chat_id = c.fetchone()

        print(chat_id)
        # なければ作成、あればスルー
        if chat_id == None:

            c.execute("select name from user where id = ?", (my_id,))
            myname = c.fetchone()[0]
            c.execute("select name from user where id = ?", (other_id,))
            othername = c.fetchone()[0]
            room = myname + "と" + othername + "のチャット"

            c.execute("insert into chat values(null,?,?,?)",
                    (my_id, other_id, room))
            conn.commit()
            c.execute(
                "select id from chat where (user_id1 = ? and user_id2 = ?) or (user_id1 = ? and user_id2 = ?)", (my_id, other_id, other_id, my_id))
            chat_id = c.fetchone()
        conn.close()
        print(chat_id)
        return redirect("/chat/{}".format(chat_id[0]))
    else:
        return redirect("/login")


@app.route("/chat/<int:chatid>")
def chat_get(chatid):
    if "user_id" in session:
        my_id = session["user_id"]
        # ここにチャットをDBからとって、表示するプログラム
        conn = sqlite3.connect('chattest.db')
        c = conn.cursor()
        c.execute(
            "select chatmess.to_user, chatmess.from_user, chatmess.message, user.name from chatmess inner join user on chatmess.from_user = user.id where chat_id = ?", (chatid,))
        chat_fetch = c.fetchall()
        chat_info = []
        for chat in chat_fetch:
            chat_info.append(
                {"to": chat[0], "from": chat[1], "message": chat[2], "fromname": chat[3]})
        c.execute("select room from chat where id = ?", (chatid,))
        room_name = c.fetchone()[0]
        c.close()
        return render_template("chat.html", chat_list=chat_info, link_chatid=chatid, tpl_room_name=room_name,tpl_my_id=my_id)
    else:
        return redirect("/login")

@app.route("/chat/<int:chatid>", methods=["POST"])
def chat_post(chatid):
    if "user_id" in session:
        # ここにチャットの送信ボタンが押されたときにDBに格納するプログラム
        my_id = session["user_id"]
        chat_message = request.form.get("input_message")
        conn = sqlite3.connect('chattest.db')
        c = conn.cursor()
        c.execute(
            "select user_id1, user_id2 from chat where id = ?", (chatid,))
        chat_user = c.fetchone()
        print(chat_user)
        if my_id != chat_user[0]:
            to_id = chat_user[0]
        else:
            to_id = chat_user[1]
        print(to_id)
        c.execute("insert into chatmess values(null,?,?,?,?)",
                (chatid, to_id, my_id, chat_message))
        conn.commit()
        c.close()

        return redirect("/chat/{}".format(chatid))
    else:
        return redirect("/login")


@app.route("/userlist")
def userlist():
    conn = sqlite3.connect('chattest.db')
    c = conn.cursor()
    c.execute("select id, name from user")
    user_info = c.fetchall()
    conn.close()
    return render_template("userlist.html", tpl_user_info=user_info)



@app.route("/login")
def login_get():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    name = request.form.get("name")
    password = request.form.get("password")
    conn = sqlite3.connect('chattest.db')
    c = conn.cursor()
    c.execute(
        "select id from user where name = ? and password = ?", (name, password))
    user_id = c.fetchone()
    conn.close()
    print(type(user_id))
    if user_id is None:
        return render_template("login.html")
    else:
        session['user_id'] = user_id[0]
        return redirect("/userlist")


@app.route("/regist", methods=["POST"])
def regist():
    name = request.form.get("name")
    password = request.form.get("password")
    conn = sqlite3.connect('chattest.db')
    c = conn.cursor()
    c.execute("insert into user values(null,?,?)", (name, password))
    conn.commit()
    conn.close()
    return redirect("/login")


@app.route("/logout")
def logout():
    session.pop('user_id', None)
    return redirect("/login")


    
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")

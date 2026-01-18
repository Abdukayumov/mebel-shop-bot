import telebot
from telebot import types
import sqlite3

TOKEN = "7971999489:AAGlEZZNvgzx-iQtf6O294Iuqs-I37tHU4A"
ADMIN_ID = 5938434244

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

db = sqlite3.connect("shop.db", check_same_thread=False)
cur = db.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS categories(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
parent INTEGER)""")

cur.execute("""CREATE TABLE IF NOT EXISTS products(
id INTEGER PRIMARY KEY AUTOINCREMENT,
category_id INTEGER,
name TEXT,
price INTEGER,
qty INTEGER,
active INTEGER)""")
db.commit()

# ===== START =====
@bot.message_handler(commands=['start'])
def start(m):
    kb=types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🛒 Katalog")
    bot.send_message(m.chat.id,"Xush kelibsiz!",reply_markup=kb)

# ===== KATALOG =====
@bot.message_handler(func=lambda m:m.text=="🛒 Katalog")
def catalog(m):
    show_categories(m.chat.id,0)

def show_categories(chat_id,parent):
    cur.execute("SELECT id,name FROM categories WHERE parent=?",(parent,))
    cats=cur.fetchall()
    kb=types.InlineKeyboardMarkup()
    for i,n in cats:
        kb.add(types.InlineKeyboardButton(n,callback_data=f"cat_{i}"))
    bot.send_message(chat_id,"📂 Kategoriya:",reply_markup=kb)

@bot.callback_query_handler(func=lambda c:c.data.startswith("cat_"))
def open_cat(c):
    cid=c.data.split("_")[1]
    cur.execute("SELECT id,name,price,qty,active FROM products WHERE category_id=?",(cid,))
    items=cur.fetchall()

    text=""
    for i,n,p,q,a in items:
        if a:
            text+=f"🔹 {n} — {p} so‘m ({q} dona)\n"
        else:
            text+=f"🔹 {n} — ❌ TUGADI\n"

    if not text:
        text="Bu kategoriyada mahsulot yo‘q"

    kb=types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("⬅ Orqaga",callback_data="back"))
    bot.send_message(c.message.chat.id,text,reply_markup=kb)

@bot.callback_query_handler(func=lambda c:c.data=="back")
def back(c):
    show_categories(c.message.chat.id,0)

# ===== ADMIN =====
@bot.message_handler(commands=['admin'])
def admin(m):
    if m.chat.id!=ADMIN_ID: return
    bot.send_message(m.chat.id,
"""/addcat → Kategoriya qo‘shish
/delcat → Kategoriya o‘chirish
/addprod → Mahsulot qo‘shish
/delprod → Mahsulot o‘chirish
/stopprod → Mahsulot tugadi
""")

@bot.message_handler(commands=['addcat'])
def addcat(m):
    bot.send_message(m.chat.id,"Kategoriya nomi:")
    bot.register_next_step_handler(m,save_cat)

def save_cat(m):
    cur.execute("INSERT INTO categories(name,parent) VALUES(?,?)",(m.text,0))
    db.commit()
    bot.send_message(m.chat.id,"Kategoriya qo‘shildi!")

@bot.message_handler(commands=['delcat'])
def delcat(m):
    bot.send_message(m.chat.id,"Kategoriya ID:")
    bot.register_next_step_handler(m,del_cat2)

def del_cat2(m):
    cur.execute("DELETE FROM categories WHERE id=?",(m.text,))
    db.commit()
    bot.send_message(m.chat.id,"O‘chirildi")

@bot.message_handler(commands=['addprod'])
def addprod(m):
    bot.send_message(m.chat.id,"Format:\nKategoriyaID, Nomi, Narx, Soni")
    bot.register_next_step_handler(m,save_prod)

def save_prod(m):
    cid,n,p,q=[x.strip() for x in m.text.split(",")]
    cur.execute("INSERT INTO products(category_id,name,price,qty,active) VALUES(?,?,?,?,1)",
                (cid,n,p,q))
    db.commit()
    bot.send_message(m.chat.id,"Mahsulot qo‘shildi!")

@bot.message_handler(commands=['delprod'])
def delprod(m):
    bot.send_message(m.chat.id,"Mahsulot ID:")
    bot.register_next_step_handler(m,del_prod2)

def del_prod2(m):
    cur.execute("DELETE FROM products WHERE id=?",(m.text,))
    db.commit()
    bot.send_message(m.chat.id,"Mahsulot o‘chirildi")

@bot.message_handler(commands=['stopprod'])
def stopprod(m):
    bot.send_message(m.chat.id,"Mahsulot ID:")
    bot.register_next_step_handler(m,stop_prod2)

def stop_prod2(m):
    cur.execute("UPDATE products SET active=0 WHERE id=?",(m.text,))
    db.commit()
    bot.send_message(m.chat.id,"Mahsulot TUGADI deb belgilandi")

print("Bot ishga tushdi")
bot.infinity_polling()
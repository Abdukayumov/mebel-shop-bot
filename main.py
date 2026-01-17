import telebot
import sqlite3

TOKEN = "7971999489:AAHH-L0aYMbItLEItIubaUVyN2VKvkxobzg"

bot = telebot.TeleBot(TOKEN)

conn = sqlite3.connect("shop.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS categories(id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT)")
cur.execute("CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT, category_id INTEGER, name TEXT, price INTEGER)")
conn.commit()

@bot.message_handler(commands=["start"])
def start(m):
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🛒 Katalog")
    bot.send_message(m.chat.id,"Xush kelibsiz!",reply_markup=kb)

@bot.message_handler(func=lambda m:m.text=="🛒 Katalog")
def catalog(m):
    cur.execute("SELECT id,name FROM categories")
    cats=cur.fetchall()
    kb=telebot.types.InlineKeyboardMarkup()
    for i,n in cats:
        kb.add(telebot.types.InlineKeyboardButton(n,callback_data=f"c_{i}"))
    bot.send_message(m.chat.id,"Kategoriya:",reply_markup=kb)

@bot.callback_query_handler(func=lambda c:c.data.startswith("c_"))
def prod(c):
    cid=c.data.split("_")[1]
    cur.execute("SELECT name,price FROM products WHERE category_id=?",(cid,))
    for n,p in cur.fetchall():
        bot.send_message(c.message.chat.id,f"{n} — {p} so‘m")

ADMIN_ID = 5938434244

@bot.message_handler(commands=["admin"])
def admin(m):
    if m.chat.id != ADMIN_ID: return
    kb = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("➕ Kategoriya", "➕ Mahsulot")
    bot.send_message(m.chat.id,"Admin panel:",reply_markup=kb)

@bot.message_handler(func=lambda m:m.text=="➕ Kategoriya")
def add_cat(m):
    bot.send_message(m.chat.id,"Kategoriya nomi:")
    bot.register_next_step_handler(m,save_cat)

def save_cat(m):
    cur.execute("INSERT INTO categories(name) VALUES(?)",(m.text,))
    conn.commit()
    bot.send_message(m.chat.id,"✅ Kategoriya qo‘shildi")

@bot.message_handler(func=lambda m:m.text=="➕ Mahsulot")
def add_prod(m):
    cur.execute("SELECT id,name FROM categories")
    t="Kategoriya ID:\n"
    for i,n in cur.fetchall(): t+=f"{i}. {n}\n"
    bot.send_message(m.chat.id,t)
    bot.register_next_step_handler(m,prod_name)

def prod_name(m):
    m.cid=int(m.text)
    bot.send_message(m.chat.id,"Mahsulot nomi:")
    bot.register_next_step_handler(m,prod_price)

def prod_price(m):
    m.name=m.text
    bot.send_message(m.chat.id,"Narxi:")
    bot.register_next_step_handler(m,prod_save)

def prod_save(m):
    cur.execute("INSERT INTO products(category_id,name,price) VALUES(?,?,?)",(m.cid,m.name,int(m.text)))
    conn.commit()
    bot.send_message(m.chat.id,"✅ Mahsulot qo‘shildi")

bot.infinity_polling()
import telebot
from telebot import types
import sqlite3

TOKEN = "7971999489:AAHH-L0aYMbItLEItIubaUVyN2VKvkxobzg"
ADMIN_ID = 5938434244

bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

conn = sqlite3.connect("shop.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS categories(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT,category_id INTEGER,name TEXT,price INTEGER,qty INTEGER)""")
conn.commit()

# ===== START =====
@bot.message_handler(commands=['start'])
def start(m):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🛒 Katalog", "📞 Aloqa")
    bot.send_message(m.chat.id,"Xush kelibsiz Mebel Magazin botiga!",reply_markup=kb)

@bot.message_handler(func=lambda m:m.text=="📞 Aloqa")
def aloqa(m):
    bot.send_message(m.chat.id,"Savollar uchun: @Admin")

# ===== KATALOG =====
@bot.message_handler(func=lambda m:m.text=="🛒 Katalog")
def katalog(m):
    cursor.execute("SELECT id,name FROM categories")
    cats=cursor.fetchall()
    kb=types.InlineKeyboardMarkup()
    for i,n in cats:
        kb.add(types.InlineKeyboardButton(n,callback_data=f"cat_{i}"))
    bot.send_message(m.chat.id,"📂 Kategoriya tanlang:",reply_markup=kb)

@bot.callback_query_handler(func=lambda c:c.data.startswith("cat_"))
def open_cat(c):
    cid=c.data.split("_")[1]
    cursor.execute("SELECT name,price,qty FROM products WHERE category_id=?",(cid,))
    items=cursor.fetchall()
    txt="📦 <b>Mahsulotlar:</b>\n\n"
    for n,p,q in items:
        txt+=f"🔹 {n}\n💰 {p} so‘m\n📦 {q} dona\n\n"
    kb=types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🛒 Buyurtma berish",callback_data=f"order_{cid}"))
    bot.send_message(c.message.chat.id,txt,reply_markup=kb)

# ===== BUYURTMA =====
@bot.callback_query_handler(func=lambda c:c.data.startswith("order_"))
def order(c):
    c.message.cid=c.data.split("_")[1]
    kb=types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("💵 Naqd",callback_data="pay_cash"),
           types.InlineKeyboardButton("💳 Karta",callback_data="pay_card"))
    bot.send_message(c.message.chat.id,"💳 To‘lov turini tanlang:",reply_markup=kb)

@bot.callback_query_handler(func=lambda c:c.data in ["pay_cash","pay_card"])
def pay(c):
    c.message.pay="Naqd" if c.data=="pay_cash" else "Karta"
    kb=types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(types.KeyboardButton("📞 Telefon raqamni yuborish",request_contact=True))
    bot.send_message(c.message.chat.id,"📞 Telefon raqamingizni yuboring:",reply_markup=kb)

@bot.message_handler(content_types=['contact'])
def contact(m):
    phone=m.contact.phone_number
    user=m.from_user
    order_text=f"""
🛒 <b>Yangi buyurtma</b>
👤 {user.first_name}
📞 {phone}
💳 To‘lov: {m.chat.pay if hasattr(m.chat,'pay') else ''}
"""
    bot.send_message(ADMIN_ID,order_text)
    bot.send_message(m.chat.id,"✅ Buyurtmangiz qabul qilindi! Tez orada bog‘lanamiz 😊",
                     reply_markup=types.ReplyKeyboardRemove())

# ===== ADMIN =====
@bot.message_handler(commands=['admin'])
def admin(m):
    if m.chat.id!=ADMIN_ID: return
    bot.send_message(m.chat.id,"/addcat\n/addprod")

@bot.message_handler(commands=['addcat'])
def addcat(m):
    if m.chat.id!=ADMIN_ID: return
    bot.send_message(m.chat.id,"Kategoriya nomi:")
    bot.register_next_step_handler(m,save_cat)

def save_cat(m):
    cursor.execute("INSERT INTO categories(name) VALUES(?)",(m.text,))
    conn.commit()
    bot.send_message(m.chat.id,"Kategoriya saqlandi!")

@bot.message_handler(commands=['addprod'])
def addprod(m):
    if m.chat.id!=ADMIN_ID: return
    bot.send_message(m.chat.id,"Format: KategoriyaID, Mahsulot nomi, Narx, Soni")
    bot.register_next_step_handler(m,save_prod)

def save_prod(m):
    try:
        cid,name,price,qty=[x.strip() for x in m.text.split(",")]
        cursor.execute("INSERT INTO products(category_id,name,price,qty) VALUES(?,?,?,?)",(cid,name,price,qty))
        conn.commit()
        bot.send_message(m.chat.id,"Mahsulot qo‘shildi!")
    except:
        bot.send_message(m.chat.id,"Xato format!")

print("Bot ishga tushdi...")
bot.infinity_polling()
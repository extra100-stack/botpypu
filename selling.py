from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import logging
import time

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Telegram API Credentials
API_ID = 23057859
API_HASH = "4df51e414187bf527d5969ca48ce72df"
BOT_TOKEN = "8041216769:AAHL-JfEz72jAt_jLQZ4KjxL3PulmDERfyg"

# Admin ID
ADMIN_ID = 7893772903  # Replace with your actual Telegram ID

# UPI Details
UPI_ID = "testupi@paytm"  
QR_CODE_URL = "https://via.placeholder.com/300"  

# Initialize the Bot
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Product Prices and Codes
database = {
    "yt_premium": ("🔥 YT Premium", "₹99/month", "YT123"),
    "netflix": ("📺 Netflix", "₹199/month", "NF456"),
    "amazon_prime": ("🎬 Amazon Prime", "₹149/month", "AP789"),
    "jio_saavan": ("🎵 Jio Saavan", "₹49/month", "JS101")
}

pending_orders = {}

# /ping Command
@app.on_message(filters.command("ping"))
async def ping(client, message):
    start_time = time.time()
    reply = await message.reply_text("🏓 Pong!")
    latency = (time.time() - start_time) * 1000
    await reply.edit_text(f"🏓 Pong! `{int(latency)}ms`")

# /user Command
@app.on_message(filters.command("user"))
async def user_info(client, message):
    user = message.from_user
    await message.reply_text(
        f"👤 **User Info:**\n"
        f"🆔 ID: `{user.id}`\n"
        f"📛 Name: {user.first_name} {user.last_name or ''}\n"
        f"💬 Username: @{user.username if user.username else 'N/A'}"
    )

# /start Command
@app.on_message(filters.command("start"))
async def start(client, message):
    user = message.from_user.first_name
    await message.reply_text(
        f"👋 Hello {user}!\n\nWelcome to **Hidden Shop**. Select a service below:\n\n"
        "Commands:\n"
        "- /ping - Check bot status\n"
        "- /user - Get your info\n"
        "- /buy <product_code> - Purchase a product\n"
        "- /done <order_code> - Confirm payment",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔥 YT Premium", callback_data="yt_premium"),
             InlineKeyboardButton("📺 Netflix", callback_data="netflix")],
            [InlineKeyboardButton("🎬 Amazon Prime", callback_data="amazon_prime"),
             InlineKeyboardButton("🎵 Jio Saavan", callback_data="jio_saavan")],
            [InlineKeyboardButton("📢 Contact Admin", url="https://t.me/your_admin_username")]
        ])
    )

# /buy Command
@app.on_message(filters.command("buy"))
async def buy(client, message):
    command_parts = message.text.split()
    if len(command_parts) < 2:
        await message.reply_text("❌ Please specify a product code. Example: /buy yt_premium")
        return
    
    product_code = command_parts[1]
    if product_code in database:
        product_name, price, order_code = database[product_code]
        pending_orders[order_code] = message.from_user.id
        await message.reply_text(
            f"✅ **{product_name}**\n💰 Price: {price}\n📌 Order Code: `{order_code}`\n"
            "Use `/buy {order_code}` to proceed with payment."
        )
    elif product_code in pending_orders and pending_orders[product_code] == message.from_user.id:
        await message.reply_text(
            f"💳 **Payment Details**\nUPI ID: `{UPI_ID}`\n"
            "[Click to Pay](upi://pay?pa={UPI_ID}&pn=Hidden%20Shop&cu=INR)",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("📷 Scan QR Code", url=QR_CODE_URL)]]
            )
        )
    else:
        await message.reply_text("❌ Invalid product or order code!")

# /done Command
@app.on_message(filters.command("done"))
async def done(client, message):
    command_parts = message.text.split()
    if len(command_parts) < 2:
        await message.reply_text("❌ Please specify the order code. Example: /done YT123")
        return
    
    order_code = command_parts[1]
    if order_code in pending_orders and pending_orders[order_code] == message.from_user.id:
        await client.send_message(ADMIN_ID, f"📢 Payment received for order `{order_code}` from user {message.from_user.mention}")
        await message.reply_text("✅ Payment confirmation sent! Your order will be processed shortly.")
        del pending_orders[order_code]
    else:
        await message.reply_text("❌ Invalid or expired order code!")

# /user_list Command (For Admin)
@app.on_message(filters.command("user_list") & filters.user(ADMIN_ID))
async def user_list(client, message):
    if not pending_orders:
        await message.reply_text("📭 No pending orders.")
        return
    
    user_details = "📌 **Pending Orders:**\n"
    for order, user_id in pending_orders.items():
        user_details += f"🆔 `{user_id}` - Order `{order}`\n"
    
    await message.reply_text(user_details)

# Callback Query Handler
@app.on_callback_query()
async def callback_handler(client, callback_query: CallbackQuery):
    data = callback_query.data
    if data in database:
        product_name, price, order_code = database[data]
        pending_orders[order_code] = callback_query.from_user.id
        await callback_query.message.edit_text(
            f"✅ **{product_name}**\n💰 Price: {price}\n📌 Order Code: `{order_code}`\n"
            "Use `/buy {order_code}` to proceed with payment."
        )
    else:
        await callback_query.answer("❌ Invalid selection!", show_alert=True)

# Run the Bot
if __name__ == "__main__":
    print("✅ Bot is running...")
    app.run()

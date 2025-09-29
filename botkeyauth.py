import discord
from discord.ext import commands
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import random
import string
import datetime
import os
import json
from dotenv import load_dotenv

# ==== LOAD CONFIG =====
load_dotenv()  # chỉ dùng khi chạy local, Render sẽ ignore nếu không có .env

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")  # token bot
SHEET_NAME = "LicenseKeys"  # tên Google Sheet

# Google API
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Lấy creds từ biến môi trường GOOGLE_CREDS (Render)
creds_json = os.getenv("GOOGLE_CREDS")
if creds_json is None:
    raise ValueError("❌ GOOGLE_CREDS environment variable not found!")

creds = ServiceAccountCredentials.from_json_keyfile_dict(
    json.loads(creds_json), scope
)
client_gs = gspread.authorize(creds)
sheet = client_gs.open(SHEET_NAME).sheet1

# ==== CONFIG OWNER & CHANNEL =====
ALLOWED_CHANNEL_ID = 1422151486183444501  # 👈 kênh duy nhất bot hoạt động
OWNER_IDS = [1127487656608141362, 1422230798144372866]  # 👈 danh sách owner

# ==== DISCORD BOT =====
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


# Hàm tạo key ngẫu nhiên
def generate_key(length=16):
    return ''.join(
        random.choices(string.ascii_uppercase + string.digits, k=length)
    )


@bot.event
async def on_ready():
    print(f"✅ Bot đã đăng nhập thành {bot.user}")


# Middleware: check channel và owner
async def check_permission(ctx):
    if ctx.channel.id != ALLOWED_CHANNEL_ID:
        return False
    if ctx.author.id not in OWNER_IDS:
        await ctx.send("⛔ Bạn không có quyền dùng lệnh này!")
        return False
    return True


# Tạo key mới
@bot.command()
async def createkey(ctx, amount: int = 1, days: int = 30):
    """Tạo key mới: !createkey <số lượng> <số ngày>"""
    if not await check_permission(ctx):
        return

    keys = []
    expiry_date = (datetime.datetime.now() +
                   datetime.timedelta(days=days)).strftime("%d/%m/%Y %H:%M:%S")

    for _ in range(amount):
        key = generate_key()
        sheet.append_row([key, expiry_date, ""])  # thêm vào Sheet
        keys.append(key)

    msg = "\n".join(keys)
    await ctx.send(
        f"✅ Created {amount} keys, valid for {days} days:\n```{msg}```"
    )


# Liệt kê key trong sheet
@bot.command()
async def listkeys(ctx):
    """Hiển thị tất cả key trong Google Sheet"""
    if not await check_permission(ctx):
        return

    data = sheet.get_all_records()
    if not data:
        await ctx.send("📂 No keys found.")
        return

    msg = ""
    for row in data:
        msg += f"🔑 {row['KEY']} | Expiry: {row['EXPIRY_DATE']} | HWID: {row['HWID']}\n"

    await ctx.send(f"📜 **All Keys:**\n{msg}")


# Xóa key
@bot.command()
async def delkey(ctx, key: str):
    """Xóa key khỏi sheet: !delkey <key>"""
    if not await check_permission(ctx):
        return

    data = sheet.get_all_values()
    for i, row in enumerate(data):
        if row[0] == key:
            sheet.delete_rows(i + 1)
            await ctx.send(f"🗑️ Deleted key: `{key}`")
            return
    await ctx.send("❌ Key not found.")


if __name__ == "__main__":
    bot.run(DISCORD_TOKEN)

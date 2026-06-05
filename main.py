import discord
from discord.ext import commands
import asyncio
import json
import os

intents = discord.Intents.default()
intents.guilds = True
intents.guild_messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# اسم ملف قاعدة البيانات اللي هيتحفظ فيه باسوردات السيرفرات
DB_FILE = "guild_passwords.json"
PASSWORD_CHANNEL_NAME = "🔐-enter-password"

# دالة لتحميل الباسوردات من الملف
def load_passwords():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

# دالة لحفظ الباسوردات في الملف
def save_passwords(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# 1. أمر تعيين أو تغيير الباسورد (خاص بالأدمن فقط)
@bot.command()
@commands.has_permissions(administrator=True)
async def setpassword(ctx, new_password: str):
    # مسح الرسالة عشان الباسورد ميبانش في الشات أثناء التجهيز
    try:
        await ctx.message.delete()
    except:
        pass

    passwords = load_passwords()
    # حفظ الباسورد بربطه بـ ID السيرفر الحالي
    passwords[str(ctx.guild.id)] = new_password
    save_passwords(passwords)

    await ctx.send("✅ تم تعيين الباسورد الجديد لسيرفرك بنجاح! (تم مسح رسالتك لحماية الخصوصية)")

# 2. أمر إخفاء كل الرومات وإظهار روم الباسورد
@bot.command()
@commands.has_permissions(manage_channels=True)
async def hideall(ctx):
    passwords = load_passwords()
    guild_id = str(ctx.guild.id)

    # التأكد أولاً إذا كان السيرفر قام بتعيين باسورد أم لا
    if guild_id not in passwords:
        await ctx.send("❌ عذراً، يجب عليك تعيين باسورد للسيرفر أولاً باستخدام أمر: `setpassword [الباسورد]!`")
        return

    everyone = ctx.guild.default_role
    await ctx.send("🛡️ جاري تفعيل وضع الحماية القصوى وإخفاء السيرفر...")

    # البحث عن روم الباسورد أو إنشائها
    password_channel = discord.utils.get(ctx.guild.text_channels, name=PASSWORD_CHANNEL_NAME)
    if not password_channel:
        password_channel = await ctx.guild.create_text_channel(PASSWORD_CHANNEL_NAME)

    # إظهار روم الباسورد للجميع
    await password_channel.set_permissions(everyone, view_channel=True, send_messages=True)

    # إخفاء باقي الرومات
    for channel in ctx.guild.channels:
        if channel.id != password_channel.id:
            await channel.set_permissions(everyone, view_channel=False)

    await password_channel.send("🔒 **السيرفر في وضع الإغلاق التام.**\nاكتب الباسورد هنا لفتح السيرفر مرة أخرى.")

# 3. أمر فتح السيرفر (يشتغل داخل روم الباسورد فقط)
@bot.command()
async def unlock(ctx, *, password_input: str):
    if ctx.channel.name != PASSWORD_CHANNEL_NAME:
        return

    # مسح رسالة المستخدم فوراً لحماية الباسورد
    try:
        await ctx.message.delete()
    except:
        pass

    passwords = load_passwords()
    guild_id = str(ctx.guild.id)
    correct_password = passwords.get(guild_id)

    if password_input == correct_password:
        everyone = ctx.guild.default_role
        status_msg = await ctx.send("🔓 الباسورد صحيح! جاري إلغاء القفل وإعادة السيرفر لطبيعته...")
        
        # إعادة الرومات لوضعها الطبيعي
        for channel in ctx.guild.channels:
            if channel.id != ctx.channel.id:
                await channel.set_permissions(everyone, view_channel=None)
        
        # إخفاء روم الباسورد
        await ctx.channel.set_permissions(everyone, view_channel=False)
        await status_msg.delete()
    else:
        error_msg = await ctx.send("❌ الباسورد غير صحيح! حاول مرة أخرى.")
        await asyncio.sleep(3)
        await error_msg.delete()

@bot.event
async def on_ready():
    print(f'البوت العام شغال وجاهز باسم: {bot.user.name}')

# ضع التوكن الخاص ببوتك هنا
bot.run("MTUxMjUyMjcxODg0OTkyOTM4OA.Gcf3Ax.59hx4RU2d4BUdLGEC8s5MEG72veLek_c86wQs8")


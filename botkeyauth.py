from discord.ui import View, Button

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

    # Nếu tạo nhiều key → gộp thành text
    msg = "\n".join(keys)

    # Gửi kèm nút copy cho key đầu tiên (hoặc cả danh sách nếu bạn muốn)
    view = View()
    copy_button = Button(label="📋 Copy", style=discord.ButtonStyle.primary)

    async def copy_callback(interaction):
        await interaction.response.send_message(
            f"✅ Đây là key của bạn:\n```{msg}```\n*(Bạn có thể copy thủ công từ code block)*",
            ephemeral=True  # chỉ người bấm thấy
        )

    copy_button.callback = copy_callback
    view.add_item(copy_button)

    await ctx.send(
        f"✅ Created {amount} keys, valid for {days} days:\n```{msg}```",
        view=view
    )

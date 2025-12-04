import discord
from discord.ext import commands
from discord import app_commands
import os

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "1446121402267861005"))

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ {bot.user} está online!')
    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f'✅ {len(synced)} comandos sincronizados')
    except Exception as e:
        print(f'❌ Error sincronizando: {e}')

@bot.tree.command(name="hola", description="Saluda al bot ChiChi", guild=discord.Object(id=GUILD_ID))
async def hola(interaction: discord.Interaction):
    await interaction.response.send_message(f"¡Hola {interaction.user.mention}! 👋 Soy ChiChi, tu bot asistente!")

@bot.tree.command(name="ayuda", description="Muestra comandos disponibles", guild=discord.Object(id=GUILD_ID))
async def ayuda(interaction: discord.Interaction):
    embed = discord.Embed(title="📚 Comandos de ChiChi", color=0x00ff00)
    embed.add_field(name="/hola", value="Saluda al bot", inline=False)
    embed.add_field(name="/ayuda", value="Muestra esta ayuda", inline=False)
    embed.add_field(name="/info", value="Info del servidor", inline=False)
    embed.set_footer(text="ChiChi Bot - by GptHan")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="info", description="Información del servidor", guild=discord.Object(id=GUILD_ID))
async def info(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"📊 {guild.name}", color=0x0099ff)
    embed.add_field(name="👥 Miembros", value=guild.member_count, inline=True)
    embed.add_field(name="🏓 Latencia", value=f"{round(bot.latency*1000)}ms", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if bot.user.mentioned_in(message):
        await message.reply("¡Hola! 👋 Usa `/ayuda` para ver mis comandos")
    await bot.process_commands(message)

if __name__ == "__main__":
    if not TOKEN:
        print("❌ Error: DISCORD_TOKEN no configurado")
        exit(1)
    bot.run(TOKEN)

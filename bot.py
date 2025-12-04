import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import random
import asyncio
from datetime import datetime, timedelta
import aiohttp

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "1446121402267861005"))
COMPOSIO_API_KEY = os.getenv("COMPOSIO_API_KEY", "")

# Intents completos
intents = discord.Intents.all()

bot = commands.Bot(command_prefix=["!", "/", "chichi ", "ChiChi "], intents=intents)

# ============================================
# HELPER - Ejecutar herramientas de Composio
# ============================================

async def composio_execute(tool_name, params):
    """Ejecuta herramientas de Composio desde Discord"""
    if not COMPOSIO_API_KEY:
        return {"error": "COMPOSIO_API_KEY no configurada"}

    url = f"https://backend.composio.dev/api/v2/actions/{tool_name}/execute"
    headers = {
        "X-API-Key": COMPOSIO_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {"input": params}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=30) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    return {"error": f"Status {resp.status}: {await resp.text()}"}
    except Exception as e:
        return {"error": str(e)}

# ============================================
# EVENTOS PRINCIPALES
# ============================================

@bot.event
async def on_ready():
    print(f'✅ {bot.user} está ONLINE con INTEGRACIONES!')
    print(f'📊 Servidores: {len(bot.guilds)}')
    print(f'👥 Usuarios: {sum([guild.member_count for guild in bot.guilds])}')

    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f'✅ {len(synced)} comandos sincronizados')
    except Exception as e:
        print(f'❌ Error sincronizando: {e}')

    # Iniciar tareas automáticas
    auto_status.start()
    print('✅ Sistema de integraciones activado')

@bot.event
async def on_member_join(member):
    """Dar bienvenida automática"""
    channel = discord.utils.get(member.guild.channels, name='général')
    if channel:
        embed = discord.Embed(
            title="¡Bienvenido/a! 🎉",
            description=f"¡Hola {member.mention}! Bienvenido/a a **{member.guild.name}**!\n\nUsa `/ayuda` para ver mis comandos.",
            color=0x00ff00
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        await channel.send(embed=embed)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    content_lower = message.content.lower()

    # Respuestas automáticas
    if bot.user.mentioned_in(message):
        await message.reply("¡Hola! 👋 Usa `/ayuda` para ver todo lo que puedo hacer.")
    elif any(saludo in content_lower for saludo in ['hola', 'hello', 'hi', 'hey']):
        saludos = [f"¡Hola {message.author.mention}! 👋", f"¡Hey {message.author.mention}! 😊"]
        await message.reply(random.choice(saludos))
    elif 'gracias' in content_lower:
        await message.reply("¡De nada! 😊")

    await bot.process_commands(message)

# ============================================
# COMANDOS SLASH - INTEGRACIONES
# ============================================

@bot.tree.command(name="ayuda", description="Muestra todos los comandos con integraciones", guild=discord.Object(id=GUILD_ID))
async def ayuda(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📚 ChiChi Bot - TODAS LAS FUNCIONES",
        description="Bot con integraciones completas",
        color=0x00ff00
    )

    # Básicos
    embed.add_field(
        name="🎯 Comandos Básicos",
        value="**`/hola`** - Saludo\n**`/ayuda`** - Esta ayuda\n**`/info`** - Info del servidor\n**`/ping`** - Ver latencia",
        inline=False
    )

    # Integraciones Gmail
    embed.add_field(
        name="📧 Gmail",
        value="**`/enviar_email`** - Enviar email desde Discord\n**`/email_rapido`** - Email rápido a alguien",
        inline=False
    )

    # Integraciones Calendar
    embed.add_field(
        name="📅 Google Calendar",
        value="**`/crear_evento`** - Crear evento en calendario\n**`/mis_eventos`** - Ver eventos de hoy",
        inline=False
    )

    # Integraciones Sheets
    embed.add_field(
        name="📊 Google Sheets",
        value="**`/guardar_en_sheet`** - Guardar datos en hoja\n**`/leer_sheet`** - Leer datos de hoja",
        inline=False
    )

    # Integraciones Notion
    embed.add_field(
        name="📝 Notion",
        value="**`/crear_nota`** - Crear página en Notion\n**`/buscar_notion`** - Buscar en Notion",
        inline=False
    )

    # Diversión
    embed.add_field(
        name="🎮 Diversión",
        value="**`/dado`** - Lanza un dado\n**`/moneda`** - Cara o cruz\n**`/8ball`** - Bola 8\n**`/meme`** - Meme",
        inline=False
    )

    # Moderación
    embed.add_field(
        name="🛡️ Moderación",
        value="**`/clear`** - Limpiar mensajes\n**`/kick`** - Expulsar\n**`/ban`** - Banear",
        inline=False
    )

    embed.set_footer(text="ChiChi Bot - Integraciones completas 24/7 🤖")
    await interaction.response.send_message(embed=embed)

# ============================================
# INTEGRACIONES GMAIL
# ============================================

@bot.tree.command(name="enviar_email", description="Enviar email vía Gmail", guild=discord.Object(id=GUILD_ID))
async def enviar_email(interaction: discord.Interaction, destinatario: str, asunto: str, mensaje: str):
    await interaction.response.defer()

    result = await composio_execute("GMAIL_SEND_EMAIL", {
        "recipient_email": destinatario,
        "subject": asunto,
        "body": mensaje
    })

    if "error" in result:
        await interaction.followup.send(f"❌ Error: {result['error']}")
    else:
        embed = discord.Embed(title="✅ Email Enviado", color=0x00ff00)
        embed.add_field(name="Para", value=destinatario, inline=False)
        embed.add_field(name="Asunto", value=asunto, inline=False)
        await interaction.followup.send(embed=embed)

@bot.tree.command(name="email_rapido", description="Email rápido", guild=discord.Object(id=GUILD_ID))
async def email_rapido(interaction: discord.Interaction, email: str, mensaje: str):
    await interaction.response.defer()

    result = await composio_execute("GMAIL_SEND_EMAIL", {
        "recipient_email": email,
        "subject": f"Mensaje desde Discord - {interaction.user.name}",
        "body": f"{mensaje}\n\n---\nEnviado por {interaction.user.name} desde ChiChi Bot"
    })

    if "error" in result:
        await interaction.followup.send(f"❌ Error: {result['error']}")
    else:
        await interaction.followup.send(f"✅ Email enviado a {email}!")

# ============================================
# INTEGRACIONES GOOGLE CALENDAR
# ============================================

@bot.tree.command(name="crear_evento", description="Crear evento en Google Calendar", guild=discord.Object(id=GUILD_ID))
async def crear_evento(interaction: discord.Interaction, titulo: str, fecha: str, hora: str, duracion_minutos: int = 60):
    await interaction.response.defer()

    try:
        # Formato: 2025-12-05T14:00:00
        start_datetime = f"{fecha}T{hora}:00"

        result = await composio_execute("GOOGLECALENDAR_CREATE_EVENT", {
            "calendar_id": "primary",
            "summary": titulo,
            "start_datetime": start_datetime,
            "timezone": "Europe/Paris",
            "event_duration_hour": duracion_minutos // 60,
            "event_duration_minutes": duracion_minutos % 60,
            "description": f"Creado desde Discord por {interaction.user.name}"
        })

        if "error" in result:
            await interaction.followup.send(f"❌ Error: {result['error']}")
        else:
            embed = discord.Embed(title="✅ Evento Creado", color=0x4285f4)
            embed.add_field(name="📅 Título", value=titulo, inline=False)
            embed.add_field(name="🕐 Fecha", value=f"{fecha} {hora}", inline=False)
            embed.add_field(name="⏱️ Duración", value=f"{duracion_minutos} minutos", inline=False)
            await interaction.followup.send(embed=embed)
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {str(e)}\n\nFormato: fecha=YYYY-MM-DD hora=HH:MM")

# ============================================
# INTEGRACIONES GOOGLE SHEETS
# ============================================

@bot.tree.command(name="guardar_en_sheet", description="Guardar mensaje en Google Sheet", guild=discord.Object(id=GUILD_ID))
async def guardar_en_sheet(interaction: discord.Interaction, sheet_id: str, datos: str):
    await interaction.response.defer()

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    valores = [[timestamp, interaction.user.name, datos]]

    result = await composio_execute("GOOGLESHEETS_BATCH_UPDATE", {
        "spreadsheet_id": sheet_id,
        "sheet_name": "Sheet1",
        "values": valores
    })

    if "error" in result:
        await interaction.followup.send(f"❌ Error: {result['error']}")
    else:
        await interaction.followup.send(f"✅ Datos guardados en Google Sheet!")

# ============================================
# INTEGRACIONES NOTION
# ============================================

@bot.tree.command(name="crear_nota", description="Crear página en Notion", guild=discord.Object(id=GUILD_ID))
async def crear_nota(interaction: discord.Interaction, parent_id: str, titulo: str, contenido: str):
    await interaction.response.defer()

    # Crear página
    result_page = await composio_execute("NOTION_CREATE_NOTION_PAGE", {
        "parent_id": parent_id,
        "title": titulo
    })

    if "error" in result_page:
        await interaction.followup.send(f"❌ Error: {result_page['error']}")
        return

    # Agregar contenido
    page_id = result_page.get("data", {}).get("id")
    if page_id:
        await composio_execute("NOTION_ADD_MULTIPLE_PAGE_CONTENT", {
            "parent_block_id": page_id,
            "content_blocks": [
                {"content_block": {"block_property": "paragraph", "content": contenido}}
            ]
        })

    embed = discord.Embed(title="✅ Página Notion Creada", color=0x000000)
    embed.add_field(name="📝 Título", value=titulo, inline=False)
    embed.add_field(name="✍️ Contenido", value=contenido[:100] + "..." if len(contenido) > 100 else contenido, inline=False)
    await interaction.followup.send(embed=embed)

# ============================================
# COMANDOS BÁSICOS
# ============================================

@bot.tree.command(name="hola", description="Saluda al bot", guild=discord.Object(id=GUILD_ID))
async def hola(interaction: discord.Interaction):
    await interaction.response.send_message(f"¡Hola {interaction.user.mention}! 👋")

@bot.tree.command(name="info", description="Info del servidor", guild=discord.Object(id=GUILD_ID))
async def info(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"📊 {guild.name}", color=0x0099ff)
    embed.add_field(name="👥 Miembros", value=guild.member_count, inline=True)
    embed.add_field(name="🏓 Latencia", value=f"{round(bot.latency*1000)}ms", inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ping", description="Ver latencia", guild=discord.Object(id=GUILD_ID))
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    emoji = "🟢" if latency < 100 else "🟡" if latency < 200 else "🔴"
    await interaction.response.send_message(f"{emoji} Pong! {latency}ms")

# Comandos de diversión
@bot.tree.command(name="dado", description="Lanza un dado", guild=discord.Object(id=GUILD_ID))
async def dado(interaction: discord.Interaction):
    resultado = random.randint(1, 6)
    await interaction.response.send_message(f"🎲 Has sacado: **{resultado}**")

@bot.tree.command(name="moneda", description="Lanza una moneda", guild=discord.Object(id=GUILD_ID))
async def moneda(interaction: discord.Interaction):
    resultado = random.choice(["Cara", "Cruz"])
    await interaction.response.send_message(f"🪙 Resultado: **{resultado}**")

@bot.tree.command(name="8ball", description="Bola 8 mágica", guild=discord.Object(id=GUILD_ID))
async def eightball(interaction: discord.Interaction, pregunta: str):
    respuestas = ["Sí", "No", "Quizás", "Sin duda", "No lo veo claro", "Pregunta de nuevo"]
    await interaction.response.send_message(f"🎱 **{pregunta}**\nRespuesta: {random.choice(respuestas)}")

@bot.tree.command(name="meme", description="Meme aleatorio", guild=discord.Object(id=GUILD_ID))
async def meme(interaction: discord.Interaction):
    await interaction.response.defer()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://meme-api.com/gimme') as resp:
                if resp.status == 200:
                    data = await resp.json()
                    embed = discord.Embed(title=data['title'], color=0xff4500)
                    embed.set_image(url=data['url'])
                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send("❌ No pude obtener un meme")
    except:
        await interaction.followup.send("😅 Error obteniendo meme")

# Moderación
@bot.tree.command(name="clear", description="Elimina mensajes", guild=discord.Object(id=GUILD_ID))
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, cantidad: int):
    if 1 <= cantidad <= 100:
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=cantidad)
        await interaction.followup.send(f"✅ Eliminados {len(deleted)} mensajes", ephemeral=True)
    else:
        await interaction.response.send_message("⚠️ Cantidad debe ser 1-100", ephemeral=True)

# ============================================
# TAREAS AUTOMÁTICAS
# ============================================

@tasks.loop(minutes=5)
async def auto_status():
    estados = [
        discord.Game("Con integraciones Gmail, Calendar, Sheets, Notion 🚀"),
        discord.Activity(type=discord.ActivityType.watching, name="el servidor 24/7 👀"),
        discord.Activity(type=discord.ActivityType.listening, name="/ayuda para ver integraciones 🎵"),
    ]
    await bot.change_presence(activity=random.choice(estados), status=discord.Status.online)

# ============================================
# INICIAR BOT
# ============================================

if __name__ == "__main__":
    if not TOKEN:
        print("❌ DISCORD_TOKEN no configurado")
        exit(1)

    if not COMPOSIO_API_KEY:
        print("⚠️ COMPOSIO_API_KEY no configurada - integraciones deshabilitadas")

    print("🚀 Iniciando ChiChi Bot con INTEGRACIONES...")
    bot.run(TOKEN)

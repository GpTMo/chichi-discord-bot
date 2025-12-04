import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import random
import asyncio
from datetime import datetime
import aiohttp

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("GUILD_ID", "1446121402267861005"))

# Intents completos
intents = discord.Intents.all()

bot = commands.Bot(command_prefix=["!", "/", "chichi ", "ChiChi "], intents=intents)

# ============================================
# EVENTOS PRINCIPALES
# ============================================

@bot.event
async def on_ready():
    print(f'✅ {bot.user} está ONLINE con superpoderes!')
    print(f'📊 Servidores: {len(bot.guilds)}')
    print(f'👥 Usuarios: {sum([guild.member_count for guild in bot.guilds])}')

    try:
        synced = await bot.tree.sync(guild=discord.Object(id=GUILD_ID))
        print(f'✅ {len(synced)} comandos slash sincronizados')
    except Exception as e:
        print(f'❌ Error sincronizando: {e}')

    # Iniciar tareas automáticas
    auto_status.start()
    print('✅ Sistema de respuestas automáticas activado')

@bot.event
async def on_member_join(member):
    """Dar bienvenida automática a nuevos miembros"""
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

    # Respuestas automáticas inteligentes
    content_lower = message.content.lower()

    # Si mencionan al bot
    if bot.user.mentioned_in(message):
        await message.reply("¡Hola! 👋 Usa `/ayuda` para ver todo lo que puedo hacer.")

    # Saludos automáticos
    elif any(saludo in content_lower for saludo in ['hola', 'hello', 'hi', 'hey', 'buenos días', 'buenas tardes']):
        saludos = [
            f"¡Hola {message.author.mention}! 👋",
            f"¡Hey {message.author.mention}! ¿Qué tal?",
            f"¡Buenas {message.author.mention}! 😊"
        ]
        await message.reply(random.choice(saludos))

    # Responder a preguntas comunes
    elif '¿como estas?' in content_lower or '¿cómo estás?' in content_lower:
        await message.reply("¡Estoy genial! 😊 Siempre listo para ayudar. ¿Y tú?")

    elif 'gracias' in content_lower or 'thank' in content_lower:
        await message.reply("¡De nada! 😊 Para eso estoy aquí.")

    # Reaccionar a emojis
    elif '❤️' in message.content or '💙' in message.content:
        await message.add_reaction('❤️')

    await bot.process_commands(message)

@bot.event
async def on_message_delete(message):
    """Log de mensajes eliminados"""
    if message.author.bot:
        return
    print(f"🗑️ Mensaje eliminado: {message.author} - {message.content[:50]}")

# ============================================
# COMANDOS SLASH - BÁSICOS
# ============================================

@bot.tree.command(name="hola", description="Saluda al bot ChiChi", guild=discord.Object(id=GUILD_ID))
async def hola(interaction: discord.Interaction):
    saludos = [
        f"¡Hola {interaction.user.mention}! 👋",
        f"¡Qué tal {interaction.user.mention}! 😊",
        f"¡Hey {interaction.user.mention}! ¿Cómo estás?",
        f"¡Saludos {interaction.user.mention}! 🎉"
    ]
    await interaction.response.send_message(random.choice(saludos))

@bot.tree.command(name="ayuda", description="Muestra todos los comandos disponibles", guild=discord.Object(id=GUILD_ID))
async def ayuda(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📚 Comandos de ChiChi Bot",
        description="Aquí están TODOS mis comandos disponibles:",
        color=0x00ff00
    )

    # Comandos básicos
    embed.add_field(
        name="🎯 Comandos Básicos",
        value="**`/hola`** - Saludo
**`/ayuda`** - Esta ayuda
**`/info`** - Info del servidor
**`/ping`** - Ver latencia",
        inline=False
    )

    # Utilidades
    embed.add_field(
        name="🛠️ Utilidades",
        value="**`/avatar`** - Ver avatar de usuario
**`/serverinfo`** - Detalles del servidor
**`/userinfo`** - Info de un usuario",
        inline=False
    )

    # Diversión
    embed.add_field(
        name="🎮 Diversión",
        value="**`/dado`** - Lanza un dado
**`/moneda`** - Lanza una moneda
**`/8ball`** - Pregunta a la bola 8
**`/meme`** - Meme aleatorio",
        inline=False
    )

    # Moderación
    embed.add_field(
        name="🛡️ Moderación",
        value="**`/clear`** - Limpiar mensajes
**`/kick`** - Expulsar usuario
**`/ban`** - Banear usuario",
        inline=False
    )

    embed.set_footer(text="ChiChi Bot - Siempre activo 24/7 🤖")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="info", description="Información del servidor", guild=discord.Object(id=GUILD_ID))
async def info(interaction: discord.Interaction):
    guild = interaction.guild

    # Contar canales por tipo
    text_channels = len(guild.text_channels)
    voice_channels = len(guild.voice_channels)
    categories = len(guild.categories)

    embed = discord.Embed(
        title=f"📊 {guild.name}",
        color=0x0099ff,
        timestamp=datetime.utcnow()
    )
    embed.add_field(name="👑 Dueño", value=guild.owner.mention, inline=True)
    embed.add_field(name="👥 Miembros", value=guild.member_count, inline=True)
    embed.add_field(name="🏓 Latencia", value=f"{round(bot.latency*1000)}ms", inline=True)
    embed.add_field(name="💬 Canales Texto", value=text_channels, inline=True)
    embed.add_field(name="🔊 Canales Voz", value=voice_channels, inline=True)
    embed.add_field(name="📁 Categorías", value=categories, inline=True)
    embed.add_field(name="😀 Emojis", value=len(guild.emojis), inline=True)
    embed.add_field(name="🎭 Roles", value=len(guild.roles), inline=True)
    embed.add_field(name="📅 Creado", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ping", description="Verifica la latencia del bot", guild=discord.Object(id=GUILD_ID))
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)

    if latency < 100:
        emoji = "🟢"
        estado = "Excelente"
    elif latency < 200:
        emoji = "🟡"
        estado = "Bueno"
    else:
        emoji = "🔴"
        estado = "Lento"

    await interaction.response.send_message(f"{emoji} Pong! Latencia: **{latency}ms** ({estado})")

# ============================================
# COMANDOS DE UTILIDAD
# ============================================

@bot.tree.command(name="avatar", description="Muestra el avatar de un usuario", guild=discord.Object(id=GUILD_ID))
async def avatar(interaction: discord.Interaction, usuario: discord.Member = None):
    usuario = usuario or interaction.user

    embed = discord.Embed(
        title=f"Avatar de {usuario.name}",
        color=usuario.color
    )
    embed.set_image(url=usuario.display_avatar.url)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="serverinfo", description="Información detallada del servidor", guild=discord.Object(id=GUILD_ID))
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild

    embed = discord.Embed(
        title=f"Información de {guild.name}",
        color=0x7289da,
        timestamp=datetime.utcnow()
    )

    embed.add_field(name="🆔 ID", value=guild.id, inline=False)
    embed.add_field(name="👑 Dueño", value=guild.owner.mention, inline=True)
    embed.add_field(name="🌍 Región", value=str(guild.preferred_locale), inline=True)
    embed.add_field(name="🔒 Nivel Verificación", value=str(guild.verification_level), inline=True)
    embed.add_field(name="👥 Total Miembros", value=guild.member_count, inline=True)
    embed.add_field(name="🤖 Bots", value=len([m for m in guild.members if m.bot]), inline=True)
    embed.add_field(name="😀 Emojis", value=f"{len(guild.emojis)}/50", inline=True)

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    embed.set_footer(text=f"Servidor creado el {guild.created_at.strftime('%d/%m/%Y')}")

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="userinfo", description="Información de un usuario", guild=discord.Object(id=GUILD_ID))
async def userinfo(interaction: discord.Interaction, usuario: discord.Member = None):
    usuario = usuario or interaction.user

    embed = discord.Embed(
        title=f"Info de {usuario.name}",
        color=usuario.color,
        timestamp=datetime.utcnow()
    )

    embed.set_thumbnail(url=usuario.display_avatar.url)
    embed.add_field(name="👤 Usuario", value=usuario.mention, inline=True)
    embed.add_field(name="🆔 ID", value=usuario.id, inline=True)
    embed.add_field(name="📛 Apodo", value=usuario.nick or "Sin apodo", inline=True)
    embed.add_field(name="📅 Cuenta creada", value=usuario.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="📥 Se unió", value=usuario.joined_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="🎭 Roles", value=len(usuario.roles)-1, inline=True)
    embed.add_field(name="🤖 Bot?", value="Sí" if usuario.bot else "No", inline=True)
    embed.add_field(name="📊 Estado", value=str(usuario.status).title(), inline=True)

    await interaction.response.send_message(embed=embed)

# ============================================
# COMANDOS DE DIVERSIÓN
# ============================================

@bot.tree.command(name="dado", description="Lanza un dado (1-6)", guild=discord.Object(id=GUILD_ID))
async def dado(interaction: discord.Interaction):
    resultado = random.randint(1, 6)
    dados_emoji = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
    await interaction.response.send_message(f"🎲 Has sacado: **{resultado}** {dados_emoji[resultado-1]}")

@bot.tree.command(name="moneda", description="Lanza una moneda", guild=discord.Object(id=GUILD_ID))
async def moneda(interaction: discord.Interaction):
    resultado = random.choice(["Cara", "Cruz"])
    emoji = "🪙" if resultado == "Cara" else "💿"
    await interaction.response.send_message(f"{emoji} Resultado: **{resultado}**")

@bot.tree.command(name="8ball", description="Pregunta a la bola 8 mágica", guild=discord.Object(id=GUILD_ID))
async def eightball(interaction: discord.Interaction, pregunta: str):
    respuestas = [
        "Sí, definitivamente.",
        "Es cierto.",
        "Sin duda.",
        "Sí.",
        "Puedes contar con ello.",
        "Como yo lo veo, sí.",
        "Probablemente.",
        "Las perspectivas son buenas.",
        "Sí, según veo.",
        "Los signos apuntan a que sí.",
        "Respuesta confusa, intenta de nuevo.",
        "Pregunta de nuevo más tarde.",
        "Mejor no decirte ahora.",
        "No puedo predecirlo ahora.",
        "Concéntrate y pregunta de nuevo.",
        "No cuentes con ello.",
        "Mi respuesta es no.",
        "Mis fuentes dicen que no.",
        "Las perspectivas no son buenas.",
        "Muy dudoso."
    ]

    embed = discord.Embed(title="🎱 Bola 8 Mágica", color=0x000000)
    embed.add_field(name="Pregunta:", value=pregunta, inline=False)
    embed.add_field(name="Respuesta:", value=random.choice(respuestas), inline=False)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="meme", description="Genera un meme aleatorio", guild=discord.Object(id=GUILD_ID))
async def meme(interaction: discord.Interaction):
    await interaction.response.defer()

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://meme-api.com/gimme') as resp:
                if resp.status == 200:
                    data = await resp.json()

                    embed = discord.Embed(
                        title=data['title'],
                        color=0xff4500,
                        url=data['postLink']
                    )
                    embed.set_image(url=data['url'])
                    embed.set_footer(text=f"👍 {data['ups']} upvotes | r/{data['subreddit']}")

                    await interaction.followup.send(embed=embed)
                else:
                    await interaction.followup.send("❌ No pude obtener un meme ahora. Intenta de nuevo.")
    except Exception as e:
        memes_texto = [
            "¿Por qué los programadores prefieren el modo oscuro? ¡Porque la luz atrae bugs! 🐛",
            "404: Meme not found 😅",
            "Yo: Voy a dormir temprano hoy\nTambién yo a las 3am: Viendo memes 😴",
        ]
        await interaction.followup.send(random.choice(memes_texto))

# ============================================
# COMANDOS DE MODERACIÓN
# ============================================

@bot.tree.command(name="clear", description="Elimina mensajes del canal", guild=discord.Object(id=GUILD_ID))
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(interaction: discord.Interaction, cantidad: int):
    if cantidad < 1 or cantidad > 100:
        await interaction.response.send_message("⚠️ Debes especificar entre 1 y 100 mensajes.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=cantidad)
    await interaction.followup.send(f"✅ Se eliminaron {len(deleted)} mensajes.", ephemeral=True)

@bot.tree.command(name="kick", description="Expulsa a un miembro del servidor", guild=discord.Object(id=GUILD_ID))
@app_commands.checks.has_permissions(kick_members=True)
async def kick(interaction: discord.Interaction, miembro: discord.Member, razon: str = "No especificada"):
    if miembro.top_role >= interaction.user.top_role:
        await interaction.response.send_message("❌ No puedes expulsar a este usuario.", ephemeral=True)
        return

    await miembro.kick(reason=razon)

    embed = discord.Embed(
        title="👢 Usuario Expulsado",
        color=0xff9900
    )
    embed.add_field(name="Usuario", value=miembro.mention, inline=True)
    embed.add_field(name="Moderador", value=interaction.user.mention, inline=True)
    embed.add_field(name="Razón", value=razon, inline=False)

    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="ban", description="Banea a un miembro del servidor", guild=discord.Object(id=GUILD_ID))
@app_commands.checks.has_permissions(ban_members=True)
async def ban(interaction: discord.Interaction, miembro: discord.Member, razon: str = "No especificada"):
    if miembro.top_role >= interaction.user.top_role:
        await interaction.response.send_message("❌ No puedes banear a este usuario.", ephemeral=True)
        return

    await miembro.ban(reason=razon)

    embed = discord.Embed(
        title="🔨 Usuario Baneado",
        color=0xff0000
    )
    embed.add_field(name="Usuario", value=miembro.mention, inline=True)
    embed.add_field(name="Moderador", value=interaction.user.mention, inline=True)
    embed.add_field(name="Razón", value=razon, inline=False)

    await interaction.response.send_message(embed=embed)

# ============================================
# TAREAS AUTOMÁTICAS
# ============================================

@tasks.loop(minutes=5)
async def auto_status():
    """Cambiar estado del bot automáticamente"""
    estados = [
        discord.Game("Ayudando en el servidor 🤖"),
        discord.Activity(type=discord.ActivityType.watching, name="el servidor 👀"),
        discord.Activity(type=discord.ActivityType.listening, name="/ayuda 🎵"),
        discord.Game("24/7 Online ⚡")
    ]
    await bot.change_presence(activity=random.choice(estados), status=discord.Status.online)

# ============================================
# MANEJO DE ERRORES
# ============================================

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ No tienes permisos para usar este comando.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Faltan argumentos. Usa `/ayuda` para más info.")
    else:
        print(f"Error: {error}")

# ============================================
# INICIAR BOT
# ============================================

if __name__ == "__main__":
    if not TOKEN:
        print("❌ Error: DISCORD_TOKEN no configurado")
        exit(1)

    print("🚀 Iniciando ChiChi Bot ULTRA...")
    bot.run(TOKEN)

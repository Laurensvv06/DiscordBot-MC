import discord
from discord.ext import commands, tasks
from mcstatus import JavaServer

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

SERVER_ADDRESS = "SkyblockNifkes.aternos.me"
last_status_name = None  # Houdt de vorige naam bij om onnodige updates te voorkomen

@bot.event
async def on_ready():
    print(f"Ingelogd als {bot.user}")
    print("De bot is klaar en controleert de server elke 30 seconden!")
    if not update_server_status.is_running():
        update_server_status.start()

@tasks.loop(seconds=30)
async def update_server_status():
    global last_status_name
    new_name = "🔴 Server Offline"
    try:
        server = await JavaServer.async_lookup(SERVER_ADDRESS)
        status = await server.async_status()
        new_name = f"🟢 Spelers: {status.players.online}/{status.players.max}"
    except Exception:
        new_name = "🔴 Server Offline"
        
    # Alleen aanpassen als de status echt veranderd is ten opzichte van de vorige check
    if new_name == last_status_name:
        return

    for guild in bot.guilds:
        for channel in guild.voice_channels:
            if "Server" in channel.name or "Spelers" in channel.name or "🟢" in channel.name or "🔴" in channel.name:
                try:
                    if channel.name != new_name:
                        await channel.edit(name=new_name)
                        print(f"Kanaalnaam geüpdatet naar: {new_name}")
                except Exception as err:
                    print(f"Kon kanaalnaam niet aanpassen: {err}")
    
    last_status_name = new_name

@bot.command(name="status")
async def server_status(ctx):
    try:
        server = await JavaServer.async_lookup(SERVER_ADDRESS)
        status = await server.async_status()
        
        embed = discord.Embed(
            title="🖥️ SkyblockNifkes Server Status",
            color=discord.Color.green()
        )
        embed.add_field(name="Status", value="🟢 Online", inline=False)
        embed.add_field(name="Spelers online", value=f"{status.players.online} / {status.players.max}", inline=False)
        embed.add_field(name="Ping", value=f"{status.latency} ms", inline=False)
        embed.add_field(name="Server Adres", value=SERVER_ADDRESS, inline=False)
        
        await ctx.send(embed=embed)
        
    except Exception:
        embed = discord.Embed(
            title="🖥️ SkyblockNifkes Server Status",
            color=discord.Color.red()
        )
        embed.add_field(name="Status", value="🔴 De server is momenteel offline of onbereikbaar.", inline=False)
        embed.add_field(name="Server Adres", value=SERVER_ADDRESS, inline=False)
        
        await ctx.send(embed=embed)

bot.run("MTU1NzQ4Njc1Nzk3OTg4NTYzMA.G-I_kN.1_j2oKXuMyQ9-wcXf5Vc4_i1ajzRvB9-Go705k")
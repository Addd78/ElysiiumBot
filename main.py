import asyncio
import json
import typing
import re
from discord.utils import get
import pytz
import requests
from math import floor
import os
import random
from discord.app_commands import AppCommandError
from discord.ext import tasks
import discord
import traceback
from discord.ui import View
from datetime import datetime, timezone, timedelta
from discord.ext import commands
from collections import defaultdict
import time
TOTO = ''
Addd78130_user_id = 781524251332182016
chef_role = 1031253346436268162
json_bc_filename = "ressources_bc.json"
recruteur = 1031253354904572105 
faction = 1031253372327698442
allowed_channels = [1125525733595414610, 1031253440992645230, 1031253459057528912]
LOG_CHANNEL_ID = 1141292096632918067
allowed_role_id = 1031253346436268162
recup = 1212132568539996211
bad_words_json_path = 'bad_words.json'
ignored_users_json_path = 'ignored_users.json'
mute_role_id = 1098721696573300806
staff_role = 1031253367311310969
alert_delay = 3600
last_interaction_time = time.time()
alert_task = None
########################################## START #########################################

debug = True
SERVER = True
intents = discord.Intents().all()

class PersistentViewBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('!'), help_command=None, case_insensitive=True, intents=intents)

    async def setup_hook(self) -> None:
        views = [RouletteView(), RemoteButtonView(), AvoMarquesButtonView(), ItemSelectorView(), PanelCheckBC()]
        for element in views:
            self.add_view(element)


        
bot = PersistentViewBot()

@bot.command()
async def sync(ctx):
    synced = await ctx.bot.tree.sync()
    server = bot.guilds[0]
    member_count = server.member_count
    await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name=f"{member_count} membres"))
    await ctx.send(f"Synced {len(synced)} commands")

tree = bot.tree

def run_bot(token=TOTO, debug=False):
    if debug: print(bot._connection.loop)
    bot.run(token)
    if debug: print(bot._connection.loop)
    return bot._connection.loop.is_closed()
def load_coin_balances():
    try:
        with open("coin_balances.json", "r") as f:
            coin_balances = json.load(f)
        return coin_balances
    except FileNotFoundError:
        return None
    
    
###################### ARKANE ################################
EVENT_CHANNEL_ID = 1275190953652650046

event_schedule = {
    "lundi": [
        {"name": "BOSS", "time": "01:00"},
        {"name": "BOSS", "time": "10:00"},
        {"name": "BOSS", "time": "18:00"},
        {"name": "EGGHUNT", "time": "19:00", "end_time": "20:00"},
        {"name": "A VOS MARQUES", "time": "20:30", "end_time": "21:00"},
        {"name": "BOSS", "time": "22:00"},
    ],
    "mardi": [
        {"name": "BOSS", "time": "01:00"},
        {"name": "BOSS", "time": "10:00"},
        {"name": "BOSS", "time": "18:00"},
        {"name": "EGGHUNT", "time": "19:00", "end_time": "20:00"},
        {"name": "A VOS MARQUES", "time": "20:30", "end_time": "21:00"},
        {"name": "BOSS", "time": "22:00"},
    ],
    "mercredi": [
        {"name": "BOSS", "time": "01:00"},
        {"name": "BOSS", "time": "10:00"},
        {"name": "A VOS MARQUES", "time": "16:00", "end_time": "16:30"},
        {"name": "BOSS", "time": "18:00"},
        {"name": "EGGHUNT", "time": "19:00", "end_time": "20:00"},
        {"name": "TOTEM", "time": "21:00"},
        {"name": "BOSS", "time": "22:00"},
    ],
    "jeudi": [
        {"name": "BOSS", "time": "01:00"},
        {"name": "BOSS", "time": "10:00"},
        {"name": "BOSS", "time": "18:00"},
        {"name": "EGGHUNT", "time": "19:00", "end_time": "20:00"},
        {"name": "A VOS MARQUES", "time": "20:30", "end_time": "21:00"},
        {"name": "BOSS", "time": "22:00"},
    ],
    "vendredi": [
        {"name": "BOSS", "time": "01:00"},
        {"name": "BOSS", "time": "10:00"},
        {"name": "BOSS", "time": "18:00"},
        {"name": "EGGHUNT", "time": "19:00", "end_time": "20:00"},
        {"name": "A VOS MARQUES", "time": "21:00", "end_time": "21:30"},
        {"name": "BOSS", "time": "22:00"},
    ],
    "samedi": [
        {"name": "BOSS", "time": "01:00"},
        {"name": "BOSS", "time": "10:00"},
        {"name": "A VOS MARQUES", "time": "15:00", "end_time": "15:30"},
        {"name": "BOSS", "time": "18:00"},
        {"name": "EGGHUNT", "time": "19:00", "end_time": "20:00"},
        {"name": "KOTH", "time": "21:00"},
        {"name": "BOSS", "time": "22:00"},
        {"name": "TEST", "time": "23:13"}
    ],
    "dimanche": [
        {"name": "BOSS", "time": "01:00"},
        {"name": "BOSS", "time": "10:00"},
        {"name": "A VOS MARQUES", "time": "15:00", "end_time": "15:30"},
        {"name": "BOSS", "time": "18:00"},
        {"name": "EGGHUNT", "time": "19:00", "end_time": "20:00"},
        {"name": "BOSS", "time": "22:00"},
    ]
}


STATE_FILE = "bot_state.json"

def load_bot_state():
    try:
        with open(STATE_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {"last_event_time": None}

def save_bot_state(state):
    with open(STATE_FILE, "w") as file:
        json.dump(state, file)

def time_to_datetime(time_str):
    now = datetime.now(pytz.timezone("Europe/Paris"))
    return datetime.strptime(time_str, "%H:%M").replace(
        year=now.year, month=now.month, day=now.day, tzinfo=now.tzinfo
    )
MONITOR_DURATION = 45 * 60 

async def create_thread_for_event(event_name, message):
    thread_name = f"{event_name} - {datetime.now().strftime('%H:%M')}"
    thread = await message.create_thread(name=thread_name, auto_archive_duration=60)
    await monitor_thread(thread)

async def monitor_thread(thread):
    await asyncio.sleep(MONITOR_DURATION)
    async for message in thread.history(after=datetime.utcnow() - timedelta(seconds=MONITOR_DURATION)):
        if message.attachments:
            member_id = str(message.author.id)
            member_data = await load_member_data()

            if member_id not in member_data:
                member_data[member_id] = {"boss_kills": 0, "check_bc": 0, "a_vos_marques": 0}

            member_data[member_id]["a_vos_marques"] += 1
            await save_member_data(member_data)
    
    await thread.archive()

@tasks.loop(minutes=1)
async def event_notification():
    state = load_bot_state()
    now = datetime.now(pytz.timezone("Europe/Paris"))
    day_name = now.strftime("%A").lower()

    if day_name in event_schedule:
        for event in event_schedule[day_name]:
            event_time = time_to_datetime(event["time"]) - timedelta(minutes=15)

            if state["last_event_time"] != event_time.strftime("%Y-%m-%d %H:%M"):
                if now >= event_time and now < event_time + timedelta(minutes=1):
                    channel = bot.get_channel(EVENT_CHANNEL_ID)
                    message = await channel.send(f"@everyone {event['name']} commence dans 15 minutes !")

                    if "A VOS MARQUES" in event["name"].upper():
                        await create_thread_for_event(event["name"], message)

                    state["last_event_time"] = event_time.strftime("%Y-%m-%d %H:%M")
                    save_bot_state(state)

@bot.tree.command(name="start_notifications")
async def start_notifications(interaction):
    event_notification.start()
    await interaction.response.send_message("La vérification des événements a commencé.")

@bot.tree.command(name="stop_notifications")
async def stop_notifications(interaction):
    event_notification.stop()
    await interaction.response.send_message("La vérification des événements est arrêtée.")


@bot.tree.command(name="boss_winner", description="Augmente le nombre de boss tués pour un membre")
async def boss_winner(interaction: discord.Interaction, member: discord.Member):
    member_id = str(member.id)
    member_data = await load_member_data()

    if member_id not in member_data:
        member_data[member_id] = {"boss_kills": 0, "check_bc": 0, "a_vos_marques": 0}

    member_data[member_id]["boss_kills"] += 1
    await save_member_data(member_data)

    await interaction.response.send_message(f"Le nombre de boss tués pour {member.display_name} est maintenant {member_data[member_id]['boss_kills']} !")

info_member_path = 'infos_membres.json'
message_store_path = 'messages.json'

@bot.tree.command(name="member", description="Affiche les informations d'un membre")
async def member(interaction: discord.Interaction, member: discord.Member, reset: str = "non"):
    member_id = str(member.id)
    infos_membres = await load_member_data()

    if member_id in infos_membres:
        member_info = infos_membres[member_id]
        embed = discord.Embed(
            title=f"Informations pour {member.display_name}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Nombre de Boss tués", value=member_info.get("boss_kills", "N/A"), inline=False)
        embed.add_field(name="Nombre de check BC fait", value=member_info.get("check_bc", "N/A"), inline=False)
        embed.add_field(name="Nombre de A vos marques faits", value=member_info.get("a_vos_marques", "N/A"), inline=False)
        
        await interaction.response.send_message(embed=embed)
        
        if reset.lower() == "oui":
            await asyncio.sleep(2)  
            del infos_membres[member_id]
            await save_member_data(infos_membres)
            await interaction.channel.send(f"Les statistiques pour {member.display_name} ont été réinitialisées.")
    else:
        await interaction.response.send_message(f"Membre {member.display_name} non trouvé.", ephemeral=True)

async def load_alert_state():
    try:
        with open('alert_state.json', 'r') as f:
            state = json.load(f)
            return state
    except (FileNotFoundError, json.JSONDecodeError):
        return {
            'last_interaction_time': time.time(),
            'reminder_message_ids': []
        }

async def save_alert_state(state):
    with open('alert_state.json', 'w') as f:
        json.dump(state, f, indent=4)
async def load_member_data():
    try:
        with open(info_member_path, 'r') as f:
            data = json.load(f)
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

async def save_member_data(data):
    with open(info_member_path, 'w') as f:
        json.dump(data, f, indent=4)

async def load_message_data():
    try:
        with open(message_store_path, 'r') as f:
            data = json.load(f)
            if 'embed_messages' not in data:
                data['embed_messages'] = []
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return {'embed_messages': []}

async def save_message_data(data):
    with open(message_store_path, 'w') as f:
        json.dump(data, f, indent=4)

class PanelCheckBC(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='✅RAS', style=discord.ButtonStyle.green, custom_id='button_ras')
    async def button_ras(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_button_click(interaction, "RAS")

    @discord.ui.button(label='🔴Alerte 1', style=discord.ButtonStyle.red, custom_id='button_alert1')
    async def button_alert1(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_button_click(interaction, "Alerte 1")

    @discord.ui.button(label='🔴Alerte 2', style=discord.ButtonStyle.red, custom_id='button_alert2')
    async def button_alert2(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_button_click(interaction, "Alerte 2")

    @discord.ui.button(label='🔴Alerte 3', style=discord.ButtonStyle.red, custom_id='button_alert3')
    async def button_alert3(self, interaction: discord.Interaction, button: discord.ui.Button):
        await handle_button_click(interaction, "Alerte 3")


async def handle_button_click(interaction, alert_type):
    global last_interaction_time, alert_task

    await interaction.response.defer()
    
    if alert_type == "Alerte 1":
        embed = discord.Embed(title=f"{get_emoji('alarme_emoji')} Alerte {get_emoji('alarme_emoji')}", description='Assaut en cours (Wither)')
    elif alert_type == "Alerte 2":
        embed = discord.Embed(title=f"{get_emoji('alarme_emoji')} Alerte {get_emoji('alarme_emoji')}", description='Sable cassé sauf obsidienne')
    elif alert_type == "Alerte 3":
        embed = discord.Embed(title=f"{get_emoji('alarme_emoji')} Alerte {get_emoji('alarme_emoji')}", description='Tunnel mais rien de cassé')
    elif alert_type == "RAS":
        embed = discord.Embed(title=f"{get_emoji('yes_emoji')} RAS", description='Rien à signaler')
    else:
        await interaction.followup.send("Error BC_PANEL / handle_button_click", ephemeral=True)
        return

    embed.set_footer(text=f'Vérifié par {interaction.user.display_name}')
    message = await interaction.followup.send(embed=embed)

    message_data = await load_message_data()
    message_data['embed_messages'].append(message.id)

    state = await load_alert_state()
    for msg_id in state.get('reminder_message_ids', []):
        try:
            reminder_message = await interaction.channel.fetch_message(msg_id)
            await reminder_message.delete()
        except discord.NotFound:
            pass
    state['reminder_message_ids'] = []

    if alert_type != "RAS":
        await asyncio.sleep(0.5)
        reminder_message = await interaction.channel.send(content="@everyone")
        state['reminder_message_ids'].append(reminder_message.id)
    
    await save_alert_state(state)

    if len(message_data['embed_messages']) > 2:
        old_message_id = message_data['embed_messages'].pop(0)
        try:
            old_message = await interaction.channel.fetch_message(old_message_id)
            await old_message.delete()
        except discord.NotFound:
            pass

    await save_message_data(message_data)
    
    last_interaction_time = time.time()
    
    member_id = str(interaction.user.id)
    member_data = await load_member_data()

    if member_id not in member_data:
        member_data[member_id] = {"boss_kills": 0, "check_bc": 0, "a_vos_marques": 0}

    member_data[member_id]["check_bc"] += 1

    await save_member_data(member_data)
    
    if alert_task is not None and not alert_task.done():
        alert_task.cancel()
    alert_task = bot.loop.create_task(send_alert_if_needed(interaction.channel))


async def send_alert_if_needed(channel):
    global last_interaction_time, alert_task
    state = await load_alert_state()
    last_interaction_time = state['last_interaction_time']

    while True:
        await asyncio.sleep(alert_delay)
        if time.time() - last_interaction_time >= alert_delay:
            reminder_message = await channel.send(content="@everyone Un check BC est nécessaire !")
            state['reminder_message_ids'].append(reminder_message.id)
            await save_alert_state(state)
            last_interaction_time = time.time()

@bot.tree.command(name="send_bc_panel")
@discord.app_commands.checks.has_role(staff_role)
async def send_bc_panel(interaction: discord.Interaction):
    global alert_task, last_interaction_time
    embed = discord.Embed(title="Check Panel", description="")
    embed.add_field(name="✅ RAS - Rien à signaler.", value="", inline=False)
    embed.add_field(name="🔴 Alerte 1 - Assaut en cours (Wither)", value="", inline=False)
    embed.add_field(name="🔴 Alerte 2 - Sable cassé sauf obsidienne", value="", inline=False)
    embed.add_field(name="🔴 Alerte 3 - Tunnel mais rien de cassé", value="", inline=False)
    embed.set_footer(text="Un message s'affichera dans le channel ci-dessous lorsque vous aurez sélectionné l'un des boutons.")
    view = PanelCheckBC()
    await interaction.response.send_message(embed=embed, view=view)
    
    if alert_task is None or alert_task.done():
        last_interaction_time = time.time()
        state = {
            'last_interaction_time': last_interaction_time,
            'reminder_message_ids': []
        }
        await save_alert_state(state)
        alert_task = bot.loop.create_task(send_alert_if_needed(interaction.channel))

@bot.tree.command()
@discord.app_commands.checks.has_role(staff_role)
async def reset(interaction: discord.Interaction, member: str):
    member_data = await load_member_data()
    if member in member_data:
        del member_data[member]
        await save_member_data(member_data)
        await interaction.response.send_message(f"Les statistiques de {member} ont été réinitialisées.", ephemeral=True)
    else:
        await interaction.response.send_message(f"Membre {member} non trouvé.", ephemeral=True)

############################### ROULETTE ########################################

def charger_paris():
    with open('pari.json', 'r') as f:
        return json.load(f)

def sauvegarder_paris(data):
    with open('pari.json', 'w') as f:
        json.dump(data, f, indent=4)

@bot.tree.command()
@discord.app_commands.checks.has_role(faction)
async def parier(interaction, montant: int):
    """Parier une somme pour la Roulette"""
    if montant <= 0:
        embed = create_small_embed(f"Le montant du pari doit être supérieur à 0 {get_emoji('dollar_emoji')}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    data = charger_paris()
    user_id = str(interaction.user.id)

    if user_id in data["bets"]:
        data["bets"][user_id] += montant
    else:
        data["bets"][user_id] = montant

    data["total_pot"] += montant
    sauvegarder_paris(data)
    embed=create_small_embed(f"Vous avez parié : {montant} {get_emoji('dollar_emoji')}")

    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command()
@discord.app_commands.checks.has_role(staff_role)
async def roulette(interaction):
    """Créer la roulette"""
    view = RouletteView()
    embed = create_embed(title="Roulette 🎰", description=f"{get_emoji('boost_emoji')} Appuyez sur le bouton pour démarrer la roulette ")
    await interaction.response.send_message(embed=embed, view=view)
    
@bot.tree.command(name="actu_roulette")
@discord.app_commands.checks.has_role(faction)
async def actu_roulette(interaction: discord.Interaction):
    """Etat de la Roulette"""
    if not interaction.guild:
        embed = create_small_embed(f"Cette commande ne peut être utilisée que dans un serveur {get_emoji('moderator_emoji')}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    data = charger_paris()
    if not data["bets"]:
        embed = create_small_embed(f"Aucun pari n'a été placé. {get_emoji('no_emoji')}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(title="État Actuel de la Roulette", color=0xFECC05)
    for user_id, montant in data["bets"].items():
        user = interaction.guild.get_member(int(user_id))
        if user:
            embed.add_field(name=user.display_name, value=f"{montant}💲", inline=False)

    embed.add_field(name="Cagnotte Totale", value=f"{data['total_pot']} {get_emoji('dollar_emoji')}", inline=False)

    await interaction.response.send_message(embed=embed)


@bot.tree.command()
@discord.app_commands.checks.has_role(faction)
async def mise(interaction):
    """Obtenir vôtre propre mise"""
    data = charger_paris()
    user_id = str(interaction.user.id)
    if user_id in data["bets"]:
        montant = data["bets"][user_id]
        embed = create_small_embed(f"Vous avez parié : `{montant}` {get_emoji('dollar_emoji')}.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed=create_small_embed(f"Vous n'avez pas encore parié. {get_emoji('no_emoji')}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

class RouletteView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="Démarrer la Roulette", style=discord.ButtonStyle.primary, custom_id="Démarrer la Roulette")
    async def start_roulette(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild=interaction.guild
        role = guild.get_role(1031253367311310969)
        if role not in interaction.user.roles:
            embed=create_small_embed(f"Vous n'avez pas les permissions pour démarrer la roulette. {get_emoji('no_emoji')}")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        data = charger_paris()
        if not data["bets"]:
            embed = create_small_embed(f"Aucun pari n'a été placé. {get_emoji('no_emoji')}")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        participants = list(data["bets"].keys())
        random.shuffle(participants)
        winner_id = random.choice(participants)
        winner_amount = data["total_pot"]

        participant_mentions = [interaction.guild.get_member(int(user_id)).mention for user_id in data["bets"].keys()]
        participant_list = ', '.join(participant_mentions)

        embed = discord.Embed(title="Elysiium ROULETTE", color=0x00ff00)
        embed.add_field(name="Gagnant", value=f"<@{winner_id}> gagne {winner_amount} {get_emoji('dollar_emoji')}!", inline=False)
        embed.add_field(name="Cagnotte Totale {dollar_emoji}", value=f"{data['total_pot']}", inline=False)
        embed.add_field(name="Participants", value=participant_list, inline=False)

        await interaction.response.send_message(embed=embed)

        data["bets"] = {}
        data["total_pot"] = 0
        sauvegarder_paris(data)
############################### API PALADIUM ########################################
def get_emoji(name):
    return emojis.get(name, '')

@bot.tree.command()
async def agenda(interaction: discord.Interaction):
    """Affiche les événements à venir aujourd'hui."""
    url = "https://api.paladium.games/v1/paladium/events/upcoming"

    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        events = data.get('data', [])
        
        # Get today's date in local timezone
        today_local = datetime.now().astimezone().date()
        print(f"Aujourd'hui (local) : {today_local}")

        events_today = []
        for event in events:
            event_start_utc = datetime.fromtimestamp(event['start'] / 1000, tz=timezone.utc)
            event_start_local = event_start_utc.astimezone()
            event_start_local_date = event_start_local.date()
            print(f"Événement : {event['name']} commence le {event_start_local_date} à {event_start_local.time()}")

            # Check if the event's local date is today
            if event_start_local_date == today_local:
                events_today.append(event)

        if not events_today:
            await interaction.response.send_message("Aucun événement prévu pour aujourd'hui.")
            return

        embed = discord.Embed(title="Événements d'aujourd'hui", color=0x00ff00)
        for event in events_today:
            name = event['name']
            servers = ', '.join(event['servers'])
            start_time = datetime.fromtimestamp(event['start'] / 1000).astimezone().strftime('%Y-%m-%d %H:%M:%S')
            end_time = datetime.fromtimestamp(event['end'] / 1000).astimezone().strftime('%Y-%m-%d %H:%M:%S')

            embed.add_field(name="Nom", value=name, inline=False)
            embed.add_field(name="Serveurs", value=servers, inline=False)
            embed.add_field(name="Début", value=start_time, inline=False)
            embed.add_field(name="Fin", value=end_time, inline=False)

        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("Impossible de récupérer les événements pour le moment. Veuillez réessayer plus tard.")
        
serveurs_paladium = ["Soleratl", "Muzdan", "Manashino", "Luccento", "Imbali", "Keltis", "Neolith", "Untaa"]

def get_emoji_palaserv(emoji_name):
    emoji_dict = {
        "online_emoji": '<a:Online:1242550716891926663>',
        "offline_emoji": '<a:Offline:1242550693579984926>',
        "no_emoji": '<a:no:1242544552297103360>',
        "soleratl_emoji": '<a:whitecrown:1242544417882243164>',
        "muzdan_emoji": '<:Muzdan:1242550925768261662>',
        "manashino_emoji": '<:Manashino:1242550852221145098>',
        "luccento_emoji": '<:Luccento:1242550824731676818>',
        "imbali_emoji": '<:Imbali:1242550806775861280>',
        "keltis_emoji": '<:Keltis:1242550789411442799>',
        "neolith_emoji": '<:Neolith:1242550939102220381>',
        "untaa_emoji": '<:Untaa:1242550891895062558>'
    }
    return emoji_dict.get(emoji_name, '')

@bot.tree.command()
async def pala_status(interaction, server: str):
    """Status d'un serveur faction de paladium"""
    server_name = server.capitalize()
    if server_name in serveurs_paladium:
        api_url = "https://api.paladium.games/v1/status"
        response = requests.get(api_url)
        
        if response.status_code == 200:
            data = response.json()
            status = data['java']['factions'].get(server_name, "offline")
            server_emoji = f"{server_name.lower()}_emoji"
            if status == "running":
                embed = discord.Embed(title=f"Statut du serveur {server_name} {get_emoji_palaserv(server_emoji)}", description=f"Le serveur {server_name} est en ligne {get_emoji('online_emoji')} !", color=0xE7DDFF)
            else:
                embed = discord.Embed(title=f"Statut du serveur {server_name} {get_emoji_palaserv(server_emoji)}", description=f"Le serveur {server_name} n'est pas en ligne {get_emoji('offline_emoji')}.", color=0xE7DDFF)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(title="Erreur", description=f"Impossible de récupérer les informations sur l'état du serveur {server_name} {get_emoji_palaserv(server_emoji)} {get_emoji('no_emoji')}.", color=0xE7DDFF)
            await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(title="Erreur", description=f"Le serveur {server_name} n'existe pas, les serveurs valides sont : {', '.join(serveurs_paladium)}.", color=0xE7DDFF)
        await interaction.response.send_message(embed=embed, ephemeral=True)

        
@bot.tree.command()
async def player_profil(interaction, username: str):
    """Information d'un joueur paladium"""
    api_url = f"https://api.paladium.games/v1/paladium/player/profile/{username}"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        embed = discord.Embed(title=f"{get_emoji('pala_emoji')} Profil de {data['username']}", color=0xFFD700) 
        embed.add_field(name=f"{get_emoji('faction_emoji')} Faction", value=data["faction"], inline=True)
        embed.add_field(name="", value="", inline=True)
        embed.add_field(name="", value="", inline=True)
        embed.add_field(name=f"{get_emoji('alchi_emoji')} Alchimiste", value=" "*10 + str(data["jobs"]["alchemist"]["level"]), inline=True)
        embed.add_field(name="", value="      ", inline=True)
        embed.add_field(name=f"{get_emoji('farmer_emoji')} Fermier", value=" "*10 + str(data["jobs"]["farmer"]["level"]), inline=True)
        embed.add_field(name="", value="", inline=False)
        embed.add_field(name=f"{get_emoji('hunter_emoji')} Chasseur", value=str(data["jobs"]["hunter"]["level"]), inline=True)
        embed.add_field(name="", value="      ", inline=True)
        embed.add_field(name=f"{get_emoji('miner_emoji')} Mineur", value=" "*10 + str(data["jobs"]["miner"]["level"]), inline=True)
        embed.add_field(name=f"{get_emoji('argent_emoji')} Argent", value=str(data["money"]) + "  $", inline=False)
        embed.add_field(name=f"{get_emoji('heure_emoji')} Temps de jeu (en Heures)", value=data["timePlayed"]/60, inline=False)
        embed.add_field(name="", value="", inline=True)
        embed.add_field(name=f"{get_emoji('star_emosji')} Rang", value=data["rank"], inline=False)
        
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Erreur", description=f"Impossible de récupérer le profil du joueur, as-tu bien mis le bon pseudo ou les serveur de L'API sont-ils down ? {get_emoji('moderator_emoji')}", color=0xFF0000)

        await interaction.response.send_message(embed=embed)

@bot.tree.command()
async def faction_profil(interaction: discord.Interaction, name: str):
    """Profil d'une faction paladium"""
    api_url = f"https://api.paladium.games/v1/paladium/faction/profile/{name}"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        
        emblem = data["emblem"]
        emblem_url = f"https://picture.paladium.games/emblem/{emblem['backgroundId']}/{emblem['foregroundColor']}/{emblem['iconId']}.png"
        
        embed = discord.Embed(
            title=f"{get_emoji('sword_emoji')} Profil de la Faction {data['name']}",
            color=0xFFD700
        )
        
        embed.add_field(
            name=f"{get_emoji('niveau_emoji')} Niveau de la Faction",
            value=data["level"]["level"],
            inline=True
        )
        embed.add_field(
            name=f"{get_emoji('XP_emoji')} XP de la Faction",
            value=data["level"]["xp"],
            inline=True
        )
        
        created_at = datetime.fromtimestamp(data["createdAt"] / 1000)
        embed.add_field(
            name="Date de création",
            value=created_at.strftime("%d / %m / %Y"),
            inline=False
        )
        
        embed.set_footer(text=f"UUID de la Faction: `{data['uuid']}`")
        
        players_info = "\n".join([f"{player['group']} - {player['username']}" for player in data["players"]])
        embed.add_field(
            name="Joueurs",
            value=players_info,
            inline=False
        )
        
        embed.set_image(url=emblem_url)
        
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(
            title="Erreur",
            description="Impossible de récupérer les détails du profil de la faction.",
            color=0xFF0000
        )
        await interaction.response.send_message(embed=embed)

        
@bot.tree.command()
async def qdf(interaction):
    """Qdf en cours"""
    api_url = "https://api.paladium.games/v1/paladium/faction/quest"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        
        embed = discord.Embed(title="Quête de Faction", color=0xFFD700)
        
        embed.add_field(name=f"{get_emoji('objet_emoji')} Objet", value=data["item"], inline=True)
        embed.add_field(name=f"{get_emoji('quantitee_emoji')} Quantité", value=data["quantity"], inline=True)
        embed.add_field(name="", value="", inline=True)
        embed.add_field(name=f"{get_emoji('XP_emoji')} XP Gagnée", value=data["earningXp"], inline=True)
        embed.add_field(name=f"{get_emoji('argent_emoji')} Argent Gagné", value=data["earningMoney"], inline=True)
        
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Erreur", description="Impossible de récupérer les détails de la quête de faction.", color=0xFF0000)
        await interaction.response.send_message(embed=embed)

@bot.tree.command(name="send_avosmarques")
@discord.app_commands.checks.has_role(staff_role)
async def send_avosmarques(interaction: discord.Interaction):
    """Prochain A Vos Marques"""
    embed = discord.Embed(title=f"{get_emoji('ailes_emoji')}   Événement A Vos Marques", description=f"{get_emoji('fleche_rose_emoji')} Cliquez sur le bouton ci-dessous pour voir les détails du prochain A Vos Marques", color=0x2F2A9E)
    view = AvoMarquesButtonView()
    await interaction.response.send_message(embed=embed, view=view)

def load_emojis(filename='emojis.json'):
    with open(filename, 'r') as file:
        return json.load(file)

emojis = load_emojis()

def get_emoji(name):
    return emojis.get(name, '')

goal_type_translations = {
    "BREAK_BLOCKS": f"{get_emoji('pioche_emoji')}Casser des blocs :",
    "MOB_KILL": f"{get_emoji('mobkill_emoji')}Tuer des mob : ",
    "FISHING": f"Pêcher ",
    "WALK": "Marcher",
    "ITEM_CRAFT": "Fabriquer",
    "ITEM_SMELT": "Fondre/Cuire",
    "ITEM_CRAFT_PALAMACHINE": "Fabriquer avec Palamachine",
    "ITEM_ENCHANT": "Enchanter",
    "GRINDER_CRAFT": "Fabriquer avec un broyeur",
    "GRINDER_SMELT": "Fondre avec un broyeur",
    "USE_ITEM": "Utiliser"
}

server_type_translations = {
    "MINAGE": f"{get_emoji('pioche_emoji')}Minage",
    "FARMLAND": f"{get_emoji('fleche_emoji')}Farmland"
}

extra_translations = {
    "minecraft:apple/0": "pommes",
    "minecraft:iron_ingot/0": f"Minerais de fer {get_emoji('iron_emoji')}",
    "sheep": f"moutons {get_emoji('mouton_emoji')}",
    "pig": f"cochons {get_emoji('cochon_emoji')}",
    "": f"poissons {get_emoji('poisson_emoji')}",
    "cow": f"vache {get_emoji('vache_emoji')}",
    "minecraft:stone/0": "blocs de pierre",
    "minecraft:grass/0": "blocs d'herbe",
    "minecraft:sand/0" : "blocs de sable",
    "palamod:tile.amethyst.ore/0" : "minerais d'améthyste",
    "palamod:item.amethyst.sword/0" : "épées en amethyst",
    "minecraft:dye/0": "colorant",
    "minecraft:coal/1": "charbon",
    "palamod:item.potion_launcher/0": " fois le potion launcher",
    "minecraft:furnace/0": "fours",
    "palamod:item.titane.pickaxe/0":'pioche en titane',
    "minecraft:cooked_beef/0": f"steak de boeuf {get_emoji('vache_emoji')}"
}

class AvoMarquesButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="📨 Voir A Vos Marques", style=discord.ButtonStyle.primary, custom_id="avosmarquesprivate")
    async def see_avosmarques(self, interaction: discord.Interaction, button: discord.ui.Button):
        api_url = "https://api.paladium.games/v1/paladium/faction/onyourmarks"
        response = requests.get(api_url)
        
        if response.status_code == 200:
            data = response.json()
            
            start_time = datetime.fromtimestamp(data["start"])
            end_time = datetime.fromtimestamp(data["end"])
            
            goal_type = data['goalType']
            goal_type_french = goal_type_translations.get(goal_type, goal_type)
            
            server_type = data['serverType']
            server_type_french = server_type_translations.get(server_type, server_type)
            
            extra = data['extra']
            extra_french = extra_translations.get(extra, extra)
            
            amount = data["amount"]
            
            quest = f"{goal_type_french} {amount} {extra_french}"
            
            embed = discord.Embed(title=f"{get_emoji('ailes_emoji')} Événement A Vos Marques", color=0x2F2A9E)
            embed.add_field(name=f"{get_emoji('quete_emoji')} Quête", value=str(quest), inline=True)
            embed.add_field(name="", value="", inline=True)
            embed.add_field(name=f"{get_emoji('serveur_emoji')} Serveur", value=server_type_french, inline=True)
            embed.add_field(name="", value="", inline=True)
            embed.add_field(name="", value=f"{get_emoji('debut_emoji')} **Début**: `{start_time.strftime('%d / %m / %Y à %H h %M')}`", inline=False)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(title="Erreur", description="Impossible de récupérer les détails de l'événement 'À Vos Marques'.", color=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command()
async def avosmarques(interaction):
    """Prochain A vos marques"""
    api_url = "https://api.paladium.games/v1/paladium/faction/onyourmarks"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        
        start_time = datetime.fromtimestamp(data["start"])
        end_time = datetime.fromtimestamp(data["end"])
        
        goal_type = data['goalType']
        goal_type_french = goal_type_translations.get(goal_type, goal_type)
        
        server_type = data['serverType']
        server_type_french = server_type_translations.get(server_type, server_type)
        
        extra = data['extra']
        extra_french = extra_translations.get(extra, extra)
        
        amount = data["amount"]
        
        quest = f"{goal_type_french} {amount} {extra_french}"
        
        embed = discord.Embed(title=f"{get_emoji('ailes_emoji')} Événement A Vos Marques", color=0x2F2A9E)

        embed.add_field(name=f"{get_emoji('quete_emoji')} Quête", value=str(quest), inline=True)
        embed.add_field(name="", value="", inline=True)
        embed.add_field(name=f"{get_emoji('serveur_emoji')} Serveur", value=server_type_french, inline=True)
        embed.add_field(name="", value="", inline=True)
        embed.add_field(name="", value=f"{get_emoji('debut_emoji')} **Début**: `{start_time.strftime('%d / %m / %Y à %H h %M')}`", inline=False)
        
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Erreur", description="Impossible de récupérer les détails de l'événement 'À Vos Marques'.", color=0xFF0000)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        


def create_embed(title=None, description=None, color=discord.Color.gold()):
	embed = discord.Embed(
		title=title,
		description=description,
		color=color
	)
	embed.timestamp = datetime.utcnow()
	embed.set_footer(text='', icon_url='') 
	return embed
        
#######################################  ROLES  ###########################################

ROLES = {
    "Endium": "1221421183119917097",
    "Paladin": "1221421328549023774",
    "Titan": "1221421314057703535",
    "Trixium": "1221421873854943262",
    "Trixium+": "1221421701493952572"
}

def load_grades():
    try:
        with open('grades.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_grades(grades):
    with open('grades.json', 'w') as file:
        json.dump(grades, file, indent=4)

grades = load_grades()

@bot.tree.command()
@discord.app_commands.checks.has_role(faction)
async def set_grade(interaction, *, grade: str):
    """Obtenir le rôle discord correspondant à vôtre grade paladium"""
    if grade in ROLES:
        role_id = ROLES[grade]
        role = interaction.guild.get_role(int(role_id))
        if role:
            await interaction.user.add_roles(role)
            grades[str(interaction.user.id)] = grade
            save_grades(grades)
            embed=create_small_embed(f"{grade} attribué avec succès.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed=create_small_embed(f"Le rôle correspondant n'a pas été trouvé {get_emoji('no_emoji')}")
            await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = create_small_embed("Grade invalide. Les grades valides sont : Endium, Paladin, Titan, Trixium, Trixium+.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command()
@discord.app_commands.checks.has_role(faction)
async def grade_search(interaction, grade: str):
    """Rechercher quelqu'un possédant un grade spécifique"""
    
    if grade in ROLES:
        role_id = ROLES[grade]
        role = interaction.guild.get_role(int(role_id))
        if role:
            members_with_role = [member.display_name for member in interaction.guild.members if role in member.roles]
            embed = discord.Embed(
                title=f"Membres ayant le grade {grade}",
                description='\n'.join(members_with_role) if members_with_role else "Aucun membre n'a ce grade.",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed)
        else:
            embed=create_small_embed(f"Le rôle correspondant n'a pas été trouvé {get_emoji('no_emoji')}")
            await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed=create_small_embed(f"Le rôle correspondant n'a pas été trouvé {get_emoji('no_emoji')}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

######################################## RUBRIQUE DES METIERS  ########################################################

try:
    with open('niveaux.json', 'r') as f:
        niveaux = json.load(f)
except FileNotFoundError:
    niveaux = {}

@bot.tree.command(name="niveau_add")
@discord.app_commands.checks.has_role(faction)
async def niveau_add(interaction, metier : str, niveau : int):
    """ajouter ou mettre à jour un niveau"""
    metiers_valides = ["alchi", "hunter", "miner", "farmer"]
    if metier.lower() not in metiers_valides:
        embed=create_small_embed(f"Métier invalide. Veuillez choisir parmi {get_emoji('fleche_emoji')} **alchi, hunter, miner, farmer**.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    utilisateur = str(interaction.user.id)
    if utilisateur not in niveaux:
        niveaux[utilisateur] = {}
    niveaux[utilisateur][metier.lower()] = int(niveau)
    with open('niveaux.json', 'w') as f:
        json.dump(niveaux, f)
    embed=create_small_embed(f"Niveau de {metier} mis à jour {get_emoji('boost_emoji')}")
    await interaction.response.send_message(embed=embed,ephemeral=True)

@bot.tree.command()
@discord.app_commands.checks.has_role(faction)
async def niveau(interaction, metier : str):
    """Afficher le niveaux le plus élevé d'un métier"""
    metiers_valides = ["alchi", "hunter", "miner", "farmer"]
    if metier.lower() not in metiers_valides:
        embed=create_small_embed(f"Métier invalide. Veuillez choisir parmi **alchi, hunter, miner ou farmer** {get_emoji('no_emoji')}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    niveau_max = 0
    personne_max = None

    for utilisateur, niveaux_utilisateur in niveaux.items():
        if metier.lower() in niveaux_utilisateur:
            if niveaux_utilisateur[metier.lower()] > niveau_max:
                niveau_max = niveaux_utilisateur[metier.lower()]
                personne_max = utilisateur
    if personne_max:
        membre = interaction.guild.get_member(int(personne_max))
        if membre:
            embed=create_small_embed(f"La personne {membre.mention} est niveau {niveau_max} en métier {metier}.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed=create_small_embed(f"Impossible de trouver cet utilisateur {get_emoji('red_emoji')}")
            await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed=create_small_embed(f"Aucun utilisateur n'a encore défini de niveau pour ce métier.{get_emoji('boost_emoji')}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
###################################### COINS #####################################################

if not os.path.isfile("coin_balances.json"):
    with open("coin_balances.json", "w") as f:
        json.dump({}, f)
try:
    with open("coin_balances.json", "r") as f:
        coin_balances = json.load(f)
except FileNotFoundError:
    coin_balances = {}
    

    
    
@bot.event
async def on_error(event, *args, **kwargs):
    import traceback
    traceback.print_exc
                                            
@bot.tree.command()
@discord.app_commands.checks.has_role(staff_role)
async def g_coin(interaction: discord.Interaction, member: discord.Member, amount: int):
    """Attribuer des coins à un membre spécifié."""
    member_id_str = str(member.id)
    if member_id_str not in coin_balances:
        coin_balances[member_id_str] = 0
    old_balance = coin_balances.get(member_id_str, 0)
    coin_balances[member_id_str] += amount
    new_balance = coin_balances[member_id_str]
    embed=create_small_embed(f"{member.mention} a reçu```{amount}``` {get_emoji('coin_emoji')}.")
    await interaction.response.send_message(embed=embed)
    save_coin_balances()
                                            
@bot.tree.command()
@discord.app_commands.checks.has_role(staff_role)
async def r_coin(interaction: discord.Interaction, member: discord.Member, amount: int):
    """Retirer des coins"""
    member_id_str = str(member.id)
    if member_id_str not in coin_balances:
        embed=create_small_embed(f"{member.mention} n'a pas de solde de coins existant.")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        old_balance = coin_balances[member_id_str]
        coin_balances[member_id_str] = max(0, old_balance - amount)
        new_balance = coin_balances[member_id_str]
        embed=create_small_embed(f"{member.mention} a perdu ```{amount}``` {get_emoji('coin_emoji')}.")
        await interaction.response.send_message(embed=embed)
        save_coin_balances()
                                            
@bot.tree.command()
@discord.app_commands.checks.has_role(staff_role)
async def coins(interaction: discord.Interaction, member: discord.Member):
    """Obtenir le solde de coins d'un membre"""
    try:
        with open("coin_balances.json", "r") as f:
            coin_balances = json.load(f)
            member_id_str = str(member.id)
            if member_id_str in coin_balances:
                balance = coin_balances[member_id_str]
                embed=create_small_embed(f"Le solde de {member.mention} est de ```{balance}``` {get_emoji('coin_emoji')}")
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed=create_small_embed(f"L'utilisateur {member.mention} n'a pas de solde de coins existant.")
                await interaction.response.send_message(embed=embed, ephemeral=True)
    except FileNotFoundError:
        embed=create_small_embed(f"Le fichier 'coin_balances.json' n'existe pas ou est vide{get_emoji('red_emoji')}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
                                            
@bot.tree.command()
@discord.app_commands.checks.has_role(faction)
async def me(interaction):
    """Obtenir votre propre solde de coins"""
    user_id = interaction.user.id
    try:
        with open("coin_balances.json", "r") as f:
            coin_balances = json.load(f)
            if str(user_id) in coin_balances:
                balance = coin_balances[str(user_id)]
                embed = create_small_embed(f"Vous possédez : `{balance}` {get_emoji('coin_emoji')}.")
                message = await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                embed = create_small_embed(f"Vous n'avez pas de solde de coins existant.{get_emoji('no_emoji')}")
                await interaction.response.send_message(embed=embed, ephemeral=True)
    except FileNotFoundError:
        embed=create_small_embed(f"Le fichier de sauvegarde n'existe pas ou est vide. {get_emoji('no_emoji')} Contact Addd78130 d'urgence !_ {get_emoji('ailes_emoji')}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
def save_coin_balances():
    with open("coin_balances.json", "w") as f:
        json.dump(coin_balances, f)

@bot.tree.command()
@discord.app_commands.checks.has_role(faction)
async def baltop(interaction):
    """Obtenir le baltop des coins de la faction"""
    with open("coin_balances.json", "r") as file:
        coin_balances = json.load(file)
    sorted_users = sorted(coin_balances.items(), key=lambda x: x[1], reverse=True)

    embed = discord.Embed(title="Classement des utilisateurs par solde de coins", color=discord.Color.red())

    field_str = ""
    for index, (user_id, balance) in enumerate(sorted_users, start=1):
        user = interaction.guild.get_member(int(user_id))
        username = user.name if user else f"Utilisateur inconnu ({user_id})"
        field_name = f"{index}. {username}"
        field_value = f"{balance} {get_emoji('no_emoji')}"
        if len(field_str) + len(field_name) + len(field_value) + 5 > 1024:
            break
        field_str += f"{field_name}: {field_value}\n"
    embed.description = field_str
    await interaction.response.send_message(embed=embed)

items_prices = {
    "P4U3": 2400,
    "1k": 800,
    "5k": 3200,
    "Double XP": 7000,
    "Sealed XP": 800,
    "Bonbon métier": 10000
}

def load_data(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

class ItemSelector(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="1k💲", description=f"800 🪙"),
            discord.SelectOption(label="Double XP", description=f"7000 🪙"),
            discord.SelectOption(label="Sealed XP", description=f"800 🪙"),
            discord.SelectOption(label="P4U3", description=f"2400 🪙"),
            discord.SelectOption(label="5k💲", description=f"3200 🪙"),
            discord.SelectOption(label="Bonbon métier", description=f"10000 🪙")
        ]
        super().__init__(placeholder="Choisissez un item à acheter", min_values=1, max_values=1, options=options, custom_id='Selectionneritem')

    async def callback(self, interaction: discord.Interaction):
        selected_item = self.values[0]
        user_id = str(interaction.user.id)
        coin_balances = load_data("coin_balances.json")
        all_tickets = load_data("tickets.json")

        if user_id in all_tickets:
            await interaction.response.send_message("Vous avez déjà un ticket d'achat ouvert. Veuillez le clôturer avant d'en ouvrir un nouveau.", ephemeral=True)
            return

        if selected_item not in items_prices:
            await interaction.response.send_message("L'item sélectionné n'existe pas.", ephemeral=True)
            return

        item_price = items_prices[selected_item]

        if user_id in coin_balances and coin_balances[user_id] >= item_price:
            coin_balances[user_id] -= item_price
            save_data("coin_balances.json", coin_balances)
            
            embed = discord.Embed(
                title="Demande d'achat de lot",
                description=f"{interaction.user.mention} souhaite acheter le lot suivant :",
                color=0xE2EAF4
            )
            embed.add_field(name="Lot demandé", value=selected_item)
            embed.add_field(name="Solde de coins", value=f"{coin_balances[user_id]} coins")

            category = discord.utils.get(interaction.guild.categories, id=1190768986007277628)
            if category:
                ticket_channel = await category.create_text_channel(f"achat-{interaction.user}")
                await ticket_channel.set_permissions(interaction.user, read_messages=True, send_messages=True, read_message_history=True)

                role_to_ping = interaction.guild.get_member(1031253367311310969)
                if role_to_ping:
                    await ticket_channel.send(f"{role_to_ping.mention}")

                ticket_data = {
                    "user_id": user_id,
                    "refund_amount": item_price,
                    "item": selected_item,
                    "channel_id": ticket_channel.id
                }
                all_tickets[user_id] = ticket_data
                save_data("tickets.json", all_tickets)
                staff_role_id = 1031253367311310969

                view = TicketBuyActionsView(user_id, item_price, selected_item, staff_role_id)
                await ticket_channel.send(embed=embed, view=view)

                await interaction.response.send_message(embed=create_small_embed(f"Votre demande d'achat a été enregistrée. Un ticket : {ticket_channel} a été ouvert pour le suivi."), ephemeral=True)
            else:
                await interaction.response.send_message("La catégorie spécifiée n'a pas été trouvée.", ephemeral=True)
        else:
            await interaction.response.send_message("Vous n'avez pas assez de coins pour acheter cet item.", ephemeral=True)

class ItemSelectorView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ItemSelector())

class CancelButton(discord.ui.Button):
    def __init__(self, user_id, refund_amount, item):
        super().__init__(label="Annuler la demande d'achat", style=discord.ButtonStyle.danger, custom_id="cancel_purchase")
        self.user_id = user_id
        self.refund_amount = refund_amount
        self.item = item

    async def callback(self, interaction: discord.Interaction):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("Vous n'avez pas la permission d'utiliser ce bouton.", ephemeral=True)
            return

        coin_balances = load_data("coin_balances.json")
        coin_balances[str(interaction.user.id)] += self.refund_amount
        save_data("coin_balances.json", coin_balances)

        all_tickets = load_data("tickets.json")
        if self.user_id in all_tickets:
            del all_tickets[self.user_id]
            save_data("tickets.json", all_tickets)

        await interaction.channel.delete()
        await interaction.user.send(f"Votre demande d'achat pour {self.item} a été annulée et vous avez été remboursé de {self.refund_amount} coins.")

class CloseTicketButton(discord.ui.Button):
    def __init__(self, staff_role_id):
        super().__init__(label="Fermer le ticket", style=discord.ButtonStyle.primary, custom_id="close_ticket")
        self.staff_role_id = staff_role_id

    async def callback(self, interaction: discord.Interaction):
        member = interaction.guild.get_member(interaction.user.id)
        if member is None or discord.utils.get(member.roles, id=self.staff_role_id) is None:
            await interaction.response.send_message("Vous n'avez pas la permission d'utiliser ce bouton.", ephemeral=True)
            return

        all_tickets = load_data("tickets.json")
        user_id = None
        for uid, data in all_tickets.items():
            if data["channel_id"] == interaction.channel.id:
                user_id = uid
                break

        if user_id:
            del all_tickets[user_id]
            save_data("tickets.json", all_tickets)

        await interaction.channel.delete()

class TicketBuyActionsView(discord.ui.View):
    def __init__(self, user_id, refund_amount, item, staff_role_id):
        super().__init__(timeout=None)
        self.add_item(CancelButton(user_id, refund_amount, item))
        self.add_item(CloseTicketButton(staff_role_id))

@bot.event
async def on_ready():
    print(f'Connecté en tant que {bot.user}!')
    state = load_bot_state()
    if state.get("last_event_time"):
        event_notification.start()
    all_tickets = load_data("tickets.json")
    for ticket_data in all_tickets.values():
        user_id = ticket_data["user_id"]
        refund_amount = ticket_data["refund_amount"]
        item = ticket_data["item"]
        channel_id = ticket_data["channel_id"]
        staff_role_id = 1031253367311310969  
        channel = bot.get_channel(channel_id)
        if channel:
            view = TicketBuyActionsView(user_id, refund_amount, item, staff_role_id)
        global alert_task, last_interaction_time
    state = await load_alert_state()
    last_interaction_time = state['last_interaction_time']
    
    if alert_task is None or alert_task.done():
        channel_id = 1269739832146661376
        channel = bot.get_channel(channel_id)
        if channel:
            alert_task = bot.loop.create_task(send_alert_if_needed(channel))

@bot.tree.command()
async def send_buy(interaction):
    view = ItemSelectorView()
    embed = discord.Embed(title="Economie de la Elysiium 🪙", description="1 Quota = 1250 coins et 1 surplus = 450 coins")
    channel = bot.get_channel(1233099934312562728)
    await channel.send(embed=embed, view=view)
    await interaction.response.send_message("Panneau d'achat envoyé.", ephemeral=True)

################################### ABSENCES ############################################

@bot.tree.command()
@discord.app_commands.checks.has_role(faction)
async def absence(interaction: discord.Interaction,raison:str,date:str) -> None:
	"""Absence : JJ/MM/AAAA"""
	if 813928386946138153 in [x.id for x in interaction.user.roles]:
		await interaction.response.send_message('Tu es déjà absent(e) !')
		return
	try:		
		if datetime.strptime(date,'%d/%m/%Y') < datetime.now():
			await interaction.response.send_message(create_small_embed(f"La date n'est pas valide, merci de recommencer avec une date valide {get_emoji('no_emoji')}"), ephemeral=True)
			return
	except:
		await interaction.response.send_message(create_small_embed(f"La date n'est pas valide, merci de recommencer avec une date valide {get_emoji('no_emoji')}"), ephemeral=True)
		return
	with open('absence.json', 'r') as f:
		ab = json.load(f)
	if date in ab.keys():
		ab[date][interaction.user.id] = raison
	else:
		ab[date] = {interaction.user.id:raison}
	with open('absence.json', 'w') as f:
		json.dump(ab, f, indent=6)
	chanel = bot.get_channel(1087120601325506611)
	await chanel.send(create_embed(title=f"Absence de {interaction.user.mention}", description=f"{interaction.user.mention} est absent jusqu'au {date} pour {raison}"))
	role = interaction.guild.get_role(1215396472162488381)
	await interaction.user.add_roles(role)
	await interaction.response.send_message(create_small_embed(f"Votre absence a bien été prise en compte {get_emoji('yes_emoji')}"), ephemeral=True)

@tasks.loop(seconds = 360)
async def abs():
	with open('absence.json', 'r') as f:
		ab = json.load(f)
	a = []
	guild=bot.get_guild(790367917812088864)
	for date in ab.keys():
		if datetime.strptime(date,'%d/%m/%Y') < datetime.now():
			for personne in ab[date].keys():
				memb = guild.get_member(int(personne))
				role = guild.get_role(1215396472162488381)
				if memb != None:
					await memb.remove_roles(role)
				else:
					test = bot.get_channel(1143890485627342858)
					await test.send(f'Il y a eu un problème avec l\'absence de <@{personne}>')
		a.append(date)
	for date in a:
		ab.pop(date)
	with open('absence.json', 'w') as f:
		json.dump(ab, f, indent=6)
        
############################# GESTION DE FACTION ######################################
CATEGORY_ID = 1197830831377494057
STAFF_ROLE_ID = recruteur
TICKET_LOG_CHANNEL_ID = 1121377434160345118
REMOTE_CHANNEL_ID = 1073320610891059230

def load_ticket_data_rc(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_ticket_data_rc(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

@bot.tree.command(name="send_remote_button")
@discord.app_commands.checks.has_role(STAFF_ROLE_ID)
async def send_remote_button_rc(interaction: discord.Interaction):
    """Envoyer l'embed des ticket + Bouton"""
    staff_role_rc = interaction.guild.get_role(STAFF_ROLE_ID)
    if staff_role_rc not in interaction.user.roles:
        embed = create_small_embed(f"Vous n'avez pas la permission d'utiliser cette commande {get_emoji('no_emoji')}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return

    embed = discord.Embed(
        title=f"{get_emoji('crown_emoji')} Recrutement Elysiium !!!",
        description=(
            "Bienvenue à tous sur le merveilleux serveur de La Elysiium Faction.\n\n"
            "Afin d'optimiser les recrutements, nous les avons organisés sous forme de ticket donc pour toute demande de recrutement, veuillez interagir avec le bouton ci-dessous "
            "en vous rappelant que si vous créez un ticket, il sera fermé en cas de non-réponse dans un délai de 7 jours et que tout abus sera sanctionné !\n\n"
            "Veuillez aussi remplir le formulaire ci-dessous:\n\n"
            "[Formulaire de recrutement](https://docs.google.com/forms/d/e/1FAIpQLSfdSHDbH_MCrVljo1eEqVNkPoAJC0cZtGmcaaqrdxfndJXtBg/viewform)"
        )
    )

    view = RemoteButtonView()
    remote_channel_rc = interaction.guild.get_channel(REMOTE_CHANNEL_ID)
    if remote_channel_rc:
        await remote_channel_rc.send(embed=embed, view=view)
        embed = create_small_embed(f"Panel envoyé avec succès {get_emoji('yes_emoji')}")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = create_small_embed(f"Le salon de télécommande spécifié n'a pas été trouvé {get_emoji('no_emoji')}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

class RemoteButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📨 Ouvrir un Ticket", style=discord.ButtonStyle.primary, custom_id="open_ticket")
    async def open_ticket_rc(self, interaction: discord.Interaction, button: discord.ui.Button):
        if CATEGORY_ID is None:
            embed = create_small_embed(f"La catégorie pour les tickets n'a pas été configurée {get_emoji('no_emoji')}")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        category_rc = interaction.guild.get_channel(CATEGORY_ID)
        if not category_rc or not isinstance(category_rc, discord.CategoryChannel):
            embed = create_small_embed(f"La catégorie spécifiée n'existe pas ou n'est pas valide {get_emoji('no_emoji')}")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        overwrites_rc = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, read_message_history=True),
            get(interaction.guild.roles, id=STAFF_ROLE_ID): discord.PermissionOverwrite(read_messages=True, send_messages=True, read_message_history=True)
        }
        ticket_channel_rc = await category_rc.create_text_channel(f"ticket-{interaction.user.name}", overwrites=overwrites_rc)
        embed = create_small_embed(f"Ticket créé : {ticket_channel_rc.mention} {get_emoji('ticket_emoji')}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

        embed = discord.Embed(
            title="Bienvenue dans votre ticket",
            description="Merci d'avoir ouvert un ticket. Un membre de l'équipe Recrutement sera bientôt avec vous.\n Assurez-vous d'avoir rempli le formulaire : (https://docs.google.com/forms/d/e/1FAIpQLSfdSHDbH_MCrVljo1eEqVNkPoAJC0cZtGmcaaqrdxfndJXtBg/viewform)"
        )

        action_view_rc = TicketActionView(ticket_channel_rc.id, interaction.user.id)

        log_channel_rc = interaction.guild.get_channel(TICKET_LOG_CHANNEL_ID)
        if log_channel_rc:
            embed2 = create_embed(title='Ouvert', description=f"{ticket_channel_rc.mention} créé par {interaction.user.mention}.", color=0xDFC57B)
            await log_channel_rc.send(embed=embed2)

        await ticket_channel_rc.send(embed=embed, view=action_view_rc)

        ticket_data_rc = {
            "user_id": interaction.user.id,
            "channel_id": ticket_channel_rc.id
        }
        all_tickets_rc = load_ticket_data_rc("ticket_recrutement.json")
        all_tickets_rc[str(interaction.user.id)] = ticket_data_rc
        save_ticket_data_rc("ticket_recrutement.json", all_tickets_rc)

class TicketActionView(discord.ui.View):
    def __init__(self, ticket_channel_id_rc, user_id_rc):
        super().__init__(timeout=None)
        self.ticket_channel_id_rc = ticket_channel_id_rc
        self.user_id_rc = user_id_rc

    @discord.ui.button(label="Fermer le Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket_rc(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_rc = get(interaction.guild.roles, id=STAFF_ROLE_ID)
        if role_rc not in interaction.user.roles:
            small_embed = create_small_embed(f"Vous n'avez pas les permissions pour fermer ce ticket, veuillez annuler votre demande {get_emoji('no_emoji')}")
            await interaction.response.send_message(embed=small_embed, ephemeral=True)
            return

        log_channel_rc = interaction.guild.get_channel(1121377434160345118)
        ticket_channel_rc = interaction.guild.get_channel(self.ticket_channel_id_rc)
        if ticket_channel_rc:
            embed_log_rc = create_embed(title="Fermeture", description=f"{ticket_channel_rc.name} fermé par {interaction.user.mention}.", color=0xDFC57B)
            await log_channel_rc.send(embed=embed_log_rc)
            await ticket_channel_rc.delete()
            user_rc = interaction.user
            embed_mp_rc = create_small_embed(f"Ticket fermé avec succès.{get_emoji('yes_emoji')}")
            await user_rc.send(embed=embed_mp_rc)

            all_tickets_rc = load_ticket_data_rc("ticket_recrutement.json")
            if str(self.user_id_rc) in all_tickets_rc:
                del all_tickets_rc[str(self.user_id_rc)]
                save_ticket_data_rc("ticket_recrutement.json", all_tickets_rc)

    @discord.ui.button(label="Annuler la Demande", style=discord.ButtonStyle.secondary, custom_id="cancel_ticket")
    async def cancel_ticket_rc(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id_rc:
            embed_stop_rc = create_small_embed(f"Seul l'utilisateur ayant ouvert le ticket peut annuler la demande {get_emoji('no_emoji')}")
            await interaction.response.send_message(embed=embed_stop_rc, ephemeral=True)
            return

        ticket_channel_rc = interaction.guild.get_channel(self.ticket_channel_id_rc)
        if ticket_channel_rc:
            await ticket_channel_rc.delete()
            log_channel_rc = interaction.guild.get_channel(TICKET_LOG_CHANNEL_ID)
            if log_channel_rc:
                embed_log2_rc = create_embed(title="Annulation de Ticket", description=f"Ticket {ticket_channel_rc.name} annulé par {interaction.user.mention}.", color=0xDFC57B)
                user_rc = interaction.user
                await user_rc.send(embed=embed_log2_rc)
                await log_channel_rc.send(embed=embed_log2_rc)

            all_tickets_rc = load_ticket_data_rc("ticket_recrutement.json")
            if str(self.user_id_rc) in all_tickets_rc:
                del all_tickets_rc[str(self.user_id_rc)]
                save_ticket_data_rc("ticket_recrutement.json", all_tickets_rc)

@bot.tree.command()
@discord.app_commands.checks.has_any_role(staff_role,recruteur)
async def kick(interaction, member: discord.Member, reason: str):
    """Kick quelqu'un de la faction"""
    guild = interaction.guild
    with open("coin_balances.json", "r") as f:
        coin_balances = json.load(f)
    if str(member.id) in coin_balances:
        del coin_balances[str(member.id)]
    with open("coin_balances.json", "w") as f:
        json.dump(coin_balances, f)
    
    embed = discord.Embed(title="🛑 Kick 🛑", description=f"Vous avez été kick de la Elysiium pour la raison suivante : {reason}", color=discord.Color.red())
    await member.send(embed=embed)
    await member.send(f"{member.mention}")
    visiteur = guild.get_role(1031253365948153867)
    veterant = guild.get_role(1031253364190752839)
    for rol in member.roles:
        try:
            await member.remove_roles(rol)
        except discord.NotFound:
            continue
    await member.add_roles(visiteur)
    await member.add_roles(veterant)
    log_channel = guild.get_channel(1236223187923111946)
    log_message = discord.Embed(title="😶‍🌫️ Leave", description=f"La personne {member.display_name} a quitté la faction, kick par {interaction.user} pour le motif : {reason}", color=0x1E1730)
    await log_channel.send(embed=log_message)
    
    await interaction.response.send_message(f"{get_emoji('yes_emoji')}")
@bot.tree.command()
@discord.app_commands.checks.has_role(recruteur)
async def admis(interaction, member: discord.Member, specialisation: str):
    """Accepter quelqu'un dans la faction"""
    guild = interaction.guild
    babysiium = guild.get_role(1031253356234166352)
    farmeur = guild.get_role(1185671072616550491)
    pilleur = guild.get_role(1185671395624108072)
    pvp = guild.get_role(1185669746570575922)
    mineur = guild.get_role(1185669529368539156)
    faction = guild.get_role(1031253372327698442)
    if specialisation == "farmeur":
        for rol in member.roles:
            try:
                await member.remove_roles(rol)
            except discord.NotFound:
                continue
        await member.add_roles(babysiium)
        await member.add_roles(farmeur)
        await member.add_roles(faction)
        spe = "Farmeur"
    elif specialisation == "mineur":
        for rol in member.roles:
            try:
                await member.remove_roles(rol)
            except discord.NotFound:
                continue
        await member.add_roles(babysiium)
        await member.add_roles(mineur)
        await member.add_roles(faction)
        spe = "Mineur"
    elif specialisation == "pilleur":
        for rol in member.roles:
            try:
                await member.remove_roles(rol)
            except discord.NotFound:
                continue
        await member.add_roles(babysiium)
        await member.add_roles(pilleur)
        await member.add_roles(faction)
        spe = "Pilleur"
    elif specialisation == "pvp":
        for rol in member.roles:
            try:
                await member.remove_roles(rol)
            except discord.NotFound:
                continue
        await member.add_roles(babysiium)
        await member.add_roles(pvp)
        await member.add_roles(faction)
        spe = "PvP"
    else:
        embed=create_small_embed(f"Erreur lors de la commande {get_emoji('red_emoji')}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

    log_channel = guild.get_channel(1236223187923111946)
    log_message = discord.Embed(title="👋 Join", description=f"La personne {member.display_name} a rejoint la faction avec le rôle {spe}, admis par {interaction.user}", color=0x060270)
    await log_channel.send(embed=log_message)
    message = discord.Embed(title="👋 Welcome !", description="Bienvenue dans la fac !!!", color=0x060270)
    await member.send(embed=message)
    await interaction.response.send_message(f"{get_emoji('yes_emoji')}")

    
################################## UTILITAIRE ###########################################

class GiveawayButton(discord.ui.View):
    def __init__(self, prize):
        super().__init__(timeout=None)
        self.prize = prize
        self.giveaway_active = True

    @discord.ui.button(label="Participate", style=discord.ButtonStyle.green, custom_id="participate_button")
    async def participate_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not self.giveaway_active:
            await interaction.response.send_message("The giveaway has ended. You can no longer participate.", ephemeral=True)
            return

        user_id = str(interaction.user.id)
        data = load_giveaway_data()

        if self.prize not in data:
            data[self.prize] = {'participants': [], 'end_time': '', 'message_id': ''}

        if user_id not in data[self.prize]['participants']:
            data[self.prize]['participants'].append(user_id)
            save_giveaway_data(data)
            await interaction.response.send_message("You have successfully participated!", ephemeral=True)
        else:
            await interaction.response.send_message("You have already participated.", ephemeral=True)

    def end_giveaway(self):
        self.giveaway_active = False

def load_giveaway_data():
    try:
        with open('giveaway.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_giveaway_data(data):
    with open('giveaway.json', 'w') as f:
        json.dump(data, f, indent=4)

def parse_duration(duration_str):
    pattern = r'(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?'
    match = re.match(pattern, duration_str)
    if not match:
        raise ValueError("Invalid duration format")
    days, hours, minutes, seconds = match.groups(default="0")
    total_seconds = int(days) * 86400 + int(hours) * 3600 + int(minutes) * 60 + int(seconds)
    return total_seconds

async def update_giveaway_embed(message, end_time, prize):
    while True:
        remaining_time = end_time - datetime.utcnow()
        if remaining_time.total_seconds() <= 0:
            break
        embed = discord.Embed(title="🎉 Giveaway 🎉", description=f"Prize: {prize}", color=0x00ff00)
        embed.add_field(name="How to enter", value="Click the button below to participate!")
        embed.set_footer(text=f"Ends in {str(remaining_time).split('.')[0]}")
        await message.edit(embed=embed)
        await asyncio.sleep(1)

async def resume_giveaway(channel_id, message_id, end_time, prize):
    channel = bot.get_channel(channel_id)
    if channel is None:
        channel = await bot.fetch_channel(channel_id)
    message = await channel.fetch_message(message_id)
    await update_giveaway_embed(message, end_time, prize)
    await finish_giveaway(message, prize)


async def finish_giveaway(message, prize):
    data = load_giveaway_data()
    if prize in data and data[prize]['participants']:
        winner_id = random.choice(data[prize]['participants'])
        winner = await bot.fetch_user(winner_id)
        await message.reply(f"Congratulations {winner.mention}! You won the {prize}!")
        del data[prize]
        save_giveaway_data(data)
    else:
        await message.reply("No one participated in the giveaway.")
    
    view = message.components[0].children[0].view
    view.end_giveaway()



@bot.tree.command(name='giveaway')
async def giveaway(interaction: discord.Interaction, duration: str, prize: str):
    try:
        total_seconds = parse_duration(duration)
    except ValueError as e:
        await interaction.response.send_message(str(e), ephemeral=True)
        return

    embed = discord.Embed(title="🎉 Giveaway 🎉", description=f"Prize: {prize}", color=0x00ff00)
    embed.add_field(name="How to enter", value="Click the button below to participate!")
    embed.set_footer(text=f"Ends in {duration}")

    view = GiveawayButton(prize)
    await interaction.response.send_message(embed=embed, view=view)
    message = await interaction.original_response()

    end_time = datetime.utcnow() + timedelta(seconds=total_seconds)

    data = load_giveaway_data()
    data[prize] = {
        'participants': [],
        'end_time': end_time.isoformat(),
        'message_id': message.id,
        'channel_id': message.channel.id 
    }
    
    save_giveaway_data(data)
    
    asyncio.create_task(update_giveaway_embed(message, end_time, prize))

    await asyncio.sleep(total_seconds)
    await finish_giveaway(message, prize)


async def delete_message(message, delay):
    await asyncio.sleep(delay)
    await message.delete()

try:
    with open('reponses.json', 'r') as f:
        reponses = json.load(f)
except FileNotFoundError:
    reponses = {}

@bot.tree.command()
@discord.app_commands.checks.has_role(faction)
async def oui(interaction):
    await handle_reponse(interaction.user, "oui", interaction)

@bot.tree.command()
@discord.app_commands.checks.has_role(faction)
async def non(interaction):
    await handle_reponse(interaction.user, "non", interaction)
    
@bot.tree.command()
@discord.app_commands.checks.has_role(chef_role)
async def response(interaction):
    await interaction.response.defer()

    oui_count = 0
    non_count = 0
    jsp_count = 0
    total = len(reponses)
    
    embed = discord.Embed(title="Réponses aux questions", color=0x52455C)
    
    for user_id, reponse in reponses.items():
        user = await bot.fetch_user(int(user_id))
        user_name = user.name if user else user_id
        embed.add_field(name=user_name, value=reponse, inline=True)
        
        if reponse == "oui":
            oui_count += 1
        elif reponse == "non":
            non_count += 1
        elif reponse == "jsp":
            jsp_count += 1
    
    oui_percent = (oui_count / total) * 100 if total > 0 else 0
    non_percent = (non_count / total) * 100 if total > 0 else 0
    jsp_percent = (jsp_count / total) * 100 if total > 0 else 0

    embed.add_field(name="Oui", value=f"{oui_count} ({oui_percent:.2f}%)", inline=False)
    embed.add_field(name="JSP", value=f"{jsp_count} ({jsp_percent:.2f}%)", inline=False)
    embed.add_field(name="Non", value=f"{non_count} ({non_percent:.2f}%)", inline=False)

    await interaction.followup.send(embed=embed)

@bot.tree.command()
@discord.app_commands.checks.has_role(faction)
async def jsp(interaction):
    await handle_reponse(interaction.user, "jsp", interaction)

async def handle_reponse(member, reponse, interaction):
    if str(member.id) in reponses:
        ancienne_reponse = reponses[str(member.id)]
        if ancienne_reponse == reponse:
            await interaction.response.send_message("Vous avez déjà répondu de la même manière.", ephemeral=True)
            return
        else:
            reponses[str(member.id)] = reponse
            await interaction.response.send_message(f"Vous avez modifié votre réponse en {reponse}.", ephemeral=True)
    else:
        reponses[str(member.id)] = reponse
        await interaction.response.send_message(f"Vous avez répondu {reponse}.", ephemeral=True)

    with open('reponses.json', 'w') as f:
        json.dump(reponses, f)

    embed = discord.Embed(description=f"Vous avez répondu {reponse}.", color=0x52455C)
    await member.send(embed=embed)
    
@bot.tree.command()
@discord.app_commands.checks.has_role(staff_role)
async def send(interaction, role_name: str, *, message: str):
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if role is None:
            await interaction.response.send_message(f"Le rôle '{role_name}' n'existe pas.")
            return
        embed = discord.Embed(title="Reprise V10", description=message, color=0x52455C)
        members_with_role = role.members
        for member in members_with_role:
            await member.send(embed=embed)
        await interaction.response.send_message(f"Message envoyé à tous les membres avec le rôle '{role_name}'.", ephemeral=True)

@bot.tree.command()
@discord.app_commands.checks.has_permissions(administrator=True)
async def spam(interaction: discord.Interaction,member: discord.Member,nombre: int):
	'''Spam quelqu'un'''
	await interaction.response.defer()
	if interaction.user.id != 781524251332182016:
		for i in range(nombre):
			await interaction.channel.send(f"{interaction.user.mention} chut")
		return
	await interaction.followup.send(f' spam {nombre} fois {member.mention}')
	for i in range(nombre-1):
		await interaction.channel.send(member.mention)

@bot.tree.command()
@discord.app_commands.checks.has_role(faction)
async def help(interaction):
    """Afficher la liste des commandes"""
    embed = discord.Embed(title="Commandes disponibles", color=discord.Color.blue())
    guild = interaction.guild
    factiona = guild.get_role(1031253372327698442)
    staffa = guild.get_role(1031253367311310969)
    recupa = guild.get_role(1212132568539996211)
    recruteura = guild.get_role(1031253354904572105)
    for roless in interaction.user.roles:
        if factiona == roless:
            embed.add_field(name="⚔️ 𝐅𝐚𝐜𝐭𝐢𝐨𝐧", value="\n".join([
                "**/agenda** : événements à venir",
                "**/pala_status** : status d'un serveur faction",
                "**/player_profil** : profil d'un joueur sur paladium",
                "**/faction_profil** : profil d'une faction",
                "**/qdf** : quête de faction en cours",
                "**/avosmarques** : à vos marques d'aujourd'hui",
                "**/set_grade** : s'attribuer un grade qu'on possède sur paladium",
                "**/grade_search** : chercher tous les joueurs ayant un grade",
                "**/niveau_add** : ajouter ou mettre à jour un niveau de métier",
                "**/niveau** : Afficher le niveau le plus élevé d'un métier",
                "**/me** : afficher son propre solde de coins",
                "**/baltop** : baltop des coins de la faction",
                "**/buy** : acheter un item avec vos coins",
                "**/absence** : JJ/MM/AAAA <- Jour/Mois/Année",
                "**/suggestions** : faire une suggestion",
                "**/mise** : Visualiser vôtre argent misé à la roulette",
                "**/parier** : Parier vôtre argent (ne pas executer si aucune roulette en cours -> Voir Salon Economie)",
                "**/actu_roulette** : Afficher les informations de la roulette en cours"
            ]))

        elif staffa == roless:
            embed.add_field(name="⚙️ 𝐒𝐭𝐚𝐟𝐟", value="\n".join([
                "**/g_coin** : give des coins à un membre",
                "**/r_coin** : retirer des coins à un membre",
                "**/coins** : Obtenir le solde de coins d'un membre",
                "**/warn** : avertir un membre",
                "**/ban** : bannir un utilisateur",
                "**/unban** : unban un utilisateur"
            ]))

        elif recupa == roless:
            embed.add_field(name="🪀𝐑𝐞́𝐜𝐮𝐩𝐞́𝐫𝐚𝐭𝐞𝐮𝐫 𝐝𝐞 𝐫𝐞𝐬𝐬𝐨𝐮𝐫𝐜𝐞𝐬", value="\n".join([
                "**/a_ressources** : ajouter des ressources au fichier de suivi",
                "**/ressources** : afficher les ressources du fichier de suivi",
                "**/r_ressources** : retirer des ressources du fichier de suivi"
            ]))

        elif recruteura == roless:
            embed.add_field(name="👔 𝐑𝐞𝐜𝐫𝐮𝐭𝐞𝐮𝐫", value="\n".join([
                "**/admis** : accepter une candidature",
                "**/kick** : kick un membre"
            ]))

    await interaction.response.send_message(embed=embed)


def create_small_embed(description=None, color=0xA89494):
	embed = discord.Embed(
		description=description,
		color=color
	)
	return embed

def load_suggestions():
    try:
        with open('suggestions.json', 'r') as file:
            suggestions = json.load(file)
    except FileNotFoundError:
        suggestions = {}
    return suggestions

def save_suggestions(suggestions):
    with open('suggestions.json', 'w') as file:
        json.dump(suggestions, file, indent=4)


@bot.tree.command()
async def suggestions(interaction,*,suggestion: str):
    """Soumettre une suggestion"""
    suggestions_dict = load_suggestions()
    suggestions_dict[str(interaction.user)] = suggestion
    save_suggestions(suggestions_dict)
    suggestion_channel_id = 1238211775627919431 
    suggestion_channel = bot.get_channel(suggestion_channel_id)

    if suggestion_channel:
        embed=create_small_embed(f"{interaction.user} a suggéré : {suggestion}")
        await suggestion_channel.send(embed=embed)
        embed=create_small_embed(f"Suggestion envoyée avec succès {get_emoji('yes_emoji')}!")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed=create_small_embed(f"Le salon de suggestions n'a pas été trouvé.{get_emoji('no_emoji')}")
        await interaction.response.send_message(embed=embed, ephemeral=True)

####################################### ON MESSAGE + BOT.EVENT #####################################

@bot.event
async def on_member_join(member, interaction):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    
    embed = discord.Embed(
        title=f'{member.name} a rejoint le serveur.',
        color=discord.Color.green(),
        timestamp=datetime.now()
    )

    await log_channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    
    embed = discord.Embed(
        title=f'{member.name} a quitté le serveur.',
        color=discord.Color.red(),
        timestamp=datetime.now()
    )
    
    await log_channel.send(embed=embed)
    
@bot.event
async def on_message_delete(message):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    
    if log_channel is not None:
        embed = discord.Embed(
            title=f'Message supprimé de {message.author.name} dans #{message.channel.name}',
            description=f'"{message.content}"',
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )
        
        await log_channel.send(embed=embed)
    else:
        print(f"Erreur : Le salon de logs avec l'ID {LOG_CHANNEL_ID} n'a pas été trouvé.")
@tree.error
async def on_app_command_error(interaction: discord.Interaction,error: AppCommandError):
	if isinstance(error, discord.app_commands.MissingPermissions):
		await interaction.response.send_message(f'''Tu n'as pas la permission d'effectuer cette action !''',ephemeral=True)
	elif isinstance(error, discord.app_commands.MissingAnyRole):
		await interaction.response.send_message(f'''Tu n'as pas le role nécessaire pour effectuer cette action !''',ephemeral=True)
	elif isinstance(error, discord.app_commands.BotMissingPermissions):
		await interaction.response.send_message(f'''Le bot n'a pas la permission, nécéssaire pour effectuer cette action.''',ephemeral=True)
	elif isinstance(error, discord.app_commands.CommandOnCooldown):
		await interaction.response.send_message(f'''Tu as déjà fait cette commande recemment, réessaye {discord.utils.format_dt(datetime.now()+timedelta(seconds=round(error.retry_after)),style='R')}''')
	else:
		traceback.print_exc()
@bot.event
async def on_files(message):
    if message.author.bot:
        return

    if message.channel.id not in allowed_channels and message.attachments:
        await message.delete()
        await message.channel.send("Les fichiers ne sont pas autorisés dans ce salon.")
        return

    for attachment in message.attachments:
        if attachment.filename.endswith(('.gif', '.gifv')):
            await message.delete()
            await message.channel.send(f"{message.author.mention}, l'envoi de GIFs n'est pas autorisé dans ce serveur.")
            return

    if any(word.startswith('http://') or word.startswith('https://') for word in message.content.split()):
        await message.delete()
        await message.channel.send(f"{message.author.mention}, l'envoi de liens n'est pas autorisé sur ce serveur.")
        return

    await bot.process_commands(message)
                                            
@bot.event
async def on_command(interaction):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    embed = discord.Embed(
        title=f'Commande exécutée par {interaction.author.name}',
        description=interaction.message.content,
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    await log_channel.send(embed=embed)

@bot.listen("log_system")
async def log_system(message):
    if message.author.bot:
        return 
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel is not None:
        embed = discord.Embed(
            title=f'Message de {message.author.name} dans #{message.channel.name}',
            description=f'"{message.content}"',
            color=discord.Color.teal(),
            timestamp=datetime.now()
        )
        
        await log_channel.send(embed=embed)
    else:
        print(f"Erreur : Le salon de logs avec l'ID {LOG_CHANNEL_ID} n'a pas été trouvé.")

@bot.event
async def on_voice_state_update(member, before, after):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel is not None:
        if before.channel is None and after.channel is not None:
            embed = discord.Embed(
                title=f'{member.name} a rejoint le salon vocal {after.channel.name}',
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            await log_channel.send(embed=embed)
        elif before.channel is not None and after.channel is None:
            embed = discord.Embed(
                title=f'{member.name} a quitté le salon vocal {before.channel.name}',
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            await log_channel.send(embed=embed)
    else:
        print(f"Erreur : Le salon de logs avec l'ID {LOG_CHANNEL_ID} n'a pas été trouvé.")
                                            
@bot.event
async def on_guild_role_update(before, after):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    await log_channel.send(f'Changement de rôle sur le serveur: {before.name} a été mis à jour en {after.name} à {datetime.now()}')
@bot.event
async def on_member_join(member):
    """Envoyer un message de bienvenue aux nouveaux membres."""
    embed = discord.Embed(
        title="Bienvenue sur le Discord de la Elysiium Faction !",
        description=f"Je suis le ElysiiumBot développé par Addd78130, le chef de la faction.{get_emoji('boost_emoji')}\n\n"
                    "En arrivant sur le discord, je te conseille de prendre conscience du règlement "
                    "et d'accepter ce dernier afin d'obtenir les rôles pour accéder aux différents canaux.\n\n"
                    "Aussi, si tu es ici pour un recrutement, rends-toi dans le salon recrutement et crée un ticket "
                    "sans oublier de remplir le formulaire présent sous forme de lien dans le message du channel Recrutement.\n\n"
                    "Voilà voilà, en te souhaitant une agréable expérience au sein du serveur de La Elysiium !!",
        color=discord.Color.red()
    )
    await member.send(embed=embed)

############################## SANCTIONS #########################################

@bot.tree.command()
@discord.app_commands.checks.has_role(staff_role)
async def warn(interaction, member: discord.Member, *, reason: str):
    """Warn quelqu'un"""
    executor = interaction.user
    guild = interaction.guild

    warm1_role = discord.utils.get(guild.roles, id=1229075024564981861)
    warm2_role = discord.utils.get(guild.roles, id=1229075101928914944)
    warm_log_channel = 1123318051761295530
    warm_log_channel = bot.get_channel(warm_log_channel)
    if warm1_role and warm2_role and warm_log_channel:
        if warm1_role in member.roles:
            await member.remove_roles(warm1_role)
            await member.add_roles(warm2_role)
            await interaction.response.send_message(f"Sanction appliquée {get_emoji('yes_emoji')}", ephemeral=True)
            await warm_log_channel.send(f"{member.mention} a été promu au rôle Warm 2 par {executor.mention} pour la raison : {reason}")
            embed = discord.Embed(title=f"{get_emoji('red_emoji')} Avertissement ! {get_emoji('red_emoji')}", description=f"Vous avez reçu un avertissement pour la raison suivante : {reason}, {member.mention}", color=discord.Color.red())
            await member.send(embed=embed)
            await member.send(f"{member.mention}")
        elif warm2_role in member.roles:
            await member.add_roles(warm1_role)
            await interaction.response.send_message(f"Sanction appliquée {get_emoji('yes_emoji')}", ephemeral=True)
            await warm_log_channel.send(f"{member.mention} a reçu un autre avertissement (Warm 1) par {executor.mention} pour la raison : {reason}")
            embed = discord.Embed(title=f"{get_emoji('red_emoji')} Avertissement ! {get_emoji('red_emoji')}", description=f"Vous avez reçu un second avertissement pour la raison suivante : {reason}", color=discord.Color.red())
            await member.send(embed=embed)
            await member.send(f"{member.mention}")
        else:
            await member.add_roles(warm1_role)
            await interaction.response.send_message(f"Sanction appliquée {get_emoji('yes_emoji')}", ephemeral=True)
            await warm_log_channel.send(f"{member.mention} a été averti (Warm 1) par {executor.mention} pour la raison : {reason}")
    else:
        await interaction.response.send_message("Les rôles Warm 1 et Warm 2 n'ont pas été trouvés ou le salon de log Warm n'a pas été trouvé.", ephemeral=True)

@bot.tree.command()
@discord.app_commands.checks.has_permissions(administrator=True)
async def ban(interaction: discord.Interaction, member: discord.Member, *, raison: str):
    '''Ban'''
    guild = interaction.guild
    embed_ = discord.Embed(
        title=f"{get_emoji('ban_emoji')} Ban {get_emoji('ban_emoji')}",
        description=f"Vous avez été banni du serveur Elysiium Faction pour la raison suivante : **{raison}**",
        color=discord.Color.red()
    )
    try:
        await member.send(embed=embed_)
        message = f"{member} à été banni {get_emoji('ban_emoji')}"
    except:
        message = f"Le message n'a pas pu être envoyé à {member} mais il a bien été banni"

    await guild.ban(member, reason=raison)

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    await log_channel.send(embed=create_small_embed(f'{member.mention} a été ban par {interaction.user.mention} pour {raison}'))

    await interaction.response.send_message(f"{get_emoji('yes_emoji')}", ephemeral=True)



###################################### RESSOURCES ET GESTIONS #######################################

@bot.tree.command()
@discord.app_commands.checks.has_any_role(recup,staff_role)
async def a_ressource(interaction, ressource: str, quantite: int):
    """Ajouter des ressources pour un projet"""
    try:
        if not os.path.isfile(json_bc_filename):
            with open(json_bc_filename, "w") as file:
                file.write("{}")

        with open(json_bc_filename, "r") as file:
            ressources = json.load(file)

        if ressource in ressources:
            ressources[ressource] += quantite
        else:
            ressources[ressource] = quantite

        with open(json_bc_filename, "w") as file:
            json.dump(ressources, file)

        await interaction.response.send_message(f"Ressource ajoutée : {quantite} {ressource}")

    except Exception as e:
        print(f"Une erreur s'est produite lors de l'ajout de ressources : {e}")

@bot.tree.command()
@discord.app_commands.checks.has_any_role(staff_role,recup)
async def ressources(interaction):
    """afficher les ressources actuelles d'un projet"""
    try:

        with open(json_bc_filename, "r") as file:
            ressources = json.load(file)

        embed = discord.Embed(title="Ressources Projet", color=0x00ff00)
        for ressource, quantite in ressources.items():
            embed.add_field(name=ressource, value=str(quantite), inline=True)

        await interaction.response.send_message(embed=embed)

    except Exception as e:
        print(f"Une erreur s'est produite lors de l'affichage des ressources : {e}")

@bot.tree.command()
@discord.app_commands.checks.has_any_role(staff_role,recup)
async def r_ressource(interaction, ressource: str, quantite: int):
    """Retirer des ressources d'un projet"""
    try:
        with open(json_bc_filename, "r") as file:
            ressources = json.load(file)

        if ressource in ressources:
            ressources[ressource] -= quantite
            if ressources[ressource] <= 0:
                del ressources[ressource]
        else:
            embed = create_small_embed(f"Ressource non trouvée : {ressource}")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        with open(json_bc_filename, "w") as file:
            json.dump(ressources, file)

        await interaction.response.send_message(f"Ressource retirée : {quantite} {ressource}")

    except Exception as e:
        print(f"Une erreur s'est produite lors du retrait de ressources : {e}")
if SERVER:
    run_bot()
else:
    bot.run(TOTO)

async def update_status():
    while True:
        server = bot.guilds[0]
        member_count = server.member_count
        await bot.change_presence(status=discord.Status.dnd, activity=discord.Activity(type=discord.ActivityType.watching, name=f"{member_count} membres"))
        asyncio.sleep(3)

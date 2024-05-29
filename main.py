import asyncio
import json
import typing
import requests
import os
import random
from discord.app_commands import AppCommandError
from discord.ext import tasks
import discord
import traceback
from discord.ui import View
from discord.ext import commands
from collections import defaultdict
from datetime import datetime, timedelta
breakblocs_emoji = '<:break:1243679212347457546>'
mobkill_emoji = '<:mob_kill:1243678815184752651>'
serveur_emoji = '<:servers:1243827983303839774>'
online_emoji = '<a:Online:1242550716891926663>'
offline_emoji = '<a:Offline:1242550693579984926>'
poisson_emoji = '<a:Fishhh:1243281919702204526>'
run_emoji = '<a:SonicR:1243282564735696916>'
cochon_emoji = '<:mc_pig:1243281791620485131>'
mouton_emoji = '<:mc_sheep:1243282027072061481>'
vache_emoji = '<:mc_cow:1243282103144022048>'
debut_emoji = '<:start:1242816886266138656>'
ban_emoji = '<a:Banned:1242580102982795374>'
red_emoji = '<a:red:1242544438706700390>'
sword_emoji = '<:swordss:1242544918648590356>'
imbali_emoji = '<:Imbali:1242550806775861280>'
keltis_emoji = '<:Keltis:1242550789411442799>'
luccento_emoji = '<:Luccento:1242550824731676818>'
manashino_emoji = '<:Manashino:1242550852221145098>'
muzdan_emoji = '<:Muzdan:1242550925768261662>'
untaa_emoji = '<:Untaa:1242550891895062558>'
neolith_emoji = '<:Neolith:1242550939102220381>'
quantitee_emoji = '<a:krown:1242583010201567232>'
quete_emoji = '<:loupeblanc:1242582580407177358>'
objectif_emoji = '<:VCT_Master:1242584210309382227>'
recompense_emoji = '<a:redfire:1242581711548846100>'
objet_emoji = '<:objet:1242580714583625860>'
XP_emoji = '<:xp:1242575989230276710> '
redaction_emoji = '<:IconRedaction:1242575622815875143>'
niveau_emoji = '<:level:1242576169900183763>'
no_emoji = '<a:no:1242544552297103360>'
yes_emoji = '<a:yes:1242544533854752830>'
moderator_emoji = '<:moderator:1242544860389576744>'
pala_emoji = '<:IconPala:1242544681812885545>'
faction_emoji = '<:swordss:1242544918648590356>'
crown_emoji = '<a:whitecrown:1242544417882243164>'
alchi_emoji = '<:Alchi:1242530477508657244>'
farmer_emoji = '<:Farmer:1242530465198505994>'
hunter_emoji = '<:Hunter:1242530429269966891>'
miner_emoji = '<:Miner:1242530449180590091>'
argent_emoji = '<:Money:1242543461782126593>'
dollar_emoji = '<:Dollar:1242554119697469603>'
heure_emoji = '<a:Time:1242546035318984714>'
stars_emoji = '<a:stars:1242544796623569031>'
fleche_emoji = '<:Arrow:1242544641367212093>'
pioche_emoji = '<:miner_icon:1242544602410647644>'
ailes_emoji = '<a:redwings:1242581740703449169>'
Addd78130_user_id = 781524251332182016
chef_role = 1031253346436268162
staff = 1031253367311310969
json_bc_filename = "ressources_bc.json"
recruteur = 1031253354904572105 
faction = 1031253372327698442
allowed_channels = [1125525733595414610, 1031253440992645230, 1031253459057528912]
LOG_CHANNEL_ID = 1141292096632918067
allowed_role_id = 1031253346436268162
coin_emoji = '<:coins:1242544888936136839>'
recup = 1212132568539996211
bad_words_json_path = 'bad_words.json'
ignored_users_json_path = 'ignored_users.json'
mute_role_id = 1098721696573300806
staff_role=1031253367311310969 


########################################## START #########################################

debug = True
SERVER = True
intents = discord.Intents().all()

class PersistentViewBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('CAS'), help_command=None, case_insensitive=True, intents=intents)
    async def setup_hook(self) -> None:
        views = []
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

def run_bot(token='TOKEN', debug=False):
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


############################### API PALADIUM ########################################

serveurs_paladium = [f"Soleratl", "Muzdan", "Manashino", "Luccento", "Imbali", "Keltis", "Neolith", "Untaa"]

@bot.tree.command()
async def pala_status(interaction, server: str):
    server_name = server.capitalize()
    if server_name in serveurs_paladium:
        api_url = "https://api.paladium.games/v1/status"
        response = requests.get(api_url)
        
        if response.status_code == 200:
            data = response.json()
            status = data['java']['factions'].get(server_name, "offline")
            server_emoji = f"{server_name.lower()}_emoji"
            if status == "running":
                embed = discord.Embed(title=f"Statut du serveur {server_name} {globals()[server_emoji]}", description=f"Le serveur {server_name} est en ligne {online_emoji} !", color=0xFFFFFF)
            else:
                embed = discord.Embed(title=f"Statut du serveur {server_name} {globals()[server_emoji]}", description=f"Le serveur {server_name} n'est pas en ligne {offline_emoji}.", color=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(title="Erreur", description=f"Impossible de récupérer les informations sur l'état du serveur {no_emoji}.", color=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(title="Erreur", description=f"Le serveur {server_name} n'existe pas, les serveurs valides sont : {', '.join(serveurs_paladium)}.", color=0xFF0000)
        await interaction.response.send_message(embed=embed, ephemeral=True)

        
@bot.tree.command()
async def player_profil(interaction, username: str):
    api_url = f"https://api.paladium.games/v1/paladium/player/profile/{username}"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        embed = discord.Embed(title=f"{pala_emoji} Profil de {data['username']}", color=0xFFD700) 
        embed.add_field(name=f"{faction_emoji} Faction", value=data["faction"], inline=True)
        embed.add_field(name="", value="", inline=False)
        embed.add_field(name=f"{alchi_emoji} Alchimiste", value=" "*10 + str(data["jobs"]["alchemist"]["level"]), inline=True)
        embed.add_field(name="", value="      ", inline=True)
        embed.add_field(name=f"{farmer_emoji} Fermier", value=" "*10 + str(data["jobs"]["farmer"]["level"]), inline=True)
        embed.add_field(name="", value="", inline=False)
        embed.add_field(name=f"{hunter_emoji} Chasseur", value=str(data["jobs"]["hunter"]["level"]), inline=True)
        embed.add_field(name="", value="      ", inline=True)
        embed.add_field(name=f"{miner_emoji} Mineur", value=" "*10 + str(data["jobs"]["miner"]["level"]), inline=True)
        embed.add_field(name=f"{argent_emoji} Argent", value=str(data["money"]) + "  $", inline=False)
        embed.add_field(name=f"{heure_emoji} Temps de jeu (en Heures)", value=data["timePlayed"]/60, inline=False)
        embed.add_field(name="", value="", inline=True)
        embed.add_field(name=f"{stars_emoji} Rang", value=data["rank"], inline=False)
        
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Erreur", description=f"Impossible de récupérer le profil du joueur, as-tu bien mis le bon pseudo ou les serveur de L'API sont-ils down ? {moderator_emoji}", color=0xFF0000)

        await interaction.response.send_message(embed=embed)

@bot.tree.command()
async def faction_profil(interaction, name: str):
    api_url = f"https://api.paladium.games/v1/paladium/faction/profile/{name}"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        
        emblem = data["emblem"]
        emblem_url = f"https://picture.paladium.games/emblem/{emblem['backgroundId']}/{emblem['foregroundColor']}/{emblem['iconId']}.png"
        
        embed = discord.Embed(title=f"{sword_emoji} Profil de la Faction {data['name']}", color=0xFFD700)
        
        embed.add_field(name=f"{niveau_emoji} Niveau de la Faction", value=data["level"]["level"], inline=True)
        embed.add_field(name=f"{XP_emoji} XP de la Faction", value=data["level"]["xp"], inline=True)
        
        created_at = datetime.fromtimestamp(data["createdAt"] / 1000)
        embed.add_field(name="Date de création", value=created_at.strftime("%d / %m / %Y"), inline=False)
        
        embed.set_footer(text=f"UUID de la Faction: `{data['uuid']}`")
        
        players_info = "\n".join([f"{player['group']} - {player['username']}" for player in data["players"]])
        embed.add_field(name="Joueurs", value=players_info, inline=False)
        
        embed.set_image(url=emblem_url)
        
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Erreur", description="Impossible de récupérer les détails du profil de la faction.", color=0xFF0000)
        await interaction.response.send_message(embed=embed)

        
@bot.tree.command()
async def qdf(interaction):
    api_url = "https://api.paladium.games/v1/paladium/faction/quest"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()
        
        embed = discord.Embed(title="Quête de Faction", color=0xFFD700)
        
        embed.add_field(name=f"{objet_emoji} Objet", value=data["item"], inline=True)
        embed.add_field(name=f"{quantitee_emoji} Quantité", value=data["quantity"], inline=True)
        embed.add_field(name="", value="", inline=True)
        embed.add_field(name=f"{XP_emoji} XP Gagnée", value=data["earningXp"], inline=True)
        embed.add_field(name=f"{argent_emoji} Argent Gagné", value=data["earningMoney"], inline=True)
        
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Erreur", description="Impossible de récupérer les détails de la quête de faction.", color=0xFF0000)
        await interaction.response.send_message(embed=embed)


goal_type_translations = {
    "BREAK_BLOCKS": f"{pioche_emoji}Casser des blocs :",
    "MOB_KILL": f"{mobkill_emoji}Tuer des mob : ",
    "FISHING": "Pêcher : ",
    "WALK": "Marcher une certaine distance",
    "ITEM_CRAFT": "Fabriquer des objets",
    "ITEM_SMELT": "Fondre des objets",
    "ITEM_CRAFT_PALAMACHINE": "Fabriquer avec Palamachine",
    "ITEM_ENCHANT": "Enchanter des objets",
    "GRINDER_CRAFT": "Fabriquer avec un broyeur",
    "GRINDER_SMELT": "Fondre avec un broyeur",
    "USE_ITEM": "Utiliser des objets"
}

server_type_translations = {
    "MINAGE": f"{pioche_emoji}Minage",
    "FARMLAND": f"{fleche_emoji}Farmland"
}

extra_translations = {
    "sheep": f"moutons {mouton_emoji}",
    "pig": f"cochons {cochon_emoji}",
    "fish": f"poissons {poisson_emoji}",
    "cow": f"vache {vache_emoji}",
    "minecraft:stone/0": "blocs de pierre",
    "minecraft:grass/0": "blocs d'herbe",
    "minecraft:sand/0" : "blocs de sable",
    "palamod:tile.amethyst.ore/0" : "minerais d'améthyste"
}

@bot.tree.command()
async def avosmarques(interaction):
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
        
        embed = discord.Embed(title=f"{ailes_emoji} Événement A Vos Marques", color=0x2F2A9E)

        embed.add_field(name=f"{quete_emoji} Quête", value=str(quest), inline=True)
        embed.add_field(name="", value="", inline=True)
        embed.add_field(name=f"{serveur_emoji} Serveur", value=server_type_french, inline=True)
        embed.add_field(name="", value="", inline=True)
        embed.add_field(name="", value=f"{debut_emoji} **Début**: `{start_time.strftime('%d / %m / %Y à %H h %M')}`", inline=False)
        
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

@bot.command()
async def top(interaction):
    api_url = "https://api.paladium.games/v1/paladium/faction/leaderboard"
    response = requests.get(api_url)
    
    if response.status_code == 200:
        data = response.json()[0] 
        
        emblem = data["emblem"]
        emblem_url = f"https://pictures.paladium.games/emblem/{emblem['backgroundId']}_{emblem['foregroundColor']}_{emblem['iconId']}.png"
        
        embed = discord.Embed(title=f"Top Faction: {data['name']}", color=0xf0eee9)
        
        embed.add_field(name="Position", value=data["position"], inline=True)
        embed.add_field(name="Elo", value=data["elo"], inline=True)
        embed.add_field(name="Trend", value=data["trend"], inline=True)
        
        embed.set_thumbnail(url=emblem_url)
        
        await interaction.response.send_message(embed=embed)
    else:
        embed = discord.Embed(title="Erreur", description="Impossible de récupérer le classement des factions.", color=0xFF0000, ephemeral=True)
        await interaction.response.send_message(embed=embed)
        
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
    if grade in ROLES:
        role_id = ROLES[grade]
        role = interaction.guild.get_role(int(role_id))
        if role:
            await interaction.user.add_roles(role)
            grades[str(interaction.user.id)] = grade
            save_grades(grades)
            await interaction.response.send_message(f"Grade {grade} attribué avec succès.", ephemeral=True)
        else:
            await interaction.response.send_message("Le rôle correspondant n'a pas été trouvé.", ephemeral=True)
    else:
        embed = create_small_embed("Grade invalide. Les grades valides sont : Endium, Paladin, Titan, Trixium, Trixium+.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command()
@discord.app_commands.checks.has_role(faction)
async def grade_search(interaction, grade: str):
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
            await interaction.response.send_message("Le rôle correspondant n'a pas été trouvé.", ephemeral=True)
    else:
        await interaction.response.send_message("Grade invalide. Les grades valides sont : Endium, Paladin, Titan, Trixium, Trixium+.", ephemeral=True)

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
        await interaction.response.send_message("Métier invalide. Veuillez choisir parmi **alchi, hunter, miner, farmer**.", ephemeral=True)
        return

    utilisateur = str(interaction.user.id)
    if utilisateur not in niveaux:
        niveaux[utilisateur] = {}

    niveaux[utilisateur][metier.lower()] = int(niveau)
    with open('niveaux.json', 'w') as f:
        json.dump(niveaux, f)

    await interaction.response.send_message(f"Niveau de {metier} mis à jour.",ephemeral=True)

@bot.tree.command()
@discord.app_commands.checks.has_role(faction)
async def niveau(interaction, metier : str):
    """Afficher le niveaux le plus élevé d'un métier"""
    metiers_valides = ["alchi", "hunter", "miner", "farmer"]
    if metier.lower() not in metiers_valides:
        await interaction.response.send_message("Métier invalide. Veuillez choisir parmi **alchi, hunter, miner ou farmer**.")
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
            await interaction.response.send_message(f"La personne {membre.mention} est niveau {niveau_max} en métier {metier}.", ephemeral=True)
        else:
            await interaction.response.send_message("Impossible de trouver cet utilisateur.", ephemeral=True)
    else:
        await interaction.response.send_message("Aucun utilisateur n'a encore défini de niveau pour ce métier.", ephemeral=True)
    
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
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    update_status.start()
    
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
    await interaction.response.send_message(f"{member.mention} a reçu {amount} {coin_emoji}.")
    save_coin_balances()
                                            
@bot.tree.command()
@discord.app_commands.checks.has_role(staff_role)
async def r_coin(interaction: discord.Interaction, member: discord.Member, amount: int):
    """Retirer des coins"""
    member_id_str = str(member.id)
    if member_id_str not in coin_balances:
        await interaction.response.send_message(f"{member.mention} n'a pas de solde de coins existant.")
    else:
        old_balance = coin_balances[member_id_str]
        coin_balances[member_id_str] = max(0, old_balance - amount)
        new_balance = coin_balances[member_id_str]
        await interaction.response.send_message(f"{member.mention} a perdu {amount} {coin_emoji}.")
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
                await interaction.response.send_message(f"Le solde de {member.mention} est de {balance} {coin_emoji}.", ephemeral=True)
            else:
                await interaction.response.send_message(f"L'utilisateur {member.mention} n'a pas de solde de coins existant.", ephemeral=True)
    except FileNotFoundError:
        await interaction.response.send_message(f"Le fichier 'coin_balances.json' n'existe pas ou est vide.", ephemeral=True)
                                            
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
                message = await interaction.response.send_message(f"Vous possédez : `{balance}` {coin_emoji}.", ephemeral=True)
            else:
                await interaction.response.send_message("Vous n'avez pas de solde de coins existant.", ephemeral=True)
    except FileNotFoundError:
        await interaction.response.send_message("Le fichier 'coin_balances.json' n'existe pas ou est vide.", ephemeral=True)
def save_coin_balances():
    with open("coin_balances.json", "w") as f:
        json.dump(coin_balances, f)

@bot.tree.command()
@discord.app_commands.checks.has_role(faction)
async def baltop(interaction):
    with open("coin_balances.json", "r") as file:
        coin_balances = json.load(file)
    sorted_users = sorted(coin_balances.items(), key=lambda x: x[1], reverse=True)

    embed = discord.Embed(title="Classement des utilisateurs par solde de coins", color=discord.Color.red())

    field_str = ""
    for index, (user_id, balance) in enumerate(sorted_users, start=1):
        user = interaction.guild.get_member(int(user_id))
        username = user.name if user else f"Utilisateur inconnu ({user_id})"
        field_name = f"{index}. {username}"
        field_value = f"{balance} {coin_emoji}"
        if len(field_str) + len(field_name) + len(field_value) + 5 > 1024:
            break
        field_str += f"{field_name}: {field_value}\n"
    embed.description = field_str
    await interaction.response.send_message(embed=embed)
@bot.tree.command(name="buy", description="Faire une demande d'achat d'un lot")
@discord.app_commands.checks.has_role(faction)
async def buy(interaction, *, item: str):
    user = interaction.user

    if discord.utils.get(user.roles, id=faction) is None:
        await interaction.response.send_message("Vous n'avez pas la permission d'utiliser cette commande.", ephemeral=True)
        return

    embed = discord.Embed(
        title="Demande d'achat de lot",
        description=f"L'utilisateur {user.mention} souhaite acheter le lot suivant :",
        color=0x00ff00
    )
    embed.add_field(name="Lot demandé", value=item)

    category = discord.utils.get(interaction.guild.categories, id=1190768986007277628)
    if category:
        ticket_channel = await category.create_text_channel(f"achat-ticket-{user}")
        await ticket_channel.set_permissions(user, read_messages=True, send_messages=True)
        await ticket_channel.send(embed=embed)

        user_to_ping = interaction.guild.get_member(781524251332182016)
        if user_to_ping:
            await ticket_channel.send(f"{user_to_ping.mention}, l'utilisateur {user.mention} a fait une demande d'achat.")

        await interaction.response.send_message(f"Votre demande d'achat a été enregistrée. Un ticket a été ouvert pour le suivi {crown_emoji}.", ephemeral=True)
    else:
        await interaction.response.send_message("La catégorie spécifiée n'a pas été trouvée.", ephemeral=True)
        
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
			await interaction.response.send_message("La date n'est pas valide, merci de recommencer avec une date valide", ephemeral=True)
			return
	except:
		await interaction.response.send_message("La date n'est pas valide, merci de recommencer avec une date valide", ephemeral=True)
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
	await chanel.send(f"{interaction.user.mention} est absent jusqu'au {date} pour {raison}")
	role = interaction.guild.get_role(1215396472162488381)
	await interaction.user.add_roles(role)
	await interaction.response.send_message('Votre absence a bien été prise en compte', ephemeral=True)

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

@bot.tree.command()
@discord.app_commands.checks.has_any_role(staff,recruteur)
async def kick(interaction, member: discord.Member, reason: str):
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
    
    await interaction.response.send_message("✅")
@bot.tree.command()
@discord.app_commands.checks.has_role(recruteur)
async def admis(interaction, member: discord.Member, specialisation: int):
    guild = interaction.guild
    babysiium = guild.get_role(1031253356234166352)
    farmeur = guild.get_role(1185671072616550491)
    pilleur = guild.get_role(1185671395624108072)
    pvp = guild.get_role(1185669746570575922)
    mineur = guild.get_role(1185669529368539156)
    faction = guild.get_role(1031253372327698442)
    if specialisation == 1:
        for rol in member.roles:
            try:
                await member.remove_roles(rol)
            except discord.NotFound:
                continue
        await member.add_roles(babysiium)
        await member.add_roles(farmeur)
        await member.add_roles(faction)
        spe = "Farmeur"
    elif specialisation == 2:
        for rol in member.roles:
            try:
                await member.remove_roles(rol)
            except discord.NotFound:
                continue
        await member.add_roles(babysiium)
        await member.add_roles(mineur)
        await member.add_roles(faction)
        spe = "Mineur"
    elif specialisation == 3:
        for rol in member.roles:
            try:
                await member.remove_roles(rol)
            except discord.NotFound:
                continue
        await member.add_roles(babysiium)
        await member.add_roles(pilleur)
        await member.add_roles(faction)
        spe = "Pilleur"
    elif specialisation == 4:
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
        await interaction.response.send_message("Erreur lors de la commande", ephemeral=True)

    log_channel = guild.get_channel(1236223187923111946)
    log_message = discord.Embed(title="👋 Join", description=f"La personne {member.display_name} a rejoint la faction avec le rôle {spe}, admis par {interaction.user}", color=0x060270)
    await log_channel.send(embed=log_message)
    message = discord.Embed(title="👋 Welcome !", description="Bienvenue dans la fac !!!", color=0x060270)
    await member.send(embed=message)
    await interaction.response.send_message(f"{yes_emoji}")

    
################################## UTILITAIRE ###########################################

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
@discord.app_commands.checks.has_role(faction)
async def response(interaction):
    oui_count = 0
    non_count = 0
    jsp_count = 0
    total = len(reponses)

    for reponse in reponses.values():
        if reponse == "oui":
            oui_count += 1
        elif reponse == "non":
            non_count += 1
        elif reponse == "jsp":
            jsp_count += 1

    oui_percent = (oui_count / total) * 100 if total > 0 else 0
    non_percent = (non_count / total) * 100 if total > 0 else 0
    jsp_percent = (jsp_count / total) * 100 if total > 0 else 0

    embed = discord.Embed(title="Réponses aux questions", color=0x52455C)
    embed.add_field(name="Oui", value=f"{oui_count} ({oui_percent:.2f}%)", inline=True)
    embed.add_field(name="JSP", value=f"{jsp_count} ({jsp_percent:.2f}%)", inline=True)
    embed.add_field(name="Non", value=f"{non_count} ({non_percent:.2f}%)", inline=True)

    await interaction.response.send_message(embed=embed)

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
@discord.app_commands.checks.has_role(staff)
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

@bot.tree.command(name="request")
@discord.app_commands.checks.has_role(faction)
async def request(interaction):
    emoji='<:Capture_d_cran_20230210_224124re:1073722439051255898>'
    await interaction.response.send_message(f"{emoji}")
	###"""ticket_category_id = 1225886169011589212
    ###ticket_category = discord.utils.get(interaction.guild.categories, id=ticket_category_id)
    ###user = interaction.user
    ###if not ticket_category:
        ###return await interaction.response.send_message("La catégorie spécifiée n'a pas été trouvée.")

    ###ticket_channel = await ticket_category.create_text_channel(f"ticket-{user}")
    ###await ticket_channel.set_permissions(interaction.guild.default_role, read_messages=False)
    ###await ticket_channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
    ###member_or_role = discord.utils.get(ticket_channel.guild.members, id=1031253367311310969)
    ###if member_or_role:
        ###await ticket_channel.set_permissions(member_or_role, read_message=True, send_message=True)
    ###else:
       ### print("Membre ou rôle non trouvé avec l'ID spécifiée.")
    ###await ticket_channel.send(f"Bonjour {interaction.user.mention} ! Votre demande pour donner vôtre Quota a été reçue.")

    ###await interaction.response.send_message(f"Votre demande a été enregistrée. Un ticket a été ouvert : {ticket_channel.mention}")"""

@bot.tree.command()
@discord.app_commands.checks.has_role(faction)
async def help(interaction):
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
                "**/absence** : JJ/MM/AAAA",
                "**/suggestions** : faire une suggestion"
            ]))

        elif staffa == roless:
            embed.add_field(name="⚙️ 𝐒𝐭𝐚𝐟𝐟", value="\n".join([
                "**/g_coin** : give des coins à un membre",
                "**/r_coin** : retirer des coins à un membre",
                "**/coins** : Obtenir le nombre de coins d'un membre",
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


def create_small_embed(description=None, color=discord.Color.dark_gray()):
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
@discord.app_commands.checks.has_role(faction)
async def suggestions(interaction,*,suggestion: str):
    suggestions_dict = load_suggestions()
    suggestions_dict[str(interaction.user)] = suggestion
    save_suggestions(suggestions_dict)
    suggestion_channel_id = 1238211775627919431 
    suggestion_channel = bot.get_channel(suggestion_channel_id)

    if suggestion_channel:
        await suggestion_channel.send(f"{interaction.user} a suggéré : {suggestion}")
        await interaction.response.send_message("Suggestion envoyée avec succès !", ephemeral=True)
    else:
        await interaction.response.send_message("Le salon de suggestions n'a pas été trouvé.", ephemeral=True)

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
        description="Je suis le ElysiiumBot développé par Addd78130, le chef de la faction.\n\n"
                    "En arrivant sur le discord, je te conseille de prendre conscience du règlement "
                    "et d'accepter ce dernier afin d'obtenir les rôles pour accéder aux différents canaux.\n\n"
                    "Aussi, si tu es ici pour un recrutement, rends-toi dans le salon recrutement et crée un ticket "
                    "sans oublier de remplir le formulaire présent sous forme de lien dans le message du channel Recrutement.\n\n"
                    "Voilà voilà, en te souhaitant une agréable expérience au sein du serveur de La Elysiium !!",
        color=discord.Color.red()
    )
    await member.send(embed=embed)

@bot.event
async def on_command_error(interaction, error):
    if isinstance(error, commands.CommandNotFound):
        await interaction.response.send_message("Commande non trouvée.")

############################## SANCTIONS #########################################

@bot.tree.command()
@discord.app_commands.checks.has_role(staff)
async def warn(interaction, member: discord.Member, *, reason: str):
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
            await interaction.response.send_message(f"Sanction appliquée {yes_emoji}", ephemeral=True)
            await warm_log_channel.send(f"{member.mention} a été promu au rôle Warm 2 par {executor.mention} pour la raison : {reason}")
            embed = discord.Embed(title=f"{red_emoji} Avertissement ! {red_emoji}", description=f"Vous avez reçu un avertissement pour la raison suivante : {reason}, {member.mention}", color=discord.Color.red())
            await member.send(embed=embed)
            await member.send(f"{member.mention}")
        elif warm2_role in member.roles:
            await member.add_roles(warm1_role)
            await interaction.response.send_message(f"Sanction appliquée {yes_emoji}", ephemeral=True)
            await warm_log_channel.send(f"{member.mention} a reçu un autre avertissement (Warm 1) par {executor.mention} pour la raison : {reason}")
            embed = discord.Embed(title="{red_emoji} Avertissement ! {red_emoji}", description=f"Vous avez reçu un second avertissement pour la raison suivante : {reason}", color=discord.Color.red())
            await member.send(embed=embed)
            await member.send(f"{member.mention}")
        else:
            await member.add_roles(warm1_role)
            await interaction.response.send_message(f"Sanction appliquée {yes_emoji}", ephemeral=True)
            await warm_log_channel.send(f"{member.mention} a été averti (Warm 1) par {executor.mention} pour la raison : {reason}")
    else:
        await interaction.response.send_message("Les rôles Warm 1 et Warm 2 n'ont pas été trouvés ou le salon de log Warm n'a pas été trouvé.", ephemeral=True)

@bot.tree.command()
@discord.app_commands.checks.has_permissions(administrator=True)
async def ban(interaction: discord.Interaction, member:discord.Member,*,raison:str):
	'''Ban'''
	guild = interaction.guild
	embed_ = discord.Embed(title=f'{ban_emoji} Ban {ban_emoji}',
		description=f"Vous avez été banni du serveur Elysiium Fation pour la raison suivante : {raison}",
		color=discord.Color.red())
	try:
		await member.send(embed=embed_)
		message =f'Le message a bien été envoyé à {member.mention}'
	except:
		pass
		message =f"Le message n'a pas pu être envoyé à {member.mention} mais il a bien été banni"
	await guild.ban(member,reason=raison)
	log = bot.get_channel([str(interaction.guild.id)])
	await log.send(embed=create_small_embed(member.mention + ' à été ban par ' + interaction.user.mention + " pour " + raison))
	await interaction.response.send_message(embed=create_small_embed(message), ephemeral=True)

@bot.tree.command()
@discord.app_commands.checks.has_permissions(administrator=True)
async def unban(interaction: discord.Interaction, member:discord.User,*,raison:str):
	'''unban quelqu'un'''
	if member.id == interaction.user.id:
		await interaction.response.send_message(embed=create_small_embed("Tu ne peux pas faire cela",discord.Color.red(), ephemeral=True))
		return
	guild = interaction.guild
	await guild.unban(member,reason=raison)
	log = bot.get_channel([str(interaction.guild.id)])
	await log.send(embed=create_small_embed(member.mention + ' à été unban par ' + interaction.user.mention + " pour " + raison))
	await interaction.response.send_message(embed=create_small_embed(member.mention+"à bien été déban", ephemeral=True))


###################################### RESSOURCES ET GESTIONS #######################################

@bot.tree.command()
@discord.app_commands.checks.has_any_role(recup,staff)
async def a_ressource(interaction, ressource: str, quantite: int):
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
@discord.app_commands.checks.has_any_role(staff,recup)
async def ressources(interaction):
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
@discord.app_commands.checks.has_any_role(staff,recup)
async def r_ressource(interaction, ressource: str, quantite: int):
    try:
        with open(json_bc_filename, "r") as file:
            ressources = json.load(file)

        if ressource in ressources:
            ressources[ressource] -= quantite
            if ressources[ressource] <= 0:
                del ressources[ressource]
        else:
            await interaction.response.send_message(f"Ressource non trouvée : {ressource}", ephemeral=True)
            return

        with open(json_bc_filename, "w") as file:
            json.dump(ressources, file)

        await interaction.response.send_message(f"Ressource retirée : {quantite} {ressource}")

    except Exception as e:
        print(f"Une erreur s'est produite lors du retrait de ressources : {e}")
if SERVER:
    run_bot()
else:
    bot.run('TOKEN')

@tasks.loop(seconds=30)
async def update_status():
    try:
        if bot.guilds:
            server = bot.guilds[0]
            member_count = server.member_count
            await bot.change_presence(
                status=discord.Status.dnd,
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name=f"{member_count} membres"
                )
            )
        else:
            print("Le bot n'est dans aucun serveur.")
    except Exception as e:
        print(f"Une erreur est survenue: {e}")

@update_status.before_loop
async def before_update_status():
    await bot.wait_until_ready()

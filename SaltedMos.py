# imports
import discord, os
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv
import json

#Config
Provider = json.load(open("Provider.json"))
load_dotenv("life.env")
Token = os.getenv("DISCORD_TOKEN")
Mos = commands.Bot(command_prefix="!", intents=discord.Intents.default())

#functions
def red(text):
    return f"```ansi\n\u001b[0;31m{text}\u001b[0m\n```"
def Set_Modlist(interaction):
    global Modlist
    lists = Provider.setdefault("ModLists", {})
    guild_id = str(interaction.guild_id)
    if guild_id not in lists:
        lists[guild_id] = []
    Modlist = lists[guild_id]

#Embeds
ModListerEmbed = discord.Embed(
    title="Mods",
    color=discord.Color.dark_theme()
)
def BuildModListerEmbed(interaction: discord.Interaction):
    Set_Modlist(interaction)
    ModListerEmbed.clear_fields()
    text = ""
    for Mod in Modlist:
        text += f"`{Mod['Name']}` • [`Link`]({Mod['Link']})\n"
    if text == "":
        text = "Empty List"
    ModListerEmbed.description = text
    ModListerEmbed.set_footer(text=f"{len(Modlist)} mods")
async def modslist(interaction: discord.Interaction):
    BuildModListerEmbed(interaction)

HelperEmbed = discord.Embed(
    title="Commands",
    color=discord.Color.dark_theme()
)
HelperEmbed.add_field(
    name="\u200b",
    value="`/modlist` • Show client-side mods",
    inline=False
)
HelperEmbed.add_field(
    name="\u200b",
    value="`/help` • show commands",
    inline=False
)
HelperEmbed.add_field(
    name="\u200b",
    value="`/add` • add mod from list `(Admin Only)`",
    inline=False
)
HelperEmbed.add_field(
    name="",
    value="`/remove` • remove mod from list `(Admin Only)`",
    inline=False
)

#events
@Mos.event
async def on_ready():
    print(f"Logged into as {Mos.user}")
    for guild in Mos.guilds:
        guild = discord.Object(id=guild.id)
        Mos.tree.copy_global_to(guild=guild)
        await Mos.tree.sync(guild=guild)
@Mos.event
async def on_guild_join(guild):
    Mos.tree.copy_global_to(guild)
    await Mos.tree.sync(guild=guild)

#Commands
@Mos.tree.command(name="modlist", description="List client-side mods")
async def modslist(interaction: discord.Interaction):
    Set_Modlist(interaction)
    BuildModListerEmbed(interaction)
    await interaction.response.send_message(embed=ModListerEmbed)

@Mos.tree.command(name="help", description="show commands")
async def help(interaction: discord.Interaction):
    await interaction.response.send_message(embed=HelperEmbed)

@Mos.tree.command(name="add", description="add a mod to the list")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def add(interaction: discord.Interaction, modname: str, link: str):
    Set_Modlist(interaction)
    if link.startswith("https://"):
        Modlist.append({"Name": modname, "Link": link})
        with open("Provider.json", "w") as f:
            json.dump(Provider, f, indent=2)
        await interaction.response.send_message(f"Add mod: `{modname}`")
    else:
        await interaction.response.send_message(red(f"`{link}` is not real link as it doesn't start with https://"), ephemeral=True)

@Mos.tree.command(name="remove", description="Delete mod from mod list")
@app_commands.default_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def remove(interaction: discord.Interaction, modname: str):
    Set_Modlist(interaction)
    for i, mod in enumerate(Modlist):
        if mod["Name"].lower() == modname.lower():
            Modlist.pop(i)
            with open("Provider.json", "w") as f:
                json.dump(Provider, f, indent=2)
            await interaction.response.send_message(f"Removed `{modname}`")
            break
    else:
        await interaction.response.send_message(red(f"`{modname}` doesn't exist on list"))

@add.error
async def add_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(red("only admins can add mods."), ephemeral=True)
@remove.error
async def remove_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(red("only admins can remove mods."), ephemeral=True)

Mos.run(Token)

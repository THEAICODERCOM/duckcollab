import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from typing import Dict, Any, List

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# --- Help System Components ---

class HelpDropdown(discord.ui.Select):
    def __init__(self, bot: commands.Bot, categories: Dict[str, Any]):
        options = [
            discord.SelectOption(
                label="Home",
                description="Back to the main menu",
                emoji="🏠"
            )
        ]
        
        for name, data in categories.items():
            options.append(discord.SelectOption(
                label=name,
                description=f"View {name} commands",
                emoji=data.get("emoji", "🔹")
            ))

        super().__init__(
            placeholder="Select a category to explore...",
            min_values=1,
            max_values=1,
            options=options,
        )
        self.bot = bot
        self.categories = categories

    async def callback(self, interaction: discord.Interaction):
        if self.values[0] == "Home":
            await interaction.response.edit_message(embed=create_main_help_embed(self.bot, self.categories), view=self.view)
            return

        category_name = self.values[0]
        category_data = self.categories[category_name]
        
        embed = discord.Embed(
            title=f"{category_data.get('emoji', '🔹')} {category_name} Commands",
            description=f"Detailed list of commands in the **{category_name}** category.",
            color=discord.Color.blue()
        )

        sorted_cmds = sorted(category_data["commands"], key=lambda x: x.qualified_name)

        for cmd in sorted_cmds:
            if isinstance(cmd, commands.Group):
                sub_cmds = list(cmd.walk_commands())
                sub_text = "\n".join([f"  └─ `{s.qualified_name}`: {s.short_doc or 'No description'}" for s in sub_cmds])
                embed.add_field(
                    name=f"📁 `{cmd.qualified_name}`",
                    value=f"{cmd.short_doc or 'Group command'}\n{sub_text}" if sub_text else (cmd.short_doc or "Group command"),
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"• `{cmd.qualified_name}`",
                    value=cmd.short_doc or "No description provided.",
                    inline=False
                )

        embed.set_footer(text=f"Total: {len(sorted_cmds)} commands | Use dh!help <command> for details.")
        await interaction.response.edit_message(embed=embed, view=self.view)

class HelpView(discord.ui.View):
    def __init__(self, bot: commands.Bot, categories: Dict[str, Any]):
        super().__init__(timeout=180)
        self.add_item(HelpDropdown(bot, categories))

def create_main_help_embed(bot: commands.Bot, categories: Dict[str, Any]):
    embed = discord.Embed(
        title="📚 Empire Nexus - Help Menu",
        description=(
            "Welcome to the **Empire Nexus**! Explore our features using the menu below.\n\n"
            "**Quick Links:**\n"
            "🔗 [Support Server](https://discord.gg/example)\n"
            "🌐 [Wiki](https://wiki.example.com)\n"
            "🗳️ [Vote for us](https://top.gg/bot/example)"
        ),
        color=discord.Color.blue()
    )
    
    for name, data in categories.items():
        cmd_list = ", ".join([f"`{c.name}`" for c in data["commands"][:5]])
        if len(data["commands"]) > 5:
            cmd_list += "..."
        
        embed.add_field(
            name=f"{data.get('emoji', '🔹')} {name}",
            value=f"{len(data['commands'])} commands\n{cmd_list}",
            inline=True
        )

    embed.set_footer(text="Use the dropdown menu to see all commands in a category.")
    embed.set_thumbnail(url="https://cdn.discordapp.com/embed/avatars/0.png")
    return embed

def get_categories(bot: commands.Bot):
    cat_config = {
        "🦆 Gameplay": {"emoji": "🦆", "keywords": ["bang", "reload", "hug", "revive", "random_duck", "watchpaintdry"]},
        "📊 Statistics": {"emoji": "📊", "keywords": ["me", "shooting_stats", "best_times", "kills_stats", "hugs_stats", "hurt_stats", "resist_stats", "frighten_stats", "achievements", "top", "send_exp", "commands_used", "bot_users"]},
        "🏷️ Tags": {"emoji": "🏷️", "keywords": ["tag", "tags"]},
        "⚙️ Settings": {"emoji": "⚙️", "keywords": ["settings"]},
        "💰 Economy": {"emoji": "💰", "keywords": ["inventory", "use", "shop", "prestige"]},
        "💣 Landmines": {"emoji": "💣", "keywords": ["landmine", "place", "defuse"]},
        "🛠️ Utility": {"emoji": "🛠️", "keywords": ["ping", "wiki", "invite", "support", "freetime", "credits", "translators", "event", "time", "shards", "vote"]},
        "👑 Administration": {"emoji": "👑", "keywords": ["coin", "ducks_list", "remove_user", "give_exp", "remove_all_scores_stats", "manage_bot", "beta_invite", "private_support"]}
    }

    categories = {}
    processed_commands = set()

    for cat_name, config in cat_config.items():
        cat_cmds = []
        for cmd_name in config["keywords"]:
            cmd = bot.get_command(cmd_name)
            if cmd:
                cat_cmds.append(cmd)
                processed_commands.add(cmd.name)
        
        if cat_cmds:
            categories[cat_name] = {
                "emoji": config["emoji"],
                "commands": cat_cmds
            }

    standalone = [c for c in bot.commands if c.name not in processed_commands and c.name != "help"]
    if standalone:
        if "General" not in categories:
            categories["General"] = {"emoji": "📁", "commands": []}
        categories["General"]["commands"].extend(standalone)
    
    return categories


# --- Bot Setup ---

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(
            command_prefix=["dh!", "!"], 
            intents=intents,
            help_command=None
        )

bot = MyBot()


# --- 🏷️ Tags Category ---

@bot.command(name="tag")
async def tag(ctx):
    """Show a given tag based on the name."""
    await ctx.send("Tag content...")

@bot.group(name="tags", invoke_without_command=True)
async def tags(ctx):
    """Commands to interact with tags: creations, editions, deletions, ..."""
    await ctx.send_help(ctx.command)

@tags.command(name="create")
async def tags_create(ctx):
    """Create a new tag."""
    await ctx.send("Tag created!")

@tags.command(name="edit")
async def tags_edit(ctx):
    """Edit an existing tag."""
    await ctx.send("Tag edited!")

@tags.command(name="list")
async def tags_list(ctx):
    """List all the existing tags."""
    await ctx.send("Tags list...")

@tags.command(name="alias")
async def tags_alias(ctx):
    """Alias an existing tag to a new name."""
    await ctx.send("Tag aliased!")

@tags.command(name="delete")
async def tags_delete(ctx):
    """Delete an existing tag."""
    await ctx.send("Tag deleted!")

@tags.command(name="raw")
async def tags_raw(ctx):
    """View the raw version of the tag."""
    await ctx.send("Raw tag content...")


# --- ⚙️ Settings Category ---

@bot.group(name="settings", invoke_without_command=True)
async def settings(ctx):
    """Commands to view and edit settings."""
    await ctx.send_help(ctx.command)

@settings.command(name="prefix")
async def settings_prefix(ctx):
    """Change/view the server prefix."""
    await ctx.send("Prefix setting...")

@settings.command(name="language")
async def settings_language(ctx):
    """Change/view the server language."""
    await ctx.send("Language setting...")

@settings.command(name="enabled")
async def settings_enabled(ctx):
    """Allow ducks to spawn."""
    await ctx.send("Enabled setting...")

@settings.command(name="super_ducks_min_life")
async def settings_super_ducks_min_life(ctx):
    """Set the minimum lives of a super duck."""
    await ctx.send("Setting updated.")

@settings.command(name="clover_max_experience")
async def settings_clover_max_experience(ctx):
    """Set the maximum experience a clover will give."""
    await ctx.send("Setting updated.")

@settings.command(name="landmines_enabled")
async def settings_landmines_enabled(ctx):
    """Allow the landmines game to take place here."""
    await ctx.send("Setting updated.")

@settings.command(name="tax_on_user_send")
async def settings_tax_on_user_send(ctx):
    """Change the tax taken from users when they send exp."""
    await ctx.send("Setting updated.")

@settings.command(name="auto_roles")
async def settings_auto_roles(ctx):
    """Commands to edit auto roles."""
    await ctx.send("Setting updated.")

@settings.command(name="base_duck_exp")
async def settings_base_duck_exp(ctx):
    """Set the normal amount of experience a duck will give."""
    await ctx.send("Setting updated.")

@settings.command(name="landmines_commands_enabled")
async def settings_landmines_commands_enabled(ctx):
    """Allow landmines commands to be ran in this channel."""
    await ctx.send("Setting updated.")

@settings.command(name="mentions_when_killed")
async def settings_mentions_when_killed(ctx):
    """Control if users might be pinged when they get killed."""
    await ctx.send("Setting updated.")

@settings.command(name="auto_prestige_roles")
async def settings_auto_prestige_roles(ctx):
    """Commands to edit auto prestige roles."""
    await ctx.send("Setting updated.")

@settings.command(name="use_webhooks")
async def settings_use_webhooks(ctx):
    """Specify whether the bot should use webhooks."""
    await ctx.send("Setting updated.")

@settings.command(name="super_ducks_max_life")
async def settings_super_ducks_max_life(ctx):
    """Set the maximum lives of a super duck."""
    await ctx.send("Setting updated.")

@settings.command(name="per_life_exp")
async def settings_per_life_exp(ctx):
    """Set additional exp given for every life of a super duck."""
    await ctx.send("Setting updated.")

@settings.command(name="ping")
async def settings_ping_pref(ctx):
    """Set your preference on whether replies should ping you."""
    await ctx.send("Setting updated.")

@settings.command(name="show_duck_lives")
async def settings_show_duck_lives(ctx):
    """Show how many lives super ducks have left."""
    await ctx.send("Setting updated.")

@settings.command(name="templates")
async def settings_templates(ctx):
    """Set server settings to specific modes."""
    await ctx.send("Setting updated.")

@settings.command(name="permissions")
async def settings_permissions(ctx):
    """Commands to edit permissions."""
    await ctx.send("Setting updated.")

@settings.command(name="allow_global_items")
async def settings_allow_global_items(ctx):
    """Control if hunters can use special items earned elsewhere."""
    await ctx.send("Setting updated.")

@settings.command(name="anti_trigger_wording")
async def settings_anti_trigger_wording(ctx):
    """Avoid references to triggering actions/words."""
    await ctx.send("Setting updated.")

@settings.command(name="ducks_per_day")
async def settings_ducks_per_day(ctx):
    """Set the amount of ducks that will spawn every day."""
    await ctx.send("Setting updated.")

@settings.command(name="my_language")
async def settings_my_language(ctx):
    """Change/view your own language."""
    await ctx.send("Setting updated.")

@settings.command(name="kill_on_miss_chance")
async def settings_kill_on_miss_chance(ctx):
    """Set how likely it is to kill someone when missing."""
    await ctx.send("Setting updated.")

@settings.command(name="add_webhook")
async def settings_add_webhook(ctx):
    """Add a new webhook to the channel."""
    await ctx.send("Setting updated.")

@settings.command(name="night_time")
async def settings_night_time(ctx):
    """Set the night time."""
    await ctx.send("Setting updated.")

@settings.command(name="weights")
async def settings_weights(ctx):
    """Set a duck probability to spawn to a certain weight."""
    await ctx.send("Setting updated.")

@settings.command(name="duck_frighten_chance")
async def settings_duck_frighten_chance(ctx):
    """Set how likely it is to frighten a duck."""
    await ctx.send("Setting updated.")

@settings.command(name="use_emojis")
async def settings_use_emojis(ctx):
    """Allow ducks to use emojis when they spawn."""
    await ctx.send("Setting updated.")

@settings.command(name="api_key")
async def settings_api_key(ctx):
    """Enable/disable the DuckHunt API for this channel."""
    await ctx.send("Setting updated.")

@settings.command(name="ducks_time_to_live")
async def settings_ducks_time_to_live(ctx):
    """Set for how many seconds a duck will stay."""
    await ctx.send("Setting updated.")

@settings.command(name="clover_min_experience")
async def settings_clover_min_experience(ctx):
    """Set the minimum experience a clover will give."""
    await ctx.send("Setting updated.")

@settings.command(name="channel_disabled_message")
async def settings_channel_disabled_message(ctx):
    """Enable or disable the channel disabled message."""
    await ctx.send("Setting updated.")



# --- 🦆 Gameplay Category ---

@bot.command(name="bang")
async def bang(ctx):
    """Shoot at the duck that appeared first."""
    await ctx.send("BANG!")

@bot.command(name="reload")
async def reload(ctx):
    """Reload your gun."""
    await ctx.send("Reloaded!")

@bot.command(name="hug")
async def hug(ctx):
    """Hug the duck that appeared first."""
    await ctx.send("HUG!")

@bot.command(name="revive")
async def revive(ctx):
    """Revive yourself by eating brains."""
    await ctx.send("Revived!")

@bot.command(name="random_duck")
async def random_duck(ctx):
    """Shows a random duck image."""
    await ctx.send("🦆")

@bot.command(name="watchpaintdry")
async def watchpaintdry(ctx):
    """Watch paint dry."""
    await ctx.send("🎨 Drying...")


# --- 📊 Statistics Category ---

@bot.command(name="me")
async def me(ctx):
    """Get some quickstats about yourself."""
    await ctx.send("Your stats...")

@bot.command(name="shooting_stats")
async def shooting_stats(ctx):
    """Get shooting stats."""
    await ctx.send("Shooting stats...")

@bot.command(name="best_times")
async def best_times(ctx):
    """Get best times to kill of ducks."""
    await ctx.send("Best times...")

@bot.command(name="kills_stats")
async def kills_stats(ctx):
    """Get number of each type of duck killed."""
    await ctx.send("Kills stats...")

@bot.command(name="hugs_stats")
async def hugs_stats(ctx):
    """Get number of each type of duck hugged."""
    await ctx.send("Hugs stats...")

@bot.command(name="hurt_stats")
async def hurt_stats(ctx):
    """Get number of each type of duck hurt."""
    await ctx.send("Hurt stats...")

@bot.command(name="resist_stats")
async def resist_stats(ctx):
    """Get number of each type of duck that resisted a shot."""
    await ctx.send("Resist stats...")

@bot.command(name="frighten_stats")
async def frighten_stats(ctx):
    """Get number of each type of duck that fled."""
    await ctx.send("Frighten stats...")

@bot.command(name="commands_used")
async def commands_used(ctx):
    """Shows a paginator with the most used commands."""
    await ctx.send("Commands used...")

@bot.command(name="bot_users")
async def bot_users(ctx):
    """Shows a paginator with the users that have used the bot the most."""
    await ctx.send("Bot users...")

@bot.command(name="top")
async def top(ctx):
    """Who's the best?"""
    await ctx.send("Leaderboard...")

@bot.command(name="achievements")
async def achievements(ctx):
    """Show your achievements."""
    await ctx.send("Achievements...")

@bot.command(name="send_exp")
async def send_exp(ctx):
    """Send some of your experience to another player."""
    await ctx.send("EXP sent!")


# --- 💰 Economy Category ---

@bot.group(name="inventory", aliases=["inv"], invoke_without_command=True)
async def inventory(ctx):
    """Show your inventory content."""
    await ctx.send("Inventory content...")

@inventory.command(name="give")
async def inventory_give(ctx):
    """Give something to some player."""
    await ctx.send("Item given!")

@inventory.command(name="use")
async def inventory_use(ctx):
    """Use one of the items in your inventory."""
    await ctx.send("Item used!")

@bot.command(name="use")
async def use_alias(ctx):
    """Alias for dh!inv use."""
    await ctx.invoke(bot.get_command('inventory use'))

@bot.group(name="shop", invoke_without_command=True)
async def shop(ctx):
    """Buy items here."""
    await ctx.send("Shop items: explosive, sabotage, sunglasses, weapon, decoy, clothes, ...")

@bot.group(name="prestige", invoke_without_command=True)
async def prestige(ctx):
    """Prestige related commands."""
    await ctx.send_help(ctx.command)

@prestige.command(name="confirm")
async def prestige_confirm(ctx):
    """Execute the prestige process."""
    await ctx.send("Prestiged!")

@prestige.command(name="info")
async def prestige_info(ctx):
    """More info about prestige."""
    await ctx.send("Prestige info...")


# --- 💣 Landmines Category ---

@bot.group(name="landmine", invoke_without_command=True)
async def landmine(ctx):
    """Commands related to 'Landmines' game."""
    await ctx.send_help(ctx.command)

@landmine.command(name="defuse_kit")
async def landmine_defuse_kit(ctx):
    """Buy a defuse kit."""
    await ctx.send("Defuse kit bought!")

@landmine.command(name="guide")
async def landmine_guide(ctx):
    """This command explains how to place a landmine."""
    await ctx.send("Landmine guide...")

@landmine.command(name="protect")
async def landmine_protect(ctx):
    """Buy a shield that will be placed on a given word."""
    await ctx.send("Shield bought.")

@landmine.command(name="me")
async def landmine_me(ctx):
    """View your event statistics."""
    await ctx.send("Your event stats.")

@landmine.command(name="top")
async def landmine_top(ctx):
    """Show statistics about landmines on this server."""
    await ctx.send("Landmine leaderboard.")

@landmine.command(name="landmine")
async def landmine_cmd(ctx):
    """[THIS COMMAND WORKS IN DMs]"""
    await ctx.send("Landmine action.")

@bot.command(name="freetime")
async def freetime(ctx):
    """Get the time when you'll get free magazines."""
    await ctx.send("Freetime info.")

@bot.command(name="credits")
async def credits_cmd(ctx):
    """Thanks to those fine people who helped make the bot."""
    await ctx.send("Credits...")

@bot.command(name="translators")
async def translators(ctx):
    """Thanks to those fine people who helped translate the bot."""
    await ctx.send("Translators...")

@bot.command(name="event")
async def event(ctx):
    """See the current global event."""
    await ctx.send("Current event.")

@bot.command(name="time")
async def time_cmd(ctx):
    """This returns the current bot time."""
    await ctx.send("Bot time.")

@bot.command(name="shards")
async def shards(ctx):
    """Check the status of every shard the bot is hosting."""
    await ctx.send("Shards status.")

@bot.command(name="vote")
async def vote(ctx):
    """Sends the link you can use to vote for DuckHunt."""
    await ctx.send("Vote link.")

@bot.command(name="place")
async def place_alias(ctx):
    """Alias for landmine placement."""
    await ctx.send("Landmine placed!")

@bot.command(name="defuse")
async def defuse_alias(ctx):
    """Alias for landmine defusal."""
    await ctx.send("Landmine defused!")


# --- 👑 Administration Category ---

@bot.group(name="coin", invoke_without_command=True)
async def coin(ctx):
    """Spawns a random duck (Admin only)."""
    await ctx.send("Random duck spawned!")

@coin.command(name="normal")
async def coin_normal(ctx):
    """Spawns a normal duck."""
    await ctx.send("Normal duck spawned!")

@coin.command(name="super")
async def coin_super(ctx):
    """Spawns a super duck."""
    await ctx.send("Super duck spawned!")

@coin.command(name="kamikaze")
async def coin_kamikaze(ctx):
    """Spawns a kamikaze duck."""
    await ctx.send("Kamikaze duck spawned!")

@coin.command(name="baby")
async def coin_baby(ctx):
    """Spawns a baby duck."""
    await ctx.send("Baby duck spawned!")

@coin.command(name="ghost")
async def coin_ghost(ctx):
    """Spawns a ghost duck. No spawn message."""
    await ctx.send("Ghost duck spawned!")

@coin.command(name="sleeping")
async def coin_sleeping(ctx):
    """Spawns a sleeping duck."""
    await ctx.send("Sleeping duck spawned!")

@coin.command(name="armored")
async def coin_armored(ctx):
    """Spawns an armored duck."""
    await ctx.send("Armored duck spawned!")

@coin.command(name="roulette")
async def coin_roulette(ctx):
    """Spawns many ducks, one mechanical."""
    await ctx.send("Roulette started!")

@coin.command(name="plastic")
async def coin_plastic(ctx):
    """Spawns a plastic duck."""
    await ctx.send("Plastic duck spawned!")

@coin.command(name="night")
async def coin_night(ctx):
    """Spawns a night duck."""
    await ctx.send("Night duck spawned!")

@coin.command(name="cartographer")
async def coin_cartographer(ctx):
    """Spawns a cartographer duck."""
    await ctx.send("Cartographer duck spawned!")

@coin.command(name="prof")
async def coin_prof(ctx):
    """Spawns a professor Duck."""
    await ctx.send("Professor duck spawned!")

@coin.command(name="moad")
async def coin_moad(ctx):
    """Spawns a MOAD."""
    await ctx.send("MOAD spawned!")

@coin.command(name="golden")
async def coin_golden(ctx):
    """Spawns a golden duck."""
    await ctx.send("Golden duck spawned!")

@bot.group(name="ducks_list", invoke_without_command=True)
async def ducks_list(ctx):
    """Show ducks currently on the channel (Admin only)."""
    await ctx.send("Ducks list...")

@ducks_list.command(name="clear")
async def ducks_list_clear(ctx):
    """Removes all ducks from the channel."""
    await ctx.send("Ducks cleared!")

@bot.command(name="remove_user")
async def remove_user(ctx):
    """Delete scores for a specific user (Moderator only)."""
    await ctx.send("User scores removed.")

@bot.command(name="give_exp")
async def give_exp(ctx):
    """Give experience to another player (Admin only)."""
    await ctx.send("EXP given.")

@bot.command(name="remove_all_scores_stats")
async def remove_all_scores_stats(ctx):
    """Delete scores for all users (Admin only)."""
    await ctx.send("All scores removed.")

@bot.command(name="beta_invite")
async def beta_invite(ctx):
    """Invite someone to the beta server (Bot Moderator only)."""
    await ctx.send("Beta invite sent.")

@bot.group(name="manage_bot", invoke_without_command=True)
async def manage_bot(ctx):
    """Manage the bot current state (Bot Moderator only)."""
    await ctx.send_help(ctx.command)

@manage_bot.command(name="update_event")
async def manage_update_event(ctx):
    """Force current event to change."""
    await ctx.send("Event updated.")

@manage_bot.command(name="stop_spawns")
async def manage_stop_spawns(ctx):
    """Stop ducks from spawning immediately."""
    await ctx.send("Spawns stopped.")

@manage_bot.command(name="locks")
async def manage_locks(ctx):
    """Manage command locks."""
    await ctx.send("Locks updated.")

@manage_bot.command(name="update_owners")
async def manage_update_owners(ctx):
    """Update @Have DuckHunt role members."""
    await ctx.send("Owners updated.")

@manage_bot.command(name="force_boss_spawn")
async def manage_force_boss_spawn(ctx):
    """Force a boss to spawn."""
    await ctx.send("Boss spawned.")

@manage_bot.command(name="planify")
async def manage_planify(ctx):
    """Reset ducks planning."""
    await ctx.send("Planning reset.")

@manage_bot.command(name="asshole")
async def manage_asshole(ctx):
    """Manage the asshole list."""
    await ctx.send("Asshole list updated.")

@manage_bot.command(name="give_trophy")
async def manage_give_trophy(ctx):
    """Congratulate an user giving them a trophy."""
    await ctx.send("Trophy given.")

@manage_bot.command(name="start_spawns")
async def manage_start_spawns(ctx):
    """Allow ducks spawning again."""
    await ctx.send("Spawns started.")

@manage_bot.command(name="socketstats")
async def manage_socketstats(ctx):
    """Check socket statistics."""
    await ctx.send("Socket stats...")

@bot.group(name="private_support", invoke_without_command=True)
async def private_support(ctx):
    """Manage private support threads."""
    await ctx.send_help(ctx.command)

@private_support.command(name="suggest_language")
async def support_suggest_language(ctx):
    """Suggest a new language to the user."""
    await ctx.send("Language suggested.")

@private_support.command(name="close_silent")
async def support_close_silent(ctx):
    """Close DM thread without sending a message."""
    await ctx.send("Thread closed silently.")

@private_support.command(name="close")
async def support_close(ctx):
    """Close DM thread and send a message."""
    await ctx.send("Thread closed.")

@private_support.command(name="tag")
async def support_tag(ctx):
    """Send a tag to the user."""
    await ctx.send("Tag sent.")

@private_support.command(name="block")
async def support_block(ctx):
    """Block user from opening DMs."""
    await ctx.send("User blocked.")


@bot.command(name="ping")
async def ping(ctx):
    """Check that the bot is online."""
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")

@bot.command(name="invite")
async def invite(ctx):
    """Get the URL to invite the bot."""
    await ctx.send("Invite link...")

@bot.command(name="support")
async def support(ctx):
    """Get a discord invite to the support server."""
    await ctx.send("Support server link...")

@bot.command(name="wiki")
async def wiki(ctx):
    """Returns the wiki URL."""
    await ctx.send("Wiki link...")


@bot.command(name="help")
async def help_command(ctx, *, query: str = None):
    """Shows this help menu or info about a command."""
    categories = get_categories(bot)
    
    if query:
        for name, data in categories.items():
            if query.lower() in name.lower():
                pass
        
        cmd = bot.get_command(query)
        if cmd:
            embed = discord.Embed(
                title=f"Command: {cmd.qualified_name}",
                description=cmd.help or "No description provided.",
                color=discord.Color.blue()
            )
            if isinstance(cmd, commands.Group):
                subcmds = "\n".join([f"`{s.name}`: {s.short_doc}" for s in cmd.commands])
                embed.add_field(name="Subcommands", value=subcmds or "None", inline=False)
            
            if cmd.aliases:
                embed.add_field(name="Aliases", value=", ".join(cmd.aliases), inline=False)
            
            await ctx.send(embed=embed)
            return

    view = HelpView(bot, categories)
    embed = create_main_help_embed(bot, categories)
    await ctx.send(embed=embed, view=view)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('Bot is ready!')

if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("Error: DISCORD_TOKEN not found in .env file.")


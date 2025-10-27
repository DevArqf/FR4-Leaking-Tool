import discord
from discord.ext import commands, tasks
import asyncio
import json
import requests
import aiohttp
import io
import difflib
from datetime import datetime, timezone
import logging
from logging.handlers import RotatingFileHandler
import os
from typing import Dict, List, Tuple, Optional, Any

# Configure logging
logger = logging.getLogger('funrun_monitor')
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler('bot.log', maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

def compare_versions(version1, version2):
    """Compare two version strings. Returns 1 if v1 > v2, -1 if v1 < v2, 0 if equal"""
    v1_parts = [int(x) for x in version1.split('.')]
    v2_parts = [int(x) for x in version2.split('.')]
    
    # Pad shorter version with zeros
    max_len = max(len(v1_parts), len(v2_parts))
    v1_parts.extend([0] * (max_len - len(v1_parts)))
    v2_parts.extend([0] * (max_len - len(v2_parts)))
    
    for v1, v2 in zip(v1_parts, v2_parts):
        if v1 > v2:
            return 1
        elif v1 < v2:
            return -1
    return 0

# Load config
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    logger.error("config.json not found. Please create it from config.example.json")
    logger.info("Copy config.example.json to config.json and fill in your Discord bot token and channel ID")
    exit(1)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

class UptodownMonitor:
    def __init__(self):
        self.version_file = "version_data.json"
        self.current_version = None
        self.last_check = None
        self.load_version_data()
    
    def load_version_data(self):
        """Load the last known version from disk"""
        try:
            if os.path.exists(self.version_file):
                with open(self.version_file, 'r') as f:
                    data = json.load(f)
                    self.current_version = data.get('version')
                    self.last_check = data.get('last_check')
                    logger.info(f"Loaded version data: {self.current_version} (last check: {self.last_check})")
            else:
                logger.info("No version data file found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading version data: {str(e)}")
    
    def save_version_data(self):
        """Save the current version data to disk"""
        try:
            data = {
                'version': self.current_version,
                'last_check': datetime.now(timezone.utc).isoformat()
            }
            with open(self.version_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved version data: {self.current_version}")
        except Exception as e:
            logger.error(f"Error saving version data: {str(e)}")
    
    async def check_uptodown_update(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check Uptodown for Fun Run 4 updates.
        Returns: (has_update, new_version, update_info)
        """
        try:
            # Try multiple URLs to get the latest version
            urls_to_try = [
                "https://fun-run-4.en.uptodown.com/android/download",  # Download page often has latest version
                "https://fun-run-4.en.uptodown.com/android",           # Main page
            ]
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            
            latest_version = None
            latest_version_source = None
            
            async with aiohttp.ClientSession() as session:
                for url in urls_to_try:
                    logger.info(f"Checking URL: {url}")
                    async with session.get(url, headers=headers) as response:
                        if response.status != 200:
                            logger.warning(f"Failed to fetch from {url}. Status: {response.status}")
                            continue
                        
                        content = await response.text()
                    
                        # Extract version information from Uptodown page
                        import re
                        
                        # Try multiple patterns for version extraction
                        version_patterns = [
                            r'Fun Run 4\s+([\d\.]+)',  # Common format on download pages
                            r'Version\s*([\d\.]+)',   # Direct version format
                            r'([\d]+\.[\d]+\.[\d]+)',  # Generic version pattern
                            r'Version\s*</span>\s*<span[^>]*>([^<]+)</span>',
                            r'<span[^>]*class="[^"]*version[^"]*"[^>]*>([^<]+)</span>',
                            r'"version":\s*"([^"]+)"',
                            r'Version\s+([\d\.]+)',
                            r'v([\d\.]+)',
                            r'Version:\s*([\d\.]+)',
                            r'<div[^>]*version[^>]*>([^<]+)</div>'
                        ]
                    
                        found_version = None
                        for pattern in version_patterns:
                            version_match = re.search(pattern, content, re.IGNORECASE)
                            if version_match:
                                raw_version = version_match.group(1).strip()
                                # Clean up version string
                                cleaned_version = re.sub(r'[^\d\.]', '', raw_version)
                                if cleaned_version and len(cleaned_version) > 0:
                                    found_version = cleaned_version
                                    break
                        
                        # Compare with current latest version
                        if found_version:
                            if latest_version is None or compare_versions(found_version, latest_version) > 0:
                                latest_version = found_version
                                latest_version_source = url
                                logger.info(f"Found higher version: {latest_version} from {url}")
                    
                # After trying all URLs, check if we found any version
                if latest_version:
                    logger.info(f"Found version on Uptodown: {latest_version} from {latest_version_source}")
                    
                    # Check if this is a new version
                    if self.current_version is None:
                        # When version is None (reset), treat it as a new update
                        self.current_version = latest_version
                        self.save_version_data()  # Persist the version
                        logger.info(f"Version detected after reset: {latest_version}")
                        return True, latest_version, f"New version detected: {latest_version}"
                    
                    if latest_version != self.current_version:
                        old_version = self.current_version
                        self.current_version = latest_version
                        self.save_version_data()  # Persist the new version
                        logger.info(f"New version detected: {old_version} -> {latest_version}")
                        return True, latest_version, f"Version updated from {old_version} to {latest_version}"
                    
                    return False, latest_version, "No update available"
                else:
                    logger.warning("Could not extract version information from any Uptodown page")
                    return False, None, "Could not extract version information"
                        
        except Exception as e:
            logger.error(f"Error checking Uptodown: {str(e)}")
            return False, None, f"Error: {str(e)}"

class ConfigComparator:
    def __init__(self):
        pass
    
    def compare_configs(self, old_config: Dict, new_config: Dict) -> Dict[str, Any]:
        """
        Compare two storeConfig.json files and return detailed changes.
        """
        changes = {
            "added": {},
            "removed": {},
            "modified": {},
            "summary": []
        }
        
        # Compare each section
        sections_to_compare = ["animals", "skins", "hats", "glasses", "chests", "feet", "powerups"]
        
        for section in sections_to_compare:
            old_section = old_config.get(section, {})
            new_section = new_config.get(section, {})
            
            # Find added items
            added_items = {}
            for item_id, item_data in new_section.items():
                if item_id not in old_section:
                    added_items[item_id] = item_data
            
            # Find removed items
            removed_items = {}
            for item_id, item_data in old_section.items():
                if item_id not in new_section:
                    removed_items[item_id] = item_data
            
            # Find modified items
            modified_items = {}
            for item_id in old_section:
                if item_id in new_section:
                    if old_section[item_id] != new_section[item_id]:
                        modified_items[item_id] = {
                            "old": old_section[item_id],
                            "new": new_section[item_id]
                        }
            
            if added_items:
                changes["added"][section] = added_items
                changes["summary"].append(f"Added {len(added_items)} {section}")
            
            if removed_items:
                changes["removed"][section] = removed_items
                changes["summary"].append(f"Removed {len(removed_items)} {section}")
            
            if modified_items:
                changes["modified"][section] = modified_items
                changes["summary"].append(f"Modified {len(modified_items)} {section}")
        
        return changes
    
    def create_modified_config(self, new_config: Dict, changes: Dict) -> Dict:
        """
        Create a modified version of the new config with preOwned: true added to new items.
        Also changes any "hidden": true to "hidden": false in the entire config.
        """
        modified_config = json.loads(json.dumps(new_config))  # Deep copy
        
        # Add preOwned: true to all added items
        for section, items in changes["added"].items():
            if section in modified_config:
                for item_id in items:
                    if item_id in modified_config[section]:
                        modified_config[section][item_id]["preOwned"] = True
        
        # Change all "hidden": true to "hidden": false throughout the entire config
        sections_to_compare = ["animals", "skins", "hats", "glasses", "chests", "feet", "powerups"]
        for section in sections_to_compare:
            if section in modified_config:
                for item_id, item_data in modified_config[section].items():
                    if isinstance(item_data, dict) and item_data.get("hidden") is True:
                        modified_config[section][item_id]["hidden"] = False
        
        return modified_config

# Initialize components
uptodown_monitor = UptodownMonitor()
config_comparator = ConfigComparator()

@bot.event
async def on_ready():
    logger.info(f'{bot.user} is online and monitoring Fun Run 4!')
    channel = bot.get_channel(int(config['channel_id']))
    if channel:
        embed = discord.Embed(
            title="🎮 Fun Run 4 Monitor Bot Started!",
            description="Bot is now monitoring for updates and ready to compare config files.",
            color=0x00ff00,
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(name="Available Commands", value="`!compare` - Compare two storeConfig.json files\n`!modify <ids>` - Add **\"preOwned: true\"** to specific item IDs\n`!check_update` - Force check for Uptodown updates\n`!test_notification` - Test Discord messaging\n`!reset_version` - Reset version data (for testing)", inline=False)
        await channel.send(embed=embed) # type: ignore
        
        # Start the update checker
        update_checker.start()
    else:
        logger.error(f"Channel ID {config['channel_id']} not found")

@tasks.loop(minutes=int(config.get('check_interval_minutes', 15)))
async def update_checker():
    """Periodic task to check for Play Store updates"""
    logger.info("Running scheduled update check...")
    
    has_update, version, info = await uptodown_monitor.check_uptodown_update()
    
    channel = bot.get_channel(int(config['channel_id']))
    if not channel:
        logger.error(f"Channel ID {config['channel_id']} not found or bot doesn't have access")
        return
    
    logger.info(f"Update check result: has_update={has_update}, version={version}, info={info}")
    
    if has_update:
        embed = discord.Embed(
            title="🚨 Fun Run 4 Update Detected!",
            description=f"A new version of Fun Run 4 has been found on Uptodown!",
            color=0xff6b00,
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(name="Version", value=version or "Unknown", inline=True)
        embed.add_field(name="Details", value=info or "No details available", inline=False)
        embed.set_footer(text="Use !compare command with old and new storeConfig.json files to see changes")
        
        try:
            await channel.send("@here", embed=embed) # type: ignore
            logger.info(f"Update notification sent successfully for version {version}")
        except Exception as e:
            logger.error(f"Failed to send Discord notification: {str(e)}")

@bot.command(name='compare')
async def compare_configs(ctx):
    """
    Compare two storeConfig.json files to detect changes.
    Usage: !compare (with two file attachments)
    """
    if len(ctx.message.attachments) != 2:
        embed = discord.Embed(
            title="❌ Invalid Usage",
            description="Please attach exactly 2 storeConfig.json files to compare.\n\n**Usage:** `!compare` with 2 file attachments",
            color=0xff0000
        )
        embed.add_field(name="Expected Files", value="1️⃣ Old version storeConfig.json\n2️⃣ New version storeConfig.json", inline=False)
        await ctx.reply(embed=embed)
        return
    
    try:
        # Download and parse the attached files
        old_attachment = ctx.message.attachments[0]
        new_attachment = ctx.message.attachments[1]
        
        if not (old_attachment.filename.endswith('.json') and new_attachment.filename.endswith('.json')):
            await ctx.reply("❌ Both files must be JSON files!")
            return
        
        # Show processing message
        processing_msg = await ctx.reply("🔄 Processing and comparing configuration files...")
        
        # Download files
        old_content = await old_attachment.read()
        new_content = await new_attachment.read()
        
        # Parse JSON
        try:
            old_config = json.loads(old_content.decode('utf-8'))
            new_config = json.loads(new_content.decode('utf-8'))
        except json.JSONDecodeError as e:
            await processing_msg.edit(content=f"❌ Error parsing JSON files: {str(e)}")
            return
        
        # Compare configurations
        changes = config_comparator.compare_configs(old_config, new_config)
        
        # Create result embed
        if not any([changes["added"], changes["removed"], changes["modified"]]):
            embed = discord.Embed(
                title="✅ No Changes Detected",
                description="The two configuration files are identical.",
                color=0x00ff00,
                timestamp=datetime.now(timezone.utc)
            )
        else:
            embed = discord.Embed(
                title="🔍 Configuration Changes Detected",
                description=f"Found {len(changes['summary'])} types of changes between the files.",
                color=0xffa500,
                timestamp=datetime.now(timezone.utc)
            )
            
            # Add summary
            if changes["summary"]:
                summary_text = "\n".join([f"• {item}" for item in changes["summary"]])
                embed.add_field(name="📊 Summary", value=summary_text, inline=False)
            
            # Add detailed changes (limit to prevent embed overflow)
            for section, items in changes["added"].items():
                if len(items) <= 5:  # Show details for small changes
                    item_details = []
                    for item_id, item_data in list(items.items())[:5]:
                        title = item_data.get('title', 'Unknown')
                        rarity = item_data.get('rarity', 'Unknown')
                        item_details.append(f"`{item_id}`: {title} (Rarity: {rarity})")
                    embed.add_field(
                        name=f"➕ Added {section.title()}",
                        value="\n".join(item_details),
                        inline=False
                    )
                else:
                    embed.add_field(
                        name=f"➕ Added {section.title()}",
                        value=f"{len(items)} items added (too many to display)",
                        inline=False
                    )
        
        await processing_msg.edit(content=None, embed=embed)
        
        # Create and upload modified config if there are changes
        if any([changes["added"], changes["removed"], changes["modified"]]):
            modified_config = config_comparator.create_modified_config(new_config, changes)
            
            # Create file buffer
            modified_json = json.dumps(modified_config, indent=2, ensure_ascii=False)
            file_buffer = io.BytesIO(modified_json.encode('utf-8'))
            file_buffer.seek(0)
            
            # Send modified config file
            discord_file = discord.File(file_buffer, filename="modified_storeConfig.json")
            
            modify_embed = discord.Embed(
                title="🔧 Modified Configuration File",
                description="Here's the new configuration file with `preOwned: true` added to all newly detected items.",
                color=0x00ff00
            )
            modify_embed.add_field(
                name="Changes Applied", 
                value=f"Added `preOwned: true` to {sum(len(items) for items in changes['added'].values())} new items",
                inline=False
            )
            
            await ctx.send(embed=modify_embed, file=discord_file)
        
    except Exception as e:
        logger.error(f"Error in compare command: {str(e)}")
        await ctx.reply(f"❌ An error occurred while processing the files: {str(e)}")

@bot.command(name='modify')
async def modify_config(ctx, *, item_ids=None):
    """
    Apply preOwned: true to specific item IDs in a storeConfig.json file.
    Usage: !modify <item_ids> (with one JSON file attachment)
    Example: !modify 2050,2051,2052 or !modify 2050 2051 2052
    """
    if len(ctx.message.attachments) != 1:
        embed = discord.Embed(
            title="❌ Invalid Usage",
            description="Please attach exactly 1 storeConfig.json file.\n\n**Usage:** `!modify <item_ids>` with 1 file attachment",
            color=0xff0000
        )
        embed.add_field(name="Examples", value="`!modify 2050,2051,2052`\n`!modify 2050 2051 2052`\n`!modify 3071,3072`", inline=False)
        embed.add_field(name="Expected File", value="📎 storeConfig.json file to modify", inline=False)
        await ctx.reply(embed=embed)
        return
    
    if not item_ids:
        embed = discord.Embed(
            title="❌ Missing Item IDs",
            description="Please specify the item IDs to add preOwned: true to.",
            color=0xff0000
        )
        embed.add_field(name="Usage", value="`!modify <item_ids>`", inline=False)
        embed.add_field(name="Examples", value="`!modify 2050,2051,2052`\n`!modify 2050 2051 2052`", inline=False)
        await ctx.reply(embed=embed)
        return
    
    try:
        # Parse item IDs from various formats
        if ',' in item_ids:
            # Comma-separated: "2050,2051,2052"
            ids_to_modify = [id.strip() for id in item_ids.split(',')]
        else:
            # Space-separated: "2050 2051 2052"
            ids_to_modify = item_ids.split()
        
        # Remove empty strings and validate
        ids_to_modify = [id for id in ids_to_modify if id.strip()]
        
        if not ids_to_modify:
            await ctx.reply("❌ No valid item IDs provided!")
            return
        
        # Download and parse the attached file
        attachment = ctx.message.attachments[0]
        
        if not attachment.filename.endswith('.json'):
            await ctx.reply("❌ File must be a JSON file!")
            return
        
        # Show processing message
        processing_msg = await ctx.reply(f"🔄 Processing config file and applying preOwned: true to {len(ids_to_modify)} items...")
        
        # Download file
        content = await attachment.read()
        
        # Parse JSON
        try:
            config_data = json.loads(content.decode('utf-8'))
        except json.JSONDecodeError as e:
            await processing_msg.edit(content=f"❌ Error parsing JSON file: {str(e)}")
            return
        
        # Apply preOwned: true to specified items
        sections_to_check = ["animals", "skins", "hats", "glasses", "chests", "feet", "powerups"]
        modified_items = []
        not_found_items = []
        
        for item_id in ids_to_modify:
            found = False
            for section in sections_to_check:
                if section in config_data and item_id in config_data[section]:
                    config_data[section][item_id]["preOwned"] = True
                    item_title = config_data[section][item_id].get('title', 'Unknown')
                    modified_items.append(f"`{item_id}`: {item_title} ({section})")
                    found = True
                    break
            
            if not found:
                not_found_items.append(item_id)
        
        # Create result embed
        if modified_items:
            embed = discord.Embed(
                title="✅ Configuration Modified",
                description=f"Successfully applied `preOwned: true` to {len(modified_items)} items.",
                color=0x00ff00,
                timestamp=datetime.now(timezone.utc)
            )
            
            # Add modified items (limit to prevent embed overflow)
            if len(modified_items) <= 10:
                embed.add_field(
                    name="📝 Modified Items",
                    value="\n".join(modified_items),
                    inline=False
                )
            else:
                embed.add_field(
                    name="📝 Modified Items",
                    value="\n".join(modified_items[:10]) + f"\n... and {len(modified_items) - 10} more",
                    inline=False
                )
            
            if not_found_items:
                embed.add_field(
                    name="⚠️ Not Found",
                    value=f"Items not found: {', '.join(not_found_items)}",
                    inline=False
                )
        else:
            embed = discord.Embed(
                title="❌ No Items Modified",
                description="None of the specified item IDs were found in the configuration file.",
                color=0xff0000,
                timestamp=datetime.now(timezone.utc)
            )
            embed.add_field(
                name="❌ Not Found Items",
                value=f"{', '.join(not_found_items)}",
                inline=False
            )
        
        await processing_msg.edit(content=None, embed=embed)
        
        # Create and upload modified config file if any items were modified
        if modified_items:
            modified_json = json.dumps(config_data, indent=2, ensure_ascii=False)
            file_buffer = io.BytesIO(modified_json.encode('utf-8'))
            file_buffer.seek(0)
            
            # Send modified config file
            discord_file = discord.File(file_buffer, filename="modified_storeConfig.json")
            
            modify_embed = discord.Embed(
                title="🔧 Modified Configuration File",
                description=f"Here's your configuration file with `preOwned: true` applied to {len(modified_items)} items.",
                color=0x00ff00
            )
            
            await ctx.send(embed=modify_embed, file=discord_file)
        
    except Exception as e:
        logger.error(f"Error in modify command: {str(e)}")
        await ctx.reply(f"❌ An error occurred while processing the file: {str(e)}")

@bot.command(name='test_notification')
async def test_notification(ctx):
    """
    Test the Discord notification system by simulating a version update.
    """
    try:
        # Simulate an update notification
        embed = discord.Embed(
            title="🧪 Test Notification - Fun Run 4 Update Simulation",
            description="This is a test to verify Discord notifications are working!",
            color=0xff6b00,
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(name="Simulated Version", value="2.31.0 (fake)", inline=True)
        embed.add_field(name="Current Version", value=uptodown_monitor.current_version or "Unknown", inline=True)
        embed.add_field(name="Status", value="✅ Discord messaging is working!", inline=False)
        embed.set_footer(text="This was a test notification - no actual update occurred")
        
        await ctx.send(embed=embed)
        logger.info("Test notification sent successfully")
        
    except Exception as e:
        logger.error(f"Error sending test notification: {str(e)}")
        await ctx.reply(f"❌ Error sending test notification: {str(e)}")

@bot.command(name='reset_version')
async def reset_version(ctx):
    """
    Reset the stored version data to test update notifications.
    This will make the bot think there's no current version, so the next check will trigger an update.
    """
    try:
        uptodown_monitor.current_version = None
        if os.path.exists(uptodown_monitor.version_file):
            os.remove(uptodown_monitor.version_file)
        
        embed = discord.Embed(
            title="🔄 Version Data Reset",
            description="Stored version data has been reset. The next automatic check will detect the current version as a 'new' update.",
            color=0x00ff00,
            timestamp=datetime.now(timezone.utc)
        )
        embed.add_field(name="Next Check", value="Within 15 minutes (or use !check_update for immediate check)", inline=False)
        embed.set_footer(text="This will trigger an update notification on the next check")
        
        await ctx.send(embed=embed)
        logger.info("Version data reset by user command")
        
    except Exception as e:
        logger.error(f"Error resetting version data: {str(e)}")
        await ctx.reply(f"❌ Error resetting version data: {str(e)}")

@bot.command(name='check_update')
async def manual_update_check(ctx):
    """
    Manually trigger a check for Fun Run 4 updates on Uptodown.
    """
    processing_msg = await ctx.reply("🔍 Checking Uptodown for Fun Run 4 updates...")
    
    try:
        has_update, version, info = await uptodown_monitor.check_uptodown_update()
        
        if has_update:
            embed = discord.Embed(
                title="🚨 Update Found!",
                description="A new version of Fun Run 4 has been detected!",
                color=0xff6b00,
                timestamp=datetime.now(timezone.utc)
            )
            embed.add_field(name="New Version", value=version or "Unknown", inline=True)
            embed.add_field(name="Info", value=info or "No additional info", inline=False)
            embed.set_footer(text="Use !compare command to analyze config changes")
        else:
            embed = discord.Embed(
                title="✅ No Updates",
                description="No new updates found for Fun Run 4.",
                color=0x00ff00,
                timestamp=datetime.now(timezone.utc)
            )
            embed.add_field(name="Current Version", value=version or "Unknown", inline=True)
            if info:
                embed.add_field(name="Status", value=info, inline=False)
        
        await processing_msg.edit(content=None, embed=embed)
        
    except Exception as e:
        logger.error(f"Error in manual update check: {str(e)}")
        await processing_msg.edit(content=f"❌ Error checking for updates: {str(e)}")

@update_checker.before_loop
async def before_update_checker():
    await bot.wait_until_ready()

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return  # Ignore unknown commands
    
    logger.error(f"Command error: {str(error)}")
    
    embed = discord.Embed(
        title="❌ Command Error",
        description=f"An error occurred: {str(error)}",
        color=0xff0000
    )
    await ctx.reply(embed=embed)

# Run the bot
if __name__ == "__main__":
    try:
        bot.run(config['discord_token'])
    except Exception as e:
        logger.error(f"Failed to start bot: {str(e)}")
        print(f"Failed to start bot: {str(e)}")
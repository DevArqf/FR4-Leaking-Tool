"""
Fun Run 4 Leaking Tool - GUI Application with Discord Integration
Modern desktop interface for monitoring updates and comparing configs
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
import asyncio
import threading
import json
import os
from datetime import datetime, timezone
import logging
from logging.handlers import RotatingFileHandler
from uptodown_monitor import UptodownMonitor
from config_comparator import ConfigComparator
from PIL import Image, ImageTk
import discord
from discord.ext import commands

# Configure logging
logger = logging.getLogger('funrun_monitor')
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler('bot.log', maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Modern Color Palette
class ModernColors:
    PRIMARY = "#6366f1"  # Indigo
    SUCCESS = "#10b981"  # Green
    WARNING = "#f59e0b"  # Orange
    ERROR = "#ef4444"    # Red
    INFO = "#3b82f6"     # Blue
    ACCENT = "#ec4899"   # Pink

class FR4LeakingToolGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Fun Run 4 Leaking Tool")
        self.geometry("1400x900")  # Larger window for more breathing room
        self.minsize(1200, 800)  # Increased minimum size
        
        # Set window icon
        try:
            if os.path.exists('assets/app_icon.png'):
                # Load icon as PhotoImage for tkinter
                icon_img = Image.open('assets/app_icon.png')
                self.iconphoto(True, ImageTk.PhotoImage(icon_img))
        except Exception as e:
            logger.warning(f"Failed to load window icon: {e}")
        
        # Initialize components
        self.monitor = UptodownMonitor()
        self.comparator = ConfigComparator()
        self.auto_check_running = False
        self.check_thread = None
        
        # Discord bot components
        self.discord_bot = None
        self.discord_enabled = False
        self.discord_thread = None
        self.discord_config = self.load_discord_config()
        
        # File paths
        self.old_config_path = None
        self.new_config_path = None
        self.modify_config_path = None
        
        # Initialize icons dictionary first (before creating layout)
        self.icons = {}
        
        # Load icons BEFORE creating UI so buttons have icons immediately
        self.load_icons_early()
        
        # Create UI
        self.create_layout()
        
        # Update any remaining icon references
        self.update_icon_references()
        
        # Update version display
        self.update_version_display()
        
        # Start Discord bot if configured
        if self.discord_config.get('discord_token') and self.discord_config.get('channel_id'):
            self.start_discord_bot()
    
    def load_discord_config(self):
        """Load Discord configuration from config.json"""
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load Discord config: {e}")
        return {}
    
    def start_discord_bot(self):
        """Start Discord bot in a separate thread"""
        if self.discord_enabled:
            return
        
        try:
            intents = discord.Intents.default()
            intents.message_content = True
            intents.members = True
            self.discord_bot = commands.Bot(
                command_prefix='!', 
                intents=intents,
                allowed_mentions=discord.AllowedMentions(everyone=True)
            )
            
            # Setup bot events
            @self.discord_bot.event
            async def on_ready():
                logger.info(f'Discord bot {self.discord_bot.user} is online!')
                self.after(0, lambda: self.add_status_log(f"✓ Discord bot connected as {self.discord_bot.user}"))
                self.discord_enabled = True
            
            # Run bot in separate thread
            def run_bot():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.discord_bot.start(self.discord_config['discord_token']))
                except Exception as err:
                    error_msg = str(err)
                    logger.error(f"Discord bot error: {error_msg}")
                    self.after(0, lambda msg=error_msg: self.add_status_log(f"✗ Discord bot error: {msg}"))
            
            self.discord_thread = threading.Thread(target=run_bot, daemon=True)
            self.discord_thread.start()
            self.add_status_log("Starting Discord bot...")
            
        except Exception as err:
            error_msg = str(err)
            logger.error(f"Failed to start Discord bot: {error_msg}")
            self.add_status_log(f"✗ Failed to start Discord bot: {error_msg}")
    
    def send_discord_notification(self, version, info):
        """Send Discord notification about update"""
        if not self.discord_enabled or not self.discord_bot:
            return
        
        async def send_message():
            try:
                channel_id = int(self.discord_config.get('channel_id'))
                channel = self.discord_bot.get_channel(channel_id)
                
                if channel:
                    embed = discord.Embed(
                        title="🚨 Fun Run 4 Update Detected!",
                        description="A new version of Fun Run 4 has been found on Uptodown!",
                        color=0xff6b00,
                        timestamp=datetime.now(timezone.utc)
                    )
                    embed.add_field(name="Version", value=version or "Unknown", inline=True)
                    embed.add_field(name="Details", value=info or "No details available", inline=False)
                    embed.set_footer(text="Detected by FR4 Leaking Tool GUI")
                    
                    await channel.send("@here", embed=embed)
                    logger.info(f"Discord notification sent for version {version}")
                    self.after(0, lambda: self.add_status_log("✓ Discord notification sent"))
            except Exception as err:
                error_msg = str(err)
                logger.error(f"Failed to send Discord notification: {error_msg}")
                self.after(0, lambda msg=error_msg: self.add_status_log(f"✗ Discord notification failed: {msg}"))
        
        # Schedule the coroutine in the bot's event loop
        if self.discord_bot.loop and self.discord_bot.loop.is_running():
            asyncio.run_coroutine_threadsafe(send_message(), self.discord_bot.loop)
    
    def load_icons_early(self):
        """Load all icons BEFORE creating UI"""
        assets_path = "assets"
        
        if os.path.exists(assets_path):
            icon_files = {
                'logo': 'app_icon.png',  # Use new app icon
                'monitor': 'monitor.png',
                'compare': 'compare.png',
                'modify': 'modify.png',
                'logs': 'logs.png',
                'check': 'btn_check.png',
                'play': 'btn_play.png',
                'pause': 'btn_pause.png',
                'reset': 'btn_reset.png',
                'refresh': 'refresh.png',
                'delete': 'delete.png',
            }
            
            for key, filename in icon_files.items():
                filepath = os.path.join(assets_path, filename)
                if os.path.exists(filepath):
                    try:
                        img = Image.open(filepath)
                        # Use smaller icons for buttons to prevent clipping
                        icon_size = (32, 32) if key == 'logo' else (20, 20)
                        self.icons[key] = ctk.CTkImage(light_image=img, dark_image=img, size=icon_size)
                    except Exception as e:
                        logger.warning(f"Failed to load icon {filename}: {e}")
    
    def update_icon_references(self):
        """Update icon references after UI is created"""
        # Update logo if loaded
        if 'logo' in self.icons and hasattr(self, 'logo_label'):
            self.logo_label.configure(image=self.icons['logo'], text="  FR4 Tool", compound="left")
    
    def load_icons(self):
        """Deprecated - kept for compatibility"""
        pass
        
        # Update logo if loaded
        if 'logo' in self.icons and hasattr(self, 'logo_label'):
            self.logo_label.configure(image=self.icons['logo'], text="  FR4 Leaking Tool", compound="left")
        
        # Update navigation buttons
        if hasattr(self, 'monitor_btn') and 'monitor' in self.icons:
            self.monitor_btn.configure(image=self.icons['monitor'])
        if hasattr(self, 'compare_btn') and 'compare' in self.icons:
            self.compare_btn.configure(image=self.icons['compare'])
        if hasattr(self, 'modify_btn') and 'modify' in self.icons:
            self.modify_btn.configure(image=self.icons['modify'])
        if hasattr(self, 'logs_btn') and 'logs' in self.icons:
            self.logs_btn.configure(image=self.icons['logs'])
        
        # Update action buttons if they exist
        if hasattr(self, 'check_now_btn') and 'check' in self.icons:
            self.check_now_btn.configure(image=self.icons['check'])
        if hasattr(self, 'auto_check_btn') and 'play' in self.icons:
            self.auto_check_btn.configure(image=self.icons['play'])
        if hasattr(self, 'reset_version_btn') and 'reset' in self.icons:
            self.reset_version_btn.configure(image=self.icons['reset'])
        
    def create_layout(self):
        """Create the main layout"""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.create_main_content()
        
    def create_sidebar(self):
        """Create sidebar with navigation"""
        self.sidebar_frame = ctk.CTkFrame(self, width=280, corner_radius=0)  # Wider sidebar
        self.sidebar_frame.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)
        
        # Logo/Title - Using modern Segoe UI Variable font style
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="FR4 Leaking Tool",
            font=ctk.CTkFont(family="Segoe UI Variable", size=22, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=25, pady=(30, 10))  # Increased padding
        
        self.version_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="v1.0 Advanced",
            font=ctk.CTkFont(family="Segoe UI Variable", size=12)
        )
        self.version_label.grid(row=1, column=0, padx=25, pady=(0, 30))  # More spacing
        
        # Navigation buttons - Consistent height and increased spacing
        self.monitor_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="    Monitor Updates",
            image=self.icons.get('monitor'),
            compound="left",
            command=self.show_monitor_tab,
            height=48,  # Consistent height
            font=ctk.CTkFont(family="Segoe UI Variable", size=14),
            corner_radius=10
        )
        self.monitor_btn.grid(row=2, column=0, padx=25, pady=(5, 8), sticky="ew")  # Increased spacing
        
        self.compare_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="    Compare Configs",
            image=self.icons.get('compare'),
            compound="left",
            command=self.show_compare_tab,
            height=48,  # Consistent height
            font=ctk.CTkFont(family="Segoe UI Variable", size=14),
            corner_radius=10
        )
        self.compare_btn.grid(row=3, column=0, padx=25, pady=8, sticky="ew")
        
        self.modify_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="    Modify Config",
            image=self.icons.get('modify'),
            compound="left",
            command=self.show_modify_tab,
            height=48,  # Consistent height
            font=ctk.CTkFont(family="Segoe UI Variable", size=14),
            corner_radius=10
        )
        self.modify_btn.grid(row=4, column=0, padx=25, pady=8, sticky="ew")
        
        self.logs_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="    View Logs",
            image=self.icons.get('logs'),
            compound="left",
            command=self.show_logs_tab,
            height=48,  # Consistent height
            font=ctk.CTkFont(family="Segoe UI Variable", size=14),
            corner_radius=10
        )
        self.logs_btn.grid(row=5, column=0, padx=25, pady=8, sticky="ew")
        
        # Appearance mode selector - Better grouped and labeled
        self.appearance_mode_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Appearance Mode:",
            anchor="w",
            font=ctk.CTkFont(family="Segoe UI Variable", size=13, weight="bold")
        )
        self.appearance_mode_label.grid(row=7, column=0, padx=25, pady=(20, 8))  # More spacing
        
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["Dark", "Light", "System"],
            command=self.change_appearance_mode,
            height=40,  # Consistent height
            font=ctk.CTkFont(family="Segoe UI Variable", size=13)
        )
        self.appearance_mode_optionemenu.grid(row=8, column=0, padx=25, pady=(0, 30))
        
    def create_main_content(self):
        """Create main content area"""
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)  # More padding
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Create tabs
        self.create_monitor_tab()
        self.create_compare_tab()
        self.create_modify_tab()
        self.create_logs_tab()
        
        # Show monitor tab by default
        self.show_monitor_tab()
        
    def create_monitor_tab(self):
        """Create the update monitoring tab with improved grouping and spacing"""
        self.monitor_tab = ctk.CTkFrame(self.main_frame)
        
        # Title with better typography
        title = ctk.CTkLabel(
            self.monitor_tab,
            text="Uptodown Update Monitor",
            font=ctk.CTkFont(family="Segoe UI Variable", size=32, weight="bold")
        )
        title.pack(pady=(0, 30))  # More breathing room
        
        # Version info group box with label
        version_group_label = ctk.CTkLabel(
            self.monitor_tab,
            text="VERSION INFORMATION",
            font=ctk.CTkFont(family="Segoe UI Variable", size=13, weight="bold"),
            anchor="w"
        )
        version_group_label.pack(fill="x", padx=30, pady=(10, 5))
        
        version_frame = ctk.CTkFrame(self.monitor_tab, corner_radius=12)
        version_frame.pack(fill="x", pady=(0, 20), padx=30)  # Increased padding
        
        self.current_version_label = ctk.CTkLabel(
            version_frame,
            text="Current Version: Loading...",
            font=ctk.CTkFont(family="Segoe UI Variable", size=18)
        )
        self.current_version_label.pack(pady=(25, 15))  # More padding
        
        self.last_check_label = ctk.CTkLabel(
            version_frame,
            text="Last Check: Never",
            font=ctk.CTkFont(family="Segoe UI Variable", size=14)
        )
        self.last_check_label.pack(pady=(0, 25))
        
        # Control buttons group with label
        control_group_label = ctk.CTkLabel(
            self.monitor_tab,
            text="ACTIONS",
            font=ctk.CTkFont(family="Segoe UI Variable", size=13, weight="bold"),
            anchor="w"
        )
        control_group_label.pack(fill="x", padx=30, pady=(10, 5))
        
        control_frame = ctk.CTkFrame(self.monitor_tab, corner_radius=12)
        control_frame.pack(fill="x", pady=(0, 25), padx=30)  # More spacing
        
        # Consistent button heights and spacing
        self.check_now_btn = ctk.CTkButton(
            control_frame,
            text="    Check Now",
            image=self.icons.get('check'),
            compound="left",
            command=self.check_update_manual,
            height=56,  # Consistent, larger height
            font=ctk.CTkFont(family="Segoe UI Variable", size=15, weight="bold"),
            fg_color=ModernColors.PRIMARY,
            hover_color="#4f46e5",
            corner_radius=10
        )
        self.check_now_btn.pack(side="left", padx=15, pady=25, expand=True, fill="x")  # More padding
        
        self.auto_check_btn = ctk.CTkButton(
            control_frame,
            text="    Start Auto-Check (15 min)",
            image=self.icons.get('play'),
            compound="left",
            command=self.toggle_auto_check,
            height=56,  # Consistent height
            font=ctk.CTkFont(family="Segoe UI Variable", size=15, weight="bold"),
            fg_color=ModernColors.SUCCESS,
            hover_color="#059669",
            corner_radius=10
        )
        self.auto_check_btn.pack(side="left", padx=15, pady=25, expand=True, fill="x")
        
        self.reset_version_btn = ctk.CTkButton(
            control_frame,
            text="    Reset Version",
            image=self.icons.get('reset'),
            compound="left",
            command=self.reset_version,
            height=56,  # Consistent height
            font=ctk.CTkFont(family="Segoe UI Variable", size=15, weight="bold"),
            fg_color=ModernColors.ERROR,
            hover_color="#dc2626",
            corner_radius=10
        )
        self.reset_version_btn.pack(side="left", padx=15, pady=25, expand=True, fill="x")
        
        # Status/Log display group with label
        status_label = ctk.CTkLabel(
            self.monitor_tab,
            text="STATUS LOG",
            font=ctk.CTkFont(family="Segoe UI Variable", size=13, weight="bold"),
            anchor="w"
        )
        status_label.pack(fill="x", padx=30, pady=(10, 5))
        
        self.status_textbox = ctk.CTkTextbox(
            self.monitor_tab, 
            height=320,  # Slightly taller
            font=ctk.CTkFont(family="Segoe UI Variable", size=13),
            corner_radius=12
        )
        self.status_textbox.pack(fill="both", expand=True, padx=30, pady=(0, 30))  # More padding
        self.status_textbox.insert("1.0", "Ready to check for updates...\n")
        
    def create_compare_tab(self):
        """Create the config comparison tab with improved layout"""
        self.compare_tab = ctk.CTkFrame(self.main_frame)
        
        # Title
        title = ctk.CTkLabel(
            self.compare_tab,
            text="Config File Comparison",
            font=ctk.CTkFont(family="Segoe UI Variable", size=32, weight="bold")
        )
        title.pack(pady=(0, 30))
        
        # File selection group with label
        file_group_label = ctk.CTkLabel(
            self.compare_tab,
            text="FILE SELECTION",
            font=ctk.CTkFont(family="Segoe UI Variable", size=13, weight="bold"),
            anchor="w"
        )
        file_group_label.pack(fill="x", padx=30, pady=(10, 5))
        
        file_frame = ctk.CTkFrame(self.compare_tab, corner_radius=12)
        file_frame.pack(fill="x", pady=(0, 20), padx=30)
        
        # Old config - Better aligned
        old_config_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        old_config_frame.pack(fill="x", pady=(20, 12), padx=20)
        
        ctk.CTkLabel(
            old_config_frame,
            text="Old Config File:",
            font=ctk.CTkFont(family="Segoe UI Variable", size=14, weight="bold"),
            width=130,
            anchor="w"
        ).pack(side="left", padx=(0, 15))
        
        self.old_config_label = ctk.CTkLabel(
            old_config_frame,
            text="No file selected",
            font=ctk.CTkFont(family="Segoe UI Variable", size=13),
            anchor="w"
        )
        self.old_config_label.pack(side="left", padx=10, fill="x", expand=True)
        
        ctk.CTkButton(
            old_config_frame,
            text="Browse",
            command=self.select_old_config,
            width=110,
            height=36,
            font=ctk.CTkFont(family="Segoe UI Variable", size=13),
            corner_radius=8
        ).pack(side="right", padx=(10, 0))
        
        # New config - Better aligned
        new_config_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        new_config_frame.pack(fill="x", pady=(12, 20), padx=20)
        
        ctk.CTkLabel(
            new_config_frame,
            text="New Config File:",
            font=ctk.CTkFont(family="Segoe UI Variable", size=14, weight="bold"),
            width=130,
            anchor="w"
        ).pack(side="left", padx=(0, 15))
        
        self.new_config_label = ctk.CTkLabel(
            new_config_frame,
            text="No file selected",
            font=ctk.CTkFont(family="Segoe UI Variable", size=13),
            anchor="w"
        )
        self.new_config_label.pack(side="left", padx=10, fill="x", expand=True)
        
        ctk.CTkButton(
            new_config_frame,
            text="Browse",
            command=self.select_new_config,
            width=110,
            height=36,
            font=ctk.CTkFont(family="Segoe UI Variable", size=13),
            corner_radius=8
        ).pack(side="right", padx=(10, 0))
        
        # Compare button - Grouped with actions
        action_group_label = ctk.CTkLabel(
            self.compare_tab,
            text="ACTIONS",
            font=ctk.CTkFont(family="Segoe UI Variable", size=13, weight="bold"),
            anchor="w"
        )
        action_group_label.pack(fill="x", padx=30, pady=(10, 5))
        
        self.compare_execute_btn = ctk.CTkButton(
            self.compare_tab,
            text="    Compare Files",
            image=self.icons.get('compare'),
            compound="left",
            command=self.compare_configs,
            height=56,
            font=ctk.CTkFont(family="Segoe UI Variable", size=15, weight="bold"),
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            corner_radius=10
        )
        self.compare_execute_btn.pack(pady=(0, 25), padx=30, fill="x")
        
        # Results display group with label
        results_label = ctk.CTkLabel(
            self.compare_tab,
            text="COMPARISON RESULTS",
            font=ctk.CTkFont(family="Segoe UI Variable", size=13, weight="bold"),
            anchor="w"
        )
        results_label.pack(fill="x", padx=30, pady=(10, 5))
        
        self.compare_results_textbox = ctk.CTkTextbox(
            self.compare_tab, 
            height=320,
            font=ctk.CTkFont(family="Segoe UI Variable", size=13),
            corner_radius=12,
            state="disabled"  # Make read-only
        )
        self.compare_results_textbox.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
    def create_modify_tab(self):
        """Create the config modification tab with improved layout"""
        self.modify_tab = ctk.CTkFrame(self.main_frame)
        
        # Title
        title = ctk.CTkLabel(
            self.modify_tab,
            text="Modify Config by Item IDs",
            font=ctk.CTkFont(family="Segoe UI Variable", size=32, weight="bold")
        )
        title.pack(pady=(0, 30))
        
        # File selection group with label
        file_group_label = ctk.CTkLabel(
            self.modify_tab,
            text="FILE SELECTION",
            font=ctk.CTkFont(family="Segoe UI Variable", size=13, weight="bold"),
            anchor="w"
        )
        file_group_label.pack(fill="x", padx=30, pady=(10, 5))
        
        file_frame = ctk.CTkFrame(self.modify_tab, corner_radius=12)
        file_frame.pack(fill="x", pady=(0, 20), padx=30)
        
        file_inner_frame = ctk.CTkFrame(file_frame, fg_color="transparent")
        file_inner_frame.pack(fill="x", pady=20, padx=20)
        
        ctk.CTkLabel(
            file_inner_frame,
            text="Config File:",
            font=ctk.CTkFont(family="Segoe UI Variable", size=14, weight="bold"),
            width=130,
            anchor="w"
        ).pack(side="left", padx=(0, 15))
        
        self.modify_config_label = ctk.CTkLabel(
            file_inner_frame,
            text="No file selected",
            font=ctk.CTkFont(family="Segoe UI Variable", size=13),
            anchor="w"
        )
        self.modify_config_label.pack(side="left", padx=10, fill="x", expand=True)
        
        ctk.CTkButton(
            file_inner_frame,
            text="Browse",
            command=self.select_modify_config,
            width=110,
            height=36,
            font=ctk.CTkFont(family="Segoe UI Variable", size=13),
            corner_radius=8
        ).pack(side="right", padx=(10, 0))
        
        # Item IDs input group with label
        ids_group_label = ctk.CTkLabel(
            self.modify_tab,
            text="ITEM IDS",
            font=ctk.CTkFont(family="Segoe UI Variable", size=13, weight="bold"),
            anchor="w"
        )
        ids_group_label.pack(fill="x", padx=30, pady=(10, 5))
        
        ids_frame = ctk.CTkFrame(self.modify_tab, corner_radius=12)
        ids_frame.pack(fill="x", pady=(0, 20), padx=30)
        
        ctk.CTkLabel(
            ids_frame,
            text="Enter Item IDs (comma or space separated):",
            font=ctk.CTkFont(family="Segoe UI Variable", size=13),
            anchor="w"
        ).pack(anchor="w", padx=20, pady=(20, 8))
        
        self.item_ids_entry = ctk.CTkEntry(
            ids_frame,
            placeholder_text="e.g., 2050, 2051, 2052 or 2050 2051 2052",
            height=44,
            font=ctk.CTkFont(family="Segoe UI Variable", size=14),
            corner_radius=8
        )
        self.item_ids_entry.pack(fill="x", padx=20, pady=(0, 20))
        
        # Modify button group with label
        action_group_label = ctk.CTkLabel(
            self.modify_tab,
            text="ACTIONS",
            font=ctk.CTkFont(family="Segoe UI Variable", size=13, weight="bold"),
            anchor="w"
        )
        action_group_label.pack(fill="x", padx=30, pady=(10, 5))
        
        self.modify_execute_btn = ctk.CTkButton(
            self.modify_tab,
            text="    Apply Modifications",
            image=self.icons.get('modify'),
            compound="left",
            command=self.modify_config,
            height=56,
            font=ctk.CTkFont(family="Segoe UI Variable", size=15, weight="bold"),
            fg_color="#2563eb",
            hover_color="#1d4ed8",
            corner_radius=10
        )
        self.modify_execute_btn.pack(pady=(0, 25), padx=30, fill="x")
        
        # Results display group with label
        results_label = ctk.CTkLabel(
            self.modify_tab,
            text="MODIFICATION RESULTS",
            font=ctk.CTkFont(family="Segoe UI Variable", size=13, weight="bold"),
            anchor="w"
        )
        results_label.pack(fill="x", padx=30, pady=(10, 5))
        
        self.modify_results_textbox = ctk.CTkTextbox(
            self.modify_tab, 
            height=280,
            font=ctk.CTkFont(family="Segoe UI Variable", size=13),
            corner_radius=12,
            state="disabled"  # Make read-only
        )
        self.modify_results_textbox.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
    def create_logs_tab(self):
        """Create the logs viewing tab with improved layout"""
        self.logs_tab = ctk.CTkFrame(self.main_frame)
        
        # Title
        title = ctk.CTkLabel(
            self.logs_tab,
            text="Application Logs",
            font=ctk.CTkFont(family="Segoe UI Variable", size=32, weight="bold")
        )
        title.pack(pady=(0, 30))
        
        # Control buttons group with label
        control_group_label = ctk.CTkLabel(
            self.logs_tab,
            text="ACTIONS",
            font=ctk.CTkFont(family="Segoe UI Variable", size=13, weight="bold"),
            anchor="w"
        )
        control_group_label.pack(fill="x", padx=30, pady=(10, 5))
        
        control_frame = ctk.CTkFrame(self.logs_tab, corner_radius=12)
        control_frame.pack(fill="x", pady=(0, 25), padx=30)
        
        ctk.CTkButton(
            control_frame,
            text="    Refresh Logs",
            image=self.icons.get('refresh'),
            compound="left",
            command=self.refresh_logs,
            height=48,
            font=ctk.CTkFont(family="Segoe UI Variable", size=14),
            corner_radius=8
        ).pack(side="left", padx=15, pady=20)
        
        ctk.CTkButton(
            control_frame,
            text="    Clear Logs",
            image=self.icons.get('delete'),
            compound="left",
            command=self.clear_logs,
            height=48,
            font=ctk.CTkFont(family="Segoe UI Variable", size=14),
            fg_color="#dc2626",
            hover_color="#b91c1c",
            corner_radius=8
        ).pack(side="left", padx=15, pady=20)
        
        # Logs display group with label
        logs_group_label = ctk.CTkLabel(
            self.logs_tab,
            text="LOG CONTENTS",
            font=ctk.CTkFont(family="Segoe UI Variable", size=13, weight="bold"),
            anchor="w"
        )
        logs_group_label.pack(fill="x", padx=30, pady=(10, 5))
        
        self.logs_textbox = ctk.CTkTextbox(
            self.logs_tab, 
            height=520,
            font=ctk.CTkFont(family="Segoe UI Variable", size=13),
            corner_radius=12
        )
        self.logs_textbox.pack(fill="both", expand=True, padx=30, pady=(0, 30))
        
    # Tab switching methods
    def show_monitor_tab(self):
        self.compare_tab.pack_forget()
        self.modify_tab.pack_forget()
        self.logs_tab.pack_forget()
        self.monitor_tab.pack(fill="both", expand=True)
        
    def show_compare_tab(self):
        self.monitor_tab.pack_forget()
        self.modify_tab.pack_forget()
        self.logs_tab.pack_forget()
        self.compare_tab.pack(fill="both", expand=True)
        
    def show_modify_tab(self):
        self.monitor_tab.pack_forget()
        self.compare_tab.pack_forget()
        self.logs_tab.pack_forget()
        self.modify_tab.pack(fill="both", expand=True)
        
    def show_logs_tab(self):
        self.monitor_tab.pack_forget()
        self.compare_tab.pack_forget()
        self.modify_tab.pack_forget()
        self.logs_tab.pack(fill="both", expand=True)
        self.refresh_logs()
        
    # Functionality methods
    def update_version_display(self):
        """Update the version display"""
        version = self.monitor.current_version or "Not detected"
        self.current_version_label.configure(text=f"Current Version: {version}")
        
        last_check = self.monitor.last_check or "Never"
        if last_check != "Never":
            try:
                dt = datetime.fromisoformat(last_check.replace('Z', '+00:00'))
                last_check = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass
        self.last_check_label.configure(text=f"Last Check: {last_check}")
        
    def add_status_log(self, message):
        """Add message to status log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_textbox.insert("end", f"[{timestamp}] {message}\n")
        self.status_textbox.see("end")
        
    def check_update_manual(self):
        """Manually check for updates"""
        self.add_status_log("Checking for updates...")
        self.check_now_btn.configure(state="disabled", text="Checking...")
        
        def check_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            has_update, version, info = loop.run_until_complete(
                self.monitor.check_uptodown_update()
            )
            loop.close()
            
            self.after(0, lambda: self.handle_update_result(has_update, version, info))
            
        threading.Thread(target=check_thread, daemon=True).start()
        
    def handle_update_result(self, has_update, version, info):
        """Handle update check result"""
        self.check_now_btn.configure(state="normal", text="  Check Now")
        self.update_version_display()
        
        if has_update:
            self.add_status_log(f"🚨 NEW UPDATE FOUND: {version}")
            self.add_status_log(f"Info: {info}")
            messagebox.showinfo("Update Found!", f"New version detected: {version}\n\n{info}")
            
            # Send Discord notification
            if self.discord_enabled:
                self.send_discord_notification(version, info)
        else:
            self.add_status_log(f"✓ No update. Current: {version}")
            if info:
                self.add_status_log(f"Info: {info}")
                
    def toggle_auto_check(self):
        """Toggle automatic update checking"""
        if not self.auto_check_running:
            self.auto_check_running = True
            self.auto_check_btn.configure(
                text="  Stop Auto-Check",
                image=self.icons.get('pause'),
                fg_color="#dc2626"
            )
            self.add_status_log("Auto-check started (15 minute interval)")
            self.start_auto_check()
        else:
            self.auto_check_running = False
            self.auto_check_btn.configure(
                text="  Start Auto-Check (15 min)",
                image=self.icons.get('play'),
                fg_color="#16a34a"
            )
            self.add_status_log("Auto-check stopped")
            
    def start_auto_check(self):
        """Start automatic checking thread"""
        def auto_check_loop():
            while self.auto_check_running:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                has_update, version, info = loop.run_until_complete(
                    self.monitor.check_uptodown_update()
                )
                loop.close()
                
                self.after(0, lambda: self.handle_auto_check_result(has_update, version, info))
                
                # Wait 15 minutes
                for _ in range(900):  # 15 * 60 seconds
                    if not self.auto_check_running:
                        break
                    threading.Event().wait(1)
        
        self.check_thread = threading.Thread(target=auto_check_loop, daemon=True)
        self.check_thread.start()
        
    def handle_auto_check_result(self, has_update, version, info):
        """Handle automatic check result"""
        self.update_version_display()
        
        if has_update:
            self.add_status_log(f"🚨 AUTO-CHECK: NEW UPDATE - {version}")
            messagebox.showwarning("Update Detected!", f"New version: {version}\n\n{info}")
            
            # Send Discord notification
            if self.discord_enabled:
                self.send_discord_notification(version, info)
        else:
            self.add_status_log(f"Auto-check: No update ({version})")
            
    def reset_version(self):
        """Reset version data"""
        if messagebox.askyesno("Confirm Reset", "Reset version data? This will trigger an update notification on next check."):
            try:
                # Log before reset
                self.add_status_log(f"Current version before reset: {self.monitor.current_version}")
                
                # Reset the monitor's version data
                self.monitor.reset_version()
                
                # Explicitly set to None
                self.monitor.current_version = None
                self.monitor.last_check = None
                
                # Log after reset
                self.add_status_log(f"Version after reset: {self.monitor.current_version}")
                
                # Update the UI immediately
                self.update_version_display()
                
                # Force UI to refresh
                self.update_idletasks()
                
                # Log success
                self.add_status_log("✓ Version data reset successfully")
                
                # Show success message
                messagebox.showinfo("Success", f"Version data has been reset!\n\nCurrent version: {self.monitor.current_version or 'Not detected'}\nLast check: {self.monitor.last_check or 'Never'}")
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                logger.error(f"Reset version error: {error_details}")
                self.add_status_log(f"✗ Error resetting version: {str(e)}")
                messagebox.showerror("Error", f"Failed to reset version:\n{str(e)}")
            
    def select_old_config(self):
        """Select old config file"""
        path = filedialog.askopenfilename(
            title="Select Old Config File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if path:
            self.old_config_path = path
            self.old_config_label.configure(text=os.path.basename(path))
            
    def select_new_config(self):
        """Select new config file"""
        path = filedialog.askopenfilename(
            title="Select New Config File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if path:
            self.new_config_path = path
            self.new_config_label.configure(text=os.path.basename(path))
            
    def select_modify_config(self):
        """Select config file to modify"""
        path = filedialog.askopenfilename(
            title="Select Config File to Modify",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if path:
            self.modify_config_path = path
            self.modify_config_label.configure(text=os.path.basename(path))
            
    def compare_configs(self):
        """Compare two config files"""
        if not self.old_config_path or not self.new_config_path:
            messagebox.showerror("Error", "Please select both old and new config files!")
            return
            
        try:
            with open(self.old_config_path, 'r', encoding='utf-8') as f:
                old_config = json.load(f)
                
            with open(self.new_config_path, 'r', encoding='utf-8') as f:
                new_config = json.load(f)
                
            changes = self.comparator.compare_configs(old_config, new_config)
            
            # Display results (enable textbox, update, then disable)
            self.compare_results_textbox.configure(state="normal")
            self.compare_results_textbox.delete("1.0", "end")
            
            if not any([changes["added"], changes["removed"], changes["modified"]]):
                self.compare_results_textbox.insert("1.0", "✓ No changes detected - files are identical\n")
            else:
                result = "=" * 60 + "\n"
                result += "COMPARISON RESULTS\n"
                result += "=" * 60 + "\n\n"
                
                result += "SUMMARY:\n"
                for item in changes["summary"]:
                    result += f"  • {item}\n"
                result += "\n"
                
                # Added items
                if changes["added"]:
                    result += "ADDED ITEMS:\n"
                    result += "-" * 60 + "\n"
                    for section, items in changes["added"].items():
                        result += f"\n{section.upper()}:\n"
                        for item_id, item_data in list(items.items())[:10]:
                            title = item_data.get('title', 'Unknown')
                            rarity = item_data.get('rarity', 'Unknown')
                            result += f"  [{item_id}] {title} (Rarity: {rarity})\n"
                        if len(items) > 10:
                            result += f"  ... and {len(items) - 10} more\n"
                    result += "\n"
                
                # Removed items
                if changes["removed"]:
                    result += "REMOVED ITEMS:\n"
                    result += "-" * 60 + "\n"
                    for section, items in changes["removed"].items():
                        result += f"\n{section.upper()}:\n"
                        for item_id, item_data in list(items.items())[:10]:
                            title = item_data.get('title', 'Unknown')
                            result += f"  [{item_id}] {title}\n"
                        if len(items) > 10:
                            result += f"  ... and {len(items) - 10} more\n"
                    result += "\n"
                
                self.compare_results_textbox.insert("1.0", result)
            
            # Disable textbox after updating
            self.compare_results_textbox.configure(state="disabled")
                
            # Save modified config
                if messagebox.askyesno("Save Modified Config?", 
                    "Do you want to save a modified config with preOwned: true added to new items?"):
                    modified_config = self.comparator.create_modified_config(new_config, changes)
                    
                    save_path = filedialog.asksaveasfilename(
                        defaultextension=".json",
                        filetypes=[("JSON files", "*.json")],
                        initialfile="modified_storeConfig.json"
                    )
                    
                    if save_path:
                        with open(save_path, 'w', encoding='utf-8') as f:
                            json.dump(modified_config, f, indent=2, ensure_ascii=False)
                        messagebox.showinfo("Success", f"Modified config saved to:\n{save_path}")
                        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to compare configs:\n{str(e)}")
            
    def modify_config(self):
        """Modify config by item IDs"""
        if not self.modify_config_path:
            messagebox.showerror("Error", "Please select a config file!")
            return
            
        item_ids_str = self.item_ids_entry.get().strip()
        if not item_ids_str:
            messagebox.showerror("Error", "Please enter item IDs!")
            return
            
        try:
            # Parse item IDs
            if ',' in item_ids_str:
                item_ids = [id.strip() for id in item_ids_str.split(',')]
            else:
                item_ids = item_ids_str.split()
            
            item_ids = [id for id in item_ids if id]
            
            if not item_ids:
                messagebox.showerror("Error", "No valid item IDs provided!")
                return
            
            # Load config
            with open(self.modify_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Modify config
            modified_config, modified_items, not_found = self.comparator.modify_config_by_ids(config, item_ids)
            
            # Display results (enable textbox, update, then disable)
            self.modify_results_textbox.configure(state="normal")
            self.modify_results_textbox.delete("1.0", "end")
            
            result = "=" * 60 + "\n"
            result += "MODIFICATION RESULTS\n"
            result += "=" * 60 + "\n\n"
            
            if modified_items:
                result += f"✓ Successfully modified {len(modified_items)} items:\n\n"
                for item in modified_items[:20]:
                    result += f"  • {item}\n"
                if len(modified_items) > 20:
                    result += f"  ... and {len(modified_items) - 20} more\n"
                result += "\n"
            
            if not_found:
                result += f"⚠ {len(not_found)} items not found:\n"
                result += f"  {', '.join(not_found)}\n"
            
            self.modify_results_textbox.insert("1.0", result)
            # Disable textbox after updating
            self.modify_results_textbox.configure(state="disabled")
            
            # Save modified config
            if modified_items:
                if messagebox.askyesno("Save Modified Config?", 
                    f"Successfully modified {len(modified_items)} items. Save the file?"):
                    save_path = filedialog.asksaveasfilename(
                        defaultextension=".json",
                        filetypes=[("JSON files", "*.json")],
                        initialfile="modified_storeConfig.json"
                    )
                    
                    if save_path:
                        with open(save_path, 'w', encoding='utf-8') as f:
                            json.dump(modified_config, f, indent=2, ensure_ascii=False)
                        messagebox.showinfo("Success", f"Modified config saved to:\n{save_path}")
            else:
                messagebox.showwarning("No Modifications", "No items were modified!")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to modify config:\n{str(e)}")
            
    def refresh_logs(self):
        """Refresh log display"""
        self.logs_textbox.delete("1.0", "end")
        
        if os.path.exists('bot.log'):
            try:
                with open('bot.log', 'r', encoding='utf-8') as f:
                    logs = f.read()
                    self.logs_textbox.insert("1.0", logs)
                    self.logs_textbox.see("end")
            except Exception as e:
                self.logs_textbox.insert("1.0", f"Error reading log file: {str(e)}")
        else:
            self.logs_textbox.insert("1.0", "No log file found.")
            
    def clear_logs(self):
        """Clear the log file"""
        if messagebox.askyesno("Clear Logs?", "Are you sure you want to clear all logs?"):
            if os.path.exists('bot.log'):
                try:
                    with open('bot.log', 'w', encoding='utf-8') as f:
                        f.write("")
                    self.logs_textbox.delete("1.0", "end")
                    self.logs_textbox.insert("1.0", "Logs cleared.")
                    messagebox.showinfo("Success", "Logs cleared successfully!")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to clear logs: {str(e)}")
                    
    def change_appearance_mode(self, new_mode: str):
        """Change appearance mode dynamically without restart"""
        ctk.set_appearance_mode(new_mode.lower())
        # Force update all widgets
        self.update()
        self.update_idletasks()
        
    def on_closing(self):
        """Handle window closing"""
        self.auto_check_running = False
        
        # Shutdown Discord bot if running
        if self.discord_bot and self.discord_enabled:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.discord_bot.close())
                loop.close()
            except:
                pass
        
        self.destroy()

def main():
    app = FR4LeakingToolGUI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

if __name__ == "__main__":
    main()

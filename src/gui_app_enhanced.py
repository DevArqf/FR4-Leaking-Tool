"""
Fun Run 4 Leaking Tool - Enhanced GUI with Modern Features
Beautiful, animated, colorful interface with advanced UX
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox, Canvas
import asyncio
import threading
import json
import os
from datetime import datetime, timezone
import logging
from logging.handlers import RotatingFileHandler
import sys
sys.path.append(os.path.dirname(__file__))
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

# Modern Color Palette
class Colors:
    # Primary Colors
    PRIMARY = "#6366f1"  # Vibrant indigo
    PRIMARY_DARK = "#4f46e5"
    PRIMARY_LIGHT = "#818cf8"
    
    # Accent Colors
    ACCENT = "#ec4899"  # Pink
    SUCCESS = "#10b981"  # Green
    WARNING = "#f59e0b"  # Orange
    ERROR = "#ef4444"  # Red
    INFO = "#3b82f6"  # Blue
    
    # Background Colors (Dark Theme)
    BG_DARK = "#0f172a"  # Slate 900
    BG_CARD_DARK = "#1e293b"  # Slate 800
    BG_HOVER_DARK = "#334155"  # Slate 700
    
    # Background Colors (Light Theme)
    BG_LIGHT = "#f8fafc"  # Slate 50
    BG_CARD_LIGHT = "#ffffff"
    BG_HOVER_LIGHT = "#e2e8f0"  # Slate 200
    
    # Text Colors
    TEXT_PRIMARY = "#f1f5f9"
    TEXT_SECONDARY = "#94a3b8"
    TEXT_DARK = "#0f172a"
    
    # Gradients
    GRADIENT_START = "#6366f1"
    GRADIENT_END = "#ec4899"

# Enhanced CustomTkinter theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AnimatedProgressBar(ctk.CTkFrame):
    """Custom animated progress bar with gradient"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.progress = 0
        self.configure(height=8, fg_color="transparent")
        
        self.canvas = Canvas(self, height=8, bg=Colors.BG_CARD_DARK, highlightthickness=0)
        self.canvas.pack(fill="x", expand=True)
        
        self.progress_bar = self.canvas.create_rectangle(
            0, 0, 0, 8, fill=Colors.PRIMARY, outline=""
        )
        
    def set(self, value):
        """Set progress value (0-1)"""
        self.progress = max(0, min(1, value))
        width = self.canvas.winfo_width()
        self.canvas.coords(self.progress_bar, 0, 0, width * self.progress, 8)
        
    def animate_to(self, target_value, steps=20):
        """Animate progress to target value"""
        def animate_step(current_step=0):
            if current_step >= steps:
                self.set(target_value)
                return
            
            progress = self.progress + (target_value - self.progress) * (current_step / steps)
            self.set(progress)
            self.after(20, lambda: animate_step(current_step + 1))
        
        animate_step()

class StatusBadge(ctk.CTkFrame):
    """Animated status badge with pulsing effect"""
    def __init__(self, master, text="", status="idle", **kwargs):
        super().__init__(master, corner_radius=20, **kwargs)
        self.status = status
        self.pulsing = False
        
        self.indicator = ctk.CTkLabel(
            self, text="●", font=("Arial", 16),
            text_color=self.get_status_color()
        )
        self.indicator.pack(side="left", padx=(10, 5))
        
        self.label = ctk.CTkLabel(
            self, text=text, font=("Arial", 12, "bold")
        )
        self.label.pack(side="left", padx=(0, 10))
        
        self.update_status(status)
    
    def get_status_color(self):
        colors = {
            "online": Colors.SUCCESS,
            "offline": Colors.TEXT_SECONDARY,
            "checking": Colors.WARNING,
            "error": Colors.ERROR,
            "idle": Colors.INFO
        }
        return colors.get(self.status, Colors.INFO)
    
    def update_status(self, status):
        """Update badge status with animation"""
        self.status = status
        color = self.get_status_color()
        self.indicator.configure(text_color=color)
        
        if status == "checking":
            self.start_pulse()
        else:
            self.stop_pulse()
    
    def start_pulse(self):
        """Start pulsing animation"""
        self.pulsing = True
        self.pulse_animation()
    
    def stop_pulse(self):
        """Stop pulsing animation"""
        self.pulsing = False
    
    def pulse_animation(self, alpha=1.0, direction=-0.1):
        """Pulse animation effect"""
        if not self.pulsing:
            return
        
        alpha += direction
        if alpha <= 0.3:
            alpha, direction = 0.3, 0.1
        elif alpha >= 1.0:
            alpha, direction = 1.0, -0.1
        
        # Update opacity would go here (customtkinter limitation)
        self.after(50, lambda: self.pulse_animation(alpha, direction))

class ModernCard(ctk.CTkFrame):
    """Modern card with hover effects and shadows"""
    def __init__(self, master, title="", **kwargs):
        super().__init__(
            master,
            corner_radius=15,
            fg_color=Colors.BG_CARD_DARK,
            **kwargs
        )
        
        # Title
        if title:
            title_label = ctk.CTkLabel(
                self, text=title,
                font=("Arial", 18, "bold"),
                text_color=Colors.TEXT_PRIMARY
            )
            title_label.pack(anchor="w", padx=20, pady=(20, 10))
        
        # Content frame
        self.content = ctk.CTkFrame(
            self, fg_color="transparent"
        )
        self.content.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Hover effects
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
    
    def on_hover(self, event):
        self.configure(fg_color=Colors.BG_HOVER_DARK)
    
    def on_leave(self, event):
        self.configure(fg_color=Colors.BG_CARD_DARK)

class TooltipLabel(ctk.CTkLabel):
    """Label with tooltip on hover"""
    def __init__(self, master, tooltip_text="", **kwargs):
        super().__init__(master, **kwargs)
        self.tooltip_text = tooltip_text
        self.tooltip_window = None
        
        self.bind("<Enter>", self.show_tooltip)
        self.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event):
        if self.tooltip_text and not self.tooltip_window:
            x = self.winfo_rootx() + 20
            y = self.winfo_rooty() + 20
            
            self.tooltip_window = ctk.CTkToplevel(self)
            self.tooltip_window.wm_overrideredirect(True)
            self.tooltip_window.wm_geometry(f"+{x}+{y}")
            
            label = ctk.CTkLabel(
                self.tooltip_window,
                text=self.tooltip_text,
                fg_color=Colors.BG_CARD_DARK,
                corner_radius=8,
                padx=10,
                pady=5
            )
            label.pack()
    
    def hide_tooltip(self, event):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

class FR4EnhancedGUI(ctk.CTk):
    """Enhanced Fun Run 4 Leaking Tool GUI"""
    
    def __init__(self):
        super().__init__()
        
        # Window configuration
        self.title("FR4 Leaking Tool - Enhanced Edition")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        
        # Set window icon
        try:
            icon_path = "../assets/logo_128.png"
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except:
            pass
        
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
        
        # Current theme
        self.current_theme = "dark"
        
        # Create UI
        self.create_modern_layout()
        
        # Start Discord bot if configured
        if self.discord_config.get('discord_token') and self.discord_config.get('channel_id'):
            self.start_discord_bot()
        
        # Update displays
        self.update_version_display()
        self.update_connection_status()
    
    def load_discord_config(self):
        """Load Discord configuration"""
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load Discord config: {e}")
        return {}
    
    def create_modern_layout(self):
        """Create modern UI layout"""
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar with gradient effect
        self.create_modern_sidebar()
        
        # Create main content area
        self.create_main_content_area()
        
        # Create status bar at bottom
        self.create_status_bar()
    
    def create_modern_sidebar(self):
        """Create modern sidebar with gradient and animations"""
        self.sidebar = ctk.CTkFrame(
            self,
            width=280,
            corner_radius=0,
            fg_color=Colors.BG_CARD_DARK
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew", rowspan=2)
        self.sidebar.grid_propagate(False)
        
        # Logo section with gradient background
        logo_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color=Colors.PRIMARY,
            corner_radius=0,
            height=120
        )
        logo_frame.pack(fill="x", pady=(0, 20))
        logo_frame.pack_propagate(False)
        
        # App title
        title = ctk.CTkLabel(
            logo_frame,
            text="🎮 FR4 Tool",
            font=("Arial", 28, "bold"),
            text_color="white"
        )
        title.pack(pady=(30, 5))
        
        version = ctk.CTkLabel(
            logo_frame,
            text="Enhanced Edition v2.0",
            font=("Arial", 12),
            text_color=Colors.PRIMARY_LIGHT
        )
        version.pack()
        
        # Connection status badge
        self.status_badge = StatusBadge(
            self.sidebar,
            text="Initializing...",
            status="idle",
            fg_color=Colors.BG_DARK
        )
        self.status_badge.pack(pady=15, padx=20, fill="x")
        
        # Navigation buttons with icons and hover effects
        nav_buttons = [
            ("📊 Monitor", self.show_monitor_tab, Colors.PRIMARY),
            ("🔄 Compare", self.show_compare_tab, Colors.INFO),
            ("✏️ Modify", self.show_modify_tab, Colors.WARNING),
            ("📝 Logs", self.show_logs_tab, Colors.ACCENT),
        ]
        
        self.nav_buttons = []
        for text, command, color in nav_buttons:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                height=50,
                font=("Arial", 14, "bold"),
                fg_color="transparent",
                hover_color=Colors.BG_HOVER_DARK,
                anchor="w",
                corner_radius=10
            )
            btn.pack(pady=8, padx=20, fill="x")
            self.nav_buttons.append(btn)
        
        # Spacer
        ctk.CTkFrame(self.sidebar, fg_color="transparent", height=20).pack(expand=True)
        
        # Theme selector
        theme_label = ctk.CTkLabel(
            self.sidebar,
            text="Theme",
            font=("Arial", 12, "bold"),
            text_color=Colors.TEXT_SECONDARY
        )
        theme_label.pack(pady=(10, 5), padx=20, anchor="w")
        
        self.theme_selector = ctk.CTkSegmentedButton(
            self.sidebar,
            values=["Dark", "Light", "Auto"],
            command=self.change_theme_live,
            selected_color=Colors.PRIMARY,
            selected_hover_color=Colors.PRIMARY_DARK
        )
        self.theme_selector.set("Dark")
        self.theme_selector.pack(pady=(0, 20), padx=20, fill="x")
    
    def create_main_content_area(self):
        """Create main content area with tabs"""
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color=Colors.BG_DARK,
            corner_radius=0
        )
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Create tab frames
        self.monitor_tab = self.create_monitor_tab()
        self.compare_tab = self.create_compare_tab()
        self.modify_tab = self.create_modify_tab()
        self.logs_tab = self.create_logs_tab()
        
        # Show default tab
        self.show_monitor_tab()
    
    def create_status_bar(self):
        """Create animated status bar at bottom"""
        self.status_bar = ctk.CTkFrame(
            self,
            height=40,
            fg_color=Colors.BG_CARD_DARK,
            corner_radius=0
        )
        self.status_bar.grid(row=1, column=1, sticky="ew", padx=0, pady=0)
        
        # Status text
        self.status_text = ctk.CTkLabel(
            self.status_bar,
            text="Ready",
            font=("Arial", 11),
            text_color=Colors.TEXT_SECONDARY
        )
        self.status_text.pack(side="left", padx=20)
        
        # Progress bar
        self.status_progress = AnimatedProgressBar(self.status_bar)
        self.status_progress.pack(side="right", padx=20, fill="x", expand=True)
    
    # Continued in next part...
    
    def create_monitor_tab(self):
        """Create enhanced monitor tab"""
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        
        # Header with gradient
        header = ModernCard(frame, title="")
        header.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(
            header.content,
            text="Update Monitor",
            font=("Arial", 32, "bold"),
            text_color=Colors.PRIMARY
        )
        title.pack(anchor="w")
        
        subtitle = ctk.CTkLabel(
            header.content,
            text="Monitor Fun Run 4 updates in real-time",
            font=("Arial", 14),
            text_color=Colors.TEXT_SECONDARY
        )
        subtitle.pack(anchor="w", pady=(5, 0))
        
        # Version info card
        version_card = ModernCard(frame, title="Current Version")
        version_card.pack(fill="x", pady=(0, 15))
        
        self.version_label = ctk.CTkLabel(
            version_card.content,
            text="Not detected",
            font=("Arial", 24, "bold"),
            text_color=Colors.PRIMARY_LIGHT
        )
        self.version_label.pack()
        
        self.last_check_label = ctk.CTkLabel(
            version_card.content,
            text="Never checked",
            font=("Arial", 12),
            text_color=Colors.TEXT_SECONDARY
        )
        self.last_check_label.pack(pady=(5, 0))
        
        # Control buttons
        controls_card = ModernCard(frame, title="Controls")
        controls_card.pack(fill="x", pady=(0, 15))
        
        button_frame = ctk.CTkFrame(controls_card.content, fg_color="transparent")
        button_frame.pack(fill="x")
        
        self.check_now_btn = ctk.CTkButton(
            button_frame,
            text="🔍 Check Now",
            command=self.check_update_manual,
            height=50,
            font=("Arial", 14, "bold"),
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_DARK
        )
        self.check_now_btn.pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        self.auto_check_btn = ctk.CTkButton(
            button_frame,
            text="▶️ Start Auto-Check",
            command=self.toggle_auto_check,
            height=50,
            font=("Arial", 14, "bold"),
            fg_color=Colors.SUCCESS,
            hover_color="#059669"
        )
        self.auto_check_btn.pack(side="left", expand=True, fill="x", padx=(10, 0))
        
        reset_btn = ctk.CTkButton(
            controls_card.content,
            text="🔄 Reset Version Data",
            command=self.reset_version,
            height=40,
            font=("Arial", 12),
            fg_color=Colors.ERROR,
            hover_color="#dc2626"
        )
        reset_btn.pack(fill="x", pady=(10, 0))
        
        # Activity log
        log_card = ModernCard(frame, title="Activity Log")
        log_card.pack(fill="both", expand=True)
        
        self.status_textbox = ctk.CTkTextbox(
            log_card.content,
            font=("Consolas", 11),
            fg_color=Colors.BG_DARK,
            corner_radius=10,
            wrap="word"
        )
        self.status_textbox.pack(fill="both", expand=True)
        
        return frame
    
    def create_compare_tab(self):
        """Create enhanced compare tab - placeholder for now"""
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        
        label = ctk.CTkLabel(
            frame,
            text="Compare Tab - Enhanced UI Coming",
            font=("Arial", 24)
        )
        label.pack(expand=True)
        
        return frame
    
    def create_modify_tab(self):
        """Create enhanced modify tab - placeholder for now"""
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        
        label = ctk.CTkLabel(
            frame,
            text="Modify Tab - Enhanced UI Coming",
            font=("Arial", 24)
        )
        label.pack(expand=True)
        
        return frame
    
    def create_logs_tab(self):
        """Create enhanced logs tab - placeholder for now"""
        frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        
        label = ctk.CTkLabel(
            frame,
            text="Logs Tab - Enhanced UI Coming",
            font=("Arial", 24)
        )
        label.pack(expand=True)
        
        return frame
    
    # Tab switching with animations
    def show_monitor_tab(self):
        """Show monitor tab with animation"""
        self.hide_all_tabs()
        self.monitor_tab.pack(fill="both", expand=True)
        self.highlight_nav_button(0)
    
    def show_compare_tab(self):
        """Show compare tab"""
        self.hide_all_tabs()
        self.compare_tab.pack(fill="both", expand=True)
        self.highlight_nav_button(1)
    
    def show_modify_tab(self):
        """Show modify tab"""
        self.hide_all_tabs()
        self.modify_tab.pack(fill="both", expand=True)
        self.highlight_nav_button(2)
    
    def show_logs_tab(self):
        """Show logs tab"""
        self.hide_all_tabs()
        self.logs_tab.pack(fill="both", expand=True)
        self.highlight_nav_button(3)
    
    def hide_all_tabs(self):
        """Hide all tab frames"""
        for tab in [self.monitor_tab, self.compare_tab, self.modify_tab, self.logs_tab]:
            tab.pack_forget()
    
    def highlight_nav_button(self, index):
        """Highlight active navigation button"""
        colors = [Colors.PRIMARY, Colors.INFO, Colors.WARNING, Colors.ACCENT]
        for i, btn in enumerate(self.nav_buttons):
            if i == index:
                btn.configure(fg_color=colors[i], text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=Colors.TEXT_SECONDARY)
    
    def change_theme_live(self, value):
        """Change theme without restart"""
        theme_map = {"Dark": "dark", "Light": "light", "Auto": "system"}
        ctk.set_appearance_mode(theme_map[value])
        self.current_theme = value.lower()
        
        # Update colors based on theme
        if value == "Light":
            self.update_colors_light()
        else:
            self.update_colors_dark()
        
        self.update()
        self.update_idletasks()
    
    def update_colors_light(self):
        """Update to light theme colors"""
        # This would update all color references
        pass
    
    def update_colors_dark(self):
        """Update to dark theme colors"""
        pass
    
    # Discord and monitoring functions (simplified for now)
    def start_discord_bot(self):
        """Start Discord bot"""
        self.add_status_log("Starting Discord bot...")
        self.status_badge.update_status("checking")
        # Implementation from original
    
    def update_version_display(self):
        """Update version display"""
        version = self.monitor.current_version or "Not detected"
        self.version_label.configure(text=version)
        
        last_check = self.monitor.last_check or "Never"
        if last_check != "Never":
            try:
                dt = datetime.fromisoformat(last_check.replace('Z', '+00:00'))
                last_check = dt.strftime("%Y-%m-%d %H:%M:%S")
            except:
                pass
        self.last_check_label.configure(text=f"Last check: {last_check}")
    
    def update_connection_status(self):
        """Update connection status badge"""
        if self.discord_enabled:
            self.status_badge.label.configure(text="Connected")
            self.status_badge.update_status("online")
        else:
            self.status_badge.label.configure(text="Disconnected")
            self.status_badge.update_status("offline")
    
    def add_status_log(self, message):
        """Add message to status log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_textbox.insert("end", f"[{timestamp}] {message}\n")
        self.status_textbox.see("end")
        
        # Update status bar
        self.status_text.configure(text=message)
    
    def check_update_manual(self):
        """Check for updates manually"""
        self.add_status_log("Checking for updates...")
        self.status_badge.update_status("checking")
        self.status_progress.animate_to(0.5)
        # Implementation continues...
    
    def toggle_auto_check(self):
        """Toggle auto-check"""
        if not self.auto_check_running:
            self.auto_check_running = True
            self.auto_check_btn.configure(
                text="⏸️ Stop Auto-Check",
                fg_color=Colors.ERROR
            )
            self.add_status_log("Auto-check started (15 min interval)")
        else:
            self.auto_check_running = False
            self.auto_check_btn.configure(
                text="▶️ Start Auto-Check",
                fg_color=Colors.SUCCESS
            )
            self.add_status_log("Auto-check stopped")
    
    def reset_version(self):
        """Reset version data"""
        if messagebox.askyesno("Confirm Reset", "Reset version data?"):
            self.monitor.reset_version()
            self.monitor.current_version = None
            self.monitor.last_check = None
            self.update_version_display()
            self.add_status_log("✓ Version data reset")
    
    def on_closing(self):
        """Handle window closing"""
        self.auto_check_running = False
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
    app = FR4EnhancedGUI()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()

if __name__ == "__main__":
    main()

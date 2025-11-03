"""
Uptodown Monitor Module
Handles checking for Fun Run 4 updates on Uptodown
"""
import os
import json
import aiohttp
from datetime import datetime, timezone
from typing import Tuple, Optional
from google_play_scraper import app
import logging

logger = logging.getLogger(__name__)

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

class StoreMonitor:
    def __init__(self, package_name: str, app_store_id: Optional[str] = None):
        """
        Initialize the store monitor.
        
        Args:
            package_name: Google Play package name (e.g., 'com.dirtybit.fra')
            app_store_id: iOS App Store ID (optional, e.g., '1451163837')
        """
        self.version_file = "version_data.json"
        self.package_name = package_name
        self.app_store_id = app_store_id
        self.current_versions = {
            'play_store': None,
            'app_store': None
        }
        self.last_check = None
        self.load_version_data()
    
    def load_version_data(self):
        """Load the last known versions from disk"""
        try:
            if os.path.exists(self.version_file):
                with open(self.version_file, 'r') as f:
                    data = json.load(f)
                    self.current_versions = data.get('versions', {
                        'play_store': None,
                        'app_store': None
                    })
                    self.last_check = data.get('last_check')
                    logger.info(f"Loaded version data: Play Store={self.current_versions.get('play_store')}, App Store={self.current_versions.get('app_store')} (last check: {self.last_check})")
            else:
                logger.info("No version data file found, starting fresh")
        except Exception as e:
            logger.error(f"Error loading version data: {str(e)}")
    
    def save_version_data(self):
        """Save the current version data to disk"""
        try:
            data = {
                'versions': self.current_versions,
                'last_check': datetime.now(timezone.utc).isoformat()
            }
            with open(self.version_file, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Saved version data: {self.current_versions}")
        except Exception as e:
            logger.error(f"Error saving version data: {str(e)}")
    
    async def get_play_store_version(self) -> Optional[str]:
        """Get the current version from Google Play Store"""
        try:
            result = app(self.package_name, lang='en', country='us')
            version = result.get('version')
            logger.info(f"Play Store version: {version}")
            return version
        except Exception as e:
            logger.error(f"Error getting Play Store version: {str(e)}")
            return None
    
    async def get_app_store_version(self) -> Optional[str]:
        """Get the current version from iOS App Store"""
        if not self.app_store_id:
            return None
        
        try:
            url = f"https://itunes.apple.com/lookup?id={self.app_store_id}"
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        logger.warning(f"Failed to fetch from App Store. Status: {response.status}")
                        return None
                    
                    data = await response.json()
                    if data.get('resultCount', 0) > 0:
                        version = data['results'][0].get('version')
                        logger.info(f"App Store version: {version}")
                        return version
                    else:
                        logger.warning("No results found for App Store ID")
                        return None
        except Exception as e:
            logger.error(f"Error getting App Store version: {str(e)}")
            return None
    
    async def check_store_updates(self) -> dict:
        """
        Check both stores for updates.
        Returns: dict with update information for each store
        """
        results = {
            'play_store': {'has_update': False, 'new_version': None, 'info': None},
            'app_store': {'has_update': False, 'new_version': None, 'info': None}
        }
        
        # Check Play Store
        play_version = await self.get_play_store_version()
        if play_version:
            if self.current_versions['play_store'] is None:
                # First time detection
                self.current_versions['play_store'] = play_version
                results['play_store'] = {
                    'has_update': False,
                    'new_version': play_version,
                    'info': f"Initial Play Store version detected: {play_version}"
                }
                logger.info(f"Initial Play Store version detected: {play_version}")
            elif play_version != self.current_versions['play_store']:
                # New version detected
                old_version = self.current_versions['play_store']
                self.current_versions['play_store'] = play_version
                results['play_store'] = {
                    'has_update': True,
                    'new_version': play_version,
                    'info': f"Play Store version updated from {old_version} to {play_version}"
                }
                logger.info(f"New Play Store version detected: {old_version} -> {play_version}")
            else:
                results['play_store'] = {
                    'has_update': False,
                    'new_version': play_version,
                    'info': "No Play Store update available"
                }
        else:
            results['play_store']['info'] = "Could not retrieve Play Store version"
        
        # Check App Store
        if self.app_store_id:
            app_version = await self.get_app_store_version()
            if app_version:
                if self.current_versions['app_store'] is None:
                    # First time detection
                    self.current_versions['app_store'] = app_version
                    results['app_store'] = {
                        'has_update': False,
                        'new_version': app_version,
                        'info': f"Initial App Store version detected: {app_version}"
                    }
                    logger.info(f"Initial App Store version detected: {app_version}")
                elif app_version != self.current_versions['app_store']:
                    # New version detected
                    old_version = self.current_versions['app_store']
                    self.current_versions['app_store'] = app_version
                    results['app_store'] = {
                        'has_update': True,
                        'new_version': app_version,
                        'info': f"App Store version updated from {old_version} to {app_version}"
                    }
                    logger.info(f"New App Store version detected: {old_version} -> {app_version}")
                else:
                    results['app_store'] = {
                        'has_update': False,
                        'new_version': app_version,
                        'info': "No App Store update available"
                    }
            else:
                results['app_store']['info'] = "Could not retrieve App Store version"
        
        # Save version data after checking
        self.save_version_data()
        
        return results
    
    async def check_update(self) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Legacy method to maintain compatibility with old code.
        Checks Play Store only and returns in the old format.
        Returns: (has_update, new_version, update_info)
        """
        play_version = await self.get_play_store_version()
        
        if play_version:
            if self.current_versions['play_store'] is None:
                self.current_versions['play_store'] = play_version
                self.save_version_data()
                logger.info(f"Initial version detected: {play_version}")
                return False, play_version, "Initial version detection"
            
            if play_version != self.current_versions['play_store']:
                old_version = self.current_versions['play_store']
                self.current_versions['play_store'] = play_version
                self.save_version_data()
                logger.info(f"New version detected: {old_version} -> {play_version}")
                return True, play_version, f"Version updated from {old_version} to {play_version}"
            
            return False, play_version, "No update available"
        else:
            logger.warning("Could not retrieve version information from Play Store")
            return False, None, "Could not retrieve version information"


# Example usage:
# For Fun Run 4
# monitor = StoreMonitor(
#     package_name='com.dirtybit.fra',  # Fun Run 4 package name
#     app_store_id='1451163837'         # Fun Run 4 App Store ID (optional)
# )
# results = await monitor.check_store_updates()
    
    def reset_version(self):
        """Reset version data for testing"""
        self.current_version = None
        if os.path.exists(self.version_file):
            os.remove(self.version_file)
        logger.info("Version data reset")

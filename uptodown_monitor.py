"""
Uptodown Monitor Module
Handles checking for Fun Run 4 updates on Uptodown
"""
import aiohttp
import re
import json
import os
from datetime import datetime, timezone
from typing import Tuple, Optional
import logging

logger = logging.getLogger('funrun_monitor')

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

class UptodownMonitor:
    def __init__(self, version_file="version_data.json"):
        self.version_file = version_file
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
            urls_to_try = [
                "https://fun-run-4.en.uptodown.com/android/download",
                "https://fun-run-4.en.uptodown.com/android",
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
                        version_patterns = [
                            r'Fun Run 4\s+([\d\.]+)',
                            r'Version\s*([\d\.]+)',
                            r'([\d]+\.[\d]+\.[\d]+)',
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
                                cleaned_version = re.sub(r'[^\d\.]', '', raw_version)
                                if cleaned_version and len(cleaned_version) > 0:
                                    found_version = cleaned_version
                                    break
                        
                        if found_version:
                            if latest_version is None or compare_versions(found_version, latest_version) > 0:
                                latest_version = found_version
                                latest_version_source = url
                                logger.info(f"Found higher version: {latest_version} from {url}")
                    
                if latest_version:
                    logger.info(f"Found version on Uptodown: {latest_version} from {latest_version_source}")
                    
                    if self.current_version is None:
                        self.current_version = latest_version
                        self.save_version_data()
                        logger.info(f"Initial version detected: {latest_version}")
                        return False, latest_version, "Initial version detection"
                    
                    if latest_version != self.current_version:
                        old_version = self.current_version
                        self.current_version = latest_version
                        self.save_version_data()
                        logger.info(f"New version detected: {old_version} -> {latest_version}")
                        return True, latest_version, f"Version updated from {old_version} to {latest_version}"
                    
                    return False, latest_version, "No update available"
                else:
                    logger.warning("Could not extract version information from any Uptodown page")
                    return False, None, "Could not extract version information"
                        
        except Exception as e:
            logger.error(f"Error checking Uptodown: {str(e)}")
            return False, None, f"Error: {str(e)}"
    
    def reset_version(self):
        """Reset version data for testing"""
        self.current_version = None
        if os.path.exists(self.version_file):
            os.remove(self.version_file)
        logger.info("Version data reset")

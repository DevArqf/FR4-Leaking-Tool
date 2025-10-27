"""
Config Comparator Module
Handles comparison and modification of storeConfig.json files
"""
import json
from typing import Dict, Any
import logging

logger = logging.getLogger('funrun_monitor')

class ConfigComparator:
    def __init__(self):
        self.sections_to_compare = ["animals", "skins", "hats", "glasses", "chests", "feet", "powerups"]
    
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
        
        for section in self.sections_to_compare:
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
        for section in self.sections_to_compare:
            if section in modified_config:
                for item_id, item_data in modified_config[section].items():
                    if isinstance(item_data, dict) and item_data.get("hidden") is True:
                        modified_config[section][item_id]["hidden"] = False
        
        return modified_config
    
    def modify_config_by_ids(self, config: Dict, item_ids: list) -> tuple:
        """
        Apply preOwned: true to specific item IDs in config.
        Returns: (modified_config, modified_items, not_found_items)
        """
        modified_config = json.loads(json.dumps(config))  # Deep copy
        modified_items = []
        not_found_items = []
        
        for item_id in item_ids:
            found = False
            for section in self.sections_to_compare:
                if section in modified_config and item_id in modified_config[section]:
                    modified_config[section][item_id]["preOwned"] = True
                    item_title = modified_config[section][item_id].get('title', 'Unknown')
                    modified_items.append(f"{item_id}: {item_title} ({section})")
                    found = True
                    break
            
            if not found:
                not_found_items.append(item_id)
        
        return modified_config, modified_items, not_found_items

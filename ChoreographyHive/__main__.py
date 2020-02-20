"""RLBotChoreography

Usage:
    choreograph [--min-bots=<min>] [--bot-folder=<folder>]

Options:
    --min-bots=<min>             The minimum number of bots to spawn [default: 10].
    --bot-folder=<folder>        Searches this folder for bot configs to use for names and appearances [default: .].
"""

import traceback
import time

try:
	import copy
	import os
	import sys
	from docopt import docopt

	from rlbot.matchconfig.conversions import parse_match_config
	from rlbot.parsing.agent_config_parser import load_bot_appearance
	from rlbot.parsing.directory_scanner import scan_directory_for_bot_configs
	from rlbot.parsing.rlbot_config_parser import create_bot_config_layout
	from rlbot.setup_manager import SetupManager
	from rlbot.utils.structures.start_match_structures import MAX_PLAYERS

	from hivemind import Hivemind

	if __name__ == '__main__':
		arguments = docopt(__doc__)
		
		min_bots = 16 # min(int(arguments['--min-bots']), MAX_PLAYERS)
		bot_directory = arguments['--bot-folder']
		bundles = scan_directory_for_bot_configs(bot_directory)
		
		# Set up RLBot.cfg
		framework_config = create_bot_config_layout()
		config_location = os.path.join(os.path.dirname(__file__), 'rlbot.cfg')
		framework_config.parse_file(config_location, max_index=MAX_PLAYERS)
		match_config = parse_match_config(framework_config, config_location, {}, {})
		
		looks_configs = {idx: bundle.get_looks_config() for idx, bundle in enumerate(bundles)}
		names = [bundle.name for bundle in bundles]
		
		mc_id = 0
		mc_2_id = 0
		player_id = 0
		
		# Figures out which config is which
		for i, cfg in enumerate(match_config.player_configs):
			loadout = cfg.loadout_config
			
			if loadout.hat_id == 1332:
				if loadout.car_id == 23:
					mc_id = i + 1
				else:
					mc_2_id = i + 1
			else:
				player_id = i + 1
			
			if mc_2_id and mc_id and player_id:
				print("Detected got all ids")
				break
		
		mc_id -= 1
		mc_2_id -= 1
		player_id -= 1
		
		if mc_id < 0:
			mc_config = match_config.player_configs[0]
		else:
			mc_config = match_config.player_configs[mc_id]
			mc_config_2 = match_config.player_configs[mc_2_id]
			player_config = match_config.player_configs[player_id]
		
		match_config.player_configs.clear()
		for i in range(min_bots):
			if mc_2_id >= 0:
				# copied = copy.copy(player_config if i >= 2 else (mc_config_2 if i else mc_config))
				copied = copy.copy(player_config if i >= 1 else mc_config_2)
				if i >= 4:
					c2 = copy.copy(copied.loadout_config)
					c2.boost_id = 32
					copied.loadout_config = c2
			else:
				copied = copy.copy(mc_config)
			match_config.player_configs.append(copied)
		
		manager = SetupManager()
		manager.load_match_config(match_config, {})
		manager.connect_to_game()
		manager.start_match()
		
		hivemind = Hivemind()
		hivemind.start()
		
except Exception as e:
	print("Exception occured")
	time.sleep(1)
	print(traceback.format_exc())
	while True:
		pass

print("end")
time.sleep(2)
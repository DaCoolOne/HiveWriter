from rlbot.agents.base_agent import BaseIndependentAgent
from rlbot.botmanager.bot_helper_process import HelperProcessRequest


class HiveBot(BaseIndependentAgent):
	"""
	This class currently does nothing at all. We don't need it because we'll be
	going outside of the normal RLBot infrastructure. Look in hivemind.py for the good stuff.
	
	It is kept here because the .cfg file is less likely to have issues if
	it points to a valid bot class.
	"""
	
	def run_independently(self, terminate_request_event):
		pass



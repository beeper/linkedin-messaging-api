"""An unofficial API for interacting with LinkedIn Messaging"""

from .api_objects import URN
from .linkedin import ChallengeException, LinkedInMessaging

__title__ = "linkedin_messaging"
__version__ = "0.5.3"
__description__ = "An unofficial API for interacting with LinkedIn Messaging"

__license__ = "Apache License 2.0"

__author__ = "Sumner Evans"
__email__ = "sumner@beeper.com"

__all__ = ("ChallengeException", "LinkedInMessaging", "URN")

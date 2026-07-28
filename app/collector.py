from abc import ABC, abstractmethod


class Collector(ABC):

    @abstractmethod
    def collect(self, context):
        """Method to fetch configuration data"""

    @abstractmethod
    def remediate(self, context):
        """Method to fix issues found by validator"""


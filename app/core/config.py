import random
from datetime import datetime


class Config:
    def __init__(self):
        pass

    def get_run_id(self):
        """
        * method: get_run_id
        * description: method to generate run id
        * return: none
        """
        self.now = datetime.now()
        self.date = self.now.date()
        self.current_time = self.now.strftime("%H%M%S")
        return str(self.date)+"_"+str(self.current_time)+"_"+str(random.randint(100000000, 999999999))
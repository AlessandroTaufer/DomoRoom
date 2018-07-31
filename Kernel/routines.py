#
#   Author: Alessandro Taufer
#   Email: alexander141220@gmail.com
#   Url: https://github.com/AlessandroTaufer
#
import logging
import datetime
from threading import Thread


class RoutinesManager:
    def __init__(self):
        self.logger = logging.getLogger("DomoRoom-routine_manager")  # Default logger
        self.logger.info("Initializing RoutinesManager...")
        self.routines = []  # Routines
        self.enabled = True  # Routine manager status
        Thread(target=self.behaviour, args=()).start()
        self.logger.info("Successfully initialized RoutinesManager")

    def behaviour(self):  # Check if some routines have to run
        while self.enabled:
            for routine in self.routines:
                if routine.time < datetime.datetime.now():
                    try:
                        routine.run()  # TODO manage repeat option
                        self.logger.info("Successfully executed '" + routine.name + "' routine")
                    except:
                        self.logger.error("Failed to run '" + routine.name + "' routine")

    def add_routine(self, name, time, script, repeat=False):  # Add a routine to the routines list
        routine = Routine(name, time, script, repeat)
        self.routines.append(routine)

    def remove_routine(self, id):  # Remove the routine at the current pos/name
        if isinstance(id, basestring):
            for routine in self.routines:
                if routine.name == id:
                    self.routines.remove(routine)
                    self.logger.info("Removed routine: " + id)
                    return True
        else:
            try:
                tmp_routine = self.routines.pop(id)
                self.logger.info("Removed routine " + tmp_routine.name + " at position: " + str(id))
                return True
            except IndexError:
                self.logger.warning("Could not remove the routine")
        return False

    @staticmethod
    def convert_to_datetime(year, month, day, hour, minutes,  second, microsecond):  # Return the corresponding date
        return datetime.datetime(year, month, day, hour, minutes, second, microsecond)


class Routine:
    def __init__(self, name, time, script, repeat=False):
        self.name = name  # Routine's name
        self.time = time  # Next time the routine will run
        self.script = script  # Routine's script
        self.repeat = repeat  # If and how much time later it will repeat the routine

    def run(self):  # Run the routine
        result = self.script()
        return result


if __name__ == "__main__":
    print(str(datetime.datetime.now() - datetime.datetime.now))

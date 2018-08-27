#
#   Author: Alessandro Taufer
#   Email: alexander141220@gmail.com
#   Url: https://github.com/AlessandroTaufer
#
import logging
import datetime
from threading import Thread


class RoutinesManager:
    def __init__(self, parent):
        self.parent = parent  # Class parent
        self.logger = logging.getLogger("DomoRoom-routine_manager")  # Default logger
        self.logger.info("Initializing RoutinesManager...")
        self.routines = []  # Routines
        self.enabled = True  # Routine manager status
        Thread(target=self.behaviour, args=()).start()
        self.logger.info("Successfully initialized RoutinesManager")

    def behaviour(self):  # Check if some routines have to run
        while self.enabled:  # TODO backup routines
            for routine in self.routines:
                if routine.time < datetime.datetime.now():
                    try:
                        routine.run()  # TODO manage repeat option
                        self.remove_routine(routine)
                        self.logger.info("Successfully executed '" + routine.name + "' routine")

                    except:
                        self.logger.error("Failed to run '" + routine.name + "' routine")

    def add_routine(self, name, time, script, script_args=(), repeat=False):  # Add a routine to the routines list
        routine = Routine(name, time, script, script_args, repeat)
        self.routines.append(routine)

    def remove_routine(self, id):  # Remove a routine with the current name/object/pos
        if isinstance(id, basestring):
            for routine in self.routines:
                if routine.name == id:
                    self.routines.remove(routine)
                    self.logger.debug("Removed routine: " + id)
                    return True
        elif isinstance(id, Routine):
            self.routines.remove(id)
            self.logger.debug("Removed routine: " + id.name)
            return True
        else:
            try:
                tmp_routine = self.routines.pop(id)
                self.logger.debug("Removed routine " + tmp_routine.name + " at position: " + str(id))
                return True
            except IndexError:
                self.logger.warning("Could not remove the routine")
        return False

    @staticmethod
    def convert_to_datetime(year, month, day, hour, minutes,  second, microsecond):  # Return the corresponding date
        return datetime.datetime(year, month, day, hour, minutes, second, microsecond)

    # Attach a telegram routine that sends a telegram message when the time occurs
    def attach_telegram_alert_routine(self, routine_name, text, chat_id=-1, time=datetime.datetime.now()):
        script = self.parent.telegram_manager.broadcast_message
        args = []
        if chat_id != -1:
            script = self.parent.telegram_manager.send_message
            args.append(chat_id)
        args.append(text)
        self.add_routine(routine_name, time, script, args)

    def routines_to_string(self):  # Return a string containing the routines names
        if len(self.routines) == 0:
            return "Currently there are not routines"
        txt = "Routines: \n"
        for routine in self.routines:
            txt += routine.name+", \n"
        return txt


class Routine:
    def __init__(self, name, time, script, script_args=(), repeat=False):
        self.name = name  # Routine's name
        self.time = time  # Next time the routine will run
        self.script = script  # Routine's script
        self.script_args = script_args  # Script's arguments
        self.repeat = repeat  # If and how much time later it will repeat the routine

    def run(self):  # Run the routine
        result = self.script(*self.script_args)
        return result


if __name__ == "__main__":
    RoutinesManager(None)

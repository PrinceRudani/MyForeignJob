from datetime import datetime


class DateParseUtils:
    """
    A utility class for date and time parsing and conversion.

    Author: Tarun Mondal
    Designation: Software Engineer
    """

    @staticmethod
    def get_current_epoch():
        create_current_time = datetime.utcnow()
        current_time_epoch = int(
            (create_current_time - datetime(1970, 1, 1)).total_seconds()
        )
        return current_time_epoch

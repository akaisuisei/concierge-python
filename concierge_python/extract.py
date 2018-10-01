from datetime import datetime
import hermes_python

class Extract:

    @staticmethod
    def _getFirst(slots, default, func):
        tmp = func(slots)
        if len (tmp):
            return tmp[0]
        return default

    @staticmethod
    def durations(slots):
        tag = []
        if slots is not None:
            for tmp in slots.all():
                duration = tmp.value
                duration = duration.hours * 3600 + duration.minutes * 60 + duration.seconds
                tag += [duration]
        return tag

    @staticmethod
    def duration(slots, default = ""):
        return Extract._getFirst(slots, default, Extract.durations)

    @staticmethod
    def values(slots):
        tag = []
        if slots is not None:
            for tmp in slots.all():
                tag.append(tmp.value)
        return tag

    @staticmethod
    def value(slots, default = ''):
        return Extract._getFirst(slots, default, Extract.values)

    @staticmethod
    def _str_to_datetime(value):
        value = value[:-7]
        try:
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
        except:
            value = value[:-3]
            return datetime.strptime(value, '%Y-%m-%d %H:%M:%S.%f')
    @staticmethod
    def timeSlots(slots):
        tag = []
        if slots is not None:
            for slot in slots.all():
                value = slot.value
                if type(value) == hermes_python.ontology.TimeIntervalValue :
                    t0 = Extract._str_to_datetime(value.from_date)
                    t1 = Extract._str_to_datetime(value.to_date)
                    delta = t1 - t0
                    tmp = t0 + delta / 2
                    tag.append(tmp)
                if type(value) == hermes_python.ontology.InstantTimeValue :
                    tmp = Extract._str_to_datetime(value.value)
                    tag.append(tmp)
        return tag

    @staticmethod
    def timeSlot(slots, default = None):
        return Extract._getFirst(slots, default, Extract.timeSlots)

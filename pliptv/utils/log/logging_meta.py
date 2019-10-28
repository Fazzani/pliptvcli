import logging


class MetaLoggingBase(type):
    def __init__(cls, *args, **kargs):
        super().__init__(*args, **kargs)

        # Explicit name mangling
        logger_attribute_name = "_" + cls.__name__ + "__logger"

        # Logger name derived accounting for inheritance for the bonus marks
        logger_name = ".".join([c.__name__ for c in cls.mro()[-2::-1]])

        setattr(cls, logger_attribute_name, logging.getLogger(logger_name))

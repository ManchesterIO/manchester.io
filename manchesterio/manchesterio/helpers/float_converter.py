from werkzeug.routing import FloatConverter


class NegativeFloatConverter(FloatConverter):
    regex = r'-?\d+\.\d+'

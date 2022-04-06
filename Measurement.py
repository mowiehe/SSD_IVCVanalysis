class Measurement:

    all_Measurement = []

    def __init__(self, filename, T, device=None, fmt=None, label=None):
        assert type(filename) == str, "Provide filename as str"
        self.filename = filename
        self.device = device
        self.fmt = fmt
        self.label = label
        self.T = T

        self.Type = type(self).__name__

        if device:
            device.add_measurement(self)

        Measurement.all_Measurement.append(self)

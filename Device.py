import pandas as pd
import csv


class Device:

    all_Device = []

    @classmethod
    def instantiate_from_csv(
        cls,
        csv_file,
        ID_column="id",
        area_column="area",
        thickness_column="thickness",
        fluence_column=None,
        annealing_column=None,
        comment="#",
    ):
        new_Devices = []
        # read csv_file
        with open(csv_file) as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["id"][0] == comment:
                    continue
                ID = row[ID_column]
                area = float(row[area_column]) if area_column else None
                thickness = float(row[thickness_column]) if thickness_column else None
                fluence = float(row[fluence_column]) if fluence_column else None
                annealing = int(row[annealing_column]) if annealing_column else None
                kwargs = {
                    key: row[key]
                    for key in row
                    if key
                    not in [
                        ID_column,
                        area_column,
                        thickness_column,
                        fluence_column,
                        annealing_column,
                    ]
                }

                dev = Device(
                    ID=ID,
                    fluence=fluence,
                    annealing=annealing,
                    thickness=thickness,
                    area=area,
                    **kwargs,
                )
                new_Devices.append(dev)
        return new_Devices

    @classmethod
    def get_DataFrame(cls, device_list=None, add_columns=[]):
        if not device_list:
            device_list = cls.all_Device
        df = pd.DataFrame()
        for i, dev in enumerate(device_list):
            default_cols = {
                "ID": dev.ID,
                "fluence": dev.fluence,
                "annealing": dev.annealing,
            }
            additional_cols = {key: getattr(dev, key) for key in add_columns}
            single_df = pd.Series({**default_cols, **additional_cols})
            single_df["Device"] = dev
            df = df.append(single_df, ignore_index=True)
        return df

    @classmethod
    def get_Device(cls, ID, fluence=0, annealing=0):
        dev_list = [dev for dev in cls.all_Device if dev.ID == ID]
        if (
            len(dev_list) > 1
        ):  # select fluence and annealing if device ID not unambiguous
            dev_list = [
                dev
                for dev in dev_list
                if dev.fluence == fluence and dev.annealing == annealing
            ]
        if len(dev_list) > 1:
            raise Exception("Device ID is ambiguous, specify fluence and annealing", ID)
        if len(dev_list) == 0:
            raise Exception("Device not found", ID)

        return dev_list[0]

    def __init__(
        self, ID, fluence=None, annealing=None, area=None, thickness=None, **kwargs
    ):
        assert type(ID) == str, "Device ID as string"
        assert type(fluence) == float or fluence == None, "Fluence as float"
        assert (
            type(annealing) == int or annealing == None
        ), "Annealing time at 60C as integer"
        assert (
            type(area) == float or area == None
        ), "Device active area as float or None"
        assert (
            type(thickness) == float or thickness == None
        ), "Device thickness as float or None"

        self.ID = ID
        self.fluence = fluence  # [neq/cm^2]
        self.annealing = annealing  # min
        self.__dict__.update(kwargs)
        self.measurements = []
        self.area = area  # [cm^2]
        self.thickness = thickness  # [µm]

        Device.all_Device.append(self)

    def add_measurement(self, measurement):
        if measurement.device:
            if measurement.device != self:
                raise Exception(
                    "Add measurement to device: Measurement device is different."
                )
            else:
                self.measurements.append(measurement)
        # set measurement device if not done
        else:
            measurement.device = self
            self.measurements.append(measurement)

    def get_measurement_df(self):
        df = pd.DataFrame()

        for i, measurement in enumerate(self.measurements):
            single_df = pd.DataFrame(
                {
                    "Type": measurement.get_Type(),
                    "filename": measurement.filename,
                    "Measurement": measurement,
                },
                index=[i],
            )
            df = pd.concat([df, single_df])
        return df

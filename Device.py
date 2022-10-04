import pandas as pd
import pdb


class Device:

    all_Device = []

    @classmethod
    def instantiate_from_csv(
        cls,
        csv_file,
        ID_column="ID",
        sep=",",
        comment="#",
        fluence="fluence",
        annealing="annealing",
    ):
        new_Devices = []
        # read csv_file
        dev_info = pd.read_csv(csv_file, sep=sep, dtype="object", comment=comment)
        # fluence and annealing can be specified as float/int of by giving the column name
        if type(fluence) == float:
            fluence_column = "fluence"
            dev_info[fluence_column] = fluence
        else:
            fluence_column = fluence
            dev_info[fluence_column] = dev_info[fluence_column].astype(float)
        if type(annealing) == int:
            annealing_column = "annealing"
            dev_info[annealing_column] = annealing
        else:
            annealing_column = annealing
            dev_info[annealing_column] = dev_info[annealing_column].astype(int)

        # instantiate one device object per row. ID, fluence and annealing are set explicitly, all other keywords are passed as kwargs
        def inst_Device_from_dev_info(x):
            dev = Device(
                ID=x[ID_column],
                fluence=x[fluence_column],
                annealing=x[annealing_column],
                **x.loc[
                    ~(
                        (x.keys() == ID_column)
                        | (x.keys() == fluence_column)
                        | (x.keys() == annealing_column)
                    ),
                ].to_dict(),
            )
            new_Devices.append(dev)
            return dev

        dev_info.apply(
            inst_Device_from_dev_info,
            axis=1,
        )
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
            raise Exception("Device ID is ambiguous, specify fluence and annealing")
        if len(dev_list) == 0:
            raise Exception("Device not found")

        return dev_list[0]

    def __init__(self, ID, fluence, annealing, **kwargs):
        assert type(ID) == str, "Device ID as string"
        assert type(fluence) == float, "Fluence as float"
        assert type(annealing) == int, "Annealing time at 60C as integer"

        self.ID = ID
        self.fluence = fluence
        self.annealing = annealing
        self.__dict__.update(kwargs)
        self.measurements = []

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

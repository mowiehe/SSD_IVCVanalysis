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
        # read csv_file
        dev_info = pd.read_csv(csv_file, sep=sep, dtype="object", comment=comment)
        # fluence and annealing can be specified as float/int of by giving the column name
        if type(fluence) == float:
            fluence_column = "fluence"
            dev_info[fluence_column] = fluence
        else:
            fluence_column = fluence
        if type(annealing) == int:
            annealing_column = "annealing"
            dev_info[annealing_column] = annealing
        else:
            annealing_column = annealing

        # instantiate one device object per row. ID, fluence and annealing are set explicitly, all other keywords are passed as kwargs
        dev_info.apply(
            lambda x: Device(
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
            ),
            axis=1,
        )

    @classmethod
    def get_DataFrame(cls, add_columns=[]):
        df = pd.DataFrame()
        for i, dev in enumerate(cls.all_Device):
            default_cols = {
                "ID": dev.ID,
                "fluence": dev.fluence,
                "annealing": dev.annealing,
            }
            additional_cols = {key: getattr(dev, key) for key in add_columns}
            single_df = pd.DataFrame({**default_cols, **additional_cols}, index=[i])
            single_df["Device"] = dev
            df = pd.concat([df, single_df])
        return df

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

import numpy as np

class TypeConverter:

    @staticmethod
    def float_to_max_decimals_string(float):
        return "{:.50f}".format(float)

    @staticmethod
    def array_to_csv_string(array):
        csv_string = ""
        for row in array:
            row_string = ",".join(TypeConverter.float_to_max_decimals_string(value) for value in row)
            csv_string += row_string + "\n"
        csv_string = csv_string.rstrip("\n") # Remove final \n
        return csv_string
from dataclasses import dataclass, field


def to_str(entries: list, truncation: int):
    return [f'{entry:.{truncation}f}' for entry in entries]


@dataclass
class SpeedData:
    base_time: float = 1
    base_multiplier: float = 1
    speed: float = 1
    productivity: float = 1
    input_coefficient: float = field(init=False)

    def __post_init__(self):
        self.input_coefficient = self.base_multiplier * (
            1 + self.speed) / self.base_time

    def str(self):
        return to_str([
            self.base_time, self.base_multiplier, self.speed, self.productivity
        ], 2)


class Item:
    pass


class SpeedDescriptor:
    data: SpeedData | None = None
    parent: Item

    def __set__(self, obj, value):
        print(self)
        print(obj)
        print(value)
        print()
        if value is self:
            return
        self.data = value
        if self.data is None:
            return
        self.parent.input_coefficient = self.data.input_coefficient
        print(self.data.input_coefficient)
        if self.parent.base_output != 0:
            self.parent.output_coefficient = (
                1 + self.data.productivity -
                self.data.productivity * self.parent.base_input /
                self.parent.base_output) * self.data.input_coefficient
        else:
            self.parent.output_coefficient = 0
        self.parent.input = self.parent.base_input * self.parent.input_coefficient
        self.parent.output = self.parent.base_output * self.parent.output_coefficient


@dataclass
class Item:
    name: str
    base_input: int = 0
    base_output: int = 0
    input: int = field(init=False, default=0)
    output: int = field(init=False, default=0)
    input_coefficient: float = field(init=False, default=1)
    output_coefficient: float = field(init=False, default=1)
    speed: SpeedDescriptor = field(default=SpeedDescriptor())

    def __post_init__(self):
        self.speed.parent = self

    def tableize(self, quantity):
        return [
            self.name, *to_str([
                self.base_input, self.base_output, self.input, self.output,
                self.input * quantity, self.output * quantity
            ], 1)
        ]


@dataclass
class Rate:
    name: str
    entries: list[Item]
    speed_data: SpeedData
    quantity: float = 1

    def __post_init__(self):
        for item in self.entries:
            self.__setattr__(item.name, item)

    def print(self):
        from rich.console import Console
        from rich.table import Table

        console = Console()
        table = Table(show_header=False)
        [table.add_column("") for x in range(7)]
        table.add_row(self.name, end_section=True)
        table.add_row("Quantity",
                      "Base Time",
                      "Base Multiplier",
                      "Speed Multiplier",
                      "Productivity Multiplier",
                      style="bold magenta",
                      end_section=True)
        table.add_row(f'{self.quantity:.2f}',
                      *self.speed_data.str(),
                      end_section=True)
        table.add_row("",
                      "Input / Operation",
                      "Output / Operation",
                      "Input / Machine / Unit Time",
                      "Output / Machine / Unit Time",
                      "Input / Unit Time",
                      "Output / Unit Time",
                      style="bold magenta",
                      end_section=True)
        for item in self.entries:
            table.add_row(*item.tableize(self.quantity))
        console.print(table)


cl = Rate('coal_liquefaction', [
    Item('coal', 10),
    Item('heavy_oil', 25, 90),
    Item('steam', 50),
    Item('light_oil', 0, 20),
    Item('petroleum_gas', 0, 10),
],
          SpeedData(5, 1, 4.29, 0.18),
          quantity=108)

# hoc = Rate(
#     'heavy_oil_cracking',
#     [Item('heavy_oil', 40),
#      Item('water', 30),
#      Item('light_oil', 0, 30)], SpeedData(2, 1, 3.94, 0.18))

# hoc.quantity = cl.quantity * ( cl.heavy_oil.output - cl.heavy_oil.input ) / hoc.heavy_oil.input

cl.print()
# hoc.print()
"""
# Recipe Description

electronic_circuit:
  productivity: 50
  speed: 300
  input:
    copper_cable: 3
    iron_plate: 1
  output:
    electronic_circuit: 1

copper_cable:
  productivity: 50
  speed: 300
  input:
    molten_copper: 10
  output:
    copper_cable: input_copper_cable
"""

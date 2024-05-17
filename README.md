# Fritz DECT200 (11081)
This module reads the current power consumption in mW, the meter reading of the DECT200 in Wh, and the measured 
temperature (corrected by the set offset). Multiple modules can be linked in a cascade so that only one web query is 
required. To do this, simply connect A6 of the predecessor module to E1 of the successor module.

## Prerequisite
- HS Firmware 4.12 / HSL 2.0.4

## Installation
Import the .hslz file with the Gira Expert. The logic module is then available in the "Data Exchange" category.

## Inputs

| Input        | Init Value | Description                                                                                         |
|--------------|------------|-----------------------------------------------------------------------------------------------------|
| Fritzbox IP  |            | IP of the FritzBox                                                                                  |
| User         |            | `User` of the FritzBox user to be used                                                              |
| Password     |            | `Password` of the FritzBox user to be used                                                          |
| AIN          |            | AIN of the FritzDECT200 to be read in the format '12345 6789123'                                    |
| On/Off       | 0          | Switching the FritzDECT 200 on/off                                                                  |
| Interval [s] | 0          | If the value is > 0, the status of the DECT200 device is queried from the Fritzbox every x seconds. |

## Outputs
All outputs are executed as SBC / Send by Change.

| Output                   | Init Value | Description                                         |
|--------------------------|------------|-----------------------------------------------------|
| Current Consumption [mW] | 0          | Current power consumption of the FritzDECT200 in mW |
| Meter Reading [Wh]       | 0          | Meter reading of the FritzDECT200 in Wh             |
| Temperature [°C]         | 0          | Temperature measured by the FritzDECT200 in °C      |

## Code

The code of the module is located in the hslz file or on [GitHub](https://github.com/En3rGy/11081-Fritz-DECT200).

### Development Environment

- [Python 2.7.18](https://www.python.org/download/releases/2.7/)
    - Install python *markdown* module (for generating the documentation) `python -m pip install markdown`
- Python editor [PyCharm](https://www.jetbrains.com/pycharm/)
- [Gira Homeserver Interface Information](http://www.hs-help.net/hshelp/gira/other_documentation/Schnittstelleninformationen.zip)

## Requirements

-

## Software Design Description
The module uses a [library](https://github.com/En3rGy/fritz_lib) to outsource communication with the FritzBox. 
Additionally, the object instantiated by the library is held as a global variable. The goal is to share the connection 
data to the FritzBox among all modules using the library.

## Validation and Verification

Units test are persormed on some functions.

## License

Copyright 2024 T. Paul

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

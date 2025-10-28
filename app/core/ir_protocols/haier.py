# Copyright 2018-2021 crankyoldgit
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Haier A/C protocols.
## The specifics of reverse engineering the protocols details:
## * HSU07-HEA03 by kuzin2006.
## * YR-W02/HSU-09HMC203 by non7top.
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/404
## @see https://www.dropbox.com/s/mecyib3lhdxc8c6/IR%20data%20reverse%20engineering.xlsx?dl=0
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/485
## @see https://www.dropbox.com/sh/w0bt7egp0fjger5/AADRFV6Wg4wZskJVdFvzb8Z0a?dl=0&preview=haer2.ods
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1480
## Direct translation from IRremoteESP8266 ir_Haier.cpp and ir_Haier.h

from typing import List, Optional

# Supports:
#   Brand: Haier,  Model: HSU07-HEA03 remote (HAIER_AC)
#   Brand: Haier,  Model: YR-W02 remote (HAIER_AC_YRW02)
#   Brand: Haier,  Model: HSU-09HMC203 A/C (HAIER_AC_YRW02)
#   Brand: Haier,  Model: V9014557 M47 8D remote (HAIER_AC176)
#   Brand: Mabe,   Model: MMI18HDBWCA6MI8 A/C (HAIER_AC176)
#   Brand: Mabe,   Model: V12843 HJ200223 remote (HAIER_AC176)
#   Brand: Daichi, Model: D-H A/C (HAIER_AC176)
#   Brand: Haier,  Model: KFR-26GW/83@UI-Ge A/C (HAIER_AC160)

# State length constants (from IRremoteESP8266.h)
kHaierACStateLength = 9
kHaierACYRW02StateLength = 14
kHaierAC176StateLength = 22
kHaierAC160StateLength = 20

kHaierACBits = kHaierACStateLength * 8
kHaierACYRW02Bits = kHaierACYRW02StateLength * 8
kHaierAC176Bits = kHaierAC176StateLength * 8
kHaierAC160Bits = kHaierAC160StateLength * 8

# Constants - Timing values (EXACT translation from ir_Haier.cpp:24-29)
kHaierAcHdr = 3000
kHaierAcHdrGap = 4300
kHaierAcBitMark = 520
kHaierAcOneSpace = 1650
kHaierAcZeroSpace = 650
kHaierAcMinGap = 150000  # Completely made up value.

# HAIER_AC Constants (EXACT translation from ir_Haier.h:74-110)
kHaierAcPrefix = 0b10100101

kHaierAcMinTemp = 16
kHaierAcDefTemp = 25
kHaierAcMaxTemp = 30
kHaierAcCmdOff =         0b0000
kHaierAcCmdOn =          0b0001
kHaierAcCmdMode =        0b0010
kHaierAcCmdFan =         0b0011
kHaierAcCmdTempUp =      0b0110
kHaierAcCmdTempDown =    0b0111
kHaierAcCmdSleep =       0b1000
kHaierAcCmdTimerSet =    0b1001
kHaierAcCmdTimerCancel = 0b1010
kHaierAcCmdHealth =      0b1100
kHaierAcCmdSwing =       0b1101

kHaierAcSwingVOff =  0b00
kHaierAcSwingVUp =   0b01
kHaierAcSwingVDown = 0b10
kHaierAcSwingVChg =  0b11

kHaierAcAuto = 0
kHaierAcCool = 1
kHaierAcDry = 2
kHaierAcHeat = 3
kHaierAcFan = 4

kHaierAcFanAuto = 0
kHaierAcFanLow = 1
kHaierAcFanMed = 2
kHaierAcFanHigh = 3

kHaierAcMaxTime = (23 * 60) + 59

kHaierAcSleepBit = 0b01000000

# HAIER_AC_YRW02 / HAIER_AC176 Constants (EXACT translation from ir_Haier.h:140-207)
kHaierAcYrw02MinTempC = 16
kHaierAcYrw02MaxTempC = 30
kHaierAcYrw02MinTempF = 60
kHaierAcYrw02MaxTempF = 86
kHaierAcYrw02DefTempC = 25

kHaierAcYrw02ModelA = 0xA6
kHaierAcYrw02ModelB = 0x59
kHaierAc176Prefix = 0xB7
kHaierAc160Prefix = 0xB5

kHaierAcYrw02SwingVOff = 0x0
kHaierAcYrw02SwingVTop = 0x1
kHaierAcYrw02SwingVMiddle = 0x2  # Not available in heat mode.
kHaierAcYrw02SwingVBottom = 0x3  # Only available in heat mode.
kHaierAcYrw02SwingVDown = 0xA
kHaierAcYrw02SwingVAuto = 0xC  # Airflow

kHaierAc160SwingVOff =     0b0000
kHaierAc160SwingVTop =     0b0001
kHaierAc160SwingVHighest = 0b0010
kHaierAc160SwingVHigh =    0b0100
kHaierAc160SwingVMiddle =  0b0110
kHaierAc160SwingVLow =     0b1000
kHaierAc160SwingVLowest =  0b0011
kHaierAc160SwingVAuto =    0b1100  # Airflow

kHaierAcYrw02SwingHMiddle = 0x0
kHaierAcYrw02SwingHLeftMax = 0x3
kHaierAcYrw02SwingHLeft = 0x4
kHaierAcYrw02SwingHRight = 0x5
kHaierAcYrw02SwingHRightMax = 0x6
kHaierAcYrw02SwingHAuto = 0x7

kHaierAcYrw02FanHigh = 0b001
kHaierAcYrw02FanMed =  0b010
kHaierAcYrw02FanLow =  0b011
kHaierAcYrw02FanAuto = 0b101  # HAIER_AC176 uses `0` in Fan2

kHaierAcYrw02Auto = 0b000  # 0
kHaierAcYrw02Cool = 0b001  # 1
kHaierAcYrw02Dry =  0b010  # 2
kHaierAcYrw02Heat = 0b100  # 4
kHaierAcYrw02Fan =  0b110  # 5

kHaierAcYrw02ButtonTempUp =   0b00000
kHaierAcYrw02ButtonTempDown = 0b00001
kHaierAcYrw02ButtonSwingV =   0b00010
kHaierAcYrw02ButtonSwingH =   0b00011
kHaierAcYrw02ButtonFan =      0b00100
kHaierAcYrw02ButtonPower =    0b00101
kHaierAcYrw02ButtonMode =     0b00110
kHaierAcYrw02ButtonHealth =   0b00111
kHaierAcYrw02ButtonTurbo =    0b01000
kHaierAcYrw02ButtonSleep =    0b01011
kHaierAcYrw02ButtonTimer =    0b10000
kHaierAcYrw02ButtonLock =     0b10100
kHaierAc160ButtonLight =      0b10101
kHaierAc160ButtonAuxHeating = 0b10110
kHaierAc160ButtonClean =      0b11001
kHaierAcYrw02ButtonCFAB =     0b11010

kHaierAcYrw02NoTimers       = 0b000
kHaierAcYrw02OffTimer       = 0b001
kHaierAcYrw02OnTimer        = 0b010
kHaierAcYrw02OnThenOffTimer = 0b100
kHaierAcYrw02OffThenOnTimer = 0b101

# Model enums (EXACT translation from ir_Haier.h)
HAIER_AC176_REMOTE_MODEL_A = 0
HAIER_AC176_REMOTE_MODEL_B = 1


## Helper function for sumBytes (used in checksums)
## EXACT translation from IRremoteESP8266 IRutils::sumBytes
def sumBytes(data: List[int], length: int) -> int:
    """Sum all bytes in the array"""
    return sum(data[:length]) & 0xFF


## Native representation of a Haier HSU07-HEA03 A/C message.
## EXACT translation from ir_Haier.h:36-70
class HaierProtocol:
    def __init__(self):
        # The state array (9 bytes for Haier)
        self.remote_state = [0] * kHaierACStateLength

    # Byte 0
    @property
    def Prefix(self) -> int:
        return self.remote_state[0]

    @Prefix.setter
    def Prefix(self, value: int) -> None:
        self.remote_state[0] = value & 0xFF

    # Byte 1
    @property
    def Command(self) -> int:
        return self.remote_state[1] & 0x0F

    @Command.setter
    def Command(self, value: int) -> None:
        self.remote_state[1] = (self.remote_state[1] & 0xF0) | (value & 0x0F)

    @property
    def Temp(self) -> int:
        return (self.remote_state[1] >> 4) & 0x0F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.remote_state[1] = (self.remote_state[1] & 0x0F) | ((value & 0x0F) << 4)

    # Byte 2
    @property
    def CurrHours(self) -> int:
        return self.remote_state[2] & 0x1F

    @CurrHours.setter
    def CurrHours(self, value: int) -> None:
        self.remote_state[2] = (self.remote_state[2] & 0xE0) | (value & 0x1F)

    @property
    def unknown(self) -> int:
        return (self.remote_state[2] >> 5) & 0x01

    @unknown.setter
    def unknown(self, value: int) -> None:
        if value:
            self.remote_state[2] |= 0x20
        else:
            self.remote_state[2] &= 0xDF

    @property
    def SwingV(self) -> int:
        return (self.remote_state[2] >> 6) & 0x03

    @SwingV.setter
    def SwingV(self, value: int) -> None:
        self.remote_state[2] = (self.remote_state[2] & 0x3F) | ((value & 0x03) << 6)

    # Byte 3
    @property
    def CurrMins(self) -> int:
        return self.remote_state[3] & 0x3F

    @CurrMins.setter
    def CurrMins(self, value: int) -> None:
        self.remote_state[3] = (self.remote_state[3] & 0xC0) | (value & 0x3F)

    @property
    def OffTimer(self) -> int:
        return (self.remote_state[3] >> 6) & 0x01

    @OffTimer.setter
    def OffTimer(self, value: int) -> None:
        if value:
            self.remote_state[3] |= 0x40
        else:
            self.remote_state[3] &= 0xBF

    @property
    def OnTimer(self) -> int:
        return (self.remote_state[3] >> 7) & 0x01

    @OnTimer.setter
    def OnTimer(self, value: int) -> None:
        if value:
            self.remote_state[3] |= 0x80
        else:
            self.remote_state[3] &= 0x7F

    # Byte 4
    @property
    def OffHours(self) -> int:
        return self.remote_state[4] & 0x1F

    @OffHours.setter
    def OffHours(self, value: int) -> None:
        self.remote_state[4] = (self.remote_state[4] & 0xE0) | (value & 0x1F)

    @property
    def Health(self) -> int:
        return (self.remote_state[4] >> 5) & 0x01

    @Health.setter
    def Health(self, value: int) -> None:
        if value:
            self.remote_state[4] |= 0x20
        else:
            self.remote_state[4] &= 0xDF

    # Byte 5
    @property
    def OffMins(self) -> int:
        return self.remote_state[5] & 0x3F

    @OffMins.setter
    def OffMins(self, value: int) -> None:
        self.remote_state[5] = (self.remote_state[5] & 0xC0) | (value & 0x3F)

    @property
    def Fan(self) -> int:
        return (self.remote_state[5] >> 6) & 0x03

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.remote_state[5] = (self.remote_state[5] & 0x3F) | ((value & 0x03) << 6)

    # Byte 6
    @property
    def OnHours(self) -> int:
        return self.remote_state[6] & 0x1F

    @OnHours.setter
    def OnHours(self, value: int) -> None:
        self.remote_state[6] = (self.remote_state[6] & 0xE0) | (value & 0x1F)

    @property
    def Mode(self) -> int:
        return (self.remote_state[6] >> 5) & 0x07

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.remote_state[6] = (self.remote_state[6] & 0x1F) | ((value & 0x07) << 5)

    # Byte 7
    @property
    def OnMins(self) -> int:
        return self.remote_state[7] & 0x3F

    @OnMins.setter
    def OnMins(self, value: int) -> None:
        self.remote_state[7] = (self.remote_state[7] & 0xC0) | (value & 0x3F)

    @property
    def Sleep(self) -> int:
        return (self.remote_state[7] >> 6) & 0x01

    @Sleep.setter
    def Sleep(self, value: int) -> None:
        if value:
            self.remote_state[7] |= 0x40
        else:
            self.remote_state[7] &= 0xBF

    # Byte 8
    @property
    def Sum(self) -> int:
        return self.remote_state[8]

    @Sum.setter
    def Sum(self, value: int) -> None:
        self.remote_state[8] = value & 0xFF


## Native representation of a Haier 176 bit A/C message.
## EXACT translation from ir_Haier.h:209-276
class HaierAc176Protocol:
    def __init__(self):
        self.raw = [0] * kHaierAC176StateLength

    # Byte 0
    @property
    def Model(self) -> int:
        return self.raw[0]

    @Model.setter
    def Model(self, value: int) -> None:
        self.raw[0] = value & 0xFF

    # Byte 1
    @property
    def SwingV(self) -> int:
        return self.raw[1] & 0x0F

    @SwingV.setter
    def SwingV(self, value: int) -> None:
        self.raw[1] = (self.raw[1] & 0xF0) | (value & 0x0F)

    @property
    def Temp(self) -> int:
        return (self.raw[1] >> 4) & 0x0F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.raw[1] = (self.raw[1] & 0x0F) | ((value & 0x0F) << 4)

    # Byte 2
    @property
    def SwingH(self) -> int:
        return (self.raw[2] >> 5) & 0x07

    @SwingH.setter
    def SwingH(self, value: int) -> None:
        self.raw[2] = (self.raw[2] & 0x1F) | ((value & 0x07) << 5)

    # Byte 3
    @property
    def Health(self) -> int:
        return (self.raw[3] >> 1) & 0x01

    @Health.setter
    def Health(self, value: int) -> None:
        if value:
            self.raw[3] |= 0x02
        else:
            self.raw[3] &= 0xFD

    @property
    def TimerMode(self) -> int:
        return (self.raw[3] >> 5) & 0x07

    @TimerMode.setter
    def TimerMode(self, value: int) -> None:
        self.raw[3] = (self.raw[3] & 0x1F) | ((value & 0x07) << 5)

    # Byte 4
    @property
    def Power(self) -> int:
        return (self.raw[4] >> 6) & 0x01

    @Power.setter
    def Power(self, value: int) -> None:
        if value:
            self.raw[4] |= 0x40
        else:
            self.raw[4] &= 0xBF

    # Byte 5
    @property
    def OffTimerHrs(self) -> int:
        return self.raw[5] & 0x1F

    @OffTimerHrs.setter
    def OffTimerHrs(self, value: int) -> None:
        self.raw[5] = (self.raw[5] & 0xE0) | (value & 0x1F)

    @property
    def Fan(self) -> int:
        return (self.raw[5] >> 5) & 0x07

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.raw[5] = (self.raw[5] & 0x1F) | ((value & 0x07) << 5)

    # Byte 6
    @property
    def OffTimerMins(self) -> int:
        return self.raw[6] & 0x3F

    @OffTimerMins.setter
    def OffTimerMins(self, value: int) -> None:
        self.raw[6] = (self.raw[6] & 0xC0) | (value & 0x3F)

    @property
    def Turbo(self) -> int:
        return (self.raw[6] >> 6) & 0x01

    @Turbo.setter
    def Turbo(self, value: int) -> None:
        if value:
            self.raw[6] |= 0x40
        else:
            self.raw[6] &= 0xBF

    @property
    def Quiet(self) -> int:
        return (self.raw[6] >> 7) & 0x01

    @Quiet.setter
    def Quiet(self, value: int) -> None:
        if value:
            self.raw[6] |= 0x80
        else:
            self.raw[6] &= 0x7F

    # Byte 7
    @property
    def OnTimerHrs(self) -> int:
        return self.raw[7] & 0x1F

    @OnTimerHrs.setter
    def OnTimerHrs(self, value: int) -> None:
        self.raw[7] = (self.raw[7] & 0xE0) | (value & 0x1F)

    @property
    def Mode(self) -> int:
        return (self.raw[7] >> 5) & 0x07

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw[7] = (self.raw[7] & 0x1F) | ((value & 0x07) << 5)

    # Byte 8
    @property
    def OnTimerMins(self) -> int:
        return self.raw[8] & 0x3F

    @OnTimerMins.setter
    def OnTimerMins(self, value: int) -> None:
        self.raw[8] = (self.raw[8] & 0xC0) | (value & 0x3F)

    @property
    def Sleep(self) -> int:
        return (self.raw[8] >> 7) & 0x01

    @Sleep.setter
    def Sleep(self, value: int) -> None:
        if value:
            self.raw[8] |= 0x80
        else:
            self.raw[8] &= 0x7F

    # Byte 10
    @property
    def ExtraDegreeF(self) -> int:
        return self.raw[10] & 0x01

    @ExtraDegreeF.setter
    def ExtraDegreeF(self, value: int) -> None:
        if value:
            self.raw[10] |= 0x01
        else:
            self.raw[10] &= 0xFE

    @property
    def UseFahrenheit(self) -> int:
        return (self.raw[10] >> 5) & 0x01

    @UseFahrenheit.setter
    def UseFahrenheit(self, value: int) -> None:
        if value:
            self.raw[10] |= 0x20
        else:
            self.raw[10] &= 0xDF

    # Byte 12
    @property
    def Button(self) -> int:
        return self.raw[12] & 0x1F

    @Button.setter
    def Button(self, value: int) -> None:
        self.raw[12] = (self.raw[12] & 0xE0) | (value & 0x1F)

    @property
    def Lock(self) -> int:
        return (self.raw[12] >> 5) & 0x01

    @Lock.setter
    def Lock(self, value: int) -> None:
        if value:
            self.raw[12] |= 0x20
        else:
            self.raw[12] &= 0xDF

    # Byte 13
    @property
    def Sum(self) -> int:
        return self.raw[13]

    @Sum.setter
    def Sum(self, value: int) -> None:
        self.raw[13] = value & 0xFF

    # Byte 14
    @property
    def Prefix2(self) -> int:
        return self.raw[14]

    @Prefix2.setter
    def Prefix2(self, value: int) -> None:
        self.raw[14] = value & 0xFF

    # Byte 16
    @property
    def Fan2(self) -> int:
        return (self.raw[16] >> 6) & 0x03

    @Fan2.setter
    def Fan2(self, value: int) -> None:
        self.raw[16] = (self.raw[16] & 0x3F) | ((value & 0x03) << 6)

    # Byte 21
    @property
    def Sum2(self) -> int:
        return self.raw[21]

    @Sum2.setter
    def Sum2(self, value: int) -> None:
        self.raw[21] = value & 0xFF


## Native representation of a Haier 160 bit A/C message.
## EXACT translation from ir_Haier.h:279-345
class HaierAc160Protocol:
    def __init__(self):
        self.raw = [0] * kHaierAC160StateLength

    # Byte 0
    @property
    def Model(self) -> int:
        return self.raw[0]

    @Model.setter
    def Model(self, value: int) -> None:
        self.raw[0] = value & 0xFF

    # Byte 1
    @property
    def SwingV(self) -> int:
        return self.raw[1] & 0x0F

    @SwingV.setter
    def SwingV(self, value: int) -> None:
        self.raw[1] = (self.raw[1] & 0xF0) | (value & 0x0F)

    @property
    def Temp(self) -> int:
        return (self.raw[1] >> 4) & 0x0F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.raw[1] = (self.raw[1] & 0x0F) | ((value & 0x0F) << 4)

    # Byte 2
    @property
    def SwingH(self) -> int:
        return (self.raw[2] >> 5) & 0x07

    @SwingH.setter
    def SwingH(self, value: int) -> None:
        self.raw[2] = (self.raw[2] & 0x1F) | ((value & 0x07) << 5)

    # Byte 3
    @property
    def Health(self) -> int:
        return (self.raw[3] >> 1) & 0x01

    @Health.setter
    def Health(self, value: int) -> None:
        if value:
            self.raw[3] |= 0x02
        else:
            self.raw[3] &= 0xFD

    @property
    def TimerMode(self) -> int:
        return (self.raw[3] >> 5) & 0x07

    @TimerMode.setter
    def TimerMode(self, value: int) -> None:
        self.raw[3] = (self.raw[3] & 0x1F) | ((value & 0x07) << 5)

    # Byte 4
    @property
    def Power(self) -> int:
        return (self.raw[4] >> 6) & 0x01

    @Power.setter
    def Power(self, value: int) -> None:
        if value:
            self.raw[4] |= 0x40
        else:
            self.raw[4] &= 0xBF

    @property
    def AuxHeating(self) -> int:
        return (self.raw[4] >> 7) & 0x01

    @AuxHeating.setter
    def AuxHeating(self, value: int) -> None:
        if value:
            self.raw[4] |= 0x80
        else:
            self.raw[4] &= 0x7F

    # Byte 5
    @property
    def OffTimerHrs(self) -> int:
        return self.raw[5] & 0x1F

    @OffTimerHrs.setter
    def OffTimerHrs(self, value: int) -> None:
        self.raw[5] = (self.raw[5] & 0xE0) | (value & 0x1F)

    @property
    def Fan(self) -> int:
        return (self.raw[5] >> 5) & 0x07

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.raw[5] = (self.raw[5] & 0x1F) | ((value & 0x07) << 5)

    # Byte 6
    @property
    def OffTimerMins(self) -> int:
        return self.raw[6] & 0x3F

    @OffTimerMins.setter
    def OffTimerMins(self, value: int) -> None:
        self.raw[6] = (self.raw[6] & 0xC0) | (value & 0x3F)

    @property
    def Turbo(self) -> int:
        return (self.raw[6] >> 6) & 0x01

    @Turbo.setter
    def Turbo(self, value: int) -> None:
        if value:
            self.raw[6] |= 0x40
        else:
            self.raw[6] &= 0xBF

    @property
    def Quiet(self) -> int:
        return (self.raw[6] >> 7) & 0x01

    @Quiet.setter
    def Quiet(self, value: int) -> None:
        if value:
            self.raw[6] |= 0x80
        else:
            self.raw[6] &= 0x7F

    # Byte 7
    @property
    def OnTimerHrs(self) -> int:
        return self.raw[7] & 0x1F

    @OnTimerHrs.setter
    def OnTimerHrs(self, value: int) -> None:
        self.raw[7] = (self.raw[7] & 0xE0) | (value & 0x1F)

    @property
    def Mode(self) -> int:
        return (self.raw[7] >> 5) & 0x07

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.raw[7] = (self.raw[7] & 0x1F) | ((value & 0x07) << 5)

    # Byte 8
    @property
    def OnTimerMins(self) -> int:
        return self.raw[8] & 0x3F

    @OnTimerMins.setter
    def OnTimerMins(self, value: int) -> None:
        self.raw[8] = (self.raw[8] & 0xC0) | (value & 0x3F)

    @property
    def Sleep(self) -> int:
        return (self.raw[8] >> 7) & 0x01

    @Sleep.setter
    def Sleep(self, value: int) -> None:
        if value:
            self.raw[8] |= 0x80
        else:
            self.raw[8] &= 0x7F

    # Byte 10
    @property
    def ExtraDegreeF(self) -> int:
        return self.raw[10] & 0x01

    @ExtraDegreeF.setter
    def ExtraDegreeF(self, value: int) -> None:
        if value:
            self.raw[10] |= 0x01
        else:
            self.raw[10] &= 0xFE

    @property
    def Clean(self) -> int:
        return (self.raw[10] >> 4) & 0x01

    @Clean.setter
    def Clean(self, value: int) -> None:
        if value:
            self.raw[10] |= 0x10
        else:
            self.raw[10] &= 0xEF

    @property
    def UseFahrenheit(self) -> int:
        return (self.raw[10] >> 5) & 0x01

    @UseFahrenheit.setter
    def UseFahrenheit(self, value: int) -> None:
        if value:
            self.raw[10] |= 0x20
        else:
            self.raw[10] &= 0xDF

    # Byte 12
    @property
    def Button(self) -> int:
        return self.raw[12] & 0x1F

    @Button.setter
    def Button(self, value: int) -> None:
        self.raw[12] = (self.raw[12] & 0xE0) | (value & 0x1F)

    @property
    def Lock(self) -> int:
        return (self.raw[12] >> 5) & 0x01

    @Lock.setter
    def Lock(self, value: int) -> None:
        if value:
            self.raw[12] |= 0x20
        else:
            self.raw[12] &= 0xDF

    # Byte 13
    @property
    def Sum(self) -> int:
        return self.raw[13]

    @Sum.setter
    def Sum(self, value: int) -> None:
        self.raw[13] = value & 0xFF

    # Byte 14
    @property
    def Prefix(self) -> int:
        return self.raw[14]

    @Prefix.setter
    def Prefix(self, value: int) -> None:
        self.raw[14] = value & 0xFF

    # Byte 15
    @property
    def Clean2(self) -> int:
        return (self.raw[15] >> 6) & 0x01

    @Clean2.setter
    def Clean2(self, value: int) -> None:
        if value:
            self.raw[15] |= 0x40
        else:
            self.raw[15] &= 0xBF

    # Byte 16
    @property
    def Fan2(self) -> int:
        return (self.raw[16] >> 5) & 0x07

    @Fan2.setter
    def Fan2(self, value: int) -> None:
        self.raw[16] = (self.raw[16] & 0x1F) | ((value & 0x07) << 5)

    # Byte 19
    @property
    def Sum2(self) -> int:
        return self.raw[19]

    @Sum2.setter
    def Sum2(self, value: int) -> None:
        self.raw[19] = value & 0xFF


## Send a Haier A/C formatted message. (HSU07-HEA03 remote)
## Status: STABLE / Known to be working.
## EXACT translation from ir_Haier.cpp:56-70
def sendHaierAC(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Haier A/C formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendHaierAC

    Returns timing array instead of transmitting via hardware.
    """
    if nbytes < kHaierACStateLength:
        return []

    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric

    all_timings = []

    for r in range(repeat + 1):
        # Pre-Header
        all_timings.append(kHaierAcHdr)
        all_timings.append(kHaierAcHdr)

        # Header + Data + Footer
        block_timings = sendGeneric(
            headermark=kHaierAcHdr,
            headerspace=kHaierAcHdrGap,
            onemark=kHaierAcBitMark,
            onespace=kHaierAcOneSpace,
            zeromark=kHaierAcBitMark,
            zerospace=kHaierAcZeroSpace,
            footermark=kHaierAcBitMark,
            gap=kHaierAcMinGap,
            dataptr=data,
            nbytes=nbytes,
            frequency=38,
            MSBfirst=True,
            repeat=0,
            dutycycle=50
        )
        all_timings.extend(block_timings)

    return all_timings


## Send a Haier YR-W02 remote A/C formatted message.
## Status: STABLE / Known to be working.
## EXACT translation from ir_Haier.cpp:79-82
def sendHaierACYRW02(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Haier YR-W02 remote A/C formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendHaierACYRW02
    """
    if nbytes >= kHaierACYRW02StateLength:
        return sendHaierAC(data, nbytes, repeat)
    return []


## Send a Haier 176 bit remote A/C formatted message.
## Status: STABLE / Known to be working.
## EXACT translation from ir_Haier.cpp:91-94
def sendHaierAC176(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Haier 176 bit remote A/C formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendHaierAC176
    """
    if nbytes >= kHaierAC176StateLength:
        return sendHaierAC(data, nbytes, repeat)
    return []


## Send a Haier 160 bit remote A/C formatted message.
## Status: STABLE / Known to be working.
## EXACT translation from ir_Haier.cpp:103-106
def sendHaierAC160(data: List[int], nbytes: int, repeat: int = 0) -> List[int]:
    """
    Send a Haier 160 bit remote A/C formatted message.
    EXACT translation from IRremoteESP8266 IRsend::sendHaierAC160
    """
    if nbytes >= kHaierAC160StateLength:
        return sendHaierAC(data, nbytes, repeat)
    return []


## Class for handling detailed Haier A/C messages.
## EXACT translation from ir_Haier.cpp:109-549
class IRHaierAC:
    ## Class Constructor
    ## EXACT translation from ir_Haier.cpp:113-115
    def __init__(self) -> None:
        self._: HaierProtocol = HaierProtocol()
        self.stateReset()

    ## Reset the internal state to a fixed known good state.
    ## EXACT translation from ir_Haier.cpp:143-151
    def stateReset(self) -> None:
        for i in range(len(self._.remote_state)):
            self._.remote_state[i] = 0
        self._.Prefix = kHaierAcPrefix
        self._.unknown = 1  # const value
        self._.OffHours = 12  # default initial state
        self._.Temp = kHaierAcDefTemp - kHaierAcMinTemp
        self._.Fan = 3  # kHaierAcFanLow
        self._.Command = kHaierAcCmdOn

    ## Calculate and set the checksum values for the internal state.
    ## EXACT translation from ir_Haier.cpp:129-131
    def checksum(self) -> None:
        self._.Sum = sumBytes(self._.remote_state, kHaierACStateLength - 1)

    ## Verify the checksum is valid for a given state.
    ## @param[in] state The array to verify the checksum of.
    ## @param[in] length The length of the state array.
    ## @return true, if the state has a valid checksum. Otherwise, false.
    ## EXACT translation from ir_Haier.cpp:137-140
    @staticmethod
    def validChecksum(state: List[int], length: int = kHaierACStateLength) -> bool:
        if length < 2:
            return False  # 1 byte of data can't have a checksum.
        return (state[length - 1] == sumBytes(state, length - 1))

    ## Get a PTR to the internal state/code for this protocol.
    ## @return PTR to a code for this protocol based on the current internal state.
    ## EXACT translation from ir_Haier.cpp:155-158
    def getRaw(self) -> List[int]:
        self.checksum()
        return self._.remote_state

    ## Set the internal state from a valid code for this protocol.
    ## @param[in] new_code A valid code for this protocol.
    ## EXACT translation from ir_Haier.cpp:162-164
    def setRaw(self, new_code: List[int]) -> None:
        for i in range(min(len(new_code), kHaierACStateLength)):
            self._.remote_state[i] = new_code[i]

    ## Set the Command/Button setting of the A/C.
    ## @param[in] command The value of the command/button that was pressed.
    ## EXACT translation from ir_Haier.cpp:168-183
    def setCommand(self, command: int) -> None:
        if command in [kHaierAcCmdOff, kHaierAcCmdOn, kHaierAcCmdMode, kHaierAcCmdFan,
                       kHaierAcCmdTempUp, kHaierAcCmdTempDown, kHaierAcCmdSleep,
                       kHaierAcCmdTimerSet, kHaierAcCmdTimerCancel, kHaierAcCmdHealth,
                       kHaierAcCmdSwing]:
            self._.Command = command

    ## Get the Command/Button setting of the A/C.
    ## @return The value of the command/button that was pressed.
    ## EXACT translation from ir_Haier.cpp:187-189
    def getCommand(self) -> int:
        return self._.Command

    ## Set the speed of the fan.
    ## @param[in] speed The desired setting.
    ## EXACT translation from ir_Haier.cpp:193-205
    def setFan(self, speed: int) -> None:
        new_speed = kHaierAcFanAuto
        if speed == kHaierAcFanLow:
            new_speed = 3
        elif speed == kHaierAcFanMed:
            new_speed = 2
        elif speed == kHaierAcFanHigh:
            new_speed = 1
        else:
            # Default to auto for anything else.
            new_speed = kHaierAcFanAuto

        if speed != self.getFan():
            self._.Command = kHaierAcCmdFan
        self._.Fan = new_speed

    ## Get the current fan speed setting.
    ## @return The current fan speed.
    ## EXACT translation from ir_Haier.cpp:209-216
    def getFan(self) -> int:
        if self._.Fan == 1:
            return kHaierAcFanHigh
        elif self._.Fan == 2:
            return kHaierAcFanMed
        elif self._.Fan == 3:
            return kHaierAcFanLow
        else:
            return kHaierAcFanAuto

    ## Set the operating mode of the A/C.
    ## @param[in] mode The desired operating mode.
    ## EXACT translation from ir_Haier.cpp:220-226
    def setMode(self, mode: int) -> None:
        new_mode = mode
        self._.Command = kHaierAcCmdMode
        # If out of range, default to auto mode.
        if mode > kHaierAcFan:
            new_mode = kHaierAcAuto
        self._.Mode = new_mode

    ## Get the operating mode setting of the A/C.
    ## @return The current operating mode setting.
    ## EXACT translation from ir_Haier.cpp:230-232
    def getMode(self) -> int:
        return self._.Mode

    ## Set the temperature.
    ## @param[in] degrees The temperature in degrees celsius.
    ## EXACT translation from ir_Haier.cpp:236-250
    def setTemp(self, degrees: int) -> None:
        temp = degrees
        if temp < kHaierAcMinTemp:
            temp = kHaierAcMinTemp
        elif temp > kHaierAcMaxTemp:
            temp = kHaierAcMaxTemp

        old_temp = self.getTemp()
        if old_temp == temp:
            return
        if old_temp > temp:
            self._.Command = kHaierAcCmdTempDown
        else:
            self._.Command = kHaierAcCmdTempUp
        self._.Temp = temp - kHaierAcMinTemp

    ## Get the current temperature setting.
    ## @return The current setting for temp. in degrees celsius.
    ## EXACT translation from ir_Haier.cpp:254-256
    def getTemp(self) -> int:
        return self._.Temp + kHaierAcMinTemp

    ## Set the Health (filter) setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from ir_Haier.cpp:260-263
    def setHealth(self, on: bool) -> None:
        self._.Command = kHaierAcCmdHealth
        self._.Health = on

    ## Get the Health (filter) setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from ir_Haier.cpp:267-269
    def getHealth(self) -> bool:
        return bool(self._.Health)

    ## Set the Sleep setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from ir_Haier.cpp:273-276
    def setSleep(self, on: bool) -> None:
        self._.Command = kHaierAcCmdSleep
        self._.Sleep = on

    ## Get the Sleep setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from ir_Haier.cpp:280-282
    def getSleep(self) -> bool:
        return bool(self._.Sleep)

    ## Get the On Timer value/setting of the A/C.
    ## @return Nr of minutes the timer is set to. -1 is Off/not set etc.
    ## EXACT translation from ir_Haier.cpp:286-292
    def getOnTimer(self) -> int:
        # Check if the timer is turned on.
        if self._.OnTimer:
            return self._.OnHours * 60 + self._.OnMins
        else:
            return -1

    ## Get the Off Timer value/setting of the A/C.
    ## @return Nr of minutes the timer is set to. -1 is Off/not set etc.
    ## EXACT translation from ir_Haier.cpp:296-302
    def getOffTimer(self) -> int:
        # Check if the timer is turned on.
        if self._.OffTimer:
            return self._.OffHours * 60 + self._.OffMins
        else:
            return -1

    ## Get the clock value of the A/C.
    ## @return The clock time, in Nr of minutes past midnight.
    ## EXACT translation from ir_Haier.cpp:306
    def getCurrTime(self) -> int:
        return self._.CurrHours * 60 + self._.CurrMins

    ## Set & enable the On Timer.
    ## @param[in] nr_mins The time expressed in total number of minutes.
    ## EXACT translation from ir_Haier.cpp:310-315
    def setOnTimer(self, nr_mins: int) -> None:
        self._.Command = kHaierAcCmdTimerSet
        self._.OnTimer = 1

        mins = nr_mins
        if nr_mins > kHaierAcMaxTime:
            mins = kHaierAcMaxTime
        self._.OnHours = mins // 60
        self._.OnMins = mins % 60

    ## Set & enable the Off Timer.
    ## @param[in] nr_mins The time expressed in total number of minutes.
    ## EXACT translation from ir_Haier.cpp:319-324
    def setOffTimer(self, nr_mins: int) -> None:
        self._.Command = kHaierAcCmdTimerSet
        self._.OffTimer = 1

        mins = nr_mins
        if nr_mins > kHaierAcMaxTime:
            mins = kHaierAcMaxTime
        self._.OffHours = mins // 60
        self._.OffMins = mins % 60

    ## Cancel/disable the On & Off timers.
    ## EXACT translation from ir_Haier.cpp:327-331
    def cancelTimers(self) -> None:
        self._.Command = kHaierAcCmdTimerCancel
        self._.OffTimer = 0
        self._.OnTimer = 0

    ## Set the clock value for the A/C.
    ## @param[in] nr_mins The clock time, in Nr of minutes past midnight.
    ## EXACT translation from ir_Haier.cpp:335-337
    def setCurrTime(self, nr_mins: int) -> None:
        mins = nr_mins
        if nr_mins > kHaierAcMaxTime:
            mins = kHaierAcMaxTime
        self._.CurrHours = mins // 60
        self._.CurrMins = mins % 60

    ## Get the Vertical Swing position setting of the A/C.
    ## @return The native vertical swing mode.
    ## EXACT translation from ir_Haier.cpp:341-343
    def getSwingV(self) -> int:
        return self._.SwingV

    ## Set the Vertical Swing mode of the A/C.
    ## @param[in] state The mode to set the vanes to.
    ## EXACT translation from ir_Haier.cpp:347-358
    def setSwingV(self, state: int) -> None:
        if state == self._.SwingV:
            return  # Nothing to do.
        if state in [kHaierAcSwingVOff, kHaierAcSwingVUp, kHaierAcSwingVDown,
                     kHaierAcSwingVChg]:
            self._.Command = kHaierAcCmdSwing
            self._.SwingV = state


## Class for handling detailed Haier 176 bit A/C messages.
## EXACT translation from ir_Haier.cpp:552-1309
class IRHaierAC176:
    ## Class Constructor
    ## EXACT translation from ir_Haier.cpp:556-558
    def __init__(self) -> None:
        self._: HaierAc176Protocol = HaierAc176Protocol()
        self.stateReset()

    ## Reset the internal state to a fixed known good state.
    ## EXACT translation from ir_Haier.cpp:597-606
    def stateReset(self) -> None:
        for i in range(len(self._.raw)):
            self._.raw[i] = 0
        self._.Model = kHaierAcYrw02ModelA
        self._.Prefix2 = kHaierAc176Prefix
        self._.Temp = kHaierAcYrw02DefTempC - kHaierAcYrw02MinTempC
        self._.Health = True
        self.setFan(kHaierAcYrw02FanAuto)
        self._.Power = True
        self._.Button = kHaierAcYrw02ButtonPower

    ## Calculate and set the checksum values for the internal state.
    ## EXACT translation from ir_Haier.cpp:572-576
    def checksum(self) -> None:
        self._.Sum = sumBytes(self._.raw, kHaierACYRW02StateLength - 1)
        self._.Sum2 = sumBytes(self._.raw[kHaierACYRW02StateLength:],
                               kHaierAC176StateLength - kHaierACYRW02StateLength - 1)

    ## Verify the checksum is valid for a given state.
    ## @param[in] state The array to verify the checksum of.
    ## @param[in] length The length of the state array.
    ## @return true, if the state has a valid checksum. Otherwise, false.
    ## EXACT translation from ir_Haier.cpp:582-594
    @staticmethod
    def validChecksum(state: List[int], length: int = kHaierAC176StateLength) -> bool:
        if length < 2:
            return False  # 1 byte of data can't have a checksum.
        if length < kHaierAC160StateLength:  # Is it too short?
            # Then it is just a checksum of the whole thing.
            return (state[length - 1] == sumBytes(state, length - 1))
        else:  # It is long enough for two checksums.
            return ((state[kHaierACYRW02StateLength - 1] ==
                     sumBytes(state, kHaierACYRW02StateLength - 1)) and
                    (state[length - 1] ==
                     sumBytes(state[kHaierACYRW02StateLength:],
                              length - kHaierACYRW02StateLength - 1)))

    ## Get a PTR to the internal state/code for this protocol.
    ## @return PTR to a code for this protocol based on the current internal state.
    ## EXACT translation from ir_Haier.cpp:610-613
    def getRaw(self) -> List[int]:
        self.checksum()
        return self._.raw

    ## Set the internal state from a valid code for this protocol.
    ## @param[in] new_code A valid code for this protocol.
    ## EXACT translation from ir_Haier.cpp:617-619
    def setRaw(self, new_code: List[int]) -> None:
        for i in range(min(len(new_code), kHaierAC176StateLength)):
            self._.raw[i] = new_code[i]

    ## Set the Button/Command setting of the A/C.
    ## @param[in] button The value of the button/command that was pressed.
    ## EXACT translation from ir_Haier.cpp:623-639
    def setButton(self, button: int) -> None:
        if button in [kHaierAcYrw02ButtonTempUp, kHaierAcYrw02ButtonTempDown,
                      kHaierAcYrw02ButtonSwingV, kHaierAcYrw02ButtonSwingH,
                      kHaierAcYrw02ButtonFan, kHaierAcYrw02ButtonPower,
                      kHaierAcYrw02ButtonMode, kHaierAcYrw02ButtonHealth,
                      kHaierAcYrw02ButtonTurbo, kHaierAcYrw02ButtonSleep,
                      kHaierAcYrw02ButtonLock, kHaierAcYrw02ButtonCFAB]:
            self._.Button = button

    ## Get/Detect the model of the A/C.
    ## @return The enum of the compatible model.
    ## EXACT translation from ir_Haier.cpp:643-648
    def getModel(self) -> int:
        if self._.Model == kHaierAcYrw02ModelB:
            return HAIER_AC176_REMOTE_MODEL_B
        else:
            return HAIER_AC176_REMOTE_MODEL_A

    ## Set the model of the A/C to emulate.
    ## @param[in] model The enum of the appropriate model.
    ## EXACT translation from ir_Haier.cpp:652-661
    def setModel(self, model: int) -> None:
        self._.Button = kHaierAcYrw02ButtonCFAB
        if model == HAIER_AC176_REMOTE_MODEL_B:
            self._.Model = kHaierAcYrw02ModelB
        else:
            self._.Model = kHaierAcYrw02ModelA

    ## Get the Button/Command setting of the A/C.
    ## @return The value of the button/command that was pressed.
    ## EXACT translation from ir_Haier.cpp:665-667
    def getButton(self) -> int:
        return self._.Button

    ## Set the operating mode of the A/C.
    ## @param[in] mode The desired operating mode.
    ## EXACT translation from ir_Haier.cpp:671-688
    def setMode(self, mode: int) -> None:
        if mode in [kHaierAcYrw02Auto, kHaierAcYrw02Dry, kHaierAcYrw02Fan]:
            # Turbo & Quiet is only available in Cool/Heat mode.
            self._.Turbo = False
            self._.Quiet = False
            self._.Button = kHaierAcYrw02ButtonMode
            self._.Mode = mode
        elif mode in [kHaierAcYrw02Cool, kHaierAcYrw02Heat]:
            self._.Button = kHaierAcYrw02ButtonMode
            self._.Mode = mode
        else:
            self.setMode(kHaierAcYrw02Auto)  # Unexpected, default to auto mode.

    ## Get the operating mode setting of the A/C.
    ## @return The current operating mode setting.
    ## EXACT translation from ir_Haier.cpp:692
    def getMode(self) -> int:
        return self._.Mode

    ## Set the default temperature units to use.
    ## @param[in] on Use Fahrenheit as the units.
    ##   true is Fahrenheit, false is Celsius.
    ## EXACT translation from ir_Haier.cpp:697
    def setUseFahrenheit(self, on: bool) -> None:
        self._.UseFahrenheit = on

    ## Get the default temperature units in use.
    ## @return true is Fahrenheit, false is Celsius.
    ## EXACT translation from ir_Haier.cpp:701
    def getUseFahrenheit(self) -> bool:
        return bool(self._.UseFahrenheit)

    ## Set the temperature.
    ## @param[in] degree The temperature in degrees.
    ## @param[in] fahrenheit Use units of Fahrenheit and set that as units used.
    ## EXACT translation from ir_Haier.cpp:706-740
    def setTemp(self, degree: int, fahrenheit: bool = False) -> None:
        old_temp = self.getTemp()
        if old_temp == degree:
            return

        if self._.UseFahrenheit == fahrenheit:
            if old_temp > degree:
                self._.Button = kHaierAcYrw02ButtonTempDown
            else:
                self._.Button = kHaierAcYrw02ButtonTempUp
        else:
            self._.Button = kHaierAcYrw02ButtonCFAB
        self._.UseFahrenheit = fahrenheit

        temp = degree
        if fahrenheit:
            if temp < kHaierAcYrw02MinTempF:
                temp = kHaierAcYrw02MinTempF
            elif temp > kHaierAcYrw02MaxTempF:
                temp = kHaierAcYrw02MaxTempF
            if degree >= 77:
                temp += 1
            if degree >= 79:
                temp += 1
            # See at IRHaierAC176::getTemp() comments for clarification
            self._.ExtraDegreeF = temp % 2
            self._.Temp = (temp - kHaierAcYrw02MinTempF - self._.ExtraDegreeF) >> 1
        else:
            if temp < kHaierAcYrw02MinTempC:
                temp = kHaierAcYrw02MinTempC
            elif temp > kHaierAcYrw02MaxTempC:
                temp = kHaierAcYrw02MaxTempC
            self._.Temp = temp - kHaierAcYrw02MinTempC

    ## Get the current temperature setting.
    ## The unit of temperature is specified by UseFahrenheit value.
    ## @return The current setting for temperature.
    ## EXACT translation from ir_Haier.cpp:745-789
    def getTemp(self) -> int:
        if not self._.UseFahrenheit:
            return self._.Temp + kHaierAcYrw02MinTempC
        degree = self._.Temp * 2 + kHaierAcYrw02MinTempF + self._.ExtraDegreeF
        # The way of coding the temperature in degree Fahrenheit is
        # kHaierAcYrw02MinTempF + Temp*2 + ExtraDegreeF, for example
        # Temp = 0b0011, ExtraDegreeF = 0b1, temperature is 60 + 3*2 + 1 = 67F
        # But around 78F there is unconsistency, see table in cpp file
        if degree >= 77:
            degree -= 1
        if degree >= 79:
            degree -= 1
        return degree

    ## Set the Health (filter) setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from ir_Haier.cpp:793-796
    def setHealth(self, on: bool) -> None:
        self._.Button = kHaierAcYrw02ButtonHealth
        self._.Health = on

    ## Get the Health (filter) setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from ir_Haier.cpp:800
    def getHealth(self) -> bool:
        return bool(self._.Health)

    ## Get the value of the current power setting.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from ir_Haier.cpp:804
    def getPower(self) -> bool:
        return bool(self._.Power)

    ## Change the power setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from ir_Haier.cpp:808-811
    def setPower(self, on: bool) -> None:
        self._.Button = kHaierAcYrw02ButtonPower
        self._.Power = on

    ## Change the power setting to On.
    ## EXACT translation from ir_Haier.cpp:814
    def on(self) -> None:
        self.setPower(True)

    ## Change the power setting to Off.
    ## EXACT translation from ir_Haier.cpp:817
    def off(self) -> None:
        self.setPower(False)

    ## Get the Sleep setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from ir_Haier.cpp:821
    def getSleep(self) -> bool:
        return bool(self._.Sleep)

    ## Set the Sleep setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from ir_Haier.cpp:825-828
    def setSleep(self, on: bool) -> None:
        self._.Button = kHaierAcYrw02ButtonSleep
        self._.Sleep = on

    ## Get the Turbo setting of the A/C.
    ## @return The current turbo setting.
    ## EXACT translation from ir_Haier.cpp:832
    def getTurbo(self) -> bool:
        return bool(self._.Turbo)

    ## Set the Turbo setting of the A/C.
    ## @param[in] on The desired turbo setting.
    ## @note Turbo & Quiet can't be on at the same time, and only in Heat/Cool mode
    ## EXACT translation from ir_Haier.cpp:837-845
    def setTurbo(self, on: bool) -> None:
        mode = self.getMode()
        if mode in [kHaierAcYrw02Cool, kHaierAcYrw02Heat]:
            self._.Turbo = on
            self._.Button = kHaierAcYrw02ButtonTurbo
            if on:
                self._.Quiet = False

    ## Get the Quiet setting of the A/C.
    ## @return The current Quiet setting.
    ## EXACT translation from ir_Haier.cpp:849
    def getQuiet(self) -> bool:
        return bool(self._.Quiet)

    ## Set the Quiet setting of the A/C.
    ## @param[in] on The desired Quiet setting.
    ## @note Turbo & Quiet can't be on at the same time, and only in Heat/Cool mode
    ## EXACT translation from ir_Haier.cpp:854-862
    def setQuiet(self, on: bool) -> None:
        mode = self.getMode()
        if mode in [kHaierAcYrw02Cool, kHaierAcYrw02Heat]:
            self._.Quiet = on
            self._.Button = kHaierAcYrw02ButtonTurbo
            if on:
                self._.Turbo = False

    ## Get the current fan speed setting.
    ## @return The current fan speed.
    ## EXACT translation from ir_Haier.cpp:866
    def getFan(self) -> int:
        return self._.Fan

    ## Set the speed of the fan.
    ## @param[in] speed The desired setting.
    ## EXACT translation from ir_Haier.cpp:870-880
    def setFan(self, speed: int) -> None:
        if speed in [kHaierAcYrw02FanLow, kHaierAcYrw02FanMed, kHaierAcYrw02FanHigh,
                     kHaierAcYrw02FanAuto]:
            self._.Fan = speed
            self._.Fan2 = 0 if (speed == kHaierAcYrw02FanAuto) else speed
            self._.Button = kHaierAcYrw02ButtonFan

    ## For backward compatibility. Use getSwingV() instead.
    ## Get the Vertical Swing position setting of the A/C.
    ## @return The native position/mode.
    ## EXACT translation from ir_Haier.cpp:885-887
    def getSwing(self) -> int:
        return self.getSwingV()

    ## For backward compatibility. Use setSwingV() instead.
    ## Set the Vertical Swing mode of the A/C.
    ## @param[in] pos The position/mode to set the vanes to.
    ## EXACT translation from ir_Haier.cpp:892
    def setSwing(self, pos: int) -> None:
        self.setSwingV(pos)

    ## Get the Vertical Swing position setting of the A/C.
    ## @return The native position/mode.
    ## EXACT translation from ir_Haier.cpp:896
    def getSwingV(self) -> int:
        return self._.SwingV

    ## Set the Vertical Swing mode of the A/C.
    ## @param[in] pos The position/mode to set the vanes to.
    ## EXACT translation from ir_Haier.cpp:900-918
    def setSwingV(self, pos: int) -> None:
        newpos = pos
        if pos in [kHaierAcYrw02SwingVOff, kHaierAcYrw02SwingVAuto,
                   kHaierAcYrw02SwingVTop, kHaierAcYrw02SwingVMiddle,
                   kHaierAcYrw02SwingVBottom, kHaierAcYrw02SwingVDown]:
            self._.Button = kHaierAcYrw02ButtonSwingV
        else:
            return  # Unexpected value so don't do anything.
        # Heat mode has no MIDDLE setting, use BOTTOM instead.
        if pos == kHaierAcYrw02SwingVMiddle and self._.Mode == kHaierAcYrw02Heat:
            newpos = kHaierAcYrw02SwingVBottom
        # BOTTOM is only allowed if we are in Heat mode, otherwise MIDDLE.
        if pos == kHaierAcYrw02SwingVBottom and self._.Mode != kHaierAcYrw02Heat:
            newpos = kHaierAcYrw02SwingVMiddle
        self._.SwingV = newpos

    ## Get the Horizontal Swing position setting of the A/C.
    ## @return The native position/mode.
    ## EXACT translation from ir_Haier.cpp:922
    def getSwingH(self) -> int:
        return self._.SwingH

    ## Set the Horizontal Swing mode of the A/C.
    ## @param[in] pos The position/mode to set the vanes to.
    ## EXACT translation from ir_Haier.cpp:926-937
    def setSwingH(self, pos: int) -> None:
        if pos in [kHaierAcYrw02SwingHMiddle, kHaierAcYrw02SwingHLeftMax,
                   kHaierAcYrw02SwingHLeft, kHaierAcYrw02SwingHRight,
                   kHaierAcYrw02SwingHRightMax, kHaierAcYrw02SwingHAuto]:
            self._.Button = kHaierAcYrw02ButtonSwingH
        else:
            return  # Unexpected value so don't do anything.
        self._.SwingH = pos

    ## Set the Timer operating mode.
    ## @param[in] mode The timer mode to use.
    ## EXACT translation from ir_Haier.cpp:942-957
    def setTimerMode(self, mode: int) -> None:
        self._.TimerMode = kHaierAcYrw02NoTimers if (mode > kHaierAcYrw02OffThenOnTimer) else mode
        if self._.TimerMode == kHaierAcYrw02NoTimers:
            self.setOnTimer(0)  # Disable the On timer.
            self.setOffTimer(0)  # Disable the Off timer.
        elif self._.TimerMode == kHaierAcYrw02OffTimer:
            self.setOnTimer(0)  # Disable the On timer.
        elif self._.TimerMode == kHaierAcYrw02OnTimer:
            self.setOffTimer(0)  # Disable the Off timer.

    ## Get the Timer operating mode.
    ## @return The mode of the timer is currently configured to.
    ## EXACT translation from ir_Haier.cpp:961
    def getTimerMode(self) -> int:
        return self._.TimerMode

    ## Set the number of minutes of the On Timer setting.
    ## @param[in] mins Nr. of Minutes for the Timer. `0` means disable the timer.
    ## EXACT translation from ir_Haier.cpp:965-985
    def setOnTimer(self, mins: int) -> None:
        nr_mins = min(23 * 60 + 59, mins)
        self._.OnTimerHrs = nr_mins // 60
        self._.OnTimerMins = nr_mins % 60

        enabled = (nr_mins > 0)
        mode = self.getTimerMode()
        if mode == kHaierAcYrw02OffTimer:
            mode = kHaierAcYrw02OffThenOnTimer if enabled else mode
        elif mode in [kHaierAcYrw02OnThenOffTimer, kHaierAcYrw02OffThenOnTimer]:
            mode = kHaierAcYrw02OffThenOnTimer if enabled else kHaierAcYrw02OffTimer
        else:
            # Enable/Disable the On timer for the simple case.
            mode = enabled << 1
        self._.TimerMode = mode

    ## Get the number of minutes of the On Timer setting.
    ## @return Nr of minutes.
    ## EXACT translation from ir_Haier.cpp:989-991
    def getOnTimer(self) -> int:
        return self._.OnTimerHrs * 60 + self._.OnTimerMins

    ## Set the number of minutes of the Off Timer setting.
    ## @param[in] mins Nr. of Minutes for the Timer. `0` means disable the timer.
    ## EXACT translation from ir_Haier.cpp:995-1015
    def setOffTimer(self, mins: int) -> None:
        nr_mins = min(23 * 60 + 59, mins)
        self._.OffTimerHrs = nr_mins // 60
        self._.OffTimerMins = nr_mins % 60

        enabled = (nr_mins > 0)
        mode = self.getTimerMode()
        if mode == kHaierAcYrw02OnTimer:
            mode = kHaierAcYrw02OnThenOffTimer if enabled else mode
        elif mode in [kHaierAcYrw02OnThenOffTimer, kHaierAcYrw02OffThenOnTimer]:
            mode = kHaierAcYrw02OnThenOffTimer if enabled else kHaierAcYrw02OnTimer
        else:
            # Enable/Disable the Off timer for the simple case.
            mode = enabled
        self._.TimerMode = mode

    ## Get the number of minutes of the Off Timer setting.
    ## @return Nr of minutes.
    ## EXACT translation from ir_Haier.cpp:1019-1021
    def getOffTimer(self) -> int:
        return self._.OffTimerHrs * 60 + self._.OffTimerMins

    ## Get the Lock setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from ir_Haier.cpp:1025
    def getLock(self) -> bool:
        return bool(self._.Lock)

    ## Set the Lock setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from ir_Haier.cpp:1029-1032
    def setLock(self, on: bool) -> None:
        self._.Button = kHaierAcYrw02ButtonLock
        self._.Lock = on


## Class for handling detailed Haier ACYRW02 A/C messages.
## EXACT translation from ir_Haier.cpp:1312-1342
class IRHaierACYRW02(IRHaierAC176):
    ## Class Constructor
    ## EXACT translation from ir_Haier.cpp:1316-1318
    def __init__(self) -> None:
        super().__init__()
        self.stateReset()

    ## Set the internal state from a valid code for this protocol.
    ## @param[in] new_code A valid code for this protocol.
    ## EXACT translation from ir_Haier.cpp:1330-1332
    def setRaw(self, new_code: List[int]) -> None:
        for i in range(min(len(new_code), kHaierACYRW02StateLength)):
            self._.raw[i] = new_code[i]

    ## Verify the checksum is valid for a given state.
    ## @param[in] state The array to verify the checksum of.
    ## @param[in] length The length of the state array.
    ## @return true, if the state has a valid checksum. Otherwise, false.
    ## EXACT translation from ir_Haier.cpp:1338-1341
    @staticmethod
    def validChecksum(state: List[int], length: int = kHaierACYRW02StateLength) -> bool:
        return IRHaierAC176.validChecksum(state, length)


## Class for handling detailed Haier 160 bit A/C messages.
## EXACT translation from ir_Haier.cpp:1491-2179
class IRHaierAC160:
    ## Class Constructor
    ## EXACT translation from ir_Haier.cpp:1495-1497
    def __init__(self) -> None:
        self._: HaierAc160Protocol = HaierAc160Protocol()
        self.stateReset()

    ## Reset the internal state to a fixed known good state.
    ## EXACT translation from ir_Haier.cpp:1518-1527
    def stateReset(self) -> None:
        for i in range(len(self._.raw)):
            self._.raw[i] = 0
        self._.Model = kHaierAcYrw02ModelA
        self._.Prefix = kHaierAc160Prefix
        self._.Temp = kHaierAcYrw02DefTempC - kHaierAcYrw02MinTempC
        self.setClean(False)
        self.setFan(kHaierAcYrw02FanAuto)
        self._.Power = True
        self._.Button = kHaierAcYrw02ButtonPower

    ## Calculate and set the checksum values for the internal state.
    ## EXACT translation from ir_Haier.cpp:1511-1515
    def checksum(self) -> None:
        self._.Sum = sumBytes(self._.raw, kHaierACYRW02StateLength - 1)
        self._.Sum2 = sumBytes(self._.raw[kHaierACYRW02StateLength:],
                               kHaierAC160StateLength - kHaierACYRW02StateLength - 1)

    ## Verify the checksum is valid for a given state.
    ## @param[in] state The array to verify the checksum of.
    ## @param[in] length The length of the state array.
    ## @return true, if the state has a valid checksum. Otherwise, false.
    ## EXACT translation from ir_Haier.cpp (same logic as AC176)
    @staticmethod
    def validChecksum(state: List[int], length: int = kHaierAC160StateLength) -> bool:
        return IRHaierAC176.validChecksum(state, length)

    ## Get a PTR to the internal state/code for this protocol.
    ## @return PTR to a code for this protocol based on the current internal state.
    ## EXACT translation from ir_Haier.cpp:1531-1534
    def getRaw(self) -> List[int]:
        self.checksum()
        return self._.raw

    ## Set the internal state from a valid code for this protocol.
    ## @param[in] new_code A valid code for this protocol.
    ## EXACT translation from ir_Haier.cpp:1538-1540
    def setRaw(self, new_code: List[int]) -> None:
        for i in range(min(len(new_code), kHaierAC160StateLength)):
            self._.raw[i] = new_code[i]

    ## Set the Button/Command setting of the A/C.
    ## @param[in] button The value of the button/command that was pressed.
    ## EXACT translation from ir_Haier.cpp:1544-1561
    def setButton(self, button: int) -> None:
        if button in [kHaierAcYrw02ButtonTempUp, kHaierAcYrw02ButtonTempDown,
                      kHaierAcYrw02ButtonSwingV, kHaierAcYrw02ButtonSwingH,
                      kHaierAcYrw02ButtonFan, kHaierAcYrw02ButtonPower,
                      kHaierAcYrw02ButtonMode, kHaierAcYrw02ButtonHealth,
                      kHaierAcYrw02ButtonTurbo, kHaierAcYrw02ButtonSleep,
                      kHaierAcYrw02ButtonLock, kHaierAc160ButtonClean,
                      kHaierAcYrw02ButtonCFAB]:
            self._.Button = button

    ## Get the Button/Command setting of the A/C.
    ## @return The value of the button/command that was pressed.
    ## EXACT translation from ir_Haier.cpp:1565
    def getButton(self) -> int:
        return self._.Button

    ## Set the operating mode of the A/C.
    ## @param[in] mode The desired operating mode.
    ## EXACT translation from ir_Haier.cpp:1569-1587
    def setMode(self, mode: int) -> None:
        if mode in [kHaierAcYrw02Auto, kHaierAcYrw02Dry, kHaierAcYrw02Fan]:
            # Turbo & Quiet is only available in Cool/Heat mode.
            self._.Turbo = False
            self._.Quiet = False
            self._.Button = kHaierAcYrw02ButtonMode
            self._.Mode = mode
        elif mode in [kHaierAcYrw02Cool, kHaierAcYrw02Heat]:
            self._.Button = kHaierAcYrw02ButtonMode
            self._.Mode = mode
        else:
            self.setMode(kHaierAcYrw02Auto)  # Unexpected, default to auto mode.
        self._.AuxHeating = (self._.Mode == kHaierAcYrw02Heat)  # Set only if heat mode.

    ## Get the operating mode setting of the A/C.
    ## @return The current operating mode setting.
    ## EXACT translation from ir_Haier.cpp:1591
    def getMode(self) -> int:
        return self._.Mode

    ## Set the default temperature units to use.
    ## @param[in] on Use Fahrenheit as the units.
    ##   true is Fahrenheit, false is Celsius.
    ## EXACT translation from ir_Haier.cpp:1596
    def setUseFahrenheit(self, on: bool) -> None:
        self._.UseFahrenheit = on

    ## Get the default temperature units in use.
    ## @return true is Fahrenheit, false is Celsius.
    ## EXACT translation from ir_Haier.cpp:1600
    def getUseFahrenheit(self) -> bool:
        return bool(self._.UseFahrenheit)

    ## Set the temperature.
    ## @param[in] degree The temperature in degrees.
    ## @param[in] fahrenheit Use units of Fahrenheit and set that as units used.
    ## EXACT translation from ir_Haier.cpp:1605-1639
    def setTemp(self, degree: int, fahrenheit: bool = False) -> None:
        old_temp = self.getTemp()
        if old_temp == degree:
            return

        if self._.UseFahrenheit == fahrenheit:
            if old_temp > degree:
                self._.Button = kHaierAcYrw02ButtonTempDown
            else:
                self._.Button = kHaierAcYrw02ButtonTempUp
        else:
            self._.Button = kHaierAcYrw02ButtonCFAB
        self._.UseFahrenheit = fahrenheit

        temp = degree
        if fahrenheit:
            if temp < kHaierAcYrw02MinTempF:
                temp = kHaierAcYrw02MinTempF
            elif temp > kHaierAcYrw02MaxTempF:
                temp = kHaierAcYrw02MaxTempF
            if degree >= 77:
                temp += 1
            if degree >= 79:
                temp += 1
            # See at IRHaierAC160::getTemp() comments for clarification
            self._.ExtraDegreeF = temp % 2
            self._.Temp = (temp - kHaierAcYrw02MinTempF - self._.ExtraDegreeF) >> 1
        else:
            if temp < kHaierAcYrw02MinTempC:
                temp = kHaierAcYrw02MinTempC
            elif temp > kHaierAcYrw02MaxTempC:
                temp = kHaierAcYrw02MaxTempC
            self._.Temp = temp - kHaierAcYrw02MinTempC

    ## Get the current temperature setting.
    ## The unit of temperature is specified by UseFahrenheit value.
    ## @return The current setting for temperature.
    ## EXACT translation from ir_Haier.cpp:1644-1688
    def getTemp(self) -> int:
        if not self._.UseFahrenheit:
            return self._.Temp + kHaierAcYrw02MinTempC
        degree = self._.Temp * 2 + kHaierAcYrw02MinTempF + self._.ExtraDegreeF
        # The way of coding the temperature in degree Fahrenheit is
        # kHaierAcYrw02MinTempF + Temp*2 + ExtraDegreeF, for example
        # Temp = 0b0011, ExtraDegreeF = 0b1, temperature is 60 + 3*2 + 1 = 67F
        # But around 78F there is unconsistency, see table in cpp file
        if degree >= 77:
            degree -= 1
        if degree >= 79:
            degree -= 1
        return degree

    ## Set the Clean setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from ir_Haier.cpp:1692-1696
    def setClean(self, on: bool) -> None:
        self._.Button = kHaierAc160ButtonClean
        self._.Clean = on
        self._.Clean2 = on

    ## Get the Clean setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from ir_Haier.cpp:1700
    def getClean(self) -> bool:
        return bool(self._.Clean and self._.Clean2)

    ## Get the value of the current power setting.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from ir_Haier.cpp:1704
    def getPower(self) -> bool:
        return bool(self._.Power)

    ## Change the power setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from ir_Haier.cpp:1708-1711
    def setPower(self, on: bool) -> None:
        self._.Button = kHaierAcYrw02ButtonPower
        self._.Power = on

    ## Change the power setting to On.
    ## EXACT translation from ir_Haier.cpp:1714
    def on(self) -> None:
        self.setPower(True)

    ## Change the power setting to Off.
    ## EXACT translation from ir_Haier.cpp:1717
    def off(self) -> None:
        self.setPower(False)

    ## Get the Sleep setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from ir_Haier.cpp:1721
    def getSleep(self) -> bool:
        return bool(self._.Sleep)

    ## Set the Sleep setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from ir_Haier.cpp:1725-1728
    def setSleep(self, on: bool) -> None:
        self._.Button = kHaierAcYrw02ButtonSleep
        self._.Sleep = on

    ## Get the Turbo setting of the A/C.
    ## @return The current turbo setting.
    ## EXACT translation from ir_Haier.cpp:1732
    def getTurbo(self) -> bool:
        return bool(self._.Turbo)

    ## Set the Turbo setting of the A/C.
    ## @param[in] on The desired turbo setting.
    ## @note Turbo & Quiet can't be on at the same time, and only in Heat/Cool mode
    ## EXACT translation from ir_Haier.cpp:1737-1745
    def setTurbo(self, on: bool) -> None:
        mode = self.getMode()
        if mode in [kHaierAcYrw02Cool, kHaierAcYrw02Heat]:
            self._.Turbo = on
            self._.Button = kHaierAcYrw02ButtonTurbo
            if on:
                self._.Quiet = False

    ## Get the Quiet setting of the A/C.
    ## @return The current Quiet setting.
    ## EXACT translation from ir_Haier.cpp:1749
    def getQuiet(self) -> bool:
        return bool(self._.Quiet)

    ## Set the Quiet setting of the A/C.
    ## @param[in] on The desired Quiet setting.
    ## @note Turbo & Quiet can't be on at the same time, and only in Heat/Cool mode
    ## EXACT translation from ir_Haier.cpp:1754-1762
    def setQuiet(self, on: bool) -> None:
        mode = self.getMode()
        if mode in [kHaierAcYrw02Cool, kHaierAcYrw02Heat]:
            self._.Quiet = on
            self._.Button = kHaierAcYrw02ButtonTurbo
            if on:
                self._.Turbo = False

    ## Get the value of the Aux Heating setting.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from ir_Haier.cpp:1766
    def getAuxHeating(self) -> bool:
        return bool(self._.AuxHeating)

    ## Change the Aux Heating setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from ir_Haier.cpp:1770-1773
    def setAuxHeating(self, on: bool) -> None:
        self._.Button = kHaierAc160ButtonAuxHeating
        self._.AuxHeating = on

    ## Get the value of the current Light toggle setting.
    ## @return true, the setting is on. false, the setting is off.
    ## @note This setting seems to be controlled just by the button setting.
    ## EXACT translation from ir_Haier.cpp:1778-1780
    def getLightToggle(self) -> bool:
        return self._.Button == kHaierAc160ButtonLight

    ## Set the Light Toggle setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## @note This setting seems to be controlled just by the button setting.
    ## EXACT translation from ir_Haier.cpp:1785-1787
    def setLightToggle(self, on: bool) -> None:
        self._.Button = kHaierAc160ButtonLight if on else kHaierAcYrw02ButtonPower

    ## Get the current fan speed setting.
    ## @return The current fan speed.
    ## EXACT translation from ir_Haier.cpp:1791
    def getFan(self) -> int:
        return self._.Fan

    ## Set the speed of the fan.
    ## @param[in] speed The desired setting.
    ## EXACT translation from ir_Haier.cpp:1795-1805
    def setFan(self, speed: int) -> None:
        if speed in [kHaierAcYrw02FanLow, kHaierAcYrw02FanMed, kHaierAcYrw02FanHigh,
                     kHaierAcYrw02FanAuto]:
            self._.Fan = speed
            self._.Fan2 = 0 if (speed == kHaierAcYrw02FanAuto) else speed
            self._.Button = kHaierAcYrw02ButtonFan

    ## Set the Health (filter) setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from ir_Haier.cpp:1809-1812
    def setHealth(self, on: bool) -> None:
        self._.Button = kHaierAcYrw02ButtonHealth
        self._.Health = on

    ## Get the Health (filter) setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from ir_Haier.cpp:1816
    def getHealth(self) -> bool:
        return bool(self._.Health)

    ## Get the Vertical Swing position setting of the A/C.
    ## @return The native position/mode.
    ## EXACT translation from ir_Haier.cpp:1820
    def getSwingV(self) -> int:
        return self._.SwingV

    ## Set the Vertical Swing mode of the A/C.
    ## @param[in] pos The position/mode to set the vanes to.
    ## EXACT translation from ir_Haier.cpp:1824-1839
    def setSwingV(self, pos: int) -> None:
        if pos in [kHaierAc160SwingVOff, kHaierAc160SwingVAuto, kHaierAc160SwingVTop,
                   kHaierAc160SwingVHighest, kHaierAc160SwingVHigh, kHaierAc160SwingVMiddle,
                   kHaierAc160SwingVLow, kHaierAc160SwingVLowest]:
            self._.Button = kHaierAcYrw02ButtonSwingV
            self._.SwingV = pos
        else:
            return  # If in doubt, Do nothing.

    ## Set the Timer operating mode.
    ## @param[in] mode The timer mode to use.
    ## EXACT translation from ir_Haier.cpp:1843-1858
    def setTimerMode(self, mode: int) -> None:
        self._.TimerMode = kHaierAcYrw02NoTimers if (mode > kHaierAcYrw02OffThenOnTimer) else mode
        if self._.TimerMode == kHaierAcYrw02NoTimers:
            self.setOnTimer(0)  # Disable the On timer.
            self.setOffTimer(0)  # Disable the Off timer.
        elif self._.TimerMode == kHaierAcYrw02OffTimer:
            self.setOnTimer(0)  # Disable the On timer.
        elif self._.TimerMode == kHaierAcYrw02OnTimer:
            self.setOffTimer(0)  # Disable the Off timer.

    ## Get the Timer operating mode.
    ## @return The mode of the timer is currently configured to.
    ## EXACT translation from ir_Haier.cpp:1862
    def getTimerMode(self) -> int:
        return self._.TimerMode

    ## Set the number of minutes of the On Timer setting.
    ## @param[in] mins Nr. of Minutes for the Timer. `0` means disable the timer.
    ## EXACT translation from ir_Haier.cpp:1866-1886
    def setOnTimer(self, mins: int) -> None:
        nr_mins = min(23 * 60 + 59, mins)
        self._.OnTimerHrs = nr_mins // 60
        self._.OnTimerMins = nr_mins % 60

        enabled = (nr_mins > 0)
        mode = self.getTimerMode()
        if mode == kHaierAcYrw02OffTimer:
            mode = kHaierAcYrw02OffThenOnTimer if enabled else mode
        elif mode in [kHaierAcYrw02OnThenOffTimer, kHaierAcYrw02OffThenOnTimer]:
            mode = kHaierAcYrw02OffThenOnTimer if enabled else kHaierAcYrw02OffTimer
        else:
            # Enable/Disable the On timer for the simple case.
            mode = enabled << 1
        self._.TimerMode = mode

    ## Get the number of minutes of the On Timer setting.
    ## @return Nr of minutes.
    ## EXACT translation from ir_Haier.cpp:1890-1892
    def getOnTimer(self) -> int:
        return self._.OnTimerHrs * 60 + self._.OnTimerMins

    ## Set the number of minutes of the Off Timer setting.
    ## @param[in] mins Nr. of Minutes for the Timer. `0` means disable the timer.
    ## EXACT translation from ir_Haier.cpp:1896-1916
    def setOffTimer(self, mins: int) -> None:
        nr_mins = min(23 * 60 + 59, mins)
        self._.OffTimerHrs = nr_mins // 60
        self._.OffTimerMins = nr_mins % 60

        enabled = (nr_mins > 0)
        mode = self.getTimerMode()
        if mode == kHaierAcYrw02OnTimer:
            mode = kHaierAcYrw02OnThenOffTimer if enabled else mode
        elif mode in [kHaierAcYrw02OnThenOffTimer, kHaierAcYrw02OffThenOnTimer]:
            mode = kHaierAcYrw02OnThenOffTimer if enabled else kHaierAcYrw02OnTimer
        else:
            # Enable/Disable the Off timer for the simple case.
            mode = enabled
        self._.TimerMode = mode

    ## Get the number of minutes of the Off Timer setting.
    ## @return Nr of minutes.
    ## EXACT translation from ir_Haier.cpp:1920-1922
    def getOffTimer(self) -> int:
        return self._.OffTimerHrs * 60 + self._.OffTimerMins

    ## Get the Lock setting of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    ## EXACT translation from ir_Haier.cpp:1926
    def getLock(self) -> bool:
        return bool(self._.Lock)

    ## Set the Lock setting of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    ## EXACT translation from ir_Haier.cpp:1930-1933
    def setLock(self, on: bool) -> None:
        self._.Button = kHaierAcYrw02ButtonLock
        self._.Lock = on


## Decode the supplied Haier HSU07-HEA03 remote message.
## Status: STABLE / Known to be working.
## EXACT translation from ir_Haier.cpp:1355-1388
def decodeHaierAC(results, offset: int = 1, nbits: int = kHaierACBits,
                  strict: bool = True) -> bool:
    """
    Decode a Haier A/C IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeHaierAC
    """
    # Import here to avoid circular imports
    from app.core.ir_protocols.ir_recv import matchMark, matchSpace, _matchGeneric, kHeader, kFooter, kMarkExcess

    if strict and nbits != kHaierACBits:
        return False  # Not strictly a HAIER_AC message.

    if results.rawlen <= (2 * nbits + kHeader) + kFooter - 1 + offset:
        return False  # Can't possibly be a valid HAIER_AC message.

    # Pre-Header
    if not matchMark(results.rawbuf[offset], kHaierAcHdr):
        return False
    offset += 1
    if not matchSpace(results.rawbuf[offset], kHaierAcHdr):
        return False
    offset += 1

    # Match Header + Data + Footer
    if not _matchGeneric(
        data_ptr=results.rawbuf[offset:],
        result_bits_ptr=None,
        result_bytes_ptr=results.state,
        use_bits=False,
        remaining=results.rawlen - offset,
        nbits=nbits,
        hdrmark=kHaierAcHdr,
        hdrspace=kHaierAcHdrGap,
        onemark=kHaierAcBitMark,
        onespace=kHaierAcOneSpace,
        zeromark=kHaierAcBitMark,
        zerospace=kHaierAcZeroSpace,
        footermark=kHaierAcBitMark,
        footerspace=kHaierAcMinGap,
        atleast=True,
        tolerance=25,
        excess=kMarkExcess,
        MSBfirst=True
    ):
        return False

    # Compliance
    if strict:
        if results.state[0] != kHaierAcPrefix:
            return False
        if not IRHaierAC.validChecksum(results.state, nbits // 8):
            return False

    # Success
    # results.decode_type = HAIER_AC  # Would set protocol type in C++
    results.bits = nbits
    return True


## Decode the supplied Haier YR-W02 remote A/C message.
## Status: BETA / Appears to be working.
## EXACT translation from ir_Haier.cpp:1401-1421
def decodeHaierACYRW02(results, offset: int = 1, nbits: int = kHaierACYRW02Bits,
                       strict: bool = True) -> bool:
    """
    Decode a Haier YR-W02 A/C IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeHaierACYRW02
    """
    if strict and nbits != kHaierACYRW02Bits:
        return False  # Not strictly a HAIER_AC_YRW02 message.

    # The protocol is almost exactly the same as HAIER_AC
    if not decodeHaierAC(results, offset, nbits, False):
        return False

    # Compliance
    if strict:
        if results.state[0] != kHaierAcYrw02ModelA:
            return False
        if not IRHaierACYRW02.validChecksum(results.state, nbits // 8):
            return False

    # Success
    # results.decode_type = HAIER_AC_YRW02  # Would set protocol type in C++
    return True


## Decode the supplied Haier 176 bit remote A/C message.
## Status: STABLE / Known to be working.
## EXACT translation from ir_Haier.cpp:1434-1455
def decodeHaierAC176(results, offset: int = 1, nbits: int = kHaierAC176Bits,
                     strict: bool = True) -> bool:
    """
    Decode a Haier 176 bit A/C IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeHaierAC176
    """
    if strict and nbits != kHaierAC176Bits:
        return False  # Not strictly a HAIER_AC176 message.

    # The protocol is almost exactly the same as HAIER_AC
    if not decodeHaierAC(results, offset, nbits, False):
        return False

    # Compliance
    if strict:
        if ((results.state[0] != kHaierAcYrw02ModelA) and
            (results.state[0] != kHaierAcYrw02ModelB)):
            return False
        if not IRHaierAC176.validChecksum(results.state, nbits // 8):
            return False

    # Success
    # results.decode_type = HAIER_AC176  # Would set protocol type in C++
    return True


## Decode the supplied Haier 160 bit remote A/C message.
## Status: STABLE / Known to be working.
## EXACT translation from ir_Haier.cpp:1468-1487
def decodeHaierAC160(results, offset: int = 1, nbits: int = kHaierAC160Bits,
                     strict: bool = True) -> bool:
    """
    Decode a Haier 160 bit A/C IR message.
    EXACT translation from IRremoteESP8266 IRrecv::decodeHaierAC160
    """
    if strict and nbits != kHaierAC160Bits:
        return False  # Not strictly a HAIER_AC160 message.

    # The protocol is almost exactly the same as HAIER_AC
    if not decodeHaierAC(results, offset, nbits, False):
        return False

    # Compliance
    if strict:
        if not IRHaierAC176.validChecksum(results.state, nbits // 8):
            return False

    # Success
    # results.decode_type = HAIER_AC160  # Would set protocol type in C++
    return True

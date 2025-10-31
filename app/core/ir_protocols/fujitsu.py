# Copyright 2017 Jonny Graham
# Copyright 2017-2022 David Conran
# Copyright 2021 siriuslzx
# Python translation: Direct conversion from C++ with NO optimizations

## @file
## @brief Support for Fujitsu A/C protocols.
## Fujitsu A/C support added by Jonny Graham & David Conran
## @warning Use of incorrect model may cause the A/C unit to lock up.
## e.g. An A/C that uses an AR-RAH1U remote may lock up requiring a physical
##      power rest, if incorrect model (ARRAH2E) is used with a Swing command.
##      The correct model for it is ARREB1E.
## @see https://github.com/crankyoldgit/IRremoteESP8266/issues/1376

from typing import List, Union

# Ref:
# These values are based on averages of measurements
kFujitsuAcHdrMark = 3324
kFujitsuAcHdrSpace = 1574
kFujitsuAcBitMark = 448
kFujitsuAcOneSpace = 1182
kFujitsuAcZeroSpace = 390
kFujitsuAcMinGap = 8100
kFujitsuAcExtraTolerance = 25  # Extra tolerance percentage (increased to handle compressed real-world captures).

# State lengths
kFujitsuAcStateLength = 16
kFujitsuAcStateLengthShort = 7
kFujitsuAcMinBits = kFujitsuAcStateLengthShort * 8
kFujitsuAcBits = kFujitsuAcStateLength * 8

# Constants
kFujitsuAcModeAuto = 0x0  # 0b000
kFujitsuAcModeCool = 0x1  # 0b001
kFujitsuAcModeDry = 0x2  # 0b010
kFujitsuAcModeFan = 0x3  # 0b011
kFujitsuAcModeHeat = 0x4  # 0b100

kFujitsuAcCmdStayOn = 0x00  # b00000000
kFujitsuAcCmdTurnOn = 0x01  # b00000001
kFujitsuAcCmdTurnOff = 0x02  # b00000010
kFujitsuAcCmdEcono = 0x09  # b00001001
kFujitsuAcCmdPowerful = 0x39  # b00111001
kFujitsuAcCmdStepVert = 0x6C  # b01101100
kFujitsuAcCmdToggleSwingVert = 0x6D  # b01101101
kFujitsuAcCmdStepHoriz = 0x79  # b01111001
kFujitsuAcCmdToggleSwingHoriz = 0x7A  # b01111010

kFujitsuAcFanAuto = 0x00
kFujitsuAcFanHigh = 0x01
kFujitsuAcFanMed = 0x02
kFujitsuAcFanLow = 0x03
kFujitsuAcFanQuiet = 0x04

kFujitsuAcMinHeat = 10  # 10C
kFujitsuAcMinTemp = 16  # 16C
kFujitsuAcMaxTemp = 30  # 30C
kFujitsuAcTempOffsetC = kFujitsuAcMinTemp
kFujitsuAcMinHeatF = 50  # 50F
kFujitsuAcMinTempF = 60  # 60F
kFujitsuAcMaxTempF = 88  # 88F
kFujitsuAcTempOffsetF = 44

kFujitsuAcSwingOff = 0x00
kFujitsuAcSwingVert = 0x01
kFujitsuAcSwingHoriz = 0x02
kFujitsuAcSwingBoth = 0x03

kFujitsuAcStopTimers = 0b00  # 0
kFujitsuAcSleepTimer = 0b01  # 1
kFujitsuAcOffTimer = 0b10  # 2
kFujitsuAcOnTimer = 0b11  # 3
kFujitsuAcTimerMax = 12 * 60  # Minutes.

# Models
ARRAH2E = 0
ARDB1 = 1
ARREB1E = 2
ARJW2 = 3
ARRY4 = 4
ARREW4E = 5


def sumBytes(state: List[int], length: int) -> int:
    """Sum bytes in a state array"""
    sum_val = 0
    for i in range(length):
        sum_val += state[i]
    return sum_val & 0xFF


def fahrenheitToCelsius(temp: float) -> float:
    """Convert Fahrenheit to Celsius"""
    return (temp - 32.0) / 1.8


## Native representation of a Fujitsu A/C message.
## This is a direct translation of the C++ union/struct
class FujitsuProtocol:
    def __init__(self):
        # The state arrays
        self.longcode = [0] * kFujitsuAcStateLength
        self.shortcode = [0] * kFujitsuAcStateLengthShort

    # Byte 0~1 - Fixed header (handled by longcode[0], longcode[1])

    # Byte 2
    @property
    def Id(self) -> int:
        return (self.longcode[2] >> 4) & 0x03

    @Id.setter
    def Id(self, value: int) -> None:
        self.longcode[2] = (self.longcode[2] & 0xCF) | ((value & 0x03) << 4)

    # Byte 5
    @property
    def Cmd(self) -> int:
        return self.longcode[5]

    @Cmd.setter
    def Cmd(self, value: int) -> None:
        self.longcode[5] = value & 0xFF

    # Byte 6
    @property
    def RestLength(self) -> int:
        return self.longcode[6]

    @RestLength.setter
    def RestLength(self, value: int) -> None:
        self.longcode[6] = value & 0xFF

    # Byte 7
    @property
    def Protocol(self) -> int:
        return self.longcode[7]

    @Protocol.setter
    def Protocol(self, value: int) -> None:
        self.longcode[7] = value & 0xFF

    # Byte 8
    @property
    def Power(self) -> int:
        return self.longcode[8] & 0x01

    @Power.setter
    def Power(self, value: bool) -> None:
        if value:
            self.longcode[8] |= 0x01
        else:
            self.longcode[8] &= 0xFE

    @property
    def Fahrenheit(self) -> int:
        return (self.longcode[8] >> 1) & 0x01

    @Fahrenheit.setter
    def Fahrenheit(self, value: bool) -> None:
        if value:
            self.longcode[8] |= 0x02
        else:
            self.longcode[8] &= 0xFD

    @property
    def Temp(self) -> int:
        return (self.longcode[8] >> 2) & 0x3F

    @Temp.setter
    def Temp(self, value: int) -> None:
        self.longcode[8] = (self.longcode[8] & 0x03) | ((value & 0x3F) << 2)

    # Byte 9
    @property
    def Mode(self) -> int:
        return self.longcode[9] & 0x07

    @Mode.setter
    def Mode(self, value: int) -> None:
        self.longcode[9] = (self.longcode[9] & 0xF8) | (value & 0x07)

    @property
    def Clean(self) -> int:
        return (self.longcode[9] >> 3) & 0x01

    @Clean.setter
    def Clean(self, value: bool) -> None:
        if value:
            self.longcode[9] |= 0x08
        else:
            self.longcode[9] &= 0xF7

    @property
    def TimerType(self) -> int:
        return (self.longcode[9] >> 4) & 0x03

    @TimerType.setter
    def TimerType(self, value: int) -> None:
        self.longcode[9] = (self.longcode[9] & 0xCF) | ((value & 0x03) << 4)

    # Byte 10
    @property
    def Fan(self) -> int:
        return self.longcode[10] & 0x07

    @Fan.setter
    def Fan(self, value: int) -> None:
        self.longcode[10] = (self.longcode[10] & 0xF8) | (value & 0x07)

    @property
    def Swing(self) -> int:
        return (self.longcode[10] >> 4) & 0x03

    @Swing.setter
    def Swing(self, value: int) -> None:
        self.longcode[10] = (self.longcode[10] & 0xCF) | ((value & 0x03) << 4)

    # Byte 11~13 - Timer values (11 bits each)
    @property
    def OffTimer(self) -> int:
        return self.longcode[11] | ((self.longcode[12] & 0x07) << 8)

    @OffTimer.setter
    def OffTimer(self, value: int) -> None:
        self.longcode[11] = value & 0xFF
        self.longcode[12] = (self.longcode[12] & 0xF8) | ((value >> 8) & 0x07)

    @property
    def OffTimerEnable(self) -> int:
        return (self.longcode[12] >> 3) & 0x01

    @OffTimerEnable.setter
    def OffTimerEnable(self, value: bool) -> None:
        if value:
            self.longcode[12] |= 0x08
        else:
            self.longcode[12] &= 0xF7

    @property
    def OnTimer(self) -> int:
        return ((self.longcode[12] >> 4) & 0x0F) | (self.longcode[13] << 4)

    @OnTimer.setter
    def OnTimer(self, value: int) -> None:
        self.longcode[12] = (self.longcode[12] & 0x0F) | ((value & 0x0F) << 4)
        self.longcode[13] = (value >> 4) & 0x7F

    @property
    def OnTimerEnable(self) -> int:
        return (self.longcode[13] >> 7) & 0x01

    @OnTimerEnable.setter
    def OnTimerEnable(self, value: bool) -> None:
        if value:
            self.longcode[13] |= 0x80
        else:
            self.longcode[13] &= 0x7F

    # Byte 14
    @property
    def Filter(self) -> int:
        return (self.longcode[14] >> 3) & 0x01

    @Filter.setter
    def Filter(self, value: bool) -> None:
        if value:
            self.longcode[14] |= 0x08
        else:
            self.longcode[14] &= 0xF7

    @property
    def unknown(self) -> int:
        return (self.longcode[14] >> 5) & 0x01

    @unknown.setter
    def unknown(self, value: Union[bool, int]) -> None:
        if value:
            self.longcode[14] |= 0x20
        else:
            self.longcode[14] &= 0xDF

    @property
    def OutsideQuiet(self) -> int:
        return (self.longcode[14] >> 7) & 0x01

    @OutsideQuiet.setter
    def OutsideQuiet(self, value: Union[bool, int]) -> None:
        if value:
            self.longcode[14] |= 0x80
        else:
            self.longcode[14] &= 0x7F


## Class for handling detailed Fujitsu A/C messages.
## Direct translation from C++ IRFujitsuAC class
class IRFujitsuAC:
    ## Class Constructor
    ## @param[in] model The enum for the model of A/C to be emulated.
    def __init__(self, model: int = ARRAH2E) -> None:
        self._: FujitsuProtocol = FujitsuProtocol()
        self._cmd: int = kFujitsuAcCmdStayOn
        self._model: int = model
        self._state_length: int = kFujitsuAcStateLength
        self._state_length_short: int = kFujitsuAcStateLengthShort
        self._rawstatemodified: bool = True
        self.setModel(model)
        self.stateReset()

    ## Set the currently emulated model of the A/C.
    ## @param[in] model An enum representing the model to support/emulate.
    def setModel(self, model: int) -> None:
        self._model = model
        if model == ARDB1:
            self._state_length = kFujitsuAcStateLength - 1
            self._state_length_short = kFujitsuAcStateLengthShort - 1
        elif model == ARJW2:
            self._state_length = kFujitsuAcStateLength - 1
            self._state_length_short = kFujitsuAcStateLengthShort - 1
        elif model == ARRY4:
            self._state_length = kFujitsuAcStateLength
            self._state_length_short = kFujitsuAcStateLengthShort
        elif model == ARRAH2E:
            self._state_length = kFujitsuAcStateLength
            self._state_length_short = kFujitsuAcStateLengthShort
        elif model == ARREB1E:
            self._state_length = kFujitsuAcStateLength
            self._state_length_short = kFujitsuAcStateLengthShort
        else:
            self._state_length = kFujitsuAcStateLength
            self._state_length_short = kFujitsuAcStateLengthShort

    ## Get the currently emulated/detected model of the A/C.
    ## @return The enum representing the model of A/C.
    def getModel(self) -> int:
        return self._model

    ## Reset the state of the remote to a known good state/sequence.
    def stateReset(self) -> None:
        for i in range(kFujitsuAcStateLength):
            self._.longcode[i] = 0
        self.setTemp(24)
        self._.Fan = kFujitsuAcFanHigh
        self._.Mode = kFujitsuAcModeCool
        self._.Swing = kFujitsuAcSwingBoth
        self._cmd = kFujitsuAcCmdTurnOn
        self._.Filter = False
        self._.Clean = False
        self._.TimerType = kFujitsuAcStopTimers
        self._.OnTimer = 0
        self._.OffTimer = 0
        self._.longcode[0] = 0x14
        self._.longcode[1] = 0x63
        self._.longcode[3] = 0x10
        self._.longcode[4] = 0x10
        self._rawstatemodified = True

    ## Update the length (size) of the state code for the current configuration.
    ## @return true, if use long codes; false, use short codes.
    def updateUseLongOrShort(self) -> bool:
        fullCmd = False
        if self._cmd == kFujitsuAcCmdTurnOff:  # 0x02
            self._.Cmd = self._cmd
            self._rawstatemodified = True
        elif self._cmd == kFujitsuAcCmdEcono:  # 0x09
            self._.Cmd = self._cmd
            self._rawstatemodified = True
        elif self._cmd == kFujitsuAcCmdPowerful:  # 0x39
            self._.Cmd = self._cmd
            self._rawstatemodified = True
        elif self._cmd == kFujitsuAcCmdStepVert:  # 0x6C
            self._.Cmd = self._cmd
            self._rawstatemodified = True
        elif self._cmd == kFujitsuAcCmdToggleSwingVert:  # 0x6D
            self._.Cmd = self._cmd
            self._rawstatemodified = True
        elif self._cmd == kFujitsuAcCmdStepHoriz:  # 0x79
            self._.Cmd = self._cmd
            self._rawstatemodified = True
        elif self._cmd == kFujitsuAcCmdToggleSwingHoriz:  # 0x7A
            self._.Cmd = self._cmd
            self._rawstatemodified = True
        else:
            if self._model == ARRY4:
                self._.Cmd = 0xFE
                self._rawstatemodified = True
            elif self._model == ARRAH2E:
                self._.Cmd = 0xFE
                self._rawstatemodified = True
            elif self._model == ARREB1E:
                self._.Cmd = 0xFE
                self._rawstatemodified = True
            elif self._model == ARREW4E:
                self._.Cmd = 0xFE
                self._rawstatemodified = True
            elif self._model == ARDB1:
                self._.Cmd = 0xFC
                self._rawstatemodified = True
            elif self._model == ARJW2:
                self._.Cmd = 0xFC
                self._rawstatemodified = True
            fullCmd = True
        return fullCmd

    ## Calculate and set the checksum values for the internal state.
    def checkSum(self) -> None:
        self._rawstatemodified = True
        if self.updateUseLongOrShort():  # Is it going to be a long code?
            # Nr. of bytes in the message after this byte.
            self._.RestLength = self._state_length - 7
            if self._model == ARREW4E:
                self._.Protocol = 0x31
            else:
                self._.Protocol = 0x30
            if self._cmd == kFujitsuAcCmdTurnOn:
                self._.Power = True
            else:
                self._.Power = self.get10CHeat()

            # These values depend on model
            if self._model != ARREB1E and self._model != ARREW4E:
                self._.OutsideQuiet = 0
                if self._model != ARRAH2E:
                    self._.TimerType = kFujitsuAcStopTimers
            if self._model != ARRY4:
                if self._model == ARRAH2E:
                    pass
                elif self._model == ARREW4E:
                    pass
                else:
                    self._.Clean = False
                self._.Filter = False
            # Set the On/Off/Sleep timer Nr of mins.
            self._.OffTimer = self.getOffSleepTimer()
            self._.OnTimer = self.getOnTimer()
            # Enable bit for the Off/Sleep timer
            if self._.OffTimer > 0:
                self._.OffTimerEnable = True
            else:
                self._.OffTimerEnable = False
            # Enable bit for the On timer
            if self._.OnTimer > 0:
                self._.OnTimerEnable = True
            else:
                self._.OnTimerEnable = False

            checksum = 0
            checksum_complement = 0
            if self._model == ARDB1:
                self._.Swing = kFujitsuAcSwingOff
                checksum = sumBytes(self._.longcode, self._state_length - 1)
                checksum_complement = 0x9B
            elif self._model == ARJW2:
                self._.Swing = kFujitsuAcSwingOff
                checksum = sumBytes(self._.longcode, self._state_length - 1)
                checksum_complement = 0x9B
            elif self._model == ARREB1E:
                self._.unknown = 1
                checksum = sumBytes(
                    self._.longcode[self._state_length_short :],
                    self._state_length - self._state_length_short - 1,
                )
            elif self._model == ARRAH2E:
                self._.unknown = 1
                checksum = sumBytes(
                    self._.longcode[self._state_length_short :],
                    self._state_length - self._state_length_short - 1,
                )
            elif self._model == ARRY4:
                self._.unknown = 1
                checksum = sumBytes(
                    self._.longcode[self._state_length_short :],
                    self._state_length - self._state_length_short - 1,
                )
            else:
                checksum = sumBytes(
                    self._.longcode[self._state_length_short :],
                    self._state_length - self._state_length_short - 1,
                )
            # and negate the checksum and store it in the last byte.
            self._.longcode[self._state_length - 1] = (checksum_complement - checksum) & 0xFF
        else:  # short codes
            for i in range(self._state_length_short):
                self._.shortcode[i] = self._.longcode[i]
            if self._model == ARRY4:
                # The last byte is the inverse of penultimate byte
                self._.shortcode[self._state_length_short - 1] = (
                    ~self._.shortcode[self._state_length_short - 2]
                ) & 0xFF
            elif self._model == ARRAH2E:
                # The last byte is the inverse of penultimate byte
                self._.shortcode[self._state_length_short - 1] = (
                    ~self._.shortcode[self._state_length_short - 2]
                ) & 0xFF
            elif self._model == ARREB1E:
                # The last byte is the inverse of penultimate byte
                self._.shortcode[self._state_length_short - 1] = (
                    ~self._.shortcode[self._state_length_short - 2]
                ) & 0xFF
            elif self._model == ARREW4E:
                # The last byte is the inverse of penultimate byte
                self._.shortcode[self._state_length_short - 1] = (
                    ~self._.shortcode[self._state_length_short - 2]
                ) & 0xFF
            else:
                pass  # We don't need to do anything for the others.

    ## Get the length (size) of the state code for the current configuration.
    ## @return The length of the state array required for this config.
    def getStateLength(self) -> int:
        if self.updateUseLongOrShort():
            return self._state_length
        else:
            return self._state_length_short

    ## Is the current binary state representation a long or a short code?
    ## @return true, if long; false, if short.
    def isLongCode(self) -> bool:
        if self._.Cmd == 0xFE:
            return True
        elif self._.Cmd == 0xFC:
            return True
        else:
            return False

    ## Get a PTR to the internal state/code for this protocol.
    ## @return PTR to a code for this protocol based on the current internal state.
    def getRaw(self) -> List[int]:
        self.checkSum()
        if self.isLongCode():
            return self._.longcode
        else:
            return self._.shortcode

    ## Build the internal state/config from the current (raw) A/C message.
    ## @param[in] length Size of the current/used (raw) A/C message array.
    def buildFromState(self, length: int) -> None:
        if length == kFujitsuAcStateLength - 1:
            self.setModel(ARDB1)
            # ARJW2 has horizontal swing.
            if self._.Swing > kFujitsuAcSwingVert:
                self.setModel(ARJW2)
        elif length == kFujitsuAcStateLengthShort - 1:
            self.setModel(ARDB1)
            # ARJW2 has horizontal swing.
            if self._.Swing > kFujitsuAcSwingVert:
                self.setModel(ARJW2)
        else:
            if self._.Cmd == kFujitsuAcCmdEcono:
                self.setModel(ARREB1E)
            elif self._.Cmd == kFujitsuAcCmdPowerful:
                self.setModel(ARREB1E)
            else:
                self.setModel(ARRAH2E)
        if self._.RestLength == 8:
            if self._model != ARJW2:
                self.setModel(ARDB1)
        elif self._.RestLength == 9:
            if self._model != ARREB1E:
                self.setModel(ARRAH2E)
        if self._.Power:
            self.setCmd(kFujitsuAcCmdTurnOn)
        else:
            self.setCmd(kFujitsuAcCmdStayOn)
        # Currently the only way we know how to tell ARRAH2E & ARRY4 apart is if
        # either the raw Filter or Clean setting is on.
        if self._model == ARRAH2E:
            if self._.Filter or self._.Clean:
                if not self.get10CHeat():
                    self.setModel(ARRY4)
        if self._state_length == kFujitsuAcStateLength:
            if self._.OutsideQuiet:
                self.setModel(ARREB1E)
        if self._.Cmd == kFujitsuAcCmdTurnOff:
            self.setCmd(self._.Cmd)
        elif self._.Cmd == kFujitsuAcCmdStepHoriz:
            self.setCmd(self._.Cmd)
        elif self._.Cmd == kFujitsuAcCmdToggleSwingHoriz:
            self.setCmd(self._.Cmd)
        elif self._.Cmd == kFujitsuAcCmdStepVert:
            self.setCmd(self._.Cmd)
        elif self._.Cmd == kFujitsuAcCmdToggleSwingVert:
            self.setCmd(self._.Cmd)
        elif self._.Cmd == kFujitsuAcCmdEcono:
            self.setCmd(self._.Cmd)
        elif self._.Cmd == kFujitsuAcCmdPowerful:
            self.setCmd(self._.Cmd)
        if self._.Protocol == 0x31:
            self.setModel(ARREW4E)

    ## Set the internal state from a valid code for this protocol.
    ## @param[in] newState A valid code for this protocol.
    ## @param[in] length Size of the newState array.
    ## @return true, if successful; Otherwise false. (i.e. size check)
    def setRaw(self, newState: List[int], length: int) -> bool:
        if length > kFujitsuAcStateLength:
            return False
        for i in range(kFujitsuAcStateLength):
            if i < length:
                self._.longcode[i] = newState[i]
            else:
                self._.longcode[i] = 0
        self.buildFromState(length)
        self._rawstatemodified = False
        return True

    ## Request the A/C to step the Horizontal Swing.
    def stepHoriz(self) -> None:
        self.setCmd(kFujitsuAcCmdStepHoriz)

    ## Request the A/C to toggle the Horizontal Swing mode.
    ## @param[in] update Do we need to update the general swing config?
    def toggleSwingHoriz(self, update: bool = True) -> None:
        # Toggle the current setting.
        if update:
            self.setSwing(self.getSwing() ^ kFujitsuAcSwingHoriz)
        # and set the appropriate special command.
        self.setCmd(kFujitsuAcCmdToggleSwingHoriz)

    ## Request the A/C to step the Vertical Swing.
    def stepVert(self) -> None:
        self.setCmd(kFujitsuAcCmdStepVert)

    ## Request the A/C to toggle the Vertical Swing mode.
    ## @param[in] update Do we need to update the general swing config?
    def toggleSwingVert(self, update: bool = True) -> None:
        # Toggle the current setting.
        if update:
            self.setSwing(self.getSwing() ^ kFujitsuAcSwingVert)
        # and set the appropriate special command.
        self.setCmd(kFujitsuAcCmdToggleSwingVert)

    ## Set the requested (special) command part for the A/C message.
    ## @param[in] cmd The special command code.
    def setCmd(self, cmd: int) -> None:
        if cmd == kFujitsuAcCmdTurnOff:
            self._cmd = cmd
        elif cmd == kFujitsuAcCmdTurnOn:
            self._cmd = cmd
        elif cmd == kFujitsuAcCmdStayOn:
            self._cmd = cmd
        elif cmd == kFujitsuAcCmdStepVert:
            self._cmd = cmd
        elif cmd == kFujitsuAcCmdToggleSwingVert:
            self._cmd = cmd
        elif cmd == kFujitsuAcCmdStepHoriz:
            # Only these remotes have horizontal.
            if self._model == ARRAH2E:
                self._cmd = cmd
            elif self._model == ARJW2:
                self._cmd = cmd
            else:
                self._cmd = kFujitsuAcCmdStayOn
        elif cmd == kFujitsuAcCmdToggleSwingHoriz:
            # Only these remotes have horizontal.
            if self._model == ARRAH2E:
                self._cmd = cmd
            elif self._model == ARJW2:
                self._cmd = cmd
            else:
                self._cmd = kFujitsuAcCmdStayOn
        elif cmd == kFujitsuAcCmdEcono:
            # Only these remotes have these commands.
            if self._model == ARREB1E:
                self._cmd = cmd
            elif self._model == ARREW4E:
                self._cmd = cmd
            else:
                self._cmd = kFujitsuAcCmdStayOn
        elif cmd == kFujitsuAcCmdPowerful:
            # Only these remotes have these commands.
            if self._model == ARREB1E:
                self._cmd = cmd
            elif self._model == ARREW4E:
                self._cmd = cmd
            else:
                self._cmd = kFujitsuAcCmdStayOn
        else:
            self._cmd = kFujitsuAcCmdStayOn

    ## Set the requested (special) command part for the A/C message.
    ## @return The special command code.
    def getCmd(self) -> int:
        return self._cmd

    ## Change the power setting.
    ## @param[in] on true, the setting is on. false, the setting is off.
    def setPower(self, on: bool) -> None:
        if on:
            self.setCmd(kFujitsuAcCmdTurnOn)
        else:
            self.setCmd(kFujitsuAcCmdTurnOff)

    ## Set the requested power state of the A/C to off.
    def off(self) -> None:
        self.setPower(False)

    ## Set the requested power state of the A/C to on.
    def on(self) -> None:
        self.setPower(True)

    ## Get the value of the current power setting.
    ## @return true, the setting is on. false, the setting is off.
    def getPower(self) -> bool:
        return self._cmd != kFujitsuAcCmdTurnOff

    ## Set the Outside Quiet mode of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    def setOutsideQuiet(self, on: Union[bool, int]) -> None:
        self._.OutsideQuiet = on
        self._rawstatemodified = True
        self.setCmd(kFujitsuAcCmdStayOn)  # No special command involved.

    ## Get the Outside Quiet mode status of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    def getOutsideQuiet(self) -> bool:
        # Only ARREB1E & ARREW4E seems to have this mode.
        if self._model == ARREB1E:
            return self._.OutsideQuiet
        elif self._model == ARREW4E:
            return self._.OutsideQuiet
        else:
            return False

    ## Set the temperature.
    ## @param[in] temp The temperature in degrees.
    ## @param[in] useCelsius Use Celsius or Fahrenheit?
    def setTemp(self, temp: Union[int, float], useCelsius: bool = True) -> None:
        mintemp = 0.0
        maxtemp = 0.0
        offset = 0
        _useCelsius = False
        _temp = 0.0

        # These models have native Fahrenheit & Celsius upport.
        if self._model == ARREW4E:
            _useCelsius = useCelsius
            _temp = temp
        else:
            # Make sure everything else uses Celsius.
            _useCelsius = True
            if useCelsius:
                _temp = temp
            else:
                _temp = fahrenheitToCelsius(temp)
        self.setCelsius(_useCelsius)
        if _useCelsius:
            mintemp = kFujitsuAcMinTemp
            maxtemp = kFujitsuAcMaxTemp
            offset = kFujitsuAcTempOffsetC
        else:
            mintemp = kFujitsuAcMinTempF
            maxtemp = kFujitsuAcMaxTempF
            offset = kFujitsuAcTempOffsetF
        _temp = max(mintemp, _temp)
        _temp = min(maxtemp, _temp)
        if _useCelsius:
            if self._model == ARREW4E:
                self._.Temp = int((_temp - (offset / 2)) * 2)
            else:
                self._.Temp = int((_temp - offset) * 4)
        else:
            self._.Temp = int(_temp - offset)
        self._rawstatemodified = True
        self.setCmd(kFujitsuAcCmdStayOn)  # No special command involved.

    ## Get the current temperature setting.
    ## @return The current setting for temp. in degrees of the currently set units.
    def getTemp(self) -> float:
        if self._model == ARREW4E:
            if self._.Fahrenheit:  # Currently only ARREW4E supports native Fahrenheit.
                return self._.Temp + kFujitsuAcTempOffsetF
            else:
                return (self._.Temp / 2.0) + (kFujitsuAcMinTemp / 2)
        else:
            return self._.Temp / 4 + kFujitsuAcMinTemp

    ## Set the speed of the fan.
    ## @param[in] fanSpeed The desired setting.
    def setFanSpeed(self, fanSpeed: int) -> None:
        if fanSpeed > kFujitsuAcFanQuiet:
            self._.Fan = kFujitsuAcFanHigh  # Set the fan to maximum if out of range.
        else:
            self._.Fan = fanSpeed
        self._rawstatemodified = True
        self.setCmd(kFujitsuAcCmdStayOn)  # No special command involved.

    ## Get the current fan speed setting.
    ## @return The current fan speed.
    def getFanSpeed(self) -> int:
        return self._.Fan

    ## Set the operating mode of the A/C.
    ## @param[in] mode The desired operating mode.
    def setMode(self, mode: int) -> None:
        if mode > kFujitsuAcModeHeat:
            self._.Mode = kFujitsuAcModeHeat  # Set the mode to maximum if out of range.
        else:
            self._.Mode = mode
        self._rawstatemodified = True
        self.setCmd(kFujitsuAcCmdStayOn)  # No special command involved.

    ## Get the operating mode setting of the A/C.
    ## @return The current operating mode setting.
    def getMode(self) -> int:
        return self._.Mode

    ## Set the requested swing operation mode of the A/C unit.
    ## @param[in] swingMode The swingMode code for the A/C.
    ##   Vertical, Horizon, or Both. See constants for details.
    ## @note Not all models support all possible swing modes.
    def setSwing(self, swingMode: int) -> None:
        self._.Swing = swingMode
        self._rawstatemodified = True
        # No Horizontal support.
        if self._model == ARDB1:
            # Set the mode to max if out of range
            if swingMode > kFujitsuAcSwingVert:
                self._.Swing = kFujitsuAcSwingVert
        elif self._model == ARREB1E:
            # Set the mode to max if out of range
            if swingMode > kFujitsuAcSwingVert:
                self._.Swing = kFujitsuAcSwingVert
        elif self._model == ARRY4:
            # Set the mode to max if out of range
            if swingMode > kFujitsuAcSwingVert:
                self._.Swing = kFujitsuAcSwingVert
        # Has Horizontal support.
        elif self._model == ARRAH2E:
            # Set the mode to max if out of range
            if swingMode > kFujitsuAcSwingBoth:
                self._.Swing = kFujitsuAcSwingBoth
        elif self._model == ARJW2:
            # Set the mode to max if out of range
            if swingMode > kFujitsuAcSwingBoth:
                self._.Swing = kFujitsuAcSwingBoth
        else:
            # Set the mode to max if out of range
            if swingMode > kFujitsuAcSwingBoth:
                self._.Swing = kFujitsuAcSwingBoth
        self.setCmd(kFujitsuAcCmdStayOn)  # No special command involved.

    ## Get the requested swing operation mode of the A/C unit.
    ## @return The contents of the swing state/mode.
    def getSwing(self) -> int:
        return self._.Swing

    ## Set the Clean mode of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    def setClean(self, on: bool) -> None:
        self._.Clean = on
        self._rawstatemodified = True
        self.setCmd(kFujitsuAcCmdStayOn)  # No special command involved.

    ## Get the Clean mode status of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    def getClean(self) -> bool:
        if self._model == ARRY4:
            return self._.Clean
        else:
            return False

    ## Set the Filter mode status of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    def setFilter(self, on: bool) -> None:
        self._.Filter = on
        self._rawstatemodified = True
        self.setCmd(kFujitsuAcCmdStayOn)  # No special command involved.

    ## Get the Filter mode status of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    def getFilter(self) -> bool:
        if self._model == ARRY4:
            return self._.Filter
        else:
            return False

    ## Set the 10C heat status of the A/C.
    ## @param[in] on true, the setting is on. false, the setting is off.
    def set10CHeat(self, on: bool) -> None:
        # Only selected models support this.
        if self._model == ARRAH2E:
            self.setClean(on)  # 10C Heat uses the same bit as Clean
            if on:
                self._.Mode = kFujitsuAcModeFan
                self._.Power = True
                self._.Fan = kFujitsuAcFanAuto
                self._.Swing = kFujitsuAcSwingOff
                self._rawstatemodified = True
        elif self._model == ARREW4E:
            self.setClean(on)  # 10C Heat uses the same bit as Clean
            if on:
                self._.Mode = kFujitsuAcModeFan
                self._.Power = True
                self._.Fan = kFujitsuAcFanAuto
                self._.Swing = kFujitsuAcSwingOff
                self._rawstatemodified = True
        else:
            pass

    ## Get the 10C heat status of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    def get10CHeat(self) -> bool:
        if self._model == ARRAH2E:
            return (
                self._.Clean
                and self._.Power
                and self._.Mode == kFujitsuAcModeFan
                and self._.Fan == kFujitsuAcFanAuto
                and self._.Swing == kFujitsuAcSwingOff
            )
        elif self._model == ARREW4E:
            return (
                self._.Clean
                and self._.Power
                and self._.Mode == kFujitsuAcModeFan
                and self._.Fan == kFujitsuAcFanAuto
                and self._.Swing == kFujitsuAcSwingOff
            )
        else:
            return False

    ## Get the Timer type of the A/C message.
    ## @return The current timer type in numeric form.
    def getTimerType(self) -> int:
        # These models seem to have timer support.
        if self._model == ARRAH2E:
            return self._.TimerType
        elif self._model == ARREB1E:
            return self._.TimerType
        else:
            return kFujitsuAcStopTimers

    ## Set the Timer type of the A/C message.
    ## @param[in] timertype The kind of timer to use for the message.
    def setTimerType(self, timertype: int) -> None:
        if timertype == kFujitsuAcSleepTimer:
            self._.TimerType = timertype
        elif timertype == kFujitsuAcOnTimer:
            self._.TimerType = timertype
        elif timertype == kFujitsuAcOffTimer:
            self._.TimerType = timertype
        elif timertype == kFujitsuAcStopTimers:
            self._.TimerType = timertype
        else:
            self._.TimerType = kFujitsuAcStopTimers
        self._rawstatemodified = True

    ## Get the On Timer setting of the A/C.
    ## @return nr of minutes left on the timer. 0 means disabled/not supported.
    def getOnTimer(self) -> int:
        if self.getTimerType() == kFujitsuAcOnTimer:
            return self._.OnTimer
        return 0

    ## Set the On Timer setting of the A/C.
    ## @param[in] nr_mins Nr. of minutes to set the timer to. 0 means disabled.
    def setOnTimer(self, nr_mins: int) -> None:
        self._.OnTimer = min(kFujitsuAcTimerMax, nr_mins)  # Bounds check.
        self._rawstatemodified = True
        if self._.OnTimer:
            self._.TimerType = kFujitsuAcOnTimer
        else:
            if self.getTimerType() == kFujitsuAcOnTimer:
                self._.TimerType = kFujitsuAcStopTimers

    ## Get the Off/Sleep Timer setting of the A/C.
    ## @return nr of minutes left on the timer. 0 means disabled/not supported.
    def getOffSleepTimer(self) -> int:
        timer_type = self.getTimerType()
        if timer_type == kFujitsuAcOffTimer:
            return self._.OffTimer
        elif timer_type == kFujitsuAcSleepTimer:
            return self._.OffTimer
        else:
            return 0

    ## Set the Off/Sleep Timer time for the A/C.
    ## @param[in] nr_mins Nr. of minutes to set the timer to. 0 means disabled.
    def setOffSleepTimer(self, nr_mins: int) -> None:
        self._.OffTimer = min(kFujitsuAcTimerMax, nr_mins)  # Bounds check.
        self._rawstatemodified = True

    ## Set the Off Timer time for the A/C.
    ## @param[in] nr_mins Nr. of minutes to set the timer to. 0 means disabled.
    def setOffTimer(self, nr_mins: int) -> None:
        self.setOffSleepTimer(nr_mins)  # This will also set _rawstatemodified to true.
        if nr_mins:
            self._.TimerType = kFujitsuAcOffTimer
        else:
            if self.getTimerType() != kFujitsuAcOnTimer:
                self._.TimerType = kFujitsuAcStopTimers

    ## Set the Sleep Timer time for the A/C.
    ## @param[in] nr_mins Nr. of minutes to set the timer to. 0 means disabled.
    def setSleepTimer(self, nr_mins: int) -> None:
        self.setOffSleepTimer(nr_mins)  # This will also set _rawstatemodified to true.
        if nr_mins:
            self._.TimerType = kFujitsuAcSleepTimer
        else:
            if self.getTimerType() != kFujitsuAcOnTimer:
                self._.TimerType = kFujitsuAcStopTimers

    ## Verify the checksum is valid for a given state.
    ## @param[in] state The array to verify the checksum of.
    ## @param[in] length The length of the state array.
    ## @return true, if the state has a valid checksum. Otherwise, false.
    @staticmethod
    def validChecksum(state: List[int], length: int) -> bool:
        sum_val = 0
        sum_complement = 0
        checksum = state[length - 1]
        if length == kFujitsuAcStateLengthShort:  # ARRAH2E, ARREB1E, & ARRY4
            return state[length - 1] == ((~state[length - 2]) & 0xFF)
        elif length == kFujitsuAcStateLength - 1:  # ARDB1 & ARJW2
            sum_val = sumBytes(state, length - 1)
            sum_complement = 0x9B
        elif length == kFujitsuAcStateLength:  # ARRAH2E, ARRY4, & ARREB1E
            sum_val = sumBytes(
                state[kFujitsuAcStateLengthShort:], length - 1 - kFujitsuAcStateLengthShort
            )
        else:  # Includes ARDB1 & ARJW2 short.
            return True  # Assume the checksum is valid for other lengths.
        return checksum == ((sum_complement - sum_val) & 0xFF)  # Does it match?

    ## Set the device's remote ID number.
    ## @param[in] num The ID for the remote. Valid number range is 0 to 3.
    def setId(self, num: int) -> None:
        self._.Id = num
        self._rawstatemodified = True

    ## Get the current device's remote ID number.
    ## @return The current device's remote ID number.
    def getId(self) -> int:
        return self._.Id

    ## Set the Temperature units for the A/C.
    ## @param[in] on true, use Celsius. false, use Fahrenheit.
    def setCelsius(self, on: bool) -> None:
        self._.Fahrenheit = not on
        self._rawstatemodified = True

    ## Get the Clean mode status of the A/C.
    ## @return true, the setting is on. false, the setting is off.
    def getCelsius(self) -> bool:
        return not self._.Fahrenheit


## Send a Fujitsu A/C formatted message.
## Status: STABLE / Known Good.
## @param[in] data The message to be sent.
## @param[in] nbytes The number of bytes of message to be sent.
##   Typically one of:
##          kFujitsuAcStateLength,
##          kFujitsuAcStateLength - 1,
##          kFujitsuAcStateLengthShort,
##          kFujitsuAcStateLengthShort - 1
## @param[in] repeat The number of times the command is to be repeated.
## Direct translation from IRremoteESP8266 IRsend::sendFujitsuAC (lines 53-59)
def sendFujitsuAC(data: List[int], nbytes: int) -> List[int]:
    """
    Send a Fujitsu A/C formatted message.
    Adapted from IRremoteESP8266 IRsend::sendFujitsuAC (hardware params removed).

    This is a wrapper around sendGeneric() with Fujitsu-specific timing constants.
    """
    # Import here to avoid circular import
    from app.core.ir_protocols.ir_send import sendGeneric

    return sendGeneric(
        headermark=kFujitsuAcHdrMark,
        headerspace=kFujitsuAcHdrSpace,
        onemark=kFujitsuAcBitMark,
        onespace=kFujitsuAcOneSpace,
        zeromark=kFujitsuAcBitMark,
        zerospace=kFujitsuAcZeroSpace,
        footermark=kFujitsuAcBitMark,
        gap=0,  # No trailing gap for single message (kFujitsuAcMinGap only for repeats)
        dataptr=data,
        nbytes=nbytes,
        MSBfirst=False,  # LSB first
        repeat=0,  # Single message only
    )

import React from 'react';

import { SPEED_CONSTANTS, ModeInputType, speedDirectionToSliderValue, sliderValueToSpeedDirection, LoopType } from '../shared/speedStuff';

import './SpeedModeInput.css';

const SpeedModeInput = ({ modeType, setPlaySpeed, setPlayDirection, setLoopType }: {
  modeType: ModeInputType,
  setPlaySpeed: (speed: number | null) => void,
  setPlayDirection: (direction: boolean) => void,
  setLoopType: (type: LoopType) => void,
}) => {
  let value: number;
  switch (modeType) {
    case "rewind":
      value = speedDirectionToSliderValue(SPEED_CONSTANTS.REWIND, false);
      break;
    case "pause":
      value = 0;
      break;
    case "play":
      value = speedDirectionToSliderValue(SPEED_CONSTANTS.PLAY, true);
      break;
    case "fast-forward":
      value = speedDirectionToSliderValue(SPEED_CONSTANTS.FAST_FORWARD, true);
      break;
  }
  return (
      <input
        id={`${modeType}-mode-input`}
        type="range"
        // min/max covers only legitimate speed values, skipping past "illegal" stopped values
        min={speedDirectionToSliderValue(SPEED_CONSTANTS.MAX, false)}
        max={speedDirectionToSliderValue(SPEED_CONSTANTS.MAX, true)}
        value={value}
        readOnly
        onClick={() => {
          setLoopType(null);
          const [speed, direction] = sliderValueToSpeedDirection(value);
          setPlaySpeed(speed);
          setPlayDirection(direction);
        }}
      />
  );
};

export default SpeedModeInput;

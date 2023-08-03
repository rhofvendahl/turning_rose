import React from 'react';

import './Slider.css';
import { SPEED_CONSTANTS, ModeInputType, speedDirectionToSliderValue, sliderValueToSpeedDirection, LoopType } from '../shared/speedStuff';

const SpeedModeInput = ({ modeType, setPlaySpeed, setPlayDirection, setPlaying, setLoopType }: {
  modeType: ModeInputType,
  setPlaySpeed: (speed: number) => void,
  setPlayDirection: (direction: boolean) => void,
  setPlaying: (playing: boolean) => void,
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
          if (value === 0) {
            // Don't do anything with playSpeed or playDirection for now
            // Definitely going to want to get rid of playing and add playspeed === null
            setPlaySpeed(SPEED_CONSTANTS.MIN);
            setPlayDirection(true);
            setPlaying(false);
          } else {
            const [speed, direction] = sliderValueToSpeedDirection(value);
            console.log("SPEED DIR", speed, direction)
            setPlaySpeed(speed);
            setPlayDirection(direction);
            setPlaying(true);
          }
        }}
      />
  );
};

export default SpeedModeInput;

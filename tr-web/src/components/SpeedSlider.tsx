import React, { useEffect, useState } from "react";

import { SPEED_CONSTANTS, ControlType, speedDirectionToSliderValue, sliderValueToSpeedDirection } from "../shared/controlsStuff"

import "./SpeedSlider.css";

const SpeedSlider = ({ playSpeed, setPlaySpeed, playDirection, setPlayDirection, controlType, setControlType }: {
  playSpeed: number | null,
  setPlaySpeed: (speed: number | null) => void,
  playDirection: boolean,
  setPlayDirection: (direction: boolean) => void,
  controlType: ControlType,
  setControlType: (type: ControlType) => void,
}) => {
  const [sliderValue, setSliderValue] = useState(speedDirectionToSliderValue(playSpeed, playDirection));
  useEffect(() => {
    // Adapt playSpeed to the slider's range, which doesn't include "pause" values between -min and min
    const newSliderValue = speedDirectionToSliderValue(playSpeed, playDirection);
    setSliderValue(newSliderValue);
  }, [playSpeed, playDirection]);
  return (
    <input id="speed-slider"
      type="range"
        // min/max covers only legitimate speed values, skipping past "illegal" stopped values
        min={speedDirectionToSliderValue(SPEED_CONSTANTS.MAX, false)}
        max={speedDirectionToSliderValue(SPEED_CONSTANTS.MAX, true)}
        step=".01"
      value={sliderValue}
      onChange={(event) => {
        const value = parseFloat(event.target.value);
        const [speed, direction] = sliderValueToSpeedDirection(value);
        setPlaySpeed(speed);
        setPlayDirection(direction);
        setControlType("manual");
      }}
    />
  );
};

export default SpeedSlider;

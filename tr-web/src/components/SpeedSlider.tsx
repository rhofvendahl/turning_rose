import React, { useEffect, useState } from 'react';

import SpeedModeInput from './SpeedModeInput';'./SpeedModeInput';
import { SPEED_CONSTANTS, LoopType, SNAP_FROM, speedDirectionToSliderValue, sliderValueToSpeedDirection } from "../shared/speedStuff"

import './Slider.css';

const SpeedSlider = ({ playSpeed, setPlaySpeed, playDirection, setPlayDirection, setLoopType }: {
  playSpeed: number | null,
  setPlaySpeed: (speed: number | null) => void,
  playDirection: boolean,
  setPlayDirection: (direction: boolean) => void,
  setLoopType: (type: LoopType) => void,
}) => {
  const [sliderValue, setSliderValue] = useState(speedDirectionToSliderValue(playSpeed, playDirection));
  useEffect(() => {
    // Adapt playSpeed to the slider's range, which doesn't include "pause" values between -min and min
    const newSliderValue = speedDirectionToSliderValue(playSpeed, playDirection);
    console.log("PLAYSPEED CHANGED, NEW CURRENT", playSpeed, playDirection, newSliderValue);
    setSliderValue(newSliderValue);
  }, [playSpeed, playDirection]);
  return (
    <div id='slider-container'>
      {/* Weird to code, but simple way to ensure buttons are in right place */}
      <SpeedModeInput modeType={'rewind'} setPlaySpeed={setPlaySpeed} setPlayDirection={setPlayDirection} setLoopType={setLoopType}/>
      <SpeedModeInput modeType={'pause'} setPlaySpeed={setPlaySpeed} setPlayDirection={setPlayDirection} setLoopType={setLoopType}/>
      <SpeedModeInput modeType={'play'} setPlaySpeed={setPlaySpeed} setPlayDirection={setPlayDirection} setLoopType={setLoopType}/>
      <SpeedModeInput modeType={'fast-forward'} setPlaySpeed={setPlaySpeed} setPlayDirection={setPlayDirection} setLoopType={setLoopType}/>
      <input id="speed-input"
        type='range'
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
          setLoopType(null);
        }}
        onMouseUp={() => {
          // Snap to up if appropriate
          if (Math.abs(sliderValue) < SNAP_FROM) {
            console.log("Snapping to paused");
            setPlaySpeed(null);
            setPlayDirection(true);
            }
        }}
      />
    </div>
  );
};

export default SpeedSlider;

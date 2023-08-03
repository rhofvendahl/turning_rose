import React, { useEffect, useRef } from 'react';

import SpeedModeInput from './SpeedModeInput';'./SpeedModeInput';
import { SPEED_CONSTANTS, LoopType, SNAP_FROM, speedDirectionToSliderValue, sliderValueToSpeedDirection } from "../shared/speedStuff"

import './Slider.css';

const SpeedSlider = ({ playSpeed, setPlaySpeed, playDirection, setPlayDirection, playing, setPlaying, setLoopType }: {
  playSpeed: number,
  setPlaySpeed: (speed: number) => void,
  playDirection: boolean,
  setPlayDirection: (direction: boolean) => void,
  playing: boolean,
  setPlaying: (playing: boolean) => void,
  setLoopType: (type: LoopType) => void,
}) => {
  // const [sliderValue, setSliderValue] = useState(0);
  const sliderValueRef = useRef(playSpeed);
  useEffect(() => {
    // setSliderValue(playDirection ? playSpeed : -playSpeed);
    // Adapt playSpeed to the slider's range, which doesn't include "pause" values between -min and min
    sliderValueRef.current = speedDirectionToSliderValue(playSpeed, playDirection);
  }, [playSpeed, playDirection]);
  return (
    <div id='slider-container'>
      {/* Weird to code, but simple way to ensure buttons are in right place */}
      <SpeedModeInput modeType={'rewind'} setPlaySpeed={setPlaySpeed} setPlayDirection={setPlayDirection} setPlaying={setPlaying} setLoopType={setLoopType}/>
      <SpeedModeInput modeType={'pause'} setPlaySpeed={setPlaySpeed} setPlayDirection={setPlayDirection} setPlaying={setPlaying} setLoopType={setLoopType}/>
      <SpeedModeInput modeType={'play'} setPlaySpeed={setPlaySpeed} setPlayDirection={setPlayDirection} setPlaying={setPlaying} setLoopType={setLoopType}/>
      <SpeedModeInput modeType={'fast-forward'} setPlaySpeed={setPlaySpeed} setPlayDirection={setPlayDirection} setPlaying={setPlaying} setLoopType={setLoopType}/>
      <input id="speed-input"
        type='range'
          // min/max covers only legitimate speed values, skipping past "illegal" stopped values
          min={speedDirectionToSliderValue(SPEED_CONSTANTS.MAX, false)}
          max={speedDirectionToSliderValue(SPEED_CONSTANTS.MAX, true)}
          step=".01"
        value={sliderValueRef.current}
        onChange={(event) => {
          const value = parseFloat(event.target.value);
          const [speed, direction] = sliderValueToSpeedDirection(value);
          setPlaySpeed(speed);
          setPlayDirection(direction);
          setPlaying(speed !== 0);
          // Regardless, changes mean the user's taking control
          setLoopType(null);
        }}
        onMouseUp={() => {
          // Snap to pause if close to 0
          if (Math.abs(sliderValueRef.current) < SNAP_FROM) {
            setPlaySpeed(SPEED_CONSTANTS.MIN);
            setPlayDirection(true);
            setPlaying(false);
            }
        }}
      />
    </div>
  );
};

export default SpeedSlider;

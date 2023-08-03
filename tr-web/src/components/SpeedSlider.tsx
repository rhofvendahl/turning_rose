import React, { useEffect, useState } from 'react';

import './Slider.css';

// Some duplication here, but I don't feel like pulling this all into a custom hook at this time
type ControlType = 'bouncy' | 'cyclic' | 'slider';

const SpeedSlider = ({ playSpeed, setPlaySpeed, playDirection, setPlayDirection, playing, setPlaying, setControlType, minSpeed, maxSpeed }: {
  playSpeed: number,
  setPlaySpeed: (speed: number) => void,
  playDirection: boolean,
  setPlayDirection: (direction: boolean) => void,
  playing: boolean,
  setPlaying: (playing: boolean) => void,
  setControlType: (type: ControlType) => void,
  minSpeed: number,
  maxSpeed: number,
}) => {
  const [sliderValue, setSliderValue] = useState(0);
  useEffect(() => {
    setSliderValue(playDirection ? playSpeed : -playSpeed);
  }, [playSpeed, playDirection]);

  return (
    <div id='slider-container'>
      <div id='label'>Speed</div>
      <input type='range' min={-maxSpeed} max={maxSpeed} value={sliderValue} onChange={(event) => {
        const value = parseFloat(event.target.value);
        const suggestedSpeed = Math.abs(value);
        const suggestedDirection = value >= 0;
        // Essentially there'll be a range in the middle, between -minSpeed and +minSpeed, which counts as paused
        const pauseZone = suggestedSpeed < minSpeed;
        if (!pauseZone) {
          setPlaySpeed(suggestedSpeed);
          setPlayDirection(suggestedDirection);
        }
        setPlaying(!pauseZone);
        // Regardless, changes mean the user's taking control
        setControlType('slider');
        setSliderValue(value);
      }} onMouseUp={() => {
        // Snap to center if released within 'pause' zone
        if (Math.abs(sliderValue) < minSpeed) {
          setSliderValue(0);
        }
      }}/>
    </div>
  );
};

export default SpeedSlider;

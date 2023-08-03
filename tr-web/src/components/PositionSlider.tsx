import React, { useRef } from 'react';
import { Frame } from '../hooks/useFrame';

import './Slider.css';

// NOTE: At this time PositionSlider is unused, and as development continues elsewhere may fail to integrate back in
const PositionSlider = ({ frames, currentFrame, setCurrentFrame, playing, setPlaying }: {
  frames: Frame[],
  currentFrame: Frame | null,
  setCurrentFrame: (frame: Frame) => void,
  playing: boolean,
  setPlaying: (playing: boolean) => void,
}) => {
  if (currentFrame === null) {
    // Keeps display from jumping around when currentFrame loads
    return (
      <input type='range' value='0' readOnly/>
    )
  }

  // Playback is temporarily paused while dragging around, to be resumed on mouseup. This keeps track of that.
  const wasPlaying = useRef(playing);
  
  return (
    <div id='slider-container'>
      <div id='label'>Position</div>
      <input
        type='range'
        min='0'
        max={frames.length - 1}
        value={currentFrame.index}
        onChange={(event) => {
          const newIndex = parseInt(event.target.value);
          setCurrentFrame(frames[newIndex]);
        }}
        onMouseDown={() => {
          if (playing) {
            wasPlaying.current = playing;
            setPlaying(false);
          }
        }}
        onMouseUp={() => {
          if (wasPlaying.current) {
            setPlaying(true);
          }
        }}
      />
    </div>
  );
};

export default PositionSlider;

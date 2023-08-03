import React, { useEffect, useRef, useState } from 'react';

import { Frame } from '../hooks/useFrame';
import SpeedSlider from './SpeedSlider';
import PositionSlider from './PositionSlider';

import './Controls.css';

const SPEED_MIN = 2;
const SPEED_MAX = 30;

type ControlType = 'bouncy' | 'cyclic' | 'slider';

// The idea is that the speed is fast at the start, gets slow near the end (time to view rose), slowly moves backward, speeds up til the start, then can bounce back forward again.
// To do this we'll need a cosine function, with x as position and y as the rate of change (fps).
// Position has range [0, 1), returned speed has range [SPEED_MIN, SPEED_MAX]
const getSpeedBouncy = (position: number): number => {
  // At position = 1, we should be at the steep downward part of the cosine curve (1/4 through a period)
  const angle = position * (2 * Math.PI) / 4;
  // Cosine has range [0, 1], I think (could be off-by-one-ish)
  const cosine = Math.cos(angle);
  // Scale it to prevent zero values (they mess stuff up)
  return cosine * (SPEED_MAX - SPEED_MIN) + SPEED_MIN;
};

// For this one the speed begins slow, speeds up in the middle, then ends slow. So, 1/2 the period of a sine wave (if those terms make sense).
const getSpeedCyclic = (position: number): number => {
  const angle = position * (2 * Math.PI) / 2;
  // The peak of a standard cosine function is 1
  const sine = Math.sin(angle);
  return sine * (SPEED_MAX - SPEED_MIN) + SPEED_MIN;
};

// Returns a value with range [0, 1) representing the rate appropriate to some position, ignoring forward/back
const getSpeed = (position: number, controlType: ControlType): number => {
  switch (controlType) {
    case 'bouncy':
      return getSpeedBouncy(position);
    case 'cyclic':
      return getSpeedCyclic(position);
    // This really shouldn't happen
    case 'slider':
      return 0;
  }
}

// Bouncy, cyclic and slider rates all have range (-1, 1)
// NOTE: Relative rate does NOT correspond directly to fps. Basically the magnitude of the rate is scaled to be between ABS_RATE_MIN and ABS_RATE_MAX,
// and then the direction is applied to that value. Weird, but couldn't think of better.
const getNewSpeedDirection = ({ frameIndex, nFrames, prevSpeed, prevDirection, controlType, loop }: {
  frameIndex: number,
  nFrames: number,
  prevSpeed: number,
  prevDirection: boolean,
  controlType: ControlType,
  loop: boolean,
}): [number, boolean] => {
  const position = frameIndex / nFrames;
  const atStart = frameIndex <= 0;
  const atEnd = frameIndex >= nFrames - 1;

  const reachedTerminus = prevDirection && atEnd || !prevDirection && atStart;
  if (controlType === 'slider') {
    // Stop if appropriate
    if (reachedTerminus) {
      return [0, prevDirection];
    }
    return [prevSpeed, prevDirection];
  }
  // If it's not a loop, be ready to stop
  if (!loop) {
    if (reachedTerminus) {
      return [0, prevDirection];
    }
  }
  let speed = getSpeed(position, controlType);
  // Since it's a loop, be ready to turn around
  const direction = reachedTerminus ? !prevDirection : prevDirection;
  return [speed, direction];
};

// The number of frames that must be loaded before play starts
// Constant for now; might want to make it dependent on internet speed or something, later
const LOADED_THRESHOLD = 5;

// Call some function after n frames past current have loaded
const waitOnLoading = (frames: Frame[], currentFrameIndex: number, loadedThreshold: number, callOnLoaded: () => void) => {
  if (frames.length === 0) {
    return;
  }

  const waitingInterval = window.setInterval(() => {
    // Wait until frames have been created
    const remaining = frames.slice(currentFrameIndex)
    const nLoaded = remaining.filter((frame) => frame.model !== null).length;
    // If enough have loaded OR if all subsequent frames have loaded
    if (nLoaded >= loadedThreshold || nLoaded >= remaining.length) {
      callOnLoaded();
      window.clearInterval(waitingInterval);
    }
  }, 10);
};

const Controls = ({ frames, currentFrame, setCurrentFrame }: {
  frames: Frame[],
  currentFrame: Frame | null,
  setCurrentFrame: (frame: Frame) => void
}) => {
  const [playing, setPlaying] = useState(false);
  const [playTimeout, setPlayTimeout] = useState<number | null>(null);
  // speed has range [SPEED_MIN, SPEED_MAX]
  const [playSpeed, setPlaySpeed] = useState<number>(0);
  // true is forward, false is back
  const [playDirection, setPlayDirection] = useState<boolean>(true);
  const [playControlType, setPlayControlType] = useState<ControlType>('bouncy');

  // This allows access to the latest frame from within a timeout function
  const currentFrameRef = useRef(currentFrame);
  useEffect(() => {
    currentFrameRef.current = currentFrame;
  }, [currentFrame]);

  // This should only run once
  useEffect(() => {
    if (frames.length === 0) {
      return;
    }
    setPlaying(false);
    waitOnLoading(frames, 0, LOADED_THRESHOLD, () => setPlaying(true));
  }, [frames]);

  useEffect(() => {
    if (playing) {
      // Set play interval going if playing but no timeout (e.g. if frame transition has finished)
      if (playTimeout === null) {
        if (currentFrame === null) {
          return;
        };
        if (currentFrame.model === null) {
          // Wait a bit to allow loading to continue
          setPlaying(false);
          waitOnLoading(frames, currentFrame.index, LOADED_THRESHOLD, () => setPlaying(true));
          return;
        }
        const [speed, direction] = getNewSpeedDirection({
          frameIndex: currentFrame === null ? 0 : currentFrame.index,
          nFrames: frames.length,
          prevSpeed: playSpeed,
          prevDirection: playDirection,
          controlType: playControlType,
          // Might actually use this later
          loop: playControlType == 'bouncy' || playControlType == 'cyclic',
        });
        setPlaySpeed(speed);
        setPlayDirection(direction);
        if (speed === 0) {
          setPlaying(false);
          setPlayTimeout(null);
          return;
        }
        const interval = 1 / speed * 1000;
        const timeout = window.setTimeout(() => {
          if (currentFrameRef.current === null) {
            return;
          }
          const nextFrameIndex = direction ? currentFrameRef.current.index + 1 : currentFrameRef.current.index - 1;
          setCurrentFrame(frames[nextFrameIndex]);
          setPlayTimeout(null);
        }, interval);
        setPlayTimeout(timeout);
      }
    }
  }, [playing, playTimeout]);

  return (
    <div>
      <div id='buttons-container'>
        <button onClick={() => {
          // If player is at the start then play almost certainly means 'go forward'
          if (currentFrame && currentFrame.index === 0) {
            setPlayDirection(true);
            // Split the difference
            setPlaySpeed((SPEED_MAX + SPEED_MIN) / 2);
          }
          setPlaying(true);
        }}>Play</button>
        <button onClick={() => {
          setPlaying(false);
        }}>Pause</button>
        <button onClick={() => {
          setPlayControlType('bouncy');
          setPlaying(true);
          if (currentFrame !== null && currentFrame.index + 1 < frames.length) {
            const nextFrame = frames[currentFrame.index + 1];
            setCurrentFrame(nextFrame);
          }
        }}>Loop</button>
      </div>
      <div id='slider-container'>
        <SpeedSlider
          playSpeed={playSpeed}
          setPlaySpeed={setPlaySpeed}
          playDirection={playDirection}
          setPlayDirection={setPlayDirection}
          playing={playing}
          setPlaying={setPlaying}
          setControlType={setPlayControlType}
          minSpeed={SPEED_MIN}
          maxSpeed={SPEED_MAX}
        />
        <PositionSlider
          frames={frames}
          currentFrame={currentFrame}
          setCurrentFrame={setCurrentFrame}
          playing={playing}
          setPlaying={setPlaying}
        />
      </div>
    </div>
  );
};

export default Controls;
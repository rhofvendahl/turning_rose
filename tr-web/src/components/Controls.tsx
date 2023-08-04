import React, { useEffect, useRef, useState } from "react";

import { Frame } from "../hooks/useFrame";
import SpeedSlider from "./SpeedSlider";
import SpeedModeButton from "./SpeedModeButton";

import "./Controls.css";
import { SPEED_CONSTANTS, ControlType, LOADED_THRESHOLD } from "../shared/speedStuff";

// GENERAL NOTE: "Speed" throughout is always positive, and "direction" is a boolean where true=forward & false=backward

// The idea is that the speed is fast at the start, gets slow near the end (time to view rose), slowly moves backward, speeds up til the start, then can bounce back forward again.
// To do this we'll need a cosine function, with x as position and y as the rate of change (fps).
// Position has range [0, 1], returned speed has range [SPEED_MIN, SPEED_MAX]
const getSpeedBouncy = (position: number): number => {
  // At position = 1, we should be at the steep downward part of the cosine curve (1/4 through a period)
  const angle = position * (2 * Math.PI) / 4;
  // Cosine has range [0, 1], I think (could be off-by-one-ish)
  const cosine = Math.cos(angle);
  // Scale it to prevent zero values (they mess stuff up)
  return cosine * (SPEED_CONSTANTS.MAX - SPEED_CONSTANTS.MIN) + SPEED_CONSTANTS.MIN;
};

// For this one the speed begins slow, speeds up in the middle, then ends slow. So, 1/2 the period of a sine wave (if those terms make sense).
const getSpeedCyclic = (position: number): number => {
  const angle = position * (2 * Math.PI) / 2;
  // The peak of a standard cosine function is 1
  const sine = Math.sin(angle);
  return sine * (SPEED_CONSTANTS.MAX - SPEED_CONSTANTS.MIN) + SPEED_CONSTANTS.MIN;
};

const getSpeedLinear = (position: number): number | null => {
  return position * (SPEED_CONSTANTS.MAX - SPEED_CONSTANTS.MIN) + SPEED_CONSTANTS.MIN;
}

const getLoopSpeed = (position: number, controlType: ControlType): number | null => {
  switch (controlType) {
    case "bouncyLoop":
      return getSpeedBouncy(position);
    case "cyclicLoop":
      return getSpeedCyclic(position);
    case "linearLoop":
      return getSpeedLinear(position);
    // This shouldn"t happen
    case "manual":
      return null;
  }
}

const getNewSpeedDirection = ({ frameIndex, nFrames, prevSpeed, prevDirection, controlType }: {
  frameIndex: number,
  nFrames: number,
  prevSpeed: number,
  prevDirection: boolean,
  controlType: ControlType,
}): [number | null, boolean] => {
  // Position 0 if 0 or 1 frames
  const position = nFrames > 1 ? frameIndex / (nFrames - 1) : 0;
  const atStart = frameIndex <= 0;
  const atEnd = frameIndex >= nFrames - 1;

  const reachedTerminus = prevDirection && atEnd || !prevDirection && atStart;
  if (controlType === "manual") {
    // Stop if appropriate
    if (reachedTerminus) {
      return [null, prevDirection];
    }
    return [prevSpeed, prevDirection];
  }
  const speed = getLoopSpeed(position, controlType);
  // Since it"s a loop, be ready to turn around
  const direction = reachedTerminus ? !prevDirection : prevDirection;
  return [speed, direction];
};

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
  const [playTimeout, setPlayTimeout] = useState<number | null>(null);
  // speed has range [SPEED_MIN, SPEED_MAX]
  const [playSpeed, setPlaySpeed] = useState<number | null>(null);
  // true is forward, false is back
  const [playDirection, setPlayDirection] = useState<boolean>(true);
  // NOTE: Probably will change this to speedControlType
  const [playControlType, setPlayControlType] = useState<ControlType>("bouncyLoop");

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
    waitOnLoading(frames, 0, LOADED_THRESHOLD, () => setPlaySpeed(SPEED_CONSTANTS.PLAY));
  }, [frames]);

  useEffect(() => {
    // If slider is set to positive or if it"s supposed to be looping
    if (playSpeed !== null) {
      // Set play interval going if playing but no timeout (e.g. if frame transition has finished)
      if (playTimeout === null) {
        if (currentFrame === null) {
          return;
        };
        if (currentFrame.model === null) {
          // Wait a bit to allow loading to continue
          const prevPlaySpeed = playSpeed;
          setPlaySpeed(null);
          waitOnLoading(frames, currentFrame.index, LOADED_THRESHOLD, () => setPlaySpeed(prevPlaySpeed));
          return;
        }
        const [speed, direction] = getNewSpeedDirection({
          frameIndex: currentFrame === null ? 0 : currentFrame.index,
          nFrames: frames.length,
          prevSpeed: playSpeed,
          prevDirection: playDirection,
          controlType: playControlType,
        });
        if (speed === null) {
          setPlaySpeed(null);
          setPlayTimeout(null);
          return;
        }
        setPlaySpeed(speed);
        setPlayDirection(direction);
        const interval = 1 / speed * 1000;
        const timeout = window.setTimeout(() => {
          if (currentFrameRef.current === null) {
            return;
          }
          // TODO: Add some checks (but for now relying on getNewSpeedDirection)
          const nextFrameIndex = direction ? currentFrameRef.current.index + 1 : currentFrameRef.current.index - 1;
          setCurrentFrame(frames[nextFrameIndex]);
          setPlayTimeout(null);
        }, interval);
        setPlayTimeout(timeout);
      }
    }
  }, [playSpeed, playTimeout]);

  return (
    <div>
      <button id="loop-button" className={ playControlType ? `${playControlType}-loop` : `no-loop`} onClick={() => {
        // Toggle between no loop and bouncy loop
        setPlayControlType(playControlType === "manual" ? "bouncyLoop" : "manual");
        if (playSpeed === null) {
          // The value shouldn't matter, as it's about to be overwritten as a result
          setPlaySpeed(SPEED_CONSTANTS.MIN);
        }
      }}>Loop</button>
      <div id="speed-mode-buttons">
        <SpeedModeButton modeType={"rewind"} setPlaySpeed={setPlaySpeed} setPlayDirection={setPlayDirection} setControlType={setPlayControlType}/>
        <SpeedModeButton modeType={"pause"} setPlaySpeed={setPlaySpeed} setPlayDirection={setPlayDirection} setControlType={setPlayControlType}/>
        <SpeedModeButton modeType={"play"} setPlaySpeed={setPlaySpeed} setPlayDirection={setPlayDirection} setControlType={setPlayControlType}/>
        <SpeedModeButton modeType={"fastForward"} setPlaySpeed={setPlaySpeed} setPlayDirection={setPlayDirection} setControlType={setPlayControlType}/>
      </div>
      <SpeedSlider
        playSpeed={playSpeed}
        setPlaySpeed={setPlaySpeed}
        playDirection={playDirection}
        setPlayDirection={setPlayDirection}
        setControlType={setPlayControlType}
      />
    </div>
  );
};

export default Controls;
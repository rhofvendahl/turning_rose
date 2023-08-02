import React, { useEffect, useRef, useState } from 'react';

import { Frame } from '../hooks/useFrame';

const Controls = ({ frames, currentFrame, setCurrentFrame }: {
  frames: Frame[],
  currentFrame: Frame | null,
  setCurrentFrame: (x: any) => void
}
) => {
  // 'play' is whether the viewer should be playing
  const [play, setPlay] = useState(false);
  // 'playInterval' keeps track of whether viewer actually is playing
  const [playInterval, setPlayInterval] = useState<number | null>(null);

  const playIndex = useRef(0);

  useEffect(() => {
    if (currentFrame === null) {
      return;
    }
    if (play) {
      // Only set an interval if none exists
      if (playInterval === null) {
        // Used within the interval to keep track of play
        playIndex.current = 0;
        const interval = window.setInterval(() => {
          if (playIndex.current < frames.length) {
            setCurrentFrame(frames[playIndex.current]);
          } else {
            // Stop at the end
            setPlay(false);
          }
          playIndex.current += 1;
        }, 50);
        setPlayInterval(interval);
      }
    } else {
      // Only clear an interval if one exists
      if (playInterval !== null) {
        window.clearInterval(playInterval);
        setPlayInterval(null);
      }
    }
  }, [play, playInterval]);

  return (
    <div>
      {/* {frames.map((_, index) => (
        <button key={index} onClick={() => setCurrentFrame(frames[index])}>
          {frames[index].path.split("/").pop()}
        </button>
      ))} */}
      <button onClick={() => {
        if (currentFrame !== null && currentFrame.index > 0) {
          const nextFrame = frames[currentFrame.index - 1];
          setCurrentFrame(nextFrame);
        }
      }}>Prev</button>
      <button onClick={() => setPlay(true)}>Play</button>
      <button onClick={() => setPlay(false)}>Pause</button>
      <button onClick={() => {
        setPlay(false);
        if (currentFrame !== null && currentFrame.index + 1 < frames.length) {
          const nextFrame = frames[currentFrame.index + 1];
          setCurrentFrame(nextFrame);
        }
      }}>Next</button>
    </div>
  );
}

export default Controls;
import React, { useEffect, useRef, useState } from 'react';

import { Frame } from '../hooks/useFrame';

const Controls = ({ frames, currentFrame, setCurrentFrame }: {
  frames: Frame[],
  currentFrame: Frame | null,
  setCurrentFrame: (x: any) => void}
) => {
  const [play, setPlay] = useState(false);
  const [playInterval, setPlayInterval] = useState<number | null>(null);
  
  // Give access to mutable currentFrame within playInterval below
  const currentFrameRef = useRef(currentFrame);
  useEffect(() => {
    currentFrameRef.current = currentFrame;
  }, [currentFrame]);

  useEffect(() => {
    if (currentFrame === null) {
      return;
    }
    if (play) {
      if (playInterval === null) {
        const interval = window.setInterval(() => {
          const current = currentFrameRef.current;
          if (current === null) {
            return;
          }
          const nextFrame = frames[(current.index + 1) % frames.length];
          setCurrentFrame(nextFrame);
        }, 500);
        setPlayInterval(interval);
      }
    } else {
      if (playInterval !== null) {
        window.clearInterval(playInterval);
        setPlayInterval(null);
      }
    }
  }, [play, playInterval]);

  return (
    <div>
        {frames.map((_, index) => (
          <button key={index} onClick={() => setCurrentFrame(frames[index])}>
            Frame {index + 1}
          </button>
        ))}
        <button onClick={() => setPlay(true)}>Play</button>
        <button onClick={() => setPlay(false)}>Pause</button>
      <div id="frames">
      </div>
      <div id="play-pause">
      </div>
    </div>
  );
}

export default Controls;
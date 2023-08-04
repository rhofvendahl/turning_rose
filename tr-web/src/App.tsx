import React, { useEffect, useState, useRef } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";

import "./App.css";
import ViewFrame from "./components/ViewFrame";
import Controls from "./components/Controls";
import { useFrame, Frame } from "./hooks/useFrame";

// This doesn't seem ideal, but even useEffect with empty inputs within App seems to run twice over the app"s lifecycle - no good.
let hasInitialized = false;

const App = () => {
  const [frames, setFrames] = useState<Frame[]>([]);
  const [currentFrame, setCurrentFrame] = useState<Frame | null>(null);
  const currentFrameRef = useRef(currentFrame);

  // Provide a way to access current frame within frame loading functions, so that the appropriate frame is loaded next
  useEffect(() => {
    currentFrameRef.current = currentFrame;
  }, [currentFrame]);

  // useEffect necessary for React to notice currentFrame update
  useEffect(() => {
    if (!hasInitialized) {
      useFrame({ frames, setFrames, currentFrameRef, setCurrentFrame });
      hasInitialized = true;
    }
  }, []);
  
  return (
    <div id="content-container">
      <div id="controls-wrapper">
        <Controls frames={frames} currentFrame={currentFrame} setCurrentFrame={setCurrentFrame} />
      </div>
      <Canvas id="canvas">
        <ambientLight intensity={1} />
        <OrbitControls />
        <mesh position={[0, .2, 0]}>
          { currentFrame && <ViewFrame frame={currentFrame} /> }
        </mesh>
      </Canvas>
    </div>
  );
};

export default App;
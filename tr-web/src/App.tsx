import React, { useEffect, useState} from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';

import './App.css';
import ViewFrame from './components/ViewFrame';
import Controls from './components/Controls';
import { useFrame, Frame } from './hooks/useFrame';
import modelPaths from './assets/json/modelPaths.json';

// This doesn't seem ideal, but even useEffect with empty inputs within App seems to run twice over the app's lifecycle - no good.
let useFrameDidRun = false;

const App = () => {
  const frameValues: Frame[] = modelPaths.map((path, i) => {
    const frame: Frame = {
      index: i,
      path: path,
      model: null,
    };
    return frame;
  });
  const [frames, _] = useState<Frame[]>(frameValues);
  const [currentFrame, setCurrentFrame] = useState<Frame | null>(null);

  // useEffect necessary for React to notice currentFrame update
  useEffect(() => {
    if (!useFrameDidRun) {
      useFrame({ frames, currentFrame, setCurrentFrame });
      useFrameDidRun = true;
    }
  }, []);
  
  return (
    <div id='content-container'>
        <Controls frames={frames} currentFrame={currentFrame} setCurrentFrame={setCurrentFrame} />
      <div id="controls-wrapper">
      </div>
      <Canvas id="canvas">
        <ambientLight intensity={1} />
        <OrbitControls />
       { currentFrame && <ViewFrame frame={currentFrame} /> }
      </Canvas>
    </div>
  );
}

export default App;
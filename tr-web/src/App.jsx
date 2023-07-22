import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';

import './App.css';
import Model from './components/Model';

function App() {
  return (
    <div id="canvas-container">
      <Canvas>
        <Model />
        <ambientLight intensity={1} />
        <OrbitControls />
      </Canvas>
    </div>
  );
}

export default App;

import { Canvas } from '@react-three/fiber';
import { Html, OrbitControls, useProgress } from '@react-three/drei';

import './App.css';
import ModelViewer from './components/ModelViewer';
import { Suspense, useState } from 'react';
import Loader from './components/Loader';

function App() {
  const [currentModel, setCurrentModel] = useState(3);
  const models = [
    // '/db/gltf/2023-07-19_13_reduced.gltf',
    '/db/gltf/2023-07-19_19_reduced.gltf',
    '/db/gltf/2023-07-20_01_reduced.gltf',
    '/db/gltf/2023-07-20_07_reduced.gltf',
    '/db/gltf/2023-07-20_13_darker_reduced.gltf',
  ];

  return (
    <div id="canvas-container">
      <Canvas>
        <ambientLight intensity={1} />
        <OrbitControls />
        <Suspense fallback={<Loader />}>
          <ModelViewer model={models[currentModel]} />
        </Suspense>
      </Canvas>
    </div>
  );
}

export default App;

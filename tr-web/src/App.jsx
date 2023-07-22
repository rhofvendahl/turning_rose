import { Canvas } from '@react-three/fiber';
import { Html, OrbitControls, useProgress } from '@react-three/drei';

import './App.css';
import Model from './components/Model';
import { Suspense, useEffect, useState } from 'react';
import Loader from './components/Loader';
import Controls from './components/Controls';

function App() {
  const [models, setModels] = useState([]);
  const [currentModel, setCurrentModel] = useState(null);

  useEffect(() => {
    const modelPaths = [
      // '/db/gltf/2023-07-19_13_reduced.gltf',
      // '/db/gltf/2023-07-19_19_reduced.gltf',
      '/db/gltf/2023-07-20_01_reduced.gltf',
      '/db/gltf/2023-07-20_07_reduced.gltf',
      '/db/gltf/2023-07-20_13_darker_reduced.gltf',
    ];

    setModels(modelPaths);
    setCurrentModel(modelPaths[2]);
  }, []);

  return (
    <div id="canvas-container">
      <Controls models={models} setCurrentModel={setCurrentModel} />
      <Canvas>
        <ambientLight intensity={1} />
        <OrbitControls />
        <Suspense fallback={<Loader />}>
          <Model modelPath={currentModel} />
        </Suspense>
      </Canvas>
    </div>
  );
}

export default App;

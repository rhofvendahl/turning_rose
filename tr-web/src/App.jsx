import { Canvas } from '@react-three/fiber'

import './App.css'
import Model from './components/Model'

function App() {
  return (
    <div id="canvas-container">
      <Canvas>
        <Model />
        <ambientLight intensity={.4} />
      </Canvas>
    </div>
  )
}

export default App

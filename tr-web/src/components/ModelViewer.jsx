import { useLoader } from '@react-three/fiber';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';

function ModelViewer({ model }) {
  const obj = useLoader(GLTFLoader, model);
  return <primitive object={obj.scene} scale={[4, 4, 4]} />;
}

export default ModelViewer;

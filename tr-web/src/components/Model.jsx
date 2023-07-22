import { useLoader } from '@react-three/fiber';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';

function Model({ modelPath }) {
  console.log("Loading: ", modelPath);
  const gltf = useLoader(GLTFLoader, modelPath);
  return <primitive object={gltf.scene} scale={[4, 4, 4]} />;
}

export default Model;

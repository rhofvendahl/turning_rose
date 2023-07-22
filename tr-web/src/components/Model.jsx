import { useLoader } from '@react-three/fiber';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';

function Model() {
  const obj = useLoader(GLTFLoader, '/gltf/2023_07_20_noon_darker_embedded.gltf');
  return <primitive object={obj.scene} scale={[4, 4, 4]} />
}

export default Model

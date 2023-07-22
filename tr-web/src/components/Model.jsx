// import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader'
import { useLoader } from '@react-three/fiber'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader'

function Model() {
  // const obj = useLoader(OBJLoader, '/obj/2023_07_19_evening_darker/model.obj')
  // return <primitive object={obj} />
  const obj = useLoader(GLTFLoader, '/gltf/2023_07_20_noon_darker_embedded.gltf')
  return <primitive object={obj.scene} scale={[10, 10, 10]} />
}

export default Model

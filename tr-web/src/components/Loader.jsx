import { Html, useProgress } from "@react-three/drei";

import './Loader.css';

function Loader() {
  const { progress } = useProgress();
  return <Html center>
    <div id='loaded'>{Math.round(progress)} % loaded</div>
  </Html>;
}


export default Loader;

import React from 'react';
import { Frame } from '../hooks/useFrame';

const ViewFrame = ({ frame }: { frame: Frame }) => {
  if (frame.model === null) {
    console.log("Frame model is null:", frame);
    return null;
  }

  // const { scene } = frame.model;
  // scene.traverse((child) => {
  //   if (child.isMesh) {
  //     child.customDepthMaterial.tra
  //   }
  // })

  console.log("Viewing:", frame.index, frame.path.split("/").pop());
  return <primitive object={frame.model.scene} scale={[4, 4, 4]} />;
}

export default ViewFrame;

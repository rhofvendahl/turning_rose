import { GLTF, GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';

export interface Frame {
  index: number;
  path: string;
  model: GLTF | null;
}

const getNextIndex = (frames: Frame[], currentFrame: Frame | null): number | null => {
  if (currentFrame === null) {
    return 0;
  }

  // First load from the current frame onward; the current frame should already be loaded but no harm checking
  for (let i = currentFrame.index; i < frames.length; i++) {
    if (frames[i].model === null) {
      return i;
    }
  }
  // If everything ahead is loaded, load any skipped frames
  for (let i = 0; i < currentFrame.index; i++) {
    if (frames[i].model === null) {
      return i;
    }
  }
  // All frames loaded
  console.log("All frames loaded:", frames);
  return null;
};

interface Params {
  frames: Frame[];
  currentFrame: Frame | null;
  setCurrentFrame: (x: any) => void;
}

const loadNext = async ({ frames, currentFrame, setCurrentFrame }: Params) => {
  const loader = new GLTFLoader();
  
  let nextIndex = getNextIndex(frames, currentFrame);
  // There's a clever way to use a for loop, but I was finding it confusing
  while (nextIndex !== null) {
    const nextFrame = frames[nextIndex];
    nextFrame.model = await loader.loadAsync(nextFrame.path);
    if (currentFrame === null) {
      setCurrentFrame(nextFrame);
      currentFrame = nextFrame;
    }
    nextIndex = getNextIndex(frames, currentFrame);
  } 
};



export const useFrame = ({ frames, currentFrame, setCurrentFrame }: Params) => {
  console.log('Loading frames...');
  loadNext({ frames, currentFrame, setCurrentFrame });
};
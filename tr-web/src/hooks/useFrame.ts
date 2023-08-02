import { Mesh } from 'three';
import { GLTF, GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';

export interface Frame {
  index: number;
  name: string;
  model: GLTF | null;
}

export const MODEL_PATH_BASE = '/db/gltf/';

const getNextIndex = (frames: Frame[], loadForwardFrom: Frame | null): number | null => {
  if (loadForwardFrom === null) {
    return 0;
  }

  // First load from the current frame onward; the current frame should already be loaded but no harm checking
  for (let i = loadForwardFrom.index; i < frames.length; i++) {
    if (frames[i].model === null) {
      return i;
    }
  }
  // If everything ahead is loaded, load any skipped frames
  for (let i = 0; i < loadForwardFrom.index; i++) {
    if (frames[i].model === null) {
      return i;
    }
  }
  // All frames loaded
  console.log('All frames loaded:', frames);
  return null;
};

// Modifies model inplace
const configureModel = (model: GLTF) => {
  model.scene.traverse((child) => {
    // Harmless due to isMesh check, and necessary to quiet ts errors
    let mesh = child as Mesh;
    if (mesh.isMesh) {
      let material = mesh.material;
      if (!Array.isArray(material)) {
        material.transparent = true;
      }
    }
  })
}

const loadModels = async ({ frames, currentFrameRef, setCurrentFrame }: {
  frames: Frame[],
  currentFrameRef: React.MutableRefObject<Frame | null>,
  setCurrentFrame: (x: any) => void,
}) => {
  const loader = new GLTFLoader();

  let nextIndex = getNextIndex(frames, currentFrameRef.current);
  let prevCurrentFrameRefValue = currentFrameRef.current;
  while (nextIndex !== null) {
    const loadingFrame = frames[nextIndex];
    const model = await loader.loadAsync(MODEL_PATH_BASE + loadingFrame.name);
    console.log(`Loaded: ${loadingFrame.index} ${loadingFrame.name}`)
    configureModel(model);
    loadingFrame.model = model;
    if (currentFrameRef.current === null) {
      setCurrentFrame(loadingFrame);
      currentFrameRef.current = loadingFrame;
    }
    // In theory setCurrentFrame should result in the recalculation of currentFrameRef, but timing may be unreliable.
    // So, currentFrameRef.current should have either the previous currentFrameValue, or the one that's just been set.
    // If it's something else, however, that means somewhere external has changed it, in which case that new value
    // should be respected as the new place to load forward from.
    const latestCurrentFrameRefValue = currentFrameRef.current;
    const notPrevValue = latestCurrentFrameRefValue?.name !== prevCurrentFrameRefValue?.name;
    const notNewValue = latestCurrentFrameRefValue?.name !== loadingFrame.name;
    const currentFrameJump = notPrevValue && notNewValue
    // The usual case, in which loading continues from the latest loaded frame
    let loadForwardFrom = loadingFrame;
    // The case where something like the user skipping forward has happened, causing currentFrame to change unexpectedly
    if (currentFrameJump && latestCurrentFrameRefValue !== null) {
      console.log("Current frame jump detected; modifying load order.")
      loadForwardFrom = latestCurrentFrameRefValue;
    }
    // Update for subsequent checks
    nextIndex = getNextIndex(frames, loadForwardFrom);
    prevCurrentFrameRefValue = latestCurrentFrameRefValue;
  }
};

const getFrames = async (): Promise<Frame[]> => {
    const response = await fetch('/db/json/modelNames.json');
    const modelNames: string[] = await response.json();
    const frames = modelNames.map((name, i) => {
      const frame: Frame = {
        index: i,
        name: name,
        model: null,
      };
      return frame;
    });
    return frames;
};

export const useFrame = ({ frames, setFrames, currentFrameRef, setCurrentFrame }: {
  frames: Frame[],
  setFrames: (x: any) => void,
  currentFrameRef: React.MutableRefObject<Frame | null>,
  setCurrentFrame: (x: any) => void, 
}) => {
  console.log('Loading frames...');

  getFrames()
    .then((frames) => {
      setFrames(frames);
      loadModels({ frames, currentFrameRef, setCurrentFrame });
    });
};
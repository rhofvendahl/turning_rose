// NOTE: "Speed" throughout is always positive, and "direction" is a boolean where true=forward & false=backward

const SPEED_MIN = 2;
const SPEED_MAX = 40;

export const SPEED_CONSTANTS = {
  MIN: SPEED_MIN,
  MAX: SPEED_MAX,
  REWIND: (SPEED_MAX - SPEED_MIN) * .8,
  PLAY: (SPEED_MAX - SPEED_MIN) * .2,
  FAST_FORWARD: (SPEED_MAX - SPEED_MIN) * .8
}

// Used mainly to tell ModeInput what to be; NOT a state.
export type ModeInputType = 'rewind' | 'pause' | 'play' | 'fast-forward';

// values for playLoopType state. null indicates non-loop manual control
export type LoopType = 'bouncy' | 'cyclic' | 'linear' | null;

// NOTE: I'm tempted to combine ModeInputType and LoopType into SpeedMode or something, but
// a) I think ModeInputType should have to do with setting the speed value, but speed should be a simple value
// b) That's getting ahead of myself / not currently necessary

// The number of frames that must be loaded before play starts
// Constant for now; might want to make it dependent on internet speed or something, later
export const LOADED_THRESHOLD = 5;


// How close speed slider should be to 0 before snapping there
export const SNAP_FROM = 2;

export const speedDirectionToSliderValue = (speed: number, direction: boolean): number => {
  console.log("TO VAL", speed, direction, direction ? (speed - SPEED_CONSTANTS.MIN) : - (speed - SPEED_CONSTANTS.MIN));
  return direction ? (speed - SPEED_CONSTANTS.MIN) : - (speed - SPEED_CONSTANTS.MIN);
};

export const sliderValueToSpeedDirection = (sliderValue: number): [number, boolean] => {
  const direction = sliderValue >= 0;
  const speed = Math.abs(sliderValue) + SPEED_CONSTANTS.MIN;
  console.log("FROM VAL", sliderValue, speed, direction);
  return [speed, direction];
};
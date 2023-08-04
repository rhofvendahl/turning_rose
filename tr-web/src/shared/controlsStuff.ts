// NOTE: "Speed" throughout is always positive, and "direction" is a boolean where true=forward & false=backward

const SPEED_MIN = 2;
const SPEED_MAX = 30;

export const SPEED_CONSTANTS = {
  MIN: SPEED_MIN,
  MAX: SPEED_MAX,
  REWIND: SPEED_MAX * .7,
  PLAY: 8,
  FAST_FORWARD: SPEED_MAX * .7,
  LOOP_CAP: SPEED_MAX * .7
}

// Used mainly to tell ModeInput what to be; NOT a state.
export type ModeInputType = 'rewind' | 'pause' | 'play' | 'fastForward';

// values for playControlType state. null indicates non-loop manual control
export type ControlType = 'bouncyLoop' | 'cyclicLoop' | 'linearLoop' | 'manual';

// The number of frames that must be loaded before play starts
// Constant for now; might want to make it dependent on internet speed or something, later
export const LOADED_THRESHOLD = 5;

export const speedDirectionToSliderValue = (speed: number | null, direction: boolean): number => {
  if (speed === null) {
    return 0;
  }
  return direction ? (speed - SPEED_CONSTANTS.MIN) : - (speed - SPEED_CONSTANTS.MIN);
};

export const sliderValueToSpeedDirection = (sliderValue: number): [number | null, boolean] => {
  const direction = sliderValue >= 0;
  const speed = sliderValue === 0 ? null : Math.abs(sliderValue) + SPEED_CONSTANTS.MIN;
  return [speed, direction];
};
import React from "react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { IconDefinition, faBackward, faPause, faPlay, faForward } from "@fortawesome/free-solid-svg-icons";

import { SPEED_CONSTANTS, ModeInputType, speedDirectionToSliderValue, sliderValueToSpeedDirection, LoopType } from "../shared/speedStuff";

import "./SpeedModeButton.css";

// Get relative position along slider as a value with range [0, 100]
const getButtonPosition = (speed: number | null, direction: boolean): number => {
  // Ranges from [-(max - min), (max  1)]
  const sliderValue = speedDirectionToSliderValue(speed, direction);
  // Ranges from [-1, 1]
  const sliderValueNormalized = sliderValue / (SPEED_CONSTANTS.MAX - SPEED_CONSTANTS.MIN);
  // Ranges from [0, 100]
  return (sliderValueNormalized + 1) * 50;
};

const SpeedModeButton = ({ modeType, setPlaySpeed, setPlayDirection, setLoopType }: {
  modeType: ModeInputType,
  setPlaySpeed: (speed: number | null) => void,
  setPlayDirection: (direction: boolean) => void,
  setLoopType: (type: LoopType) => void,
}) => {
  let speed: number | null;
  let direction: boolean;
  let icon: IconDefinition;
  switch (modeType) {
    case "rewind":
      speed = SPEED_CONSTANTS.REWIND;
      direction = false;
      icon = faBackward;
      break;
    case "pause":
      speed = null;
      direction = true;
      icon = faPause;
      break;
    case "play":
      speed = SPEED_CONSTANTS.PLAY;
      direction = true;
      icon = faPlay;
      break;
    case "fastForward":
      speed = SPEED_CONSTANTS.FAST_FORWARD;
      direction = true;
      icon = faForward;
      break;
  }
  return (
    <div id="mode-button-wrapper">
      <div
        id={`${modeType}-button`}
        style={{ "left": `${getButtonPosition(speed, direction)}%` }}
        className="mode-button"
        onClick={() => {
          setLoopType(null);
          setPlaySpeed(speed);
          setPlayDirection(direction);
        }}
      >
        <FontAwesomeIcon className="mode-icon" icon={icon} />
      </div>
    </div>
  );
};

export default SpeedModeButton;

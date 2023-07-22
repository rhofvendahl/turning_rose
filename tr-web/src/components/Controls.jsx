import './Controls.css';

const Controls = ({ models, setCurrentModel }) => {
  return (
    <div>
      {models.map((model, index) => (
        <button key={index} onClick={() => setCurrentModel(model)}>
          Frame {index + 1}
        </button>
      ))}
    </div>
  );
};

export default Controls;
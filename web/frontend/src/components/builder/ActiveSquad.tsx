import { useBuilderStore } from "../../stores/builderStore";
import PilotCard from "./PilotCard";

export default function ActiveSquad() {
  const { squad, totalPoints, squadName, setSquadName } = useBuilderStore();

  if (squad.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-40 text-gray-600 text-sm border-2 border-dashed border-gray-800 rounded-lg">
        Add pilots from the pool on the left
      </div>
    );
  }

  const pts = totalPoints();
  const over = pts > 200;

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3">
        <input
          value={squadName}
          onChange={(e) => setSquadName(e.target.value)}
          className="flex-1 bg-transparent border-b border-gray-700 text-white text-sm focus:outline-none focus:border-brand-500 pb-0.5"
          placeholder="Squad name…"
        />
        <span className={`text-sm font-bold tabular-nums ${over ? "text-red-400" : "text-brand-400"}`}>
          {pts} / 200 pts
        </span>
      </div>

      {squad.map((sp, idx) => (
        <PilotCard key={`${sp.pilot_name}-${idx}`} squadPilot={sp} pilotIdx={idx} />
      ))}
    </div>
  );
}

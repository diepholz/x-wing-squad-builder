import { Upgrade } from "../../types";
import { prettifyName } from "../../lib/squadLogic";

interface Props {
  slot: string;
  equipped: string | undefined;
  onOpen: () => void;
  onUnequip: () => void;
}

const SLOT_COLORS: Record<string, string> = {
  talent:         "text-red-400",
  force:          "text-purple-400",
  crew:           "text-blue-400",
  gunner:         "text-cyan-400",
  astromech:      "text-green-400",
  modification:   "text-gray-400",
  title:          "text-yellow-400",
  sensor:         "text-sky-400",
  cannon:         "text-orange-400",
  missile:        "text-rose-400",
  torpedo:        "text-red-300",
  turret:         "text-teal-400",
  tech:           "text-indigo-400",
  configuration:  "text-emerald-400",
  illicit:        "text-pink-400",
  payload:        "text-amber-400",
  command:        "text-lime-400",
  hardpoint:      "text-gray-300",
  cargo:          "text-stone-400",
  team:           "text-violet-400",
  "tactical relay": "text-sky-300",
};

export default function UpgradeSlot({ slot, equipped, onOpen, onUnequip }: Props) {
  const color = SLOT_COLORS[slot] ?? "text-gray-400";
  return (
    <div className="flex items-center gap-2 py-1">
      <span className={`text-xs w-24 shrink-0 ${color}`}>{slot}</span>
      {equipped ? (
        <div className="flex items-center gap-1 flex-1">
          <span className="text-sm text-white flex-1">{prettifyName(equipped)}</span>
          <button
            onClick={onOpen}
            className="text-xs text-gray-500 hover:text-blue-400 transition-colors"
            title="Change"
          >
            ✎
          </button>
          <button
            onClick={onUnequip}
            className="text-xs text-gray-500 hover:text-red-400 transition-colors"
            title="Remove"
          >
            ×
          </button>
        </div>
      ) : (
        <button
          onClick={onOpen}
          className="text-xs text-gray-600 hover:text-gray-300 flex-1 text-left italic transition-colors"
        >
          — empty —
        </button>
      )}
    </div>
  );
}

import { Faction } from "../../types";
import { prettifyName } from "../../lib/squadLogic";
import clsx from "clsx";

interface Props {
  factions: Faction[];
  selected: string | null;
  onSelect: (name: string) => void;
}

const FACTION_COLORS: Record<string, string> = {
  "rebel alliance":       "border-red-700 hover:border-red-500",
  "galactic empire":      "border-gray-500 hover:border-gray-300",
  "scum and villainy":    "border-yellow-700 hover:border-yellow-500",
  "resistance":           "border-orange-700 hover:border-orange-500",
  "first order":          "border-red-900 hover:border-red-700",
  "galactic republic":    "border-blue-700 hover:border-blue-500",
  "separatist alliance":  "border-purple-700 hover:border-purple-500",
};

export default function FactionPicker({ factions, selected, onSelect }: Props) {
  return (
    <div>
      <h2 className="text-xs uppercase tracking-widest text-gray-500 mb-3">Choose Faction</h2>
      <div className="grid grid-cols-2 gap-2">
        {factions.map((f) => (
          <button
            key={f.name}
            onClick={() => onSelect(f.name)}
            className={clsx(
              "border-2 rounded-lg px-3 py-2.5 text-sm font-medium text-left transition-all",
              FACTION_COLORS[f.name] ?? "border-gray-700 hover:border-gray-500",
              selected === f.name
                ? "bg-gray-800 text-white"
                : "bg-gray-900 text-gray-300"
            )}
          >
            {prettifyName(f.name)}
          </button>
        ))}
      </div>
    </div>
  );
}

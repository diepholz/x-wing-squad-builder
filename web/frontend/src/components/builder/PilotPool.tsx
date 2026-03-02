import { useState } from "react";
import { Faction } from "../../types";
import { prettifyName } from "../../lib/squadLogic";

interface Props {
  faction: Faction;
  onAddPilot: (shipName: string, pilotName: string) => void;
}

export default function PilotPool({ faction, onAddPilot }: Props) {
  const [search, setSearch] = useState("");
  const [expandedShip, setExpandedShip] = useState<string | null>(null);

  const query = search.toLowerCase();
  const ships = faction.ships.filter(
    (s) =>
      !query ||
      s.name.includes(query) ||
      s.pilots.some((p) => p.name.includes(query))
  );

  return (
    <div className="flex flex-col gap-2">
      <input
        placeholder="Search ships or pilots…"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="bg-gray-800 border border-gray-700 rounded px-3 py-1.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-brand-500"
      />
      <div className="space-y-1 overflow-y-auto max-h-[calc(100vh-280px)]">
        {ships.map((ship) => {
          const isOpen = expandedShip === ship.name;
          const pilots = query
            ? ship.pilots.filter((p) => p.name.includes(query))
            : ship.pilots;
          return (
            <div key={ship.name} className="rounded bg-gray-900 border border-gray-800">
              <button
                className="w-full flex justify-between items-center px-3 py-2 text-sm text-gray-200 hover:text-white"
                onClick={() => setExpandedShip(isOpen ? null : ship.name)}
              >
                <span className="font-medium">{prettifyName(ship.name)}</span>
                <span className="text-gray-500 text-xs">{ship.pilots.length} pilots</span>
              </button>
              {(isOpen || query) && (
                <div className="border-t border-gray-800">
                  {pilots
                    .sort((a, b) => {
                      if (a.unique !== b.unique) return a.unique ? 1 : -1;
                      return a.initiative - b.initiative || a.cost - b.cost;
                    })
                    .map((pilot) => (
                      <button
                        key={pilot.name}
                        onClick={() => onAddPilot(ship.name, pilot.name)}
                        className="w-full flex items-center justify-between px-4 py-1.5 text-sm text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
                      >
                        <div className="flex items-center gap-2">
                          <span className="text-gray-500 text-xs w-4 text-center">
                            {pilot.initiative}
                          </span>
                          <span className={pilot.unique ? "text-yellow-300" : ""}>
                            {prettifyName(pilot.name)}
                          </span>
                        </div>
                        <span className="text-gray-400 text-xs">{pilot.cost} pts</span>
                      </button>
                    ))}
                </div>
              )}
            </div>
          );
        })}
        {ships.length === 0 && (
          <p className="text-gray-500 text-sm text-center py-4">No results</p>
        )}
      </div>
    </div>
  );
}

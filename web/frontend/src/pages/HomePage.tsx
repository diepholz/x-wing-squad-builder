import { useNavigate } from "react-router-dom";

const FACTIONS = [
  { id: "rebel alliance", label: "Rebel Alliance", color: "border-red-600 hover:bg-red-900/20" },
  { id: "galactic empire", label: "Galactic Empire", color: "border-gray-500 hover:bg-gray-700/30" },
  { id: "scum and villainy", label: "Scum & Villainy", color: "border-yellow-600 hover:bg-yellow-900/20" },
  { id: "resistance", label: "Resistance", color: "border-orange-500 hover:bg-orange-900/20" },
  { id: "first order", label: "First Order", color: "border-red-800 hover:bg-red-900/30" },
  { id: "galactic republic", label: "Galactic Republic", color: "border-blue-500 hover:bg-blue-900/20" },
  { id: "separatist alliance", label: "Separatist Alliance", color: "border-teal-500 hover:bg-teal-900/20" },
];

export default function HomePage() {
  const navigate = useNavigate();

  function startBuild(faction: string) {
    navigate(`/build?faction=${encodeURIComponent(faction)}`);
  }

  return (
    <div className="max-w-3xl mx-auto py-12 px-4">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-white mb-3">X-Wing Squad Builder</h1>
        <p className="text-gray-400 text-lg">
          Build, save, and share your X-Wing Miniatures squads.
        </p>
      </div>

      <h2 className="text-sm font-semibold uppercase tracking-widest text-gray-500 mb-4">
        Choose a faction to start
      </h2>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {FACTIONS.map((f) => (
          <button
            key={f.id}
            onClick={() => startBuild(f.id)}
            className={`border rounded-lg p-4 text-left transition-colors ${f.color} text-white`}
          >
            <span className="font-medium">{f.label}</span>
          </button>
        ))}
      </div>

      <div className="mt-10 text-center text-gray-600 text-sm">
        Sign in to save and share your squads across devices.
      </div>
    </div>
  );
}

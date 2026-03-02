import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { squadsApi } from "../api/client";
import { SharedSquadResponse, SquadPilot } from "../types";
import { prettifyName } from "../lib/squadLogic";

export default function SharePage() {
  const { token } = useParams<{ token: string }>();

  const { data, isLoading, isError } = useQuery({
    queryKey: ["shared", token],
    queryFn: () => squadsApi.viewShared(token!).then((r) => r.data as SharedSquadResponse),
    enabled: !!token,
    retry: false,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen bg-gray-950 text-gray-500">
        Loading shared squad…
      </div>
    );
  }

  if (isError || !data) {
    return (
      <div className="flex flex-col items-center justify-center h-screen bg-gray-950 gap-4">
        <p className="text-gray-400">This squad link is invalid or has been removed.</p>
        <Link to="/" className="text-brand-400 hover:text-brand-300 text-sm transition-colors">
          ← Go home
        </Link>
      </div>
    );
  }

  const { squad, owner } = data;
  const pilots: SquadPilot[] = squad.data.pilots;

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      <div className="max-w-2xl mx-auto py-10 px-4">
        {/* Header */}
        <div className="mb-2">
          <Link to="/" className="text-xs text-gray-600 hover:text-gray-400 transition-colors">
            ← X-Wing Squad Builder
          </Link>
        </div>

        <div className="mb-6">
          <h1 className="text-2xl font-bold">{squad.name}</h1>
          <p className="text-gray-400 mt-1 capitalize">{prettifyName(squad.faction)}</p>
          {owner && (
            <p className="text-xs text-gray-600 mt-0.5">Shared by {owner}</p>
          )}
        </div>

        {/* Pilot list */}
        <div className="space-y-3">
          {pilots.map((sp, idx) => (
            <div key={idx} className="bg-gray-900 border border-gray-800 rounded-lg p-4">
              <div className="flex items-start justify-between mb-1">
                <div>
                  <span className="font-medium text-white">{prettifyName(sp.pilot_name)}</span>
                  <p className="text-xs text-gray-500 mt-0.5">{prettifyName(sp.ship_name)}</p>
                </div>
              </div>

              {sp.upgrades.length > 0 && (
                <div className="mt-2 border-t border-gray-800 pt-2 space-y-1">
                  {sp.upgrades.map((eu, i) => (
                    <div key={i} className="flex items-center gap-2 text-sm">
                      <span className="text-xs text-gray-600 w-20 shrink-0 capitalize">
                        {eu.slot}
                      </span>
                      <span className="text-gray-300">{prettifyName(eu.upgrade_name)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="mt-8 text-center">
          <Link
            to="/build"
            className="inline-block bg-brand-700 hover:bg-brand-600 text-white text-sm px-6 py-2 rounded transition-colors"
          >
            Build your own squad →
          </Link>
        </div>
      </div>
    </div>
  );
}

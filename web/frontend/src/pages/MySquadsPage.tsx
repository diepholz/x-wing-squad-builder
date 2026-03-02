import { useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useAuthStore } from "../stores/authStore";
import { useBuilderStore } from "../stores/builderStore";
import { squadsApi } from "../api/client";
import { ApiSquad, SquadPilot } from "../types";
import SquadCard from "../components/squad/SquadCard";

export default function MySquadsPage() {
  const { user } = useAuthStore();
  const { loadSquad } = useBuilderStore();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: squads, isLoading } = useQuery({
    queryKey: ["squads"],
    queryFn: () => squadsApi.list().then((r) => r.data as ApiSquad[]),
    enabled: !!user,
  });

  const deleteMutation = useMutation({
    mutationFn: (id: number) => squadsApi.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["squads"] }),
  });

  function handleLoad(squad: ApiSquad) {
    loadSquad(squad.faction, squad.data.pilots as SquadPilot[]);
    navigate(`/build?faction=${encodeURIComponent(squad.faction)}`);
  }

  if (!user) {
    return (
      <div className="flex flex-col items-center justify-center h-64 gap-4">
        <p className="text-gray-400">Sign in to view your saved squads.</p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        Loading squads…
      </div>
    );
  }

  const squadList = squads ?? [];

  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-semibold text-white">My Squads</h1>
        <button
          onClick={() => navigate("/build")}
          className="text-sm bg-brand-700 hover:bg-brand-600 text-white px-4 py-2 rounded transition-colors"
        >
          + New Squad
        </button>
      </div>

      {squadList.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-48 border-2 border-dashed border-gray-800 rounded-lg text-gray-600">
          <p>No squads yet.</p>
          <button
            onClick={() => navigate("/build")}
            className="mt-3 text-sm text-brand-400 hover:text-brand-300 transition-colors"
          >
            Build your first squad →
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {squadList.map((squad) => (
            <SquadCard
              key={squad.id}
              squad={squad}
              onLoad={() => handleLoad(squad)}
              onDelete={() => deleteMutation.mutate(squad.id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

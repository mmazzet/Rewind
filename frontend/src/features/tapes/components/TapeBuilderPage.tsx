import { useSuspenseQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { tapesApi } from "../api/tapesApi";
import type { Tape } from "../types";

export function TapeBuilderPage() {
  const { tapeId } = useParams<{ tapeId: string }>();

  const { data: tape } = useSuspenseQuery<Tape>({
    queryKey: ["tape", tapeId],
    queryFn: () => tapesApi.getTape(Number(tapeId)),
  });

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="w-full max-w-md p-8 bg-white rounded-lg shadow">
        <h1 className="text-2xl font-bold mb-2">{tape.title}</h1>
        <p className="text-sm text-gray-500 mb-1">
          Style: {tape.cassette_style}
        </p>
        <p className="text-sm text-gray-500">
          Length: {tape.length_minutes} minutes
        </p>
        <p className="text-xs text-gray-400 mt-4">Status: {tape.status}</p>
      </div>
    </div>
  );
}

import React, { useCallback } from "react";
import {
  useSuspenseQuery,
  useQueryClient,
  useMutation,
} from "@tanstack/react-query";
import toast from "react-hot-toast";
import { outboxApi } from "../api/outboxApi";
import { getErrorMessage } from "@/api/errorMessage";
import type { SentTapeListItem } from "../types";

const OutboxPage: React.FC = () => {
  const queryClient = useQueryClient();

  const { data } = useSuspenseQuery({
    queryKey: ["tapes", "sent"],
    queryFn: () => outboxApi.getSentTapes(),
  });

  const archiveMutation = useMutation({
    mutationFn: (tapeId: number) => outboxApi.archiveTape(tapeId),
    onSuccess: () => {
      // Invalidate so the list refetches without the archived tape
      queryClient.invalidateQueries({ queryKey: ["tapes", "sent"] });
      toast.success("Tape archived");
    },
    onError: (error) => {
      toast.error(getErrorMessage(error, "Failed to archive tape"));
    },
  });

  const handleArchive = useCallback(
    (tapeId: number) => {
      archiveMutation.mutate(tapeId);
    },
    [archiveMutation],
  );

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Sent tapes</h1>

      {data.length === 0 ? (
        <p className="text-gray-500">You have not sent any tapes yet.</p>
      ) : (
        <ul className="flex flex-col gap-4">
          {data.map((tape: SentTapeListItem) => (
            <li
              key={tape.id}
              className="flex items-center justify-between rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
            >
              <div className="flex flex-col gap-1">
                <span className="font-semibold text-gray-900">
                  {tape.title}
                </span>
                <span className="text-sm text-gray-500">
                  To: {tape.recipient_email}
                </span>
                <span className="text-sm text-gray-500">
                  {new Date(tape.sent_at).toLocaleDateString()}
                </span>
                <span className="text-xs font-medium uppercase tracking-wide text-indigo-600">
                  {tape.status}
                </span>
              </div>

              <button
                onClick={() => handleArchive(tape.id)}
                disabled={archiveMutation.isPending}
                className="ml-4 rounded px-3 py-1 text-sm text-red-600 border border-red-200 hover:bg-red-50 disabled:opacity-50 transition-colors"
              >
                Archive
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default OutboxPage;

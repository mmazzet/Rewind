import React from "react";
import { useSuspenseQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { inboxApi } from "../api/inboxApi";
import type { ReceivedTapeListItem } from "../types";

const InboxPage: React.FC = () => {
  const { data } = useSuspenseQuery({
    queryKey: ["tapes", "received"],
    queryFn: () => inboxApi.getReceivedTapes(),
  });

  return (
    <div className="max-w-2xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Received tapes</h1>

      {data.length === 0 ? (
        <p className="text-gray-500">You have not received any tapes yet.</p>
      ) : (
        <ul className="flex flex-col gap-4">
          {data.map((tape: ReceivedTapeListItem) => {
            const card = (
              <>
                <span className="font-semibold text-gray-900">
                  {tape.title}
                </span>
                {/* sender_id is a number for now — Phase 7 will add sender_email */}
                <span className="text-sm text-gray-500">
                  From: user #{tape.sender_id}
                </span>
                <span className="text-sm text-gray-500">
                  {new Date(tape.sent_at).toLocaleDateString()}
                </span>
                <span className="text-xs font-medium uppercase tracking-wide text-indigo-600">
                  {tape.status}
                </span>
                {tape.spotify_playlist_url && (
                  <a
                    href={tape.spotify_playlist_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    onClick={(e) => e.stopPropagation()}
                    className="text-sm text-green-600 hover:underline mt-1"
                  >
                    Listen on Spotify →
                  </a>
                )}
              </>
            );

            if (tape.public_token) {
              return (
                <li
                  key={tape.id}
                  className="flex flex-col gap-1 rounded-lg border border-gray-200 bg-white p-4 shadow-sm hover:border-indigo-300 hover:shadow-md transition-all"
                >
                  <Link
                    to={`/tape/${tape.public_token}`}
                    className="flex flex-col gap-1"
                  >
                    {card}
                  </Link>
                </li>
              );
            }

            return (
              <li
                key={tape.id}
                className="flex flex-col gap-1 rounded-lg border border-gray-200 bg-white p-4 shadow-sm"
              >
                {card}
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
};

export default InboxPage;
